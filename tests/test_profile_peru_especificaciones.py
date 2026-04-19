"""Tests for :mod:`xpertik_odontograma.profiles.peru.specifications` (REQ-8.x).

Covers the four public helpers:

* :func:`validate_especificaciones_shape` — raises
  ``ValidationError(code="especificaciones_not_str")`` on non-string input.
* :func:`extract_tooth_especificaciones` — tolerant reader, coerces
  non-string / missing → ``""``.
* :func:`extract_global_especificaciones` — tolerant reader for the
  top-level key.
* :func:`set_tooth_especificaciones` / :func:`set_global_especificaciones` —
  write helpers that drop empty strings (REQ-8.3 normalization).

Also pins the integration against the strict validator — v0.1.0 data
(without any ``especificaciones*`` key) MUST validate unchanged under the
peru profile (REQ-8.4 backward compat).
"""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError

from xpertik_odontograma.profiles.peru.specifications import (
    extract_global_especificaciones,
    extract_tooth_especificaciones,
    set_global_especificaciones,
    set_tooth_especificaciones,
    validate_especificaciones_shape,
)
from xpertik_odontograma.profiles.peru.validators import validate_peru_strict

# ---------------------------------------------------------------------------
# validate_especificaciones_shape (REQ-8.1, REQ-8.2)
# ---------------------------------------------------------------------------


class TestValidateShape:
    def test_none_is_ok(self):
        validate_especificaciones_shape(None, field="x")

    def test_string_is_ok(self):
        validate_especificaciones_shape("nota", field="x")

    def test_empty_string_is_ok(self):
        # Shape-wise an empty string is a string. The REQ-8.3 empty-≡-absent
        # rule is enforced by set_* helpers, not by the validator.
        validate_especificaciones_shape("", field="x")

    def test_int_rejected_with_stable_code(self):
        with pytest.raises(ValidationError) as excinfo:
            validate_especificaciones_shape(42, field="x")
        assert excinfo.value.code == "especificaciones_not_str"

    def test_list_rejected(self):
        with pytest.raises(ValidationError):
            validate_especificaciones_shape(["a", "b"], field="x")

    def test_dict_rejected(self):
        with pytest.raises(ValidationError):
            validate_especificaciones_shape({"k": "v"}, field="x")


# ---------------------------------------------------------------------------
# extract_tooth_especificaciones
# ---------------------------------------------------------------------------


class TestExtractTooth:
    def test_missing_returns_empty_string(self):
        assert extract_tooth_especificaciones({"caras": {}}) == ""

    def test_present_string_preserved(self):
        assert (
            extract_tooth_especificaciones({"especificaciones": "nota"})
            == "nota"
        )

    def test_non_string_coerced_to_empty(self):
        # Read-path is tolerant — widget must not crash on legacy data.
        assert extract_tooth_especificaciones({"especificaciones": 42}) == ""

    def test_empty_string_preserved_as_empty(self):
        assert extract_tooth_especificaciones({"especificaciones": ""}) == ""


# ---------------------------------------------------------------------------
# extract_global_especificaciones
# ---------------------------------------------------------------------------


class TestExtractGlobal:
    def test_missing_returns_empty(self):
        assert extract_global_especificaciones({}) == ""

    def test_present_string_preserved(self):
        assert (
            extract_global_especificaciones(
                {"especificaciones_generales": "global note"}
            )
            == "global note"
        )

    def test_non_dict_input_returns_empty(self):
        assert extract_global_especificaciones("not-a-dict") == ""

    def test_non_string_payload_returns_empty(self):
        assert (
            extract_global_especificaciones({"especificaciones_generales": 42})
            == ""
        )


# ---------------------------------------------------------------------------
# set_tooth_especificaciones (REQ-8.3 — empty drops the key)
# ---------------------------------------------------------------------------


class TestSetTooth:
    def test_writes_string_value(self):
        entry = set_tooth_especificaciones({"caras": {}}, "nota")
        assert entry["especificaciones"] == "nota"
        assert entry["caras"] == {}

    def test_empty_drops_key(self):
        entry = set_tooth_especificaciones({"especificaciones": "old"}, "")
        assert "especificaciones" not in entry

    def test_does_not_mutate_original(self):
        original = {"caras": {}}
        entry = set_tooth_especificaciones(original, "nota")
        assert "especificaciones" not in original
        assert entry is not original


# ---------------------------------------------------------------------------
# set_global_especificaciones
# ---------------------------------------------------------------------------


class TestSetGlobal:
    def test_writes_string_value(self):
        new = set_global_especificaciones({}, "global")
        assert new["especificaciones_generales"] == "global"

    def test_empty_drops_key(self):
        new = set_global_especificaciones(
            {"especificaciones_generales": "old"}, ""
        )
        assert "especificaciones_generales" not in new

    def test_does_not_mutate_original(self):
        original = {"especificaciones_generales": "old"}
        new = set_global_especificaciones(original, "fresh")
        assert original["especificaciones_generales"] == "old"
        assert new["especificaciones_generales"] == "fresh"


# ---------------------------------------------------------------------------
# Integration — peru strict validator accepts/rejects as expected
# ---------------------------------------------------------------------------


class TestValidatorIntegration:
    def test_per_tooth_specs_pass(self):
        value = {
            "16": {
                "caras": {"oclusal_incisal": "caries"},
                "especificaciones": "dolor al frío",
            }
        }
        validate_peru_strict(value, "permanente")

    def test_global_specs_pass(self):
        value = {"especificaciones_generales": "findings"}
        validate_peru_strict(value, "permanente")

    def test_both_per_tooth_and_global_specs_pass(self):
        value = {
            "16": {
                "caras": {"oclusal_incisal": "caries"},
                "especificaciones": "note",
            },
            "especificaciones_generales": "global note",
        }
        validate_peru_strict(value, "permanente")

    def test_v0_1_shape_without_specs_passes(self):
        # REQ-8.4 backward compat: data that predates v0.2.0 has no
        # `especificaciones*` keys — peru strict must accept it.
        value = {"16": {"caras": {"oclusal_incisal": "caries"}}}
        validate_peru_strict(value, "permanente")

    def test_per_tooth_non_string_rejected(self):
        value = {
            "16": {
                "caras": {"oclusal_incisal": "caries"},
                "especificaciones": 123,
            }
        }
        with pytest.raises(ValidationError):
            validate_peru_strict(value, "permanente")

    def test_global_non_string_rejected(self):
        value = {"especificaciones_generales": {"not": "a string"}}
        with pytest.raises(ValidationError):
            validate_peru_strict(value, "permanente")
