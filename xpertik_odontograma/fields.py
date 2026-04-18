"""Model-field layer for the odontograma.

:class:`OdontogramaField` subclasses :class:`django.db.models.JSONField`
and wires:

* a :class:`~xpertik_odontograma.validators._FieldBoundValidator` that
  captures the field's ``denticion`` as instance state (ADR-1 / R3) and
  runs on :meth:`~django.db.models.Model.full_clean`,

* a :meth:`formfield` override defaulting to
  :class:`~xpertik_odontograma.forms.OdontogramaFormField` +
  :class:`~xpertik_odontograma.widgets.OdontogramaWidget` while honoring
  caller-provided ``widget=`` / ``form_class=`` kwargs (REQ-4.5, ADR-4),

* a :meth:`deconstruct` that preserves ``denticion`` when non-default
  (ADR-10) so migrations round-trip correctly,

* a :meth:`check` hook placeholder for the future denticion-downgrade
  warning (ADR-12). v0.1.0 emits nothing — the real check requires a
  DB probe that is explicitly scheduled for v0.2.
"""

from __future__ import annotations

from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from .forms import OdontogramaFormField
from .validators import _FieldBoundValidator

__all__ = ["OdontogramaField"]


class OdontogramaField(models.JSONField):
    """A :class:`~django.db.models.JSONField` carrying an odontograma.

    Args:
        denticion: ``"permanente"`` (default), ``"temporal"``, or ``"mixta"``.
            Any other value raises :class:`ValueError` immediately.
    """

    description = _(
        "Odontograma FDI/ISO 3950 con schema por-diente-por-cara "
        "(5 caras, estado XOR caras, denticion configurable)."
    )

    VALID_DENTICIONES: tuple[str, ...] = ("permanente", "temporal", "mixta")

    def __init__(
        self,
        *args: Any,
        denticion: str = "permanente",
        **kwargs: Any,
    ) -> None:
        if denticion not in self.VALID_DENTICIONES:
            raise ValueError(
                f"denticion must be one of {self.VALID_DENTICIONES!r}, got {denticion!r}"
            )
        self.denticion = denticion

        # JSONField's default is None; our JSON is always a dict, so callable
        # default keeps makemigrations from serializing a literal `{}`.
        kwargs.setdefault("default", dict)

        super().__init__(*args, **kwargs)

        # ADR-1 / R3: bind denticion as instance state inside the validator.
        self.validators.append(_FieldBoundValidator(denticion))

    def deconstruct(self) -> tuple[str, str, list[Any], dict[str, Any]]:
        name, path, args, kwargs = super().deconstruct()
        if self.denticion != "permanente":
            kwargs["denticion"] = self.denticion
        # Let JSONField re-emit its own default handling; keep our kwargs minimal.
        return name, path, args, kwargs

    def formfield(self, **kwargs: Any):  # noqa: ANN201 — Django returns forms.Field
        defaults: dict[str, Any] = {
            "form_class": OdontogramaFormField,
            "denticion": self.denticion,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def check(self, **kwargs: Any):  # noqa: ANN201 — Django returns list[CheckMessage]
        errors = super().check(**kwargs)
        # ADR-12 / D3: the full downgrade-orphan warning requires a DB probe
        # and is explicitly deferred to v0.2 (a management command). v0.1.0
        # keeps the hook present for compatibility and emits nothing.
        return errors
