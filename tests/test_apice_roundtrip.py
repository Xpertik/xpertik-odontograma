"""Phase 7 — apice DB roundtrip tests (v0.3.0-alpha.1).

The v0.3.0 schema adds an optional per-tooth ``apice`` key alongside
``caras`` (REQ-4.1). These tests exercise the full write path end-to-end:

* Base validator + peru validator accept the new shape.
* SQLite roundtrip through :class:`PatientPeru` preserves the dict.
* apice is additive — v0.2.0-shaped data (no ``apice``) still works.
* apice + caras can coexist (different anatomical zones).
* Global ``estado`` XOR (``caras`` or ``apice``) — mixing raises
  ``ValidationError``.
* Peru strict rejects coronal nomenclaturas under ``apice`` with
  ``wrong_zone_for_apice``.
"""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError

from .models import PatientPeru

# ---------------------------------------------------------------------------
# Happy-path roundtrips
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_apice_tratamiento_pulpar_roundtrip_preserves_dict() -> None:
    # Canonical apice shape from REQ-4.1 example.
    payload = {
        "16": {
            "apice": {"estado": "tratamiento_pulpar", "parametros": {"tipo": "TC"}}
        }
    }
    p = PatientPeru.objects.create(name="tc", odontograma=payload)
    reloaded = PatientPeru.objects.get(pk=p.pk)
    assert reloaded.odontograma == payload


@pytest.mark.django_db
def test_apice_full_clean_does_not_raise_for_valid_tipo() -> None:
    for tipo in ("TC", "PC", "PP"):
        p = PatientPeru(
            name=f"tipo-{tipo}",
            odontograma={
                "16": {
                    "apice": {
                        "estado": "tratamiento_pulpar",
                        "parametros": {"tipo": tipo},
                    }
                }
            },
        )
        p.full_clean()  # must not raise


@pytest.mark.django_db
def test_apice_remanente_radicular_roundtrip() -> None:
    # Remanente radicular has no parametros — just estado on apice.
    payload = {"16": {"apice": {"estado": "remanente_radicular"}}}
    p = PatientPeru.objects.create(name="rr", odontograma=payload)
    p.full_clean()
    reloaded = PatientPeru.objects.get(pk=p.pk)
    assert reloaded.odontograma == payload


@pytest.mark.django_db
def test_apice_and_caras_coexist_roundtrip() -> None:
    # Clinically realistic: caries oclusal + tratamiento pulpar en raíz.
    payload = {
        "16": {
            "caras": {"oclusal_incisal": "caries"},
            "apice": {
                "estado": "tratamiento_pulpar",
                "parametros": {"tipo": "TC"},
            },
        }
    }
    p = PatientPeru.objects.create(name="mix", odontograma=payload)
    p.full_clean()
    reloaded = PatientPeru.objects.get(pk=p.pk)
    assert reloaded.odontograma["16"]["caras"] == {"oclusal_incisal": "caries"}
    assert reloaded.odontograma["16"]["apice"]["estado"] == "tratamiento_pulpar"


# ---------------------------------------------------------------------------
# Backward compat — v0.2.0 shape survives
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_v0_2_payload_without_apice_still_roundtrips() -> None:
    # v0.2.0 canonical shape — no apice key at all.
    payload = {"16": {"caras": {"oclusal_incisal": "caries"}}}
    p = PatientPeru.objects.create(name="v2", odontograma=payload)
    reloaded = PatientPeru.objects.get(pk=p.pk)
    assert reloaded.odontograma == payload
    # No ghost `apice` key appears on reload.
    assert "apice" not in reloaded.odontograma["16"]


# ---------------------------------------------------------------------------
# XOR invariant — estado vs per-zone data
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_estado_plus_apice_raises_validation_error() -> None:
    # XOR: whole-tooth estado cannot coexist with per-zone apice (base validator).
    p = PatientPeru(
        name="bad",
        odontograma={
            "16": {
                "estado": "ausente",
                "apice": {"estado": "tratamiento_pulpar"},
            }
        },
    )
    with pytest.raises(ValidationError):
        p.full_clean()


@pytest.mark.django_db
def test_apice_missing_estado_raises_validation_error() -> None:
    # Base validator: `apice` dict without `estado` is rejected.
    p = PatientPeru(
        name="bad",
        odontograma={"16": {"apice": {"parametros": {"tipo": "TC"}}}},
    )
    with pytest.raises(ValidationError):
        p.full_clean()


# ---------------------------------------------------------------------------
# Peru zone enforcement — wrong_zone_for_apice
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_coronal_nomenclatura_rejected_in_apice() -> None:
    # `caries` has zona=CORONA — peru strict must reject it under apice.
    p = PatientPeru(
        name="bad",
        odontograma={"16": {"apice": {"estado": "caries"}}},
    )
    with pytest.raises(ValidationError) as exc_info:
        p.full_clean()
    # ``full_clean`` aggregates per-field errors; the odontograma field
    # emits one wrapper ValidationError whose message cites the zona.
    # Scan both error_dict and stringified form to stay resilient across
    # Django versions.
    err_repr = str(exc_info.value)
    assert "zona" in err_repr
    assert "caries" in err_repr


@pytest.mark.django_db
def test_apice_invalid_parametro_raises_validation_error() -> None:
    # tratamiento_pulpar accepts tipo ∈ {TC, PC, PP}. XX is out-of-schema.
    p = PatientPeru(
        name="bad",
        odontograma={
            "16": {
                "apice": {
                    "estado": "tratamiento_pulpar",
                    "parametros": {"tipo": "XX"},
                }
            }
        },
    )
    with pytest.raises(ValidationError):
        p.full_clean()


@pytest.mark.django_db
def test_apice_with_unknown_estado_raises_validation_error() -> None:
    # Estado not in the peru catalog — peru strict flags it.
    p = PatientPeru(
        name="bad",
        odontograma={"16": {"apice": {"estado": "not_in_catalog"}}},
    )
    with pytest.raises(ValidationError):
        p.full_clean()
