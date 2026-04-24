"""Peru profile SVG odontogram widgets (v0.3.0-alpha.1).

This module specializes the generic :class:`OdontogramaSvgWidget` with:

* A profile-specific template
  (``xpertik_odontograma/profiles/peru/peru_chart.html``) that emits the
  catalog JSON blob consumed by the client-side popover.
* A :meth:`PeruOdontogramaWidget.get_catalog_by_zona` override that
  builds the zona-grouped catalog from the extended (consumer-merged)
  Peru nomenclaturas registry — so the server-side SVG renderer can draw
  sigla text in Anexo II recuadros and the client-side popover can filter
  entries by the clicked zona.
* Additional CSS / JS assets layered on top of the base bundle (Media
  composition order: base → peru per ADR-U13).

Architecture
------------

Per ADR-U12 / ADR-U13 the Peru profile is idiomatic Django: a widget
subclass that overrides ``template_name`` and ``Media`` and plugs the
catalog via a single ``get_catalog_by_zona`` hook. The generic base
widget has no knowledge of Peru-specific behavior.
"""

from __future__ import annotations

import json

from django import forms

from xpertik_odontograma.svg.renderer import build_catalog_by_zona
from xpertik_odontograma.widgets import OdontogramaSvgWidget

from .states import get_extended_catalog

__all__ = [
    "PeruOdontogramaWidget",
    "PeruReadOnlyOdontogramaWidget",
]


class PeruOdontogramaWidget(OdontogramaSvgWidget):
    """Peru profile SVG widget — Anexo II layout + catalog-driven popover.

    Extends :class:`OdontogramaSvgWidget` with:

    * Profile template that embeds the catalog JSON blob (``<script
      type="application/json">``) read by the client-side popover.
    * ``get_catalog_by_zona`` returning the full extended Peru catalog
      so the server renderer emits Anexo II recuadros with auto-derived
      sigla text (D2) and the client-side popover can filter by zona.
    * Additional CSS + JS assets layered on top of the base bundle.
    """

    template_name = "xpertik_odontograma/profiles/peru/peru_chart.html"

    class Media:
        css = {
            "all": (
                "xpertik_odontograma/css/odontograma-svg.css",
                "xpertik_odontograma/profiles/peru/css/peru-chart.css",
            )
        }
        js = (
            "xpertik_odontograma/js/odontograma-svg.js",
            "xpertik_odontograma/profiles/peru/js/peru-chart.js",
        )

    def get_catalog_by_zona(self) -> dict[str, list[dict]]:
        """Return the full extended Peru catalog grouped by zona."""
        return build_catalog_by_zona(get_extended_catalog().values())

    def get_context(self, name, value, attrs):
        # Base widget already computes svg_markup + catalog_by_zona_json
        # via the ``get_catalog_by_zona`` hook. Peru widget additionally
        # stores ``catalog_json`` (a client-safe string-coerced copy) for
        # the profile template's popover <script> blob.
        context = super().get_context(name, value, attrs)
        catalog_by_zona = context["widget"]["catalog_by_zona"]
        context["widget"]["catalog_json"] = self._serialize_catalog_for_client(
            catalog_by_zona
        )
        return context

    @staticmethod
    def _serialize_catalog_for_client(
        catalog_by_zona: dict[str, list[dict]],
    ) -> str:
        """Serialize catalog into client-safe JSON (lazy proxies resolved).

        :func:`build_catalog_by_zona` already coerces ``label`` to ``str``
        before emitting, so every value in ``catalog_by_zona`` is plain
        JSON data. This helper re-serializes with ``ensure_ascii=False``
        so the Spanish labels stay readable in the page source.
        """
        return json.dumps(catalog_by_zona, ensure_ascii=False)


class PeruReadOnlyOdontogramaWidget(PeruOdontogramaWidget):
    """Peru profile readonly variant. No hidden ``<input>``, no JS."""

    readonly = True

    @property
    def media(self):  # noqa: D401 — Django property return
        # Same rationale as base ReadOnlyOdontogramaSvgWidget: override
        # ``media`` directly so the JS bundle is not inherited via the
        # MediaDefiningClass merge (INV-3).
        return forms.Media(
            css={
                "all": (
                    "xpertik_odontograma/css/odontograma-svg.css",
                    "xpertik_odontograma/profiles/peru/css/peru-chart.css",
                )
            },
        )


# ---------------------------------------------------------------------------
# Aliases matching the base widget naming convention used in design docs.
# Keeping both spellings so downstream code can import either name.
# ---------------------------------------------------------------------------

# Export an alias for parity with ``ReadOnlyOdontogramaSvgWidget``.
PeruReadonlyOdontogramaWidget = PeruReadOnlyOdontogramaWidget
# (Reminder: the class name with capitalized ``Only`` is the canonical one.
# ``Readonly`` alias exists because design doc spellings varied.)
