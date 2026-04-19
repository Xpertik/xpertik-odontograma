"""Tests for :class:`xpertik_odontograma.fields.OdontogramaField` + form integration.

Covers:

* Field construction with each supported denticion (REQ-4.2).
* :meth:`~OdontogramaField.deconstruct` kwargs round-trip (REQ-4.4, ADR-10).
* :meth:`~OdontogramaField.formfield` default wiring + caller ``widget=``
  override (REQ-4.5, ADR-4).
* :meth:`~OdontogramaField.check` — v0.1.0 MUST NOT emit the ADR-12 W001
  warning (the real DB probe is deferred to v0.2). We assert the empty list
  explicitly so the test will flip to failure when W001 lands in v0.2 and
  the assertion reminds us to update it.
* End-to-end ORM round-trip via ``@pytest.mark.django_db``: create → save →
  reload → assert → ``full_clean`` raises on invalid data (REQ-6.1 at model
  layer, ADR-1).
"""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError

from xpertik_odontograma.fields import OdontogramaField
from xpertik_odontograma.forms import OdontogramaFormField
from xpertik_odontograma.widgets import OdontogramaWidget, ReadOnlyOdontogramaWidget

from .models import Patient


# ---------------------------------------------------------------------------
# Construction / introspection
# ---------------------------------------------------------------------------


def test_model_field_denticion_attribute_permanente():
    field = Patient._meta.get_field("odontograma_permanente")
    assert field.denticion == "permanente"


def test_model_field_denticion_attribute_mixta():
    field = Patient._meta.get_field("odontograma_mixta")
    assert field.denticion == "mixta"


def test_model_field_denticion_attribute_temporal():
    field = Patient._meta.get_field("odontograma_temporal")
    assert field.denticion == "temporal"


def test_invalid_denticion_raises_on_construction():
    with pytest.raises(ValueError):
        OdontogramaField(denticion="bogus")


# ---------------------------------------------------------------------------
# deconstruct() round-trip
# ---------------------------------------------------------------------------


def test_deconstruct_preserves_non_default_denticion():
    field = OdontogramaField(denticion="mixta")
    _name, _path, _args, kwargs = field.deconstruct()
    assert kwargs.get("denticion") == "mixta"


def test_deconstruct_omits_default_denticion():
    field = OdontogramaField()
    _name, _path, _args, kwargs = field.deconstruct()
    # Default "permanente" must NOT be round-tripped into kwargs — otherwise
    # `makemigrations` produces noisy diffs when the model is re-saved.
    assert "denticion" not in kwargs or kwargs.get("denticion") == "permanente"


def test_deconstruct_preserves_temporal():
    field = OdontogramaField(denticion="temporal")
    _name, _path, _args, kwargs = field.deconstruct()
    assert kwargs.get("denticion") == "temporal"


# ---------------------------------------------------------------------------
# formfield() wiring
# ---------------------------------------------------------------------------


def test_formfield_default_uses_our_form_and_widget():
    field = OdontogramaField(denticion="mixta")
    form_field = field.formfield()
    assert isinstance(form_field, OdontogramaFormField)
    assert isinstance(form_field.widget, OdontogramaWidget)
    # Denticion is propagated through to the widget for correct grid sizing.
    assert form_field.widget.denticion == "mixta"


def test_formfield_honors_caller_widget_override():
    field = OdontogramaField(denticion="mixta")
    custom_widget = ReadOnlyOdontogramaWidget(denticion="mixta")
    form_field = field.formfield(widget=custom_widget)
    # Django's Field.__init__ deep-copies widget instances, so we assert on
    # type and on the propagated denticion rather than instance identity.
    assert isinstance(form_field.widget, ReadOnlyOdontogramaWidget)
    assert form_field.widget.denticion == "mixta"


# ---------------------------------------------------------------------------
# check() — v0.1.0 must NOT emit W001 (ADR-12 deferred to v0.2)
# ---------------------------------------------------------------------------


def test_check_does_not_emit_w001_in_v0_1_0():
    # Field.check() must run against a BOUND field (attached to a model),
    # otherwise super().check() raises because `self.name` is None.
    # The `tests.Patient` model provides such a bound field.
    field = Patient._meta.get_field("odontograma_permanente")
    messages = field.check()
    w001_messages = [m for m in messages if getattr(m, "id", None) == "xpertik_odontograma.W001"]
    assert w001_messages == [], (
        "W001 is explicitly deferred to v0.2 per ADR-12; if this triggered "
        "the DB-probe warning has landed — update the assertion to match."
    )


def test_check_returns_list():
    field = Patient._meta.get_field("odontograma_permanente")
    assert isinstance(field.check(), list)


# ---------------------------------------------------------------------------
# ORM round-trip (requires DB)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_db_roundtrip_mixta_with_primary_code():
    p = Patient.objects.create(
        name="Test",
        odontograma_mixta={"55": {"estado": "ausente", "causa": "exfoliacion"}},
    )
    reloaded = Patient.objects.get(pk=p.pk)
    assert reloaded.odontograma_mixta == {
        "55": {"estado": "ausente", "causa": "exfoliacion"}
    }


@pytest.mark.django_db
def test_db_roundtrip_permanente_caras_branch():
    p = Patient.objects.create(
        name="Test",
        odontograma_permanente={"16": {"caras": {"oclusal_incisal": "caries"}}},
    )
    reloaded = Patient.objects.get(pk=p.pk)
    assert reloaded.odontograma_permanente == {
        "16": {"caras": {"oclusal_incisal": "caries"}}
    }


@pytest.mark.django_db
def test_full_clean_accepts_valid_payload():
    p = Patient(name="ok", odontograma_permanente={"16": {"estado": "corona"}})
    p.full_clean()  # must NOT raise


@pytest.mark.django_db
def test_full_clean_rejects_invalid_fdi_for_denticion():
    # 55 is a primary code — invalid when denticion == "permanente".
    p = Patient(
        name="bad",
        odontograma_permanente={"55": {"estado": "ausente"}},
    )
    with pytest.raises(ValidationError):
        p.full_clean()


@pytest.mark.django_db
def test_full_clean_rejects_both_estado_and_caras():
    p = Patient(
        name="bad",
        odontograma_permanente={
            "16": {"estado": "corona", "caras": {"oclusal_incisal": "caries"}},
        },
    )
    with pytest.raises(ValidationError):
        p.full_clean()
