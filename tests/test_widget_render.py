"""Tests for :mod:`xpertik_odontograma.widgets` (v0.3.0 SVG redesign).

v0.3.0 swapped the legacy HTML grid for a server-rendered ``<svg>`` chart.
This module exercises the SVG widget at three levels:

* **Context shape** — :meth:`OdontogramaSvgWidget.get_context` exposes the
  keys the new ``svg_chart.html`` template needs (``svg_markup``,
  ``value_json``, ``catalog_by_zona_json``, ``denticion``, ``readonly``).
* **HTML rendering** — ``OdontogramaSvgWidget`` emits a top-level ``<svg``
  plus the hidden ``<input>`` carrying the JSON payload;
  ``ReadOnlyOdontogramaSvgWidget`` omits the ``<input>``.
* **Media declaration** — editable ships CSS + JS; readonly ships CSS
  only (INV-3).

The legacy aliases ``OdontogramaWidget`` /
``ReadOnlyOdontogramaWidget`` are also exercised so v0.1/v0.2 consumers
upgrading to v0.3.0 keep their import lines working.
"""

from __future__ import annotations

from xpertik_odontograma.widgets import (
    OdontogramaSvgWidget,
    OdontogramaWidget,
    ReadOnlyOdontogramaSvgWidget,
    ReadOnlyOdontogramaWidget,
)

# ---------------------------------------------------------------------------
# Backwards-compatible aliases (ADR-U12)
# ---------------------------------------------------------------------------


def test_legacy_alias_widget_is_svg_widget():
    # ``OdontogramaWidget`` is a drop-in alias for the new SVG widget so
    # v0.1/v0.2 consumers do not need to rewrite imports.
    assert OdontogramaWidget is OdontogramaSvgWidget


def test_legacy_alias_readonly_is_svg_readonly():
    assert ReadOnlyOdontogramaWidget is ReadOnlyOdontogramaSvgWidget


# ---------------------------------------------------------------------------
# Context shape
# ---------------------------------------------------------------------------


def test_context_exposes_denticion():
    w = OdontogramaSvgWidget(denticion="mixta")
    ctx = w.get_context("foo", {}, {})
    assert ctx["widget"]["denticion"] == "mixta"


def test_context_editable_readonly_false():
    w = OdontogramaSvgWidget(denticion="permanente")
    ctx = w.get_context("foo", {}, {})
    assert ctx["widget"]["readonly"] is False


def test_context_readonly_true_for_readonly_widget():
    w = ReadOnlyOdontogramaSvgWidget(denticion="permanente")
    ctx = w.get_context("foo", {}, {})
    assert ctx["widget"]["readonly"] is True


def test_context_exposes_svg_markup_starting_with_svg_tag():
    w = OdontogramaSvgWidget(denticion="permanente")
    ctx = w.get_context("foo", {}, {})
    markup = str(ctx["widget"]["svg_markup"])
    assert markup.startswith("<svg")


def test_context_exposes_value_json_for_empty_dict():
    w = OdontogramaSvgWidget(denticion="permanente")
    ctx = w.get_context("foo", {}, {})
    # value_json is a serialized JSON string — "{}" for an empty dict.
    assert ctx["widget"]["value_json"] == "{}"


def test_context_catalog_by_zona_empty_for_base_widget():
    # Base widget has no profile catalog; popover JSON is empty.
    w = OdontogramaSvgWidget(denticion="permanente")
    ctx = w.get_context("foo", {}, {})
    assert ctx["widget"]["catalog_by_zona"] == {}
    assert ctx["widget"]["catalog_by_zona_json"] == "{}"


# ---------------------------------------------------------------------------
# Render — editable widget emits <svg> + hidden input
# ---------------------------------------------------------------------------


def test_editable_render_contains_svg_tag():
    w = OdontogramaSvgWidget(denticion="mixta")
    html = w.render("odontograma_mixta", {}, {})
    assert "<svg" in html


def test_editable_render_contains_hidden_input():
    w = OdontogramaSvgWidget(denticion="mixta")
    html = w.render("odontograma_mixta", {}, {})
    assert 'type="hidden"' in html
    # The hidden input carries the field name.
    assert 'name="odontograma_mixta"' in html


def test_editable_render_contains_silhouette_use_reference():
    # Every tooth is drawn via <use xlink:href="#xp-..."/> — the chart
    # reuses symbol defs once and references them per tooth.
    w = OdontogramaSvgWidget(denticion="permanente")
    html = w.render("od", {}, {})
    assert '<use xlink:href="#xp-molar"' in html


def test_editable_render_contains_face_paths():
    # Face-level click targets live in <path class="xp-face"> with a
    # data-face attribute naming the canonical face key.
    w = OdontogramaSvgWidget(denticion="permanente")
    html = w.render("od", {}, {})
    assert '<path class="xp-face"' in html
    assert 'data-face="oclusal_incisal"' in html


def test_editable_render_contains_apice_path():
    # Apice click target lives in <path class="xp-apice">.
    w = OdontogramaSvgWidget(denticion="permanente")
    html = w.render("od", {}, {})
    assert '<path class="xp-apice"' in html


def test_editable_render_contains_fdi_label_for_every_quadrant():
    # Every quadrant should surface at least one FDI code via the
    # xp-fdi-label text element.
    w = OdontogramaSvgWidget(denticion="permanente")
    html = w.render("od", {}, {})
    assert 'class="xp-fdi-label"' in html
    # Spot-check one code per quadrant (11, 28, 38, 48).
    for fdi in (11, 28, 38, 48):
        assert f">{fdi}<" in html


def test_editable_render_mixta_contains_primary_and_permanent_codes():
    w = OdontogramaSvgWidget(denticion="mixta")
    html = w.render("od", {}, {})
    # Sample one permanent + one primary.
    assert ">16<" in html
    assert ">55<" in html


# ---------------------------------------------------------------------------
# Render — readonly widget emits NO hidden input
# ---------------------------------------------------------------------------


def test_readonly_render_has_no_hidden_input():
    w = ReadOnlyOdontogramaSvgWidget(denticion="permanente")
    html = w.render("od", {"16": {"estado": "corona_definitiva"}}, {})
    assert "<input" not in html


def test_readonly_render_has_no_dialog_or_select():
    # Readonly MUST NOT ship any interactive chrome.
    w = ReadOnlyOdontogramaSvgWidget(denticion="permanente")
    html = w.render("od", {"16": {"estado": "corona_definitiva"}}, {})
    assert "<dialog" not in html
    assert "<select" not in html


def test_readonly_render_still_shows_svg_and_fdi_codes():
    w = ReadOnlyOdontogramaSvgWidget(denticion="permanente")
    html = w.render("od", {}, {})
    assert "<svg" in html
    for fdi in (11, 16, 36, 48):
        assert f">{fdi}<" in html


# ---------------------------------------------------------------------------
# Media declarations
# ---------------------------------------------------------------------------


def test_editable_widget_media_includes_svg_css_and_js():
    media = OdontogramaSvgWidget().media
    media_str = str(media)
    assert "odontograma-svg.css" in media_str
    assert "odontograma-svg.js" in media_str


def test_readonly_widget_media_has_svg_css_only():
    media = ReadOnlyOdontogramaSvgWidget().media
    media_str = str(media)
    assert "odontograma-svg.css" in media_str
    assert "odontograma-svg.js" not in media_str
