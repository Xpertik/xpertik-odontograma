"""Package-level settings: merges :data:`DEFAULT_ESTADOS_*` with consumer overrides.

Consumers extend the state catalogs through two Django settings keys:

* ``XPERTIK_ODONTOGRAMA_ESTADOS_CARA`` — per-face states (caries, obturación, …).
* ``XPERTIK_ODONTOGRAMA_ESTADOS_DIENTE`` — whole-tooth states (ausente, corona, …).

Both are shallow-merged with the package defaults on top of which the
consumer's dictionary wins (``{**DEFAULTS, **OVERRIDE}``). This module is
evaluated **once** on first import — tests using :func:`django.test.override_settings`
must ``importlib.reload(xpertik_odontograma.settings)`` to pick up the merge
again (documented gotcha, design R5).
"""

from __future__ import annotations

from django.conf import settings as django_settings
from django.utils.translation import gettext_lazy as _

__all__ = [
    "DEFAULT_ESTADOS_CARA",
    "DEFAULT_ESTADOS_DIENTE",
    "DEFAULT_COLOR_UNKNOWN",
    "ESTADOS_CARA",
    "ESTADOS_DIENTE",
    "PROFILE",
    "PROFILE_EXTENSIONS",
]


# ---------------------------------------------------------------------------
# Package defaults (labels wrapped in gettext_lazy per ADR-7)
# ---------------------------------------------------------------------------

DEFAULT_ESTADOS_CARA: dict[str, dict[str, object]] = {
    "sano": {
        "label": _("Sano"),
        "color": "#ffffff",
    },
    "caries": {
        "label": _("Caries"),
        "color": "#d32f2f",
    },
    "obturacion_amalgama": {
        "label": _("Obturación amalgama"),
        "color": "#424242",
    },
    "obturacion_resina": {
        "label": _("Obturación resina"),
        "color": "#1976d2",
    },
    "sellante": {
        "label": _("Sellante"),
        "color": "#81c784",
    },
    "fractura": {
        "label": _("Fractura"),
        "color": "#ff9800",
    },
}

DEFAULT_ESTADOS_DIENTE: dict[str, dict[str, object]] = {
    "no_erupcionado": {
        "label": _("No erupcionado"),
        "color": "#e0e0e0",
    },
    "ausente": {
        "label": _("Ausente"),
        "color": "#757575",
    },
    "corona": {
        "label": _("Corona"),
        "color": "#ffb300",
    },
    "implante": {
        "label": _("Implante"),
        "color": "#6a1b9a",
    },
    "protesis_fija": {
        "label": _("Prótesis fija"),
        "color": "#00838f",
    },
}

# Fallback color used by the renderer for unknown / legacy state keys
# (tolerant-read path, design ADR-9).
DEFAULT_COLOR_UNKNOWN: str = "#9e9e9e"


# ---------------------------------------------------------------------------
# Merged, effective catalogs
# ---------------------------------------------------------------------------

ESTADOS_CARA: dict[str, dict[str, object]] = {
    **DEFAULT_ESTADOS_CARA,
    **getattr(django_settings, "XPERTIK_ODONTOGRAMA_ESTADOS_CARA", {}),
}

ESTADOS_DIENTE: dict[str, dict[str, object]] = {
    **DEFAULT_ESTADOS_DIENTE,
    **getattr(django_settings, "XPERTIK_ODONTOGRAMA_ESTADOS_DIENTE", {}),
}


# ---------------------------------------------------------------------------
# Profile activation (v0.2.0+)
# ---------------------------------------------------------------------------

# REQ-9.1: optional global profile name (e.g. ``"peru"``). ``None`` keeps
# v0.1.0 behavior — no profile layer runs.
PROFILE: str | None = getattr(django_settings, "XPERTIK_ODONTOGRAMA_PROFILE", None)

# REQ-9.2: per-profile extension catalogs (e.g. ``{"peru": {...}}``). Each
# profile's ``AppConfig.ready()`` is responsible for validating its own
# extension dict; the base package only exposes the raw value.
PROFILE_EXTENSIONS: dict = getattr(
    django_settings, "XPERTIK_ODONTOGRAMA_PROFILE_EXTENSIONS", {}
)
