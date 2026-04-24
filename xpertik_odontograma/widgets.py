"""SVG odontogram widgets — v0.3.0.

BREAKING (v0.3.0): the legacy HTML-grid widget was replaced by an SVG
renderer. The public class names ``OdontogramaWidget`` and
``ReadOnlyOdontogramaWidget`` are preserved as aliases of
``OdontogramaSvgWidget`` / ``ReadOnlyOdontogramaSvgWidget`` (per design
ADR-U12/U13) so downstream imports keep working; the rendered markup is
now a ``<svg>`` with silhouette ``<symbol>`` defs instead of the v0.2.0
HTML grid.

Consumers who want the previous HTML-based widget must pin
``xpertik-odontograma<0.3.0`` (see CHANGELOG BREAKING notes).

Architecture
------------

* :class:`OdontogramaSvgWidget` — generic SVG widget. Renders
  silhouettes + clickable face / apice paths, FDI labels, and a hidden
  ``<input>`` carrying the JSON payload. No catalog JSON is embedded —
  the base widget targets consumers who do not use a region-specific
  profile.

* :class:`ReadOnlyOdontogramaSvgWidget` — readonly variant. Omits the
  hidden ``<input>`` and the JS ``Media`` bundle. ``render()`` still runs
  the value through the tolerant sanitizer so legacy data is displayed
  gracefully.

* :class:`OdontogramaWidget` / :class:`ReadOnlyOdontogramaWidget` —
  backwards-compatible aliases for v0.1 / v0.2 consumers (ADR-U12).
"""

from __future__ import annotations

import json
from typing import Any

from django import forms
from django.utils.safestring import mark_safe

from .svg.renderer import render_chart
from .validators import sanitize_odontograma_for_render

__all__ = [
    "OdontogramaSvgWidget",
    "ReadOnlyOdontogramaSvgWidget",
    # Backwards-compatible aliases (ADR-U12).
    "OdontogramaWidget",
    "ReadOnlyOdontogramaWidget",
]


class OdontogramaSvgWidget(forms.Widget):
    """Generic SVG-based odontogram widget (no profile-specific layout).

    Renders:

    * An inline ``<svg>`` document with the silhouette ``<symbol>`` defs
      + clickable face / apice ``<path>`` regions per tooth + Anexo II
      recuadros (the renderer always includes recuadros; profile-less
      consumers simply get empty boxes because no catalog is supplied).
    * A hidden ``<input>`` carrying the JSON-encoded value (editable).
    * A small ``<p>`` note advertising the alpha status of the redesign.

    Subclasses (e.g. the Peru profile widget) override ``template_name``
    to add a catalog JSON ``<script>`` blob consumed by the client-side
    popover.

    Attributes:
        template_name: Django template path for the wrapper HTML.
        denticion: ``"permanente"`` | ``"temporal"`` | ``"mixta"``.
        readonly: when ``True``, the hidden ``<input>`` is omitted and
            the JS bundle is not shipped via ``Media``.
    """

    template_name = "xpertik_odontograma/svg_chart.html"
    denticion = "permanente"
    readonly = False

    class Media:
        css = {"all": ("xpertik_odontograma/css/odontograma-svg.css",)}
        js = ("xpertik_odontograma/js/odontograma-svg.js",)

    def __init__(
        self,
        *args: Any,
        denticion: str = "permanente",
        **kwargs: Any,
    ) -> None:
        self.denticion = denticion
        super().__init__(*args, **kwargs)

    # ------------------------------------------------------------------
    # Value marshalling — mirrors the v0.1/v0.2 contract so consumers
    # upgrading from legacy HTML widget do not need to change their
    # form bindings.
    # ------------------------------------------------------------------

    def value_from_datadict(self, data, files, name):
        """Parse the hidden input's JSON back into a dict."""
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
        """Return the value as a dict; template JSON-encodes once in ``get_context``."""
        if value is None or value == "":
            return {}
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (TypeError, ValueError):
                return {}
        return value

    # ------------------------------------------------------------------
    # Catalog hook — base widget has no catalog. Peru override returns
    # the full zona-grouped nomenclatura catalog for popover filtering.
    # ------------------------------------------------------------------

    def get_catalog_by_zona(self) -> dict[str, list[dict]]:
        """Return catalog grouped by zona. Base widget returns empty."""
        return {}

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        raw = self.format_value(value)
        # Readonly path runs values through the tolerant sanitizer;
        # editable path leaves legacy data alone — strict validation
        # runs on submit.
        current_value = (
            sanitize_odontograma_for_render(raw, self.denticion)
            if self.readonly
            else (raw or {})
        )

        catalog_by_zona = self.get_catalog_by_zona()
        svg_markup = render_chart(
            current_value,
            self.denticion,
            catalog_by_zona=catalog_by_zona,
            readonly=self.readonly,
        )

        context["widget"].update(
            {
                "denticion": self.denticion,
                "readonly": self.readonly,
                "svg_markup": mark_safe(svg_markup),
                "value_json": json.dumps(
                    current_value, ensure_ascii=False, sort_keys=True
                ),
                "catalog_by_zona": catalog_by_zona,
                "catalog_by_zona_json": json.dumps(
                    catalog_by_zona, ensure_ascii=False
                ),
            }
        )
        return context


class ReadOnlyOdontogramaSvgWidget(OdontogramaSvgWidget):
    """Display-only SVG odontogram widget. No hidden ``<input>``, no JS."""

    template_name = "xpertik_odontograma/svg_chart.html"
    readonly = True

    # Django's ``MediaDefiningClass`` merges ``Media`` across the MRO.
    # A plain ``class Media`` on the subclass would still inherit the
    # parent's JS bundle. We override the ``media`` property directly so
    # readonly ships CSS only (INV-3: readonly renders server-side,
    # without JS).
    @property
    def media(self):  # noqa: D401 — Django property return
        return forms.Media(
            css={"all": ("xpertik_odontograma/css/odontograma-svg.css",)},
        )


# ---------------------------------------------------------------------------
# Backwards-compatible aliases (ADR-U12 / ADR-U13).
#
# v0.1 / v0.2 consumers imported ``OdontogramaWidget`` /
# ``ReadOnlyOdontogramaWidget`` directly. We preserve those names as
# aliases so the upgrade does not break import lines — the markup behind
# the aliases is now SVG.
# ---------------------------------------------------------------------------

OdontogramaWidget = OdontogramaSvgWidget
ReadOnlyOdontogramaWidget = ReadOnlyOdontogramaSvgWidget
