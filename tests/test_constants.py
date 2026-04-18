"""Tests for :mod:`xpertik_odontograma.constants`.

Covers:

* Exact length + membership of the FDI tooth sets (REQ-2.1, REQ-2.2).
* Canonical 5-face key tuple (REQ-2.3, D1).
* Absence-cause tuple (REQ-2.4).
* :func:`dientes_por_denticion` happy path + invalid input.
* :func:`face_label` anterior/posterior and upper/lower semantics (REQ-7.5, ADR-11),
  including the v0.1.0 simplification of ``vestibular_bucal`` to "Vestibular".
"""

from __future__ import annotations

import pytest

from xpertik_odontograma.constants import (
    CARAS,
    CAUSAS_AUSENCIA,
    DIENTES_PERMANENTES,
    DIENTES_TEMPORALES,
    dientes_por_denticion,
    face_label,
)


# ---------------------------------------------------------------------------
# FDI tooth sets
# ---------------------------------------------------------------------------


def test_permanentes_has_32_codes():
    assert len(DIENTES_PERMANENTES) == 32


def test_temporales_has_20_codes():
    assert len(DIENTES_TEMPORALES) == 20


def test_permanentes_are_unique():
    assert len(set(DIENTES_PERMANENTES)) == 32


def test_temporales_are_unique():
    assert len(set(DIENTES_TEMPORALES)) == 20


def test_no_overlap_between_permanentes_and_temporales():
    assert set(DIENTES_PERMANENTES).isdisjoint(DIENTES_TEMPORALES)


# ---------------------------------------------------------------------------
# Canonical face keys and causes
# ---------------------------------------------------------------------------


def test_caras_exact_order_and_keys():
    assert CARAS == (
        "oclusal_incisal",
        "mesial",
        "distal",
        "vestibular_bucal",
        "lingual_palatino",
    )


def test_causas_ausencia_exact_contents():
    assert CAUSAS_AUSENCIA == ("extraccion", "exfoliacion", "agenesia")


# ---------------------------------------------------------------------------
# dientes_por_denticion helper
# ---------------------------------------------------------------------------


def test_dientes_por_denticion_permanente():
    assert dientes_por_denticion("permanente") == DIENTES_PERMANENTES


def test_dientes_por_denticion_temporal():
    assert dientes_por_denticion("temporal") == DIENTES_TEMPORALES


def test_dientes_por_denticion_mixta_length():
    # 32 permanentes + 20 temporales (D2 allows coexistence).
    assert len(dientes_por_denticion("mixta")) == 52


def test_dientes_por_denticion_invalid_raises():
    with pytest.raises(ValueError):
        dientes_por_denticion("badvalue")


# ---------------------------------------------------------------------------
# face_label — ADR-11, REQ-7.5
# ---------------------------------------------------------------------------


def test_face_label_posterior_upper_is_oclusal():
    # Tooth 16 is an upper-right permanent molar (posterior).
    assert str(face_label(16, "oclusal_incisal")) == "Oclusal"


def test_face_label_anterior_upper_is_incisal():
    # Tooth 11 is an upper-right permanent central incisor (anterior).
    assert str(face_label(11, "oclusal_incisal")) == "Incisal"


def test_face_label_upper_lingual_palatino_is_palatino():
    # Quadrants 1, 2, 5, 6 are upper → "Palatino".
    assert str(face_label(16, "lingual_palatino")) == "Palatino"


def test_face_label_lower_lingual_palatino_is_lingual():
    # Quadrants 3, 4, 7, 8 are lower → "Lingual".
    assert str(face_label(36, "lingual_palatino")) == "Lingual"


def test_face_label_temporal_anterior_upper_is_incisal():
    # Tooth 51 is an upper-right primary central incisor (anterior).
    assert str(face_label(51, "oclusal_incisal")) == "Incisal"


def test_face_label_temporal_lower_lingual_palatino_is_lingual():
    # Tooth 75 is a lower-left primary molar → lingual (lower).
    assert str(face_label(75, "lingual_palatino")) == "Lingual"


def test_face_label_vestibular_bucal_is_vestibular_simplification():
    # v0.1.0 documented simplification: always "Vestibular".
    assert str(face_label(11, "vestibular_bucal")) == "Vestibular"
    assert str(face_label(16, "vestibular_bucal")) == "Vestibular"
    assert str(face_label(36, "vestibular_bucal")) == "Vestibular"


def test_face_label_mesial_is_mesial():
    assert str(face_label(16, "mesial")) == "Mesial"


def test_face_label_distal_is_distal():
    assert str(face_label(16, "distal")) == "Distal"


def test_face_label_invalid_face_key_raises():
    with pytest.raises(ValueError):
        face_label(16, "bad_face")
