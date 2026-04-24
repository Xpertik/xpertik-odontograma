"""v0.2.0 backward-compat regression tests (v0.3.0-alpha.1).

The v0.3.0 release swapped the HTML placeholder widget for a SVG renderer
and added the optional per-tooth ``apice`` key. The data layer is fully
additive — v0.2.0 consumers upgrading must see ZERO behavior change in
their existing payloads.

These tests guard that promise:

* A v0.2.0-shaped JSON payload (no ``apice``) round-trips through the
  peru strict validator unchanged.
* :class:`PatientPeru` saves + reloads v0.2.0 data identically.
* :class:`OdontogramaSvgWidget` and :class:`PeruOdontogramaWidget` render
  v0.2.0 data without crashing and without inventing ``apice`` keys.
* The base :class:`OdontogramaField` still accepts ``profile=None``
  byte-identically to v0.2.0.
"""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError

from xpertik_odontograma.fields import OdontogramaField
from xpertik_odontograma.profiles.peru.validators import validate_peru_strict
from xpertik_odontograma.profiles.peru.widgets import PeruOdontogramaWidget
from xpertik_odontograma.validators import validate_odontograma_strict
from xpertik_odontograma.widgets import OdontogramaSvgWidget

from .models import Patient, PatientPeru

# ---------------------------------------------------------------------------
# v0.2.0 JSON payloads — strict validator still accepts them
# ---------------------------------------------------------------------------

_V0_2_SIMPLE_CARIES = {"16": {"caras": {"oclusal_incisal": "caries"}}}

_V0_2_IMPLANTE = {"36": {"estado": "implante"}}

_V0_2_WITH_ESPECIFICACIONES = {
    "16": {
        "caras": {"oclusal_incisal": "caries"},
        "especificaciones": "Dolor al frío",
    },
    "especificaciones_generales": "Paciente con sensibilidad generalizada",
}


@pytest.mark.parametrize(
    "payload",
    [
        _V0_2_SIMPLE_CARIES,
        _V0_2_IMPLANTE,
        _V0_2_WITH_ESPECIFICACIONES,
    ],
)
def test_v0_2_payload_passes_peru_strict(payload: dict) -> None:
    # The strict validator must swallow v0.2.0 data without complaint.
    validate_odontograma_strict(payload, "permanente", profile="peru")


@pytest.mark.parametrize(
    "payload",
    [
        _V0_2_SIMPLE_CARIES,
        _V0_2_IMPLANTE,
    ],
)
def test_v0_2_payload_passes_direct_peru_strict_call(payload: dict) -> None:
    # Direct call (no registry dispatch) must also accept v0.2.0 shapes.
    validate_peru_strict(payload, "permanente")


# ---------------------------------------------------------------------------
# v0.2.0 DB roundtrip — no migrations, no ghost keys
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_v0_2_payload_roundtrips_through_patient_peru() -> None:
    p = PatientPeru.objects.create(name="v2", odontograma=_V0_2_SIMPLE_CARIES)
    p.full_clean()
    reloaded = PatientPeru.objects.get(pk=p.pk)
    assert reloaded.odontograma == _V0_2_SIMPLE_CARIES
    # The v0.3.0 optional key MUST NOT be invented on reload.
    for tooth_payload in reloaded.odontograma.values():
        if isinstance(tooth_payload, dict):
            assert "apice" not in tooth_payload


@pytest.mark.django_db
def test_v0_2_patient_full_clean_accepts_legacy_v0_1_data() -> None:
    # The v0.1 Patient model (no profile) must keep working in v0.3.0.
    p = Patient.objects.create(
        name="v1", odontograma_permanente=_V0_2_SIMPLE_CARIES
    )
    p.full_clean()
    reloaded = Patient.objects.get(pk=p.pk)
    assert reloaded.odontograma_permanente == _V0_2_SIMPLE_CARIES


# ---------------------------------------------------------------------------
# v0.2.0 field API — profile=None behavior unchanged
# ---------------------------------------------------------------------------


def test_default_field_profile_none_matches_v0_2() -> None:
    # OdontogramaField() with no kwargs still has profile=None.
    assert OdontogramaField().profile is None


def test_explicit_profile_none_does_not_leak_into_deconstruct() -> None:
    f = OdontogramaField(profile=None)
    _name, _path, _args, kwargs = f.deconstruct()
    assert "profile" not in kwargs


# ---------------------------------------------------------------------------
# Widget render — v0.2.0 payloads do not crash
# ---------------------------------------------------------------------------


def test_base_svg_widget_renders_v0_2_payload_without_crash() -> None:
    w = OdontogramaSvgWidget(denticion="permanente")
    html = w.render("od", _V0_2_SIMPLE_CARIES, {})
    # SVG still produced, no apice state bleed.
    assert "<svg" in html
    assert 'data-fdi="16"' in html


def test_peru_svg_widget_renders_v0_2_payload_without_crash() -> None:
    w = PeruOdontogramaWidget(denticion="permanente")
    html = w.render("od", _V0_2_SIMPLE_CARIES, {})
    assert "<svg" in html
    # The catalog JSON blob is emitted regardless of payload.
    assert '<script type="application/json"' in html


def test_peru_svg_widget_renders_v0_2_with_especificaciones() -> None:
    w = PeruOdontogramaWidget(denticion="permanente")
    html = w.render("od", _V0_2_WITH_ESPECIFICACIONES, {})
    # Must not crash; must still produce tooth groups.
    assert '<g class="xp-tooth' in html


def test_peru_svg_widget_accepts_empty_v0_2_dict() -> None:
    # A fresh v0.2.0 record starts as {} — render must not crash.
    w = PeruOdontogramaWidget(denticion="permanente")
    html = w.render("od", {}, {})
    assert "<svg" in html


# ---------------------------------------------------------------------------
# XOR invariant — still enforced as in v0.2.0
# ---------------------------------------------------------------------------


def test_v0_2_both_estado_and_caras_still_rejected() -> None:
    # Same rejection contract as v0.2.0 — just keeping it visible here.
    payload = {"16": {"estado": "corona", "caras": {"oclusal_incisal": "caries"}}}
    with pytest.raises(ValidationError):
        validate_odontograma_strict(payload, "permanente")


# ---------------------------------------------------------------------------
# Value marshalling — JSON payload survives the widget wire format
# ---------------------------------------------------------------------------


def test_value_from_datadict_passes_raw_json_string_through() -> None:
    """value_from_datadict returns the raw JSON string from POST data.

    Django's ``forms.JSONField.to_python`` parses the string into a dict
    during cleaning. Returning a dict here would break ``bound_data`` on
    re-render after a validation error (json.loads expects a string).
    """
    import json

    w = OdontogramaSvgWidget(denticion="permanente")
    payload_str = json.dumps(_V0_2_SIMPLE_CARIES)
    raw = {"odontograma": payload_str}
    parsed = w.value_from_datadict(raw, {}, "odontograma")
    assert parsed == payload_str
    # Pre-parsed dicts (test fixtures) get re-serialized to a string.
    raw_dict = {"odontograma": _V0_2_SIMPLE_CARIES}
    parsed_dict = w.value_from_datadict(raw_dict, {}, "odontograma")
    assert isinstance(parsed_dict, str)
    assert json.loads(parsed_dict) == _V0_2_SIMPLE_CARIES


def test_format_value_accepts_v0_2_dict_directly() -> None:
    w = OdontogramaSvgWidget(denticion="permanente")
    formatted = w.format_value(_V0_2_SIMPLE_CARIES)
    assert formatted == _V0_2_SIMPLE_CARIES
