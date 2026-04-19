"""Tests for :mod:`xpertik_odontograma.validators`.

Two public functions under test:

* :func:`validate_odontograma_strict` — write-path, MUST raise on any
  invariant violation (REQ-6.1, REQ-6.2).
* :func:`sanitize_odontograma_for_render` — read-path, MUST NEVER raise;
  logs warnings via the ``xpertik_odontograma.legacy_state`` logger
  (REQ-6.3..6.6).

Log-capture tests use pytest's :func:`caplog` fixture explicitly bound to
the legacy-state logger at WARNING level so each assertion gets clean text
without noise from other loggers.
"""

from __future__ import annotations

import logging

import pytest
from django.core.exceptions import ValidationError

from xpertik_odontograma.validators import (
    sanitize_odontograma_for_render,
    validate_odontograma_strict,
)


# ---------------------------------------------------------------------------
# validate_odontograma_strict — happy paths
# ---------------------------------------------------------------------------


class TestStrictHappyPaths:
    def test_empty_dict_ok(self):
        validate_odontograma_strict({}, "permanente")

    def test_none_ok(self):
        validate_odontograma_strict(None, "permanente")

    def test_caras_branch_ok(self):
        value = {
            "16": {
                "caras": {
                    "oclusal_incisal": "caries",
                    "mesial": None,
                    "distal": None,
                    "vestibular_bucal": None,
                    "lingual_palatino": None,
                }
            }
        }
        validate_odontograma_strict(value, "permanente")

    def test_estado_branch_ok(self):
        validate_odontograma_strict(
            {"16": {"estado": "ausente", "causa": "extraccion"}},
            "permanente",
        )

    def test_estado_without_causa_ok(self):
        validate_odontograma_strict({"16": {"estado": "corona"}}, "permanente")

    def test_mixta_accepts_primary_and_permanent_codes(self):
        # D2: permanent 16 and primary 55 may coexist in a mixta odontograma.
        value = {
            "16": {"estado": "corona"},
            "55": {"estado": "ausente", "causa": "exfoliacion"},
        }
        validate_odontograma_strict(value, "mixta")

    def test_primary_code_valid_for_temporal_denticion(self):
        validate_odontograma_strict(
            {"55": {"estado": "ausente", "causa": "exfoliacion"}},
            "temporal",
        )


# ---------------------------------------------------------------------------
# validate_odontograma_strict — rejection paths
# ---------------------------------------------------------------------------


class TestStrictRejections:
    def test_invalid_fdi_for_permanente(self):
        # 55 is a primary code; invalid for "permanente".
        with pytest.raises(ValidationError):
            validate_odontograma_strict(
                {"55": {"estado": "ausente", "causa": "exfoliacion"}},
                "permanente",
            )

    def test_invalid_fdi_for_temporal(self):
        # 16 is a permanent code; invalid for "temporal".
        with pytest.raises(ValidationError):
            validate_odontograma_strict({"16": {"estado": "corona"}}, "temporal")

    def test_both_estado_and_caras_rejected(self):
        with pytest.raises(ValidationError):
            validate_odontograma_strict(
                {
                    "16": {
                        "estado": "corona",
                        "caras": {"oclusal_incisal": "caries"},
                    }
                },
                "permanente",
            )

    def test_neither_estado_nor_caras_rejected(self):
        with pytest.raises(ValidationError):
            validate_odontograma_strict({"16": {}}, "permanente")

    def test_unknown_face_value_rejected(self):
        with pytest.raises(ValidationError):
            validate_odontograma_strict(
                {"16": {"caras": {"oclusal_incisal": "nonexistent"}}},
                "permanente",
            )

    def test_unknown_face_key_rejected(self):
        with pytest.raises(ValidationError):
            validate_odontograma_strict(
                {"16": {"caras": {"invalid_face": "caries"}}},
                "permanente",
            )

    def test_invalid_causa_value_rejected(self):
        with pytest.raises(ValidationError):
            validate_odontograma_strict(
                {"16": {"estado": "ausente", "causa": "robbed"}},
                "permanente",
            )

    def test_causa_on_non_ausente_rejected(self):
        with pytest.raises(ValidationError):
            validate_odontograma_strict(
                {"16": {"estado": "corona", "causa": "extraccion"}},
                "permanente",
            )

    def test_unexpected_key_under_estado_branch_rejected(self):
        with pytest.raises(ValidationError):
            validate_odontograma_strict(
                {"16": {"estado": "ausente", "unexpected": "value"}},
                "permanente",
            )

    def test_unknown_estado_rejected(self):
        with pytest.raises(ValidationError):
            validate_odontograma_strict(
                {"16": {"estado": "invented"}},
                "permanente",
            )

    def test_non_dict_value_rejected(self):
        with pytest.raises(ValidationError):
            validate_odontograma_strict("not-a-dict", "permanente")

    def test_entry_not_dict_rejected(self):
        with pytest.raises(ValidationError):
            validate_odontograma_strict({"16": "not-a-dict"}, "permanente")


# ---------------------------------------------------------------------------
# sanitize_odontograma_for_render — tolerant read path
# ---------------------------------------------------------------------------


class TestSanitize:
    def test_empty_input_returns_empty_dict(self):
        assert sanitize_odontograma_for_render({}, "permanente") == {}

    def test_none_input_returns_empty_dict(self):
        assert sanitize_odontograma_for_render(None, "permanente") == {}

    def test_valid_input_preserved(self):
        value = {"16": {"estado": "corona"}}
        result = sanitize_odontograma_for_render(value, "permanente")
        assert result == value
        # Result must be a fresh dict (mutation-safe for renderers).
        assert result is not value

    def test_unknown_estado_logs_and_preserves(self, caplog):
        caplog.set_level(logging.WARNING, logger="xpertik_odontograma.legacy_state")
        result = sanitize_odontograma_for_render(
            {"16": {"estado": "mystery_state"}},
            "permanente",
        )
        # Entry preserved verbatim; renderer decides fallback color.
        assert result["16"]["estado"] == "mystery_state"
        # Warning mentions the unknown estado value.
        assert "mystery_state" in caplog.text

    def test_unknown_face_value_logs_and_preserves(self, caplog):
        caplog.set_level(logging.WARNING, logger="xpertik_odontograma.legacy_state")
        result = sanitize_odontograma_for_render(
            {"16": {"caras": {"oclusal_incisal": "mystery_state"}}},
            "permanente",
        )
        assert result["16"]["caras"]["oclusal_incisal"] == "mystery_state"
        assert "mystery_state" in caplog.text

    def test_both_estado_and_caras_prefers_estado_and_drops_caras(self, caplog):
        caplog.set_level(logging.WARNING, logger="xpertik_odontograma.legacy_state")
        result = sanitize_odontograma_for_render(
            {
                "16": {
                    "estado": "corona",
                    "caras": {"oclusal_incisal": "caries"},
                }
            },
            "permanente",
        )
        assert result["16"]["estado"] == "corona"
        assert "caras" not in result["16"]
        # Warning was emitted about the tie-breaker.
        assert "16" in caplog.text

    def test_invalid_fdi_for_denticion_logs_and_preserves(self, caplog):
        caplog.set_level(logging.WARNING, logger="xpertik_odontograma.legacy_state")
        # 55 is a primary code; invalid for "permanente" strict, but tolerant
        # read preserves it (migration/display data-recovery case).
        result = sanitize_odontograma_for_render(
            {"55": {"estado": "ausente"}},
            "permanente",
        )
        assert "55" in result
        assert "55" in caplog.text

    def test_non_dict_input_returns_empty_and_logs(self, caplog):
        caplog.set_level(logging.WARNING, logger="xpertik_odontograma.legacy_state")
        result = sanitize_odontograma_for_render("not-a-dict", "permanente")
        assert result == {}
        assert caplog.text  # one warning line emitted

    def test_unknown_face_key_logs_and_passes_through(self, caplog):
        caplog.set_level(logging.WARNING, logger="xpertik_odontograma.legacy_state")
        result = sanitize_odontograma_for_render(
            {"16": {"caras": {"invalid_face": "caries"}}},
            "permanente",
        )
        # Face key preserved (renderer will ignore unknown keys).
        assert "invalid_face" in result["16"]["caras"]
        assert "invalid_face" in caplog.text

    def test_unknown_denticion_logs_once_but_does_not_raise(self, caplog):
        caplog.set_level(logging.WARNING, logger="xpertik_odontograma.legacy_state")
        # Bad denticion: tolerant — logs a single warning, skips range check.
        result = sanitize_odontograma_for_render(
            {"16": {"estado": "corona"}},
            "badvalue",
        )
        assert "16" in result
        assert "badvalue" in caplog.text
