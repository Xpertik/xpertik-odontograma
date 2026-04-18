"""Test-only Django models exercising :class:`~xpertik_odontograma.fields.OdontogramaField`.

Kept intentionally minimal: a single :class:`Patient` model with one field per
denticion variant so integration tests can round-trip data through SQLite
without dragging in realistic patient-record shape. The ``app_label`` matches
the ``tests`` app entry in ``tests/testproject/settings.INSTALLED_APPS``.
"""

from __future__ import annotations

from django.db import models

from xpertik_odontograma.fields import OdontogramaField


class Patient(models.Model):
    """Minimal patient record with three odontograms — one per denticion."""

    name = models.CharField(max_length=100)
    odontograma_permanente = OdontogramaField(default=dict)
    odontograma_mixta = OdontogramaField(denticion="mixta", default=dict)
    odontograma_temporal = OdontogramaField(denticion="temporal", default=dict)

    class Meta:
        app_label = "tests"
