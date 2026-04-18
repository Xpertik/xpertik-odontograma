"""Form widgets: base + editable + readonly.

All three widgets share :class:`BaseOdontogramaWidget.get_context`, which
builds the canonical context dict consumed by ``widget.html`` and
``widget_readonly.html`` via the shared ``_tooth_grid.html`` partial
(ADR-2).

* :class:`OdontogramaWidget` — renders the interactive (placeholder) grid
  with a hidden ``<input>`` carrying the JSON. v0.1.0 uses a ``<select>``
  per tooth/face; v0.2 replaces the chrome with an SVG selector. No widget
  signature changes between versions.

* :class:`ReadOnlyOdontogramaWidget` — renders the grid for display only.
  No ``<input>``, no JS ``Media``. Runs values through
  :func:`~xpertik_odontograma.validators.sanitize_odontograma_for_render`
  first so legacy data is rendered tolerantly.
"""

from __future__ import annotations

import json
from typing import Any

from django import forms

from . import settings as package_settings
from .constants import CARAS, dientes_por_denticion, face_label
from .validators import sanitize_odontograma_for_render

__all__ = [
    "BaseOdontogramaWidget",
    "OdontogramaWidget",
    "ReadOnlyOdontogramaWidget",
]


class BaseOdontogramaWidget(forms.Widget):
    """Common context builder for editable and readonly odontogram widgets."""

    #: Subclasses override ``template_name`` and ``readonly``.
    template_name: str = "xpertik_odontograma/widget.html"
    readonly: bool = False

    def __init__(
        self,
        *args: Any,
        denticion: str = "permanente",
        **kwargs: Any,
    ) -> None:
        self.denticion = denticion
        super().__init__(*args, **kwargs)

    # ------------------------------------------------------------------
    # Value marshalling (hidden <input> <-> dict)
    # ------------------------------------------------------------------

    def value_from_datadict(self, data, files, name):
        """Parse the hidden input's JSON back into a dict.

        Accepts empty strings (fresh form) as an empty dict. Invalid JSON is
        returned verbatim so the form's ``clean()`` raises a helpful error
        rather than silently coercing.
        """
        raw = data.get(name)
        if raw in (None, ""):
            return {}
        if isinstance(raw, (dict, list)):
            return raw
        try:
            return json.loads(raw)
        except (TypeError, ValueError):
            return raw

    def format_value(self, value):
        """Return the value as a dict; template is responsible for JSON-encoding."""
        if value is None or value == "":
            return {}
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (TypeError, ValueError):
                return {}
        return value

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        raw = self.format_value(value)
        # Readonly path runs values through the tolerant sanitizer; editable
        # path leaves legacy data alone — strict validation runs on submit.
        current_value = (
            sanitize_odontograma_for_render(raw, self.denticion)
            if self.readonly
            else (raw or {})
        )

        teeth = dientes_por_denticion(self.denticion)

        estados_cara = package_settings.ESTADOS_CARA
        estados_diente = package_settings.ESTADOS_DIENTE
        color_unknown = package_settings.DEFAULT_COLOR_UNKNOWN

        # Pre-build a list of per-tooth rows so the template doesn't need
        # custom filters for dict-by-variable lookup. Each row carries
        # resolved estado metadata OR resolved face rows (label + color).
        tooth_rows: list[dict[str, Any]] = []
        for fdi in teeth:
            fdi_str = str(fdi)
            raw_entry = current_value.get(fdi_str) if isinstance(current_value, dict) else None
            entry: dict[str, Any] = raw_entry if isinstance(raw_entry, dict) else {}

            row: dict[str, Any] = {
                "fdi": fdi,
                "fdi_str": fdi_str,
                "mode": None,
                "estado_key": None,
                "estado_label": None,
                "estado_color": color_unknown,
                "causa": None,
                "faces": [],
            }

            if "estado" in entry:
                estado_key = entry["estado"]
                estado_def = estados_diente.get(estado_key)
                row["mode"] = "estado"
                row["estado_key"] = estado_key
                if estado_def is not None:
                    row["estado_label"] = estado_def.get("label", estado_key)
                    row["estado_color"] = estado_def.get("color", color_unknown)
                else:
                    row["estado_label"] = estado_key  # unknown legacy value
                row["causa"] = entry.get("causa")
            elif "caras" in entry and isinstance(entry["caras"], dict):
                row["mode"] = "caras"
                legacy_caras = entry["caras"]
                for face_key in CARAS:
                    face_value = legacy_caras.get(face_key)
                    face_def = estados_cara.get(face_value) if face_value else None
                    row["faces"].append({
                        "key": face_key,
                        "label": face_label(fdi, face_key),
                        "value": face_value,
                        "color": face_def.get("color", color_unknown) if face_def else color_unknown,
                        "state_label": face_def.get("label", face_value) if face_def else face_value,
                    })
            else:
                # Empty / legacy-garbage entry — render as five blank faces.
                row["mode"] = "caras"
                for face_key in CARAS:
                    row["faces"].append({
                        "key": face_key,
                        "label": face_label(fdi, face_key),
                        "value": None,
                        "color": None,
                        "state_label": None,
                    })

            tooth_rows.append(row)

        # Serialize the hidden-input payload once so templates don't need a
        # custom filter. Empty dict -> "{}" (valid JSON).
        current_value_json = json.dumps(current_value, ensure_ascii=False, sort_keys=True)

        context["widget"].update({
            "denticion": self.denticion,
            "teeth": teeth,
            "faces": CARAS,
            "estados_cara": estados_cara,
            "estados_diente": estados_diente,
            "readonly": self.readonly,
            "current_value": current_value,
            "current_value_json": current_value_json,
            "tooth_rows": tooth_rows,
            "color_unknown": color_unknown,
        })
        return context


class OdontogramaWidget(BaseOdontogramaWidget):
    """Interactive (placeholder) odontogram widget — editable form input."""

    template_name = "xpertik_odontograma/widget.html"
    readonly = False

    class Media:
        css = {"all": ("xpertik_odontograma/css/odontograma.css",)}
        js = ("xpertik_odontograma/js/odontograma.js",)


class ReadOnlyOdontogramaWidget(BaseOdontogramaWidget):
    """Display-only odontogram widget. No form input, no JS."""

    template_name = "xpertik_odontograma/widget_readonly.html"
    readonly = True

    class Media:
        css = {"all": ("xpertik_odontograma/css/odontograma.css",)}
        # Intentionally no JS — readonly rendering is static.
