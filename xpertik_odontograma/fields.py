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

* an opt-in ``profile`` kwarg (v0.2.0+) that layers country-/regulation-
  specific constraints on top of the base invariants. ``profile=None``
  (the default) keeps v0.1.0 behavior byte-identical (REQ-7.1).

* a :meth:`check` hook placeholder for the future denticion-downgrade
  warning (ADR-12). v0.1.0 emits nothing — the real check requires a
  DB probe that is explicitly scheduled for v0.2.
"""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ImproperlyConfigured
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
        profile: Optional profile name (e.g. ``"peru"``) to layer
            country-/regulation-specific constraints on top of the base
            invariants. Default ``None`` keeps v0.1.0 behavior unchanged.
            Passing an unknown profile name raises
            :class:`~django.core.exceptions.ImproperlyConfigured` at field
            instantiation (REQ-7.3) — well before the first migration.
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
        profile: str | None = None,
        **kwargs: Any,
    ) -> None:
        if denticion not in self.VALID_DENTICIONES:
            raise ValueError(
                f"denticion must be one of {self.VALID_DENTICIONES!r}, got {denticion!r}"
            )

        if profile is not None:
            # Lazy import to avoid a circular import with the profiles package
            # at module load time.
            from .profiles import get as _get_profile

            if _get_profile(profile) is None:
                raise ImproperlyConfigured(
                    f"xpertik_odontograma: unknown profile {profile!r}. "
                    f"Register it via xpertik_odontograma.profiles.register(...) "
                    f"or add the profile's app to INSTALLED_APPS before declaring "
                    f"this field."
                )

        self.denticion = denticion
        self.profile = profile

        # JSONField's default is None; our JSON is always a dict, so callable
        # default keeps makemigrations from serializing a literal `{}`.
        kwargs.setdefault("default", dict)

        super().__init__(*args, **kwargs)

        # ADR-1 / R3: bind denticion (and optional profile) as instance state
        # inside the validator.
        self.validators.append(_FieldBoundValidator(denticion, profile=profile))

    def deconstruct(self) -> tuple[str, str, list[Any], dict[str, Any]]:
        name, path, args, kwargs = super().deconstruct()
        if self.denticion != "permanente":
            kwargs["denticion"] = self.denticion
        # REQ-7.4: emit `profile` ONLY when explicitly set, so existing v0.1.0
        # migrations stay byte-stable after upgrading.
        if self.profile is not None:
            kwargs["profile"] = self.profile
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
