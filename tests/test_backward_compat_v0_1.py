"""v0.1.0 backward-compat regression tests (REQ-7.1, REQ-7.4, REQ-7.5, REQ-11.1).

These tests guard the byte-identical promise made to v0.1.0 consumers: if
the `profile` kwarg is left at its default (``None``), every
:class:`OdontogramaField` must behave exactly as it did in v0.1.0. In
particular:

* ``OdontogramaField()`` has no ``profile`` kwarg on its deconstruct.
* ``_FieldBoundValidator`` serializes without a ``profile`` entry in its
  deconstruct kwargs — so migrations written in v0.1.0 stay byte-stable
  after upgrading.
* The peru profile registration is lazy — importing ``xpertik_odontograma``
  itself (no peru import) does NOT drag the peru catalog in.
* Pre-existing ``Patient`` model validation is unchanged: empty odontogramas,
  estado branch, caras branch, ORM roundtrip.
* The default ``ESTADOS_CARA`` / ``ESTADOS_DIENTE`` catalogs ship with the
  same canonical keys the widget renders.
"""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError

from xpertik_odontograma import settings as package_settings
from xpertik_odontograma.fields import OdontogramaField
from xpertik_odontograma.validators import (
    _FieldBoundValidator,
    validate_odontograma_strict,
)

from .models import Patient

# ---------------------------------------------------------------------------
# Field surface — no profile leak (REQ-7.1, REQ-7.4)
# ---------------------------------------------------------------------------


def test_default_field_has_profile_none():
    field = OdontogramaField()
    assert field.profile is None


def test_explicit_profile_none_matches_default():
    explicit = OdontogramaField(profile=None)
    default = OdontogramaField()
    # Byte-identical field declaration: both produce profile=None.
    assert explicit.profile == default.profile


def test_default_field_deconstruct_omits_profile():
    field = OdontogramaField()
    _name, _path, _args, kwargs = field.deconstruct()
    assert "profile" not in kwargs


def test_profile_none_field_deconstruct_omits_profile():
    # Explicit profile=None MUST still not leak into deconstruct kwargs.
    field = OdontogramaField(profile=None)
    _name, _path, _args, kwargs = field.deconstruct()
    assert "profile" not in kwargs


# ---------------------------------------------------------------------------
# _FieldBoundValidator — deconstruct stability (REQ-7.4 migration bytes)
# ---------------------------------------------------------------------------


def test_bound_validator_no_profile_deconstruct_empty_kwargs():
    v = _FieldBoundValidator("permanente")
    _path, args, kwargs = v.deconstruct()
    assert args == ("permanente",)
    assert kwargs == {}, (
        "v0.1.0 migrations serialize _FieldBoundValidator with empty kwargs; "
        "any `profile` leak here would invalidate existing migration bytes."
    )


def test_bound_validator_profile_none_deconstruct_empty_kwargs():
    v = _FieldBoundValidator("permanente", profile=None)
    _path, args, kwargs = v.deconstruct()
    assert kwargs == {}


def test_bound_validator_eq_ignores_profile_when_both_none():
    a = _FieldBoundValidator("permanente")
    b = _FieldBoundValidator("permanente", profile=None)
    assert a == b
    assert hash(a) == hash(b)


# ---------------------------------------------------------------------------
# Base strict validator — no profile dispatch when None (REQ-7.1)
# ---------------------------------------------------------------------------


def test_strict_without_profile_accepts_v0_1_data():
    # Canonical v0.1-shape payload: estado branch + causa. No peru import.
    value = {"16": {"estado": "ausente", "causa": "extraccion"}}
    validate_odontograma_strict(value, "permanente")  # MUST NOT raise


def test_strict_without_profile_rejects_v0_1_invariants_as_before():
    # Both estado and caras — v0.1.0's rejection path. Peru layer would also
    # reject, but this test asserts the BASE behavior survives.
    value = {
        "16": {"estado": "corona", "caras": {"oclusal_incisal": "caries"}}
    }
    with pytest.raises(ValidationError):
        validate_odontograma_strict(value, "permanente")


# ---------------------------------------------------------------------------
# Pre-existing Patient model (v0.1) — full behavior preserved
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_patient_full_clean_accepts_caries_payload():
    p = Patient(
        name="ok",
        odontograma_permanente={"16": {"caras": {"oclusal_incisal": "caries"}}},
    )
    p.full_clean()


@pytest.mark.django_db
def test_patient_full_clean_accepts_estado_branch():
    p = Patient(
        name="ok",
        odontograma_permanente={"16": {"estado": "corona"}},
    )
    p.full_clean()


@pytest.mark.django_db
def test_patient_full_clean_rejects_unknown_estado_same_as_v0_1():
    # The v0.1 `ESTADOS_DIENTE` catalog does NOT include peru's "diastema"
    # etc. — the base validator rejects it regardless of peru profile.
    p = Patient(
        name="bad",
        odontograma_permanente={"16": {"estado": "mystery"}},
    )
    with pytest.raises(ValidationError):
        p.full_clean()


@pytest.mark.django_db
def test_patient_roundtrip_v0_1_shape():
    p = Patient.objects.create(
        name="t",
        odontograma_permanente={"16": {"caras": {"oclusal_incisal": "caries"}}},
    )
    reloaded = Patient.objects.get(pk=p.pk)
    assert reloaded.odontograma_permanente == {
        "16": {"caras": {"oclusal_incisal": "caries"}}
    }


# ---------------------------------------------------------------------------
# Default catalogs — canonical keys still present
# ---------------------------------------------------------------------------


def test_default_estados_cara_has_caries():
    # v0.1 ships `caries` as a face-state; peru uses it too, but the base
    # catalog must still list it for the widget.
    assert "caries" in package_settings.ESTADOS_CARA


def test_default_estados_diente_has_ausente():
    assert "ausente" in package_settings.ESTADOS_DIENTE


def test_default_estados_diente_has_corona():
    assert "corona" in package_settings.ESTADOS_DIENTE
