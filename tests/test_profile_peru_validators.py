"""Tests for :mod:`xpertik_odontograma.profiles.peru.validators` (REQ-4.x + REQ-3.3).

Covers three public callables:

* :func:`resolve_color` — symbolic → hex (REQ-3.3).
* :func:`validate_peru_strict` — write-path validator (REQ-4.1–4.8).
* :func:`sanitize_peru` — tolerant read-path; never raises.

Cross-teeth rejection: one test per expected key (REQ-11.3). Each asserts
the ``cross_teeth_deferred_peru`` code AND an error message mentioning
``v0.3.0`` or ``entre piezas`` — consumers keying off either word catch the
"deferred" class of failure in admin output.
"""

from __future__ import annotations

import logging

import pytest
from django.core.exceptions import ValidationError

from xpertik_odontograma.profiles.peru.constants import AZUL_NORMA, ROJO_NORMA
from xpertik_odontograma.profiles.peru.states import (
    PeruNomenclatura,
    _add_extension,
    _reset_extended_catalog,
)
from xpertik_odontograma.profiles.peru.validators import (
    resolve_color,
    sanitize_peru,
    validate_peru_strict,
)

CROSS_TEETH_KEYS = [
    "aparato_orto_fijo",
    "aparato_orto_removible",
    "diastema",
    "geminacion_fusion",
    "transposicion",
    "supernumerario",
]


@pytest.fixture
def clean_extended_catalog():
    """Reset the runtime catalog after tests that mutate it via ``_add_extension``."""
    _reset_extended_catalog()
    yield
    _reset_extended_catalog()


# ===========================================================================
# resolve_color (REQ-3.3)
# ===========================================================================


class TestResolveColor:
    def test_rojo_resolves_to_d32f2f(self):
        assert resolve_color("rojo") == "#d32f2f"
        assert resolve_color("rojo") == ROJO_NORMA

    def test_azul_resolves_to_1565c0(self):
        assert resolve_color("azul") == "#1565c0"
        assert resolve_color("azul") == AZUL_NORMA

    def test_verde_rejected(self):
        with pytest.raises(ValueError):
            resolve_color("verde")

    def test_empty_rejected(self):
        with pytest.raises(ValueError):
            resolve_color("")

    def test_hex_rejected(self):
        # Disp. V.7: consumers cannot smuggle hex values through the resolver.
        with pytest.raises(ValueError):
            resolve_color("#d32f2f")

    def test_uppercase_rejected(self):
        # Only lowercase symbolic names match; case-sensitivity is intentional.
        with pytest.raises(ValueError):
            resolve_color("ROJO")


# ===========================================================================
# validate_peru_strict — PASS paths (REQ-4.2, REQ-4.5, REQ-4.6)
# ===========================================================================


class TestValidatePeruStrictPass:
    def test_empty_dict_passes(self):
        validate_peru_strict({}, "permanente")

    def test_none_tolerated(self):
        # Base validator handles None; peru layer must not double-raise.
        validate_peru_strict(None, "permanente")

    def test_caries_on_oclusal_face_passes(self):
        value = {"16": {"caras": {"oclusal_incisal": "caries"}}}
        validate_peru_strict(value, "permanente")

    def test_corona_definitiva_with_valid_tipo_passes(self):
        value = {"21": {"estado": "corona_definitiva", "parametros": {"tipo": "CC"}}}
        validate_peru_strict(value, "permanente")

    def test_movilidad_with_grado_2_passes(self):
        value = {"16": {"estado": "movilidad", "parametros": {"grado": 2}}}
        validate_peru_strict(value, "permanente")

    def test_restauracion_with_material_r_passes(self):
        value = {
            "16": {"estado": "restauracion", "parametros": {"material": "R"}}
        }
        validate_peru_strict(value, "permanente")

    def test_tratamiento_pulpar_with_tipo_tc_passes(self):
        value = {
            "16": {"estado": "tratamiento_pulpar", "parametros": {"tipo": "TC"}}
        }
        validate_peru_strict(value, "permanente")

    def test_parametros_with_extra_keys_allowed(self):
        # The schema enforces REQUIRED keys + allowed values; extra keys are
        # permitted (permissive on consumer extension). Phase 2 finding.
        value = {
            "16": {
                "estado": "movilidad",
                "parametros": {"grado": 2, "extra": "foo"},
            }
        }
        validate_peru_strict(value, "permanente")

    def test_especificaciones_generales_as_string_passes(self):
        value = {"especificaciones_generales": "Hallazgos radiográficos: foo"}
        validate_peru_strict(value, "permanente")

    def test_per_tooth_especificaciones_as_string_passes(self):
        value = {
            "16": {
                "caras": {"oclusal_incisal": "caries"},
                "especificaciones": "dolor al frío",
            }
        }
        validate_peru_strict(value, "permanente")

    def test_valid_extension_accepted(self, clean_extended_catalog):
        # Pre-register an extension via the test hook that mirrors the
        # runtime merge path. The validator must treat it as first-class.
        from xpertik_odontograma.profiles.peru.constants import Categoria, Zona

        _add_extension(
            PeruNomenclatura(
                key="implante_corto",
                label="Implante corto",
                color_symbolic="azul",
                zona=Zona.CORONA,
                categoria=Categoria.TRATAMIENTO,
                clausula_norma="extension",
            )
        )
        value = {"16": {"estado": "implante_corto"}}
        validate_peru_strict(value, "permanente")


# ===========================================================================
# validate_peru_strict — cross-teeth rejections (REQ-4.4, REQ-11.3)
# ===========================================================================


@pytest.mark.parametrize("cross_key", CROSS_TEETH_KEYS)
def test_cross_teeth_estado_rejected(cross_key):
    """Each of the 6 cross-teeth entries MUST raise with v0.3.0 pointer."""
    value = {"16": {"estado": cross_key}}
    with pytest.raises(ValidationError) as excinfo:
        validate_peru_strict(value, "permanente")

    message = str(excinfo.value)
    assert "v0.3" in message or "entre piezas" in message.lower(), (
        f"cross-teeth rejection for {cross_key!r} must mention v0.3.0 or "
        f"'entre piezas'; got: {message!r}"
    )

    # Each offense carries code=cross_teeth_deferred_peru.
    codes = {err.code for err in excinfo.value.error_list}
    assert "cross_teeth_deferred_peru" in codes


@pytest.mark.parametrize("cross_key", CROSS_TEETH_KEYS)
def test_cross_teeth_on_face_rejected(cross_key):
    """Cross-teeth key used on a face value is also rejected."""
    value = {"16": {"caras": {"oclusal_incisal": cross_key}}}
    with pytest.raises(ValidationError):
        validate_peru_strict(value, "permanente")


# ===========================================================================
# validate_peru_strict — other rejections (REQ-4.3, REQ-2.7 parametros)
# ===========================================================================


class TestValidatePeruStrictReject:
    def test_unknown_nomenclatura_rejected(self):
        value = {"16": {"estado": "corona_de_platino"}}
        with pytest.raises(ValidationError) as excinfo:
            validate_peru_strict(value, "permanente")
        codes = {err.code for err in excinfo.value.error_list}
        assert "unknown_nomenclatura_peru" in codes

    def test_movilidad_without_parametros_rejected(self):
        # Phase 2 finding: parametros schema enforces REQUIRED keys. Missing
        # `grado` is rejected even though the estado key itself is known.
        value = {"16": {"estado": "movilidad"}}
        with pytest.raises(ValidationError):
            validate_peru_strict(value, "permanente")

    def test_movilidad_with_invalid_grado_rejected(self):
        value = {"16": {"estado": "movilidad", "parametros": {"grado": 99}}}
        with pytest.raises(ValidationError) as excinfo:
            validate_peru_strict(value, "permanente")
        codes = {err.code for err in excinfo.value.error_list}
        assert "invalid_parametro" in codes

    def test_corona_definitiva_without_tipo_rejected(self):
        value = {"16": {"estado": "corona_definitiva"}}
        with pytest.raises(ValidationError):
            validate_peru_strict(value, "permanente")

    def test_restauracion_with_invalid_material_rejected(self):
        value = {
            "16": {
                "estado": "restauracion",
                "parametros": {"material": "NOT_A_CODE"},
            }
        }
        with pytest.raises(ValidationError):
            validate_peru_strict(value, "permanente")

    def test_unknown_face_value_rejected(self):
        value = {"16": {"caras": {"oclusal_incisal": "invented_state"}}}
        with pytest.raises(ValidationError):
            validate_peru_strict(value, "permanente")

    def test_especificaciones_generales_as_int_rejected(self):
        value = {"especificaciones_generales": 42}
        with pytest.raises(ValidationError) as excinfo:
            validate_peru_strict(value, "permanente")
        codes = {err.code for err in excinfo.value.error_list}
        assert "especificaciones_not_str" in codes

    def test_especificaciones_generales_as_list_rejected(self):
        value = {"especificaciones_generales": ["list", "of", "strs"]}
        with pytest.raises(ValidationError):
            validate_peru_strict(value, "permanente")

    def test_per_tooth_especificaciones_as_int_rejected(self):
        value = {
            "16": {
                "caras": {"oclusal_incisal": "caries"},
                "especificaciones": 123,
            }
        }
        with pytest.raises(ValidationError):
            validate_peru_strict(value, "permanente")


# ===========================================================================
# validate_peru_strict — logging (REQ-4.8)
# ===========================================================================


def test_strict_validator_logs_rejection(caplog):
    caplog.set_level(
        logging.WARNING, logger="xpertik_odontograma.profiles.peru.validators"
    )
    with pytest.raises(ValidationError):
        validate_peru_strict({"16": {"estado": "corona_de_platino"}}, "permanente")
    # At least one WARNING was emitted naming the failing code.
    assert any(
        "unknown_nomenclatura_peru" in r.getMessage() for r in caplog.records
    )


# ===========================================================================
# sanitize_peru — tolerant read path
# ===========================================================================


class TestSanitizePeru:
    def test_empty_returns_empty(self):
        assert sanitize_peru({}, "permanente") == {}

    def test_non_dict_returns_empty(self):
        assert sanitize_peru("not-a-dict", "permanente") == {}

    def test_valid_data_preserved(self):
        value = {"16": {"caras": {"oclusal_incisal": "caries"}}}
        result = sanitize_peru(value, "permanente")
        assert result == value

    def test_unknown_estado_preserved_and_logged(self, caplog):
        caplog.set_level(
            logging.WARNING,
            logger="xpertik_odontograma.profiles.peru.legacy_state",
        )
        result = sanitize_peru(
            {"16": {"estado": "mystery_key"}}, "permanente"
        )
        assert result["16"]["estado"] == "mystery_key"
        assert "mystery_key" in caplog.text

    def test_unknown_face_value_preserved_and_logged(self, caplog):
        caplog.set_level(
            logging.WARNING,
            logger="xpertik_odontograma.profiles.peru.legacy_state",
        )
        result = sanitize_peru(
            {"16": {"caras": {"oclusal_incisal": "mystery"}}}, "permanente"
        )
        assert result["16"]["caras"]["oclusal_incisal"] == "mystery"
        assert "mystery" in caplog.text

    def test_especificaciones_generales_string_preserved(self):
        result = sanitize_peru(
            {"especificaciones_generales": "nota"}, "permanente"
        )
        assert result["especificaciones_generales"] == "nota"

    def test_never_raises_on_malformed_entries(self):
        # Tolerant path must survive anything the widget could receive.
        sanitize_peru({"16": "not-a-dict"}, "permanente")
        sanitize_peru({"16": None}, "permanente")
        sanitize_peru({"especificaciones_generales": 42}, "permanente")
