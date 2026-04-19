"""Test-only Django models exercising :class:`~xpertik_odontograma.fields.OdontogramaField`.

Kept intentionally minimal: a single :class:`Patient` model with one field per
denticion variant so integration tests can round-trip data through SQLite
without dragging in realistic patient-record shape. The ``app_label`` matches
the ``tests`` app entry in ``tests/testproject/settings.INSTALLED_APPS``.

v0.2.0 adds :class:`PatientPeru` which exercises
:class:`~xpertik_odontograma.profiles.peru.fields.OdontogramaPeruInicialField`
end-to-end (strict peru validator, `especificaciones` keys, SQLite roundtrip).
The v0.1 ``Patient`` model is kept untouched so backward-compat regression tests
see no schema churn.
"""

from __future__ import annotations

from django.db import models

from xpertik_odontograma.fields import OdontogramaField
from xpertik_odontograma.profiles.peru.fields import OdontogramaPeruInicialField


class Patient(models.Model):
    """Minimal patient record with three odontograms — one per denticion."""

    name = models.CharField(max_length=100)
    # `blank=True` lets `full_clean()` accept the JSONField default `{}` —
    # an empty odontograma is semantically valid per the strict validator.
    odontograma_permanente = OdontogramaField(blank=True)
    odontograma_mixta = OdontogramaField(denticion="mixta", blank=True)
    odontograma_temporal = OdontogramaField(denticion="temporal", blank=True)

    class Meta:
        app_label = "tests"


class PatientPeru(models.Model):
    """Peru-profile patient record (v0.2.0+).

    Uses :class:`OdontogramaPeruInicialField` to lock ``profile="peru"`` at the
    class level. The field chains ``validate_peru_strict`` onto the base strict
    validator at ``full_clean()`` time (REQ-6.3).
    """

    name = models.CharField(max_length=100)
    # `blank=True` mirrors the v0.1 Patient model — empty odontograms are valid.
    odontograma = OdontogramaPeruInicialField(blank=True)

    class Meta:
        app_label = "tests"
