"""Especificaciones helpers for the Peru profile (REQ-8.1–8.4).

Two optional keys are added to the odontograma JSON under the peru profile:

* Per-tooth ``especificaciones`` — a free-text string attached to a single
  tooth entry (e.g. ``{"16": {"caras": {"oclusal_incisal": "caries"},
  "especificaciones": "dolor al frío"}}``).
* Top-level ``especificaciones_generales`` — a free-text string for findings
  that do not belong to one specific tooth (e.g. radiographic findings, notes
  about the session).

Both keys are optional. An empty string is treated identically to the key
being absent (REQ-8.3) — the round-trip helpers drop empty strings.

The helpers here are pure (no Django imports, no state) — the peru strict
validator calls :func:`validate_especificaciones_shape` to reject non-string
values, and the widget layer (v0.3.0) will reuse the extractors.
"""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

__all__ = [
    "extract_global_especificaciones",
    "extract_tooth_especificaciones",
    "set_global_especificaciones",
    "set_tooth_especificaciones",
    "validate_especificaciones_shape",
]


def validate_especificaciones_shape(value: Any, *, field: str) -> None:
    """Raise ``ValidationError`` when ``value`` is not a string or ``None``.

    Empty strings are accepted here — :func:`extract_*` normalizes them to
    ``""`` on read and :func:`set_*` drops them on write (REQ-8.3).

    Args:
        value: The observed especificaciones payload.
        field: Dotted path of the key (``"especificaciones_generales"`` or
            ``"<fdi>.especificaciones"``) for the error message.
    """
    if value is None:
        return
    if not isinstance(value, str):
        raise ValidationError(
            _("Field %(field)s must be a string (got %(type)s)."),
            code="especificaciones_not_str",
            params={"field": field, "type": type(value).__name__},
        )


def extract_tooth_especificaciones(entry: dict) -> str:
    """Return the per-tooth especificaciones string, or ``""`` if absent.

    Non-string values are coerced to the empty string; the strict validator is
    the one place that raises on shape violations. This helper is read-tolerant
    so the widget never crashes rendering legacy data.
    """
    value = entry.get("especificaciones", "")
    if not isinstance(value, str):
        return ""
    return value


def extract_global_especificaciones(value: dict) -> str:
    """Return top-level ``especificaciones_generales`` or ``""`` if absent."""
    if not isinstance(value, dict):
        return ""
    payload = value.get("especificaciones_generales", "")
    if not isinstance(payload, str):
        return ""
    return payload


def set_tooth_especificaciones(entry: dict, text: str) -> dict:
    """Return a new tooth entry dict with ``especificaciones`` set.

    An empty-or-falsy ``text`` drops the key entirely (REQ-8.3 normalization).
    The original ``entry`` is not mutated.
    """
    new = dict(entry)
    if text:
        new["especificaciones"] = text
    else:
        new.pop("especificaciones", None)
    return new


def set_global_especificaciones(value: dict, text: str) -> dict:
    """Return a new odontograma value with ``especificaciones_generales`` set.

    Empty-or-falsy text drops the key. The original ``value`` is not mutated.
    """
    new = dict(value)
    if text:
        new["especificaciones_generales"] = text
    else:
        new.pop("especificaciones_generales", None)
    return new
