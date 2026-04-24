"""Form-field layer for the odontograma.

The :class:`OdontogramaFormField` thin-wraps :class:`django.forms.JSONField`
and wires the :class:`~xpertik_odontograma.widgets.OdontogramaWidget` by
default. Validation is performed in :meth:`validate` by delegating to
:func:`~xpertik_odontograma.validators.validate_odontograma_strict` — the
same validator is also attached at the model-field level via
:class:`~xpertik_odontograma.validators._FieldBoundValidator` (ADR-1) so
the strict contract is enforced regardless of whether the write goes
through a form or straight through the ORM.
"""

from __future__ import annotations

from typing import Any

from django import forms

from .validators import validate_odontograma_strict
from .widgets import OdontogramaWidget

__all__ = ["OdontogramaFormField"]


class OdontogramaFormField(forms.JSONField):
    """Form field for an odontograma JSON payload.

    Args:
        denticion: ``"permanente"`` (default), ``"temporal"``, or ``"mixta"``.
            Passed through to both the default widget (so it builds the right
            grid) and the strict validator (so FDI range checks are correct).
    """

    widget = OdontogramaWidget

    def __init__(
        self,
        *args: Any,
        denticion: str = "permanente",
        profile: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.denticion = denticion
        self.profile = profile

        # If the caller didn't pass a widget OR passed the bare class
        # reference, instantiate our own wired to the requested denticion.
        widget = kwargs.get("widget")
        if widget is None:
            kwargs["widget"] = OdontogramaWidget(denticion=denticion)
        elif isinstance(widget, type) and issubclass(widget, OdontogramaWidget):
            kwargs["widget"] = widget(denticion=denticion)

        super().__init__(*args, **kwargs)

    def validate(self, value: Any) -> None:
        super().validate(value)
        # Pass profile through so the strict validator bypasses the base
        # ESTADOS_* checks when a profile (e.g. peru) owns the catalog.
        validate_odontograma_strict(value, self.denticion, profile=self.profile)
