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
from django.utils.translation import gettext_lazy as _

from . import settings as package_settings
from .constants import (
    CARAS,
    CAUSAS_AUSENCIA,
    dientes_por_denticion,
    face_label,
)
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
        # custom filters for dict-by-variable lookup. Each row ALWAYS carries
        # BOTH the estado block and the 5-face block so the clinical-chart
        # template can toggle between modes without re-rendering — CSS +
        # JS flip visibility based on ``row.mode``. The DOM carries the
        # complete state for whichever mode the user switches to.
        tooth_rows_by_fdi: dict[int, dict[str, Any]] = {}
        for fdi in teeth:
            fdi_str = str(fdi)
            raw_entry = current_value.get(fdi_str) if isinstance(current_value, dict) else None
            entry: dict[str, Any] = raw_entry if isinstance(raw_entry, dict) else {}

            row: dict[str, Any] = {
                "fdi": fdi,
                "fdi_str": fdi_str,
                "mode": "caras",  # default mode when tooth is empty
                "estado_key": None,
                "estado_label": None,
                "estado_color": None,
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
                    row["estado_color"] = color_unknown
                row["causa"] = entry.get("causa")
            elif "caras" in entry and isinstance(entry["caras"], dict):
                row["mode"] = "caras"

            # Always materialize the 5 face cells. When the tooth is in
            # "estado" mode, the faces still render to the DOM but are
            # hidden by CSS — this way the user can flip the mode toggle
            # without losing the DOM skeleton.
            legacy_caras = entry["caras"] if isinstance(entry.get("caras"), dict) else {}
            for face_key in CARAS:
                face_value = legacy_caras.get(face_key) if legacy_caras else None
                face_def = estados_cara.get(face_value) if face_value else None
                row["faces"].append({
                    "key": face_key,
                    "label": face_label(fdi, face_key),
                    "value": face_value,
                    "color": face_def.get("color", color_unknown) if face_def else None,
                    "state_label": face_def.get("label", face_value) if face_def else None,
                })

            tooth_rows_by_fdi[fdi] = row

        # Preserve original (input-order) row list for tests and JS.
        tooth_rows: list[dict[str, Any]] = [tooth_rows_by_fdi[fdi] for fdi in teeth]

        # --------------------------------------------------------------
        # Clinical-chart quadrant layout (patient-facing perspective)
        # --------------------------------------------------------------
        # Rows are a list of "sections" each with a heading and a list of
        # "quadrant rows". Every quadrant row has two halves separated by
        # a midline, and each half contains the pre-resolved tooth row
        # objects above in the correct left-to-right display order.

        def _row_for(fdi: int) -> dict[str, Any] | None:
            return tooth_rows_by_fdi.get(fdi)

        def _ordered(seq: tuple[int, ...]) -> list[dict[str, Any]]:
            return [r for fdi in seq if (r := _row_for(fdi)) is not None]

        sections: list[dict[str, Any]] = []
        if self.denticion in ("permanente", "mixta"):
            # Permanent dentition (32 teeth) — upper = quad 1+2, lower = quad 3+4.
            # Display order, left → right, patient-facing:
            #   upper: 18 17 16 15 14 13 12 11 | 21 22 23 24 25 26 27 28
            #   lower: 48 47 46 45 44 43 42 41 | 31 32 33 34 35 36 37 38
            upper = (
                _ordered((18, 17, 16, 15, 14, 13, 12, 11)),
                _ordered((21, 22, 23, 24, 25, 26, 27, 28)),
            )
            lower = (
                _ordered((48, 47, 46, 45, 44, 43, 42, 41)),
                _ordered((31, 32, 33, 34, 35, 36, 37, 38)),
            )
            sections.append({
                "key": "permanente",
                "label": _("Permanente"),
                "rows": [
                    {"key": "superior", "label": _("Maxilar superior"), "left": upper[0], "right": upper[1]},
                    {"key": "inferior", "label": _("Maxilar inferior"), "left": lower[0], "right": lower[1]},
                ],
                "cols_per_side": 8,
            })
        if self.denticion in ("temporal", "mixta"):
            # Primary dentition (20 teeth):
            #   upper: 55 54 53 52 51 | 61 62 63 64 65
            #   lower: 85 84 83 82 81 | 71 72 73 74 75
            upper = (
                _ordered((55, 54, 53, 52, 51)),
                _ordered((61, 62, 63, 64, 65)),
            )
            lower = (
                _ordered((85, 84, 83, 82, 81)),
                _ordered((71, 72, 73, 74, 75)),
            )
            sections.append({
                "key": "temporal",
                "label": _("Temporal"),
                "rows": [
                    {"key": "superior", "label": _("Maxilar superior"), "left": upper[0], "right": upper[1]},
                    {"key": "inferior", "label": _("Maxilar inferior"), "left": lower[0], "right": lower[1]},
                ],
                "cols_per_side": 5,
            })

        # Serialize the hidden-input payload once so templates don't need a
        # custom filter. Empty dict -> "{}" (valid JSON).
        current_value_json = json.dumps(current_value, ensure_ascii=False, sort_keys=True)

        context["widget"].update({
            "denticion": self.denticion,
            "teeth": teeth,
            "faces": CARAS,
            "estados_cara": estados_cara,
            "estados_diente": estados_diente,
            "causas_ausencia": CAUSAS_AUSENCIA,
            "readonly": self.readonly,
            "current_value": current_value,
            "current_value_json": current_value_json,
            "tooth_rows": tooth_rows,
            "sections": sections,
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
