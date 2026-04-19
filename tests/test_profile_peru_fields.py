"""Tests for :class:`OdontogramaPeruInicialField` (REQ-6.x).

Covers the field's three contract points:

* Class identity encodes the profile — consumers do NOT pass ``profile=``
  (REQ-6.1, REQ-6.2).
* ``deconstruct()`` strips ``profile`` from the kwargs dict (REQ-6.4) so
  migrations stay stable.
* ORM roundtrip preserves per-tooth and global ``especificaciones*`` keys
  byte-for-byte (REQ-6.5).
* ``makemigrations --dry-run`` is idempotent — a second run produces no
  changes (R4).
* ``full_clean()`` chains the peru strict validator and rejects cross-teeth
  input before the DB is touched.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError

from xpertik_odontograma.profiles.peru.fields import OdontogramaPeruInicialField

from .models import PatientPeru

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Instantiation + profile lock (REQ-6.1, REQ-6.2)
# ---------------------------------------------------------------------------


def test_field_instantiates_without_kwargs():
    field = OdontogramaPeruInicialField()
    assert field.profile == "peru"


def test_field_instantiates_with_denticion():
    field = OdontogramaPeruInicialField(denticion="mixta")
    assert field.profile == "peru"
    assert field.denticion == "mixta"


def test_explicit_profile_peru_rejected():
    # Even the "correct" value is rejected — the class identity IS the profile,
    # kwargs would be redundant at best and misleading at worst.
    with pytest.raises(TypeError) as excinfo:
        OdontogramaPeruInicialField(profile="peru")
    message = str(excinfo.value).lower()
    assert "profile" in message and "peru" in message


def test_explicit_profile_chile_rejected():
    with pytest.raises(TypeError):
        OdontogramaPeruInicialField(profile="chile")


def test_explicit_profile_none_rejected():
    # Passing profile=None would try to downgrade to generic validation; block.
    with pytest.raises(TypeError):
        OdontogramaPeruInicialField(profile=None)


# ---------------------------------------------------------------------------
# deconstruct (REQ-6.4)
# ---------------------------------------------------------------------------


def test_deconstruct_omits_profile_kwarg():
    field = OdontogramaPeruInicialField()
    _name, _path, _args, kwargs = field.deconstruct()
    assert "profile" not in kwargs


def test_deconstruct_preserves_denticion_when_non_default():
    field = OdontogramaPeruInicialField(denticion="mixta")
    _name, _path, _args, kwargs = field.deconstruct()
    assert kwargs.get("denticion") == "mixta"
    assert "profile" not in kwargs


def test_deconstruct_path_points_to_peru_field():
    field = OdontogramaPeruInicialField()
    _name, path, _args, _kwargs = field.deconstruct()
    # Path-by-class-identity is how the profile is preserved in migrations —
    # if this changes, migrations would silently break.
    assert "OdontogramaPeruInicialField" in path
    assert "profiles.peru" in path


# ---------------------------------------------------------------------------
# Model field integration (REQ-6.3 — formfield wiring)
# ---------------------------------------------------------------------------


def test_model_field_profile_is_peru():
    field = PatientPeru._meta.get_field("odontograma")
    assert field.profile == "peru"


def test_model_field_denticion_is_permanente():
    field = PatientPeru._meta.get_field("odontograma")
    assert field.denticion == "permanente"


def test_formfield_delegates_through_base():
    from xpertik_odontograma.forms import OdontogramaFormField

    field = PatientPeru._meta.get_field("odontograma")
    form_field = field.formfield()
    assert isinstance(form_field, OdontogramaFormField)


# ---------------------------------------------------------------------------
# ORM roundtrip (REQ-6.5)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_roundtrip_preserves_caries_and_especificaciones():
    p = PatientPeru.objects.create(
        name="Test",
        odontograma={
            "16": {
                "caras": {"oclusal_incisal": "caries"},
                "especificaciones": "dolor al frío",
            },
            "especificaciones_generales": "Hallazgos radiográficos: nada",
        },
    )
    p.refresh_from_db()
    assert p.odontograma["16"]["caras"]["oclusal_incisal"] == "caries"
    assert p.odontograma["16"]["especificaciones"] == "dolor al frío"
    assert (
        p.odontograma["especificaciones_generales"]
        == "Hallazgos radiográficos: nada"
    )


@pytest.mark.django_db
def test_roundtrip_preserves_corona_with_parametros():
    p = PatientPeru.objects.create(
        name="Test",
        odontograma={
            "21": {"estado": "corona_definitiva", "parametros": {"tipo": "CC"}},
        },
    )
    p.refresh_from_db()
    assert p.odontograma["21"]["estado"] == "corona_definitiva"
    assert p.odontograma["21"]["parametros"] == {"tipo": "CC"}


@pytest.mark.django_db
def test_roundtrip_empty_odontograma_ok():
    p = PatientPeru.objects.create(name="Test", odontograma={})
    p.refresh_from_db()
    assert p.odontograma == {}


# ---------------------------------------------------------------------------
# full_clean chains peru strict validator
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_full_clean_accepts_valid_peru_payload():
    p = PatientPeru(
        name="Test",
        odontograma={"16": {"caras": {"oclusal_incisal": "caries"}}},
    )
    p.full_clean()  # must NOT raise


@pytest.mark.django_db
def test_full_clean_rejects_cross_teeth_diastema():
    p = PatientPeru(
        name="Test",
        odontograma={"11": {"estado": "diastema"}},
    )
    with pytest.raises(ValidationError):
        p.full_clean()


@pytest.mark.django_db
def test_full_clean_rejects_unknown_peru_nomenclatura():
    p = PatientPeru(
        name="Test",
        odontograma={"16": {"estado": "corona_de_platino"}},
    )
    with pytest.raises(ValidationError):
        p.full_clean()


@pytest.mark.django_db
def test_full_clean_rejects_movilidad_without_parametros():
    p = PatientPeru(
        name="Test",
        odontograma={"16": {"estado": "movilidad"}},
    )
    with pytest.raises(ValidationError):
        p.full_clean()


# ---------------------------------------------------------------------------
# makemigrations --dry-run idempotency (R4)
# ---------------------------------------------------------------------------


def _run_makemigrations_dry_run() -> subprocess.CompletedProcess:
    """Invoke ``manage.py makemigrations --dry-run`` in a subprocess.

    Running via subprocess (rather than ``call_command``) guarantees a fresh
    Django import, mirroring how CI produces migration output. Uses the
    test project's settings module.
    """
    return subprocess.run(
        [
            sys.executable,
            "-c",
            "from django.core.management import execute_from_command_line; "
            "execute_from_command_line(['manage.py', 'makemigrations', '--dry-run'])",
        ],
        cwd=REPO_ROOT,
        env={
            "PATH": "/usr/bin:/bin",
            "DJANGO_SETTINGS_MODULE": "tests.testproject.settings",
            "PYTHONPATH": str(REPO_ROOT),
        },
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_makemigrations_dry_run_produces_no_changes():
    """A fresh dry-run must print 'No changes detected' — not a side-effecting diff."""
    result = _run_makemigrations_dry_run()
    combined = result.stdout + result.stderr
    assert result.returncode == 0, (
        f"makemigrations failed: {combined!r}"
    )
    # Either literal "No changes detected" or empty output is acceptable.
    assert (
        "No changes detected" in combined or not combined.strip()
    ), f"unexpected makemigrations output: {combined!r}"


def test_makemigrations_dry_run_idempotent_across_two_runs():
    """Second run must produce the SAME (empty) output as the first (R4)."""
    first = _run_makemigrations_dry_run()
    second = _run_makemigrations_dry_run()

    assert first.returncode == 0 and second.returncode == 0
    # Both runs must report no changes — migration bytes stay stable.
    assert "No changes detected" in (first.stdout + first.stderr) or not (
        first.stdout + first.stderr
    ).strip()
    assert "No changes detected" in (second.stdout + second.stderr) or not (
        second.stdout + second.stderr
    ).strip()
