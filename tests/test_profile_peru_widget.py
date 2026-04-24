"""Tests for :class:`PeruOdontogramaWidget` (v0.3.0-alpha.1).

The Peru profile widget extends the generic SVG widget with:

* An Anexo II catalog embedded as a ``<script type="application/json">``
  blob consumed by the client-side popover (Phase 5 wiring).
* Additional CSS / JS assets layered on top of the base bundle; Media
  composition order base → peru per ADR-U13.
* A readonly variant that strips the hidden ``<input>`` and JS bundle
  (INV-3).

This module verifies the contract surface without relying on Phase 5
client-side behavior.
"""

from __future__ import annotations

import json

from xpertik_odontograma.profiles.peru.widgets import (
    PeruOdontogramaWidget,
    PeruReadOnlyOdontogramaWidget,
)

# ---------------------------------------------------------------------------
# Catalog plumbing
# ---------------------------------------------------------------------------


def test_get_catalog_by_zona_has_corona_entries():
    # The popover filter requires a non-empty ``corona`` bucket for the
    # main face click. Spot-check that caries / restauracion are present.
    catalog = PeruOdontogramaWidget().get_catalog_by_zona()
    keys = {entry["key"] for entry in catalog.get("corona", [])}
    assert "caries" in keys
    assert "restauracion" in keys


def test_get_catalog_by_zona_has_raiz_entries():
    catalog = PeruOdontogramaWidget().get_catalog_by_zona()
    keys = {entry["key"] for entry in catalog.get("raiz", [])}
    # Phase 1 verified both RAIZ entries — tratamiento_pulpar + remanente_radicular.
    assert "tratamiento_pulpar" in keys
    assert "remanente_radicular" in keys


def test_get_catalog_by_zona_labels_are_strings():
    # gettext_lazy proxies must be resolved — the blob becomes JSON.
    catalog = PeruOdontogramaWidget().get_catalog_by_zona()
    for entries in catalog.values():
        for entry in entries:
            assert isinstance(entry["label"], str)


# ---------------------------------------------------------------------------
# Context + render
# ---------------------------------------------------------------------------


def test_context_exposes_catalog_json_string():
    w = PeruOdontogramaWidget(denticion="permanente")
    ctx = w.get_context("odontograma", {}, {})
    catalog_json = ctx["widget"]["catalog_json"]
    assert isinstance(catalog_json, str)
    # It must round-trip through json.loads cleanly.
    parsed = json.loads(catalog_json)
    assert "corona" in parsed


def test_render_contains_xp_peru_class():
    w = PeruOdontogramaWidget(denticion="permanente")
    html = w.render("odontograma", {}, {})
    assert "xp-peru" in html


def test_render_contains_catalog_script_blob():
    w = PeruOdontogramaWidget(denticion="permanente")
    html = w.render("odontograma", {}, {})
    assert "id_odontograma__catalog" in html
    assert '<script type="application/json"' in html


def test_render_contains_hidden_input():
    w = PeruOdontogramaWidget(denticion="permanente")
    html = w.render("odontograma", {}, {})
    assert 'type="hidden"' in html
    assert 'name="odontograma"' in html


def test_render_mixta_contains_all_quadrants():
    w = PeruOdontogramaWidget(denticion="mixta")
    html = w.render("od", {}, {})
    # One FDI per quadrant — permanent + primary.
    for fdi in (16, 26, 36, 46, 55, 65, 75, 85):
        assert f">{fdi}<" in html


# ---------------------------------------------------------------------------
# Media composition order (ADR-U13, R-D-6)
# ---------------------------------------------------------------------------


def test_editable_media_base_css_before_peru_css():
    # Per ADR-U13 the base bundle loads first so Peru CSS can override.
    media_str = str(PeruOdontogramaWidget().media)
    base_css_idx = media_str.find("odontograma-svg.css")
    peru_css_idx = media_str.find("peru-chart.css")
    assert base_css_idx != -1
    assert peru_css_idx != -1
    assert base_css_idx < peru_css_idx


def test_editable_media_has_base_and_peru_js():
    media_str = str(PeruOdontogramaWidget().media)
    assert "odontograma-svg.js" in media_str
    assert "peru-chart.js" in media_str


def test_editable_media_base_js_before_peru_js():
    media_str = str(PeruOdontogramaWidget().media)
    base_js_idx = media_str.find("odontograma-svg.js")
    peru_js_idx = media_str.find("peru-chart.js")
    assert base_js_idx < peru_js_idx


# ---------------------------------------------------------------------------
# Readonly variant (INV-3)
# ---------------------------------------------------------------------------


def test_readonly_render_has_no_hidden_input():
    w = PeruReadOnlyOdontogramaWidget(denticion="permanente")
    html = w.render("od", {"16": {"estado": "implante"}}, {})
    assert "<input" not in html


def test_readonly_render_has_no_catalog_script():
    # Without JS the catalog blob is irrelevant; skip it to save bytes.
    w = PeruReadOnlyOdontogramaWidget(denticion="permanente")
    html = w.render("od", {}, {})
    assert 'type="application/json"' not in html


def test_readonly_media_has_css_only():
    media_str = str(PeruReadOnlyOdontogramaWidget().media)
    assert "odontograma-svg.css" in media_str
    assert "peru-chart.css" in media_str
    assert ".js" not in media_str
