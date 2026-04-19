"""Peru profile Django model fields (REQ-6.1–6.5, ADR-4).

Today we ship one field: :class:`OdontogramaPeruInicialField`, a thin subclass
of :class:`~xpertik_odontograma.fields.OdontogramaField` that locks
``profile="peru"`` at the class level. Consumers who want strict peru
validation can declare the field directly instead of passing the ``profile=``
kwarg manually:

    odontograma_inicial = OdontogramaPeruInicialField(denticion="permanente")

The parallel evolution field (``OdontogramaPeruEvolucionField`` — Disp. V.4)
is scheduled for v0.3.0 once the full audit-trail + inalterabilidad machinery
is in place. The named class here keeps that seam explicit.
"""

from __future__ import annotations

from typing import Any

from django.utils.translation import gettext_lazy as _

from xpertik_odontograma.fields import OdontogramaField

__all__ = ["OdontogramaPeruInicialField"]


class OdontogramaPeruInicialField(OdontogramaField):
    """Odontograma inicial del perfil Perú (Disp. V.5).

    Equivalent to ``OdontogramaField(profile="peru", ...)`` but with the
    profile locked by the class identity. Passing ``profile=`` explicitly is
    rejected at instantiation time (REQ-6.2): the subclass exists precisely
    so the profile is not a per-call kwarg.

    ``deconstruct()`` drops the ``profile`` kwarg from its return value so
    migrations are driven by the class identity alone — the field's path
    (``xpertik_odontograma.profiles.peru.fields.OdontogramaPeruInicialField``)
    already encodes the profile (REQ-6.4, ADR-4).
    """

    description = _(
        "Odontograma inicial — perfil Perú (Norma Técnica del Colegio "
        "Odontológico del Perú)"
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if "profile" in kwargs:
            raise TypeError(
                "OdontogramaPeruInicialField locks profile='peru'; "
                "do not pass the 'profile' kwarg."
            )
        kwargs["profile"] = "peru"
        super().__init__(*args, **kwargs)

    def deconstruct(self) -> tuple[str, str, list[Any], dict[str, Any]]:
        name, path, args, kwargs = super().deconstruct()
        # Class identity encodes the profile; keep it out of migrations.
        kwargs.pop("profile", None)
        return name, path, args, kwargs
