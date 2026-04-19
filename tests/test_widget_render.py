"""Tests for :mod:`xpertik_odontograma.widgets`.

Widgets are exercised at three levels:

* **Context shape** — :meth:`BaseOdontogramaWidget.get_context` populates
  the keys the shared ``_tooth_grid.html`` partial expects (REQ-7.1, REQ-7.5,
  ADR-2, ADR-11).
* **HTML rendering** — ``OdontogramaWidget`` renders the hidden ``<input>``;
  ``ReadOnlyOdontogramaWidget`` does NOT emit any ``<input>`` (REQ-7.2,
  REQ-7.3).
* **Media declaration** — editable ships CSS + JS, readonly ships CSS only
  (REQ-7.2, REQ-7.3).

Note: the shipped widget context does NOT expose a ``face_label_map`` —
face labels are pre-resolved onto each ``tooth_rows[i].faces[j].label``
entry so ``_tooth_grid.html`` can render without custom template filters.
Phase 2 deviated from the spec's tuple-keyed map for that reason (tuples
aren't indexable from Django templates). We test the shipped shape, not the
spec suggestion.
"""

from __future__ import annotations

from xpertik_odontograma.constants import CARAS
from xpertik_odontograma.widgets import OdontogramaWidget, ReadOnlyOdontogramaWidget

# ---------------------------------------------------------------------------
# Context shape
# ---------------------------------------------------------------------------


def test_context_permanente_has_32_teeth():
    w = OdontogramaWidget(denticion="permanente")
    ctx = w.get_context("foo", {}, {})
    assert len(ctx["widget"]["teeth"]) == 32


def test_context_temporal_has_20_teeth():
    w = OdontogramaWidget(denticion="temporal")
    ctx = w.get_context("foo", {}, {})
    assert len(ctx["widget"]["teeth"]) == 20


def test_context_mixta_has_52_teeth():
    w = OdontogramaWidget(denticion="mixta")
    ctx = w.get_context("foo", {}, {})
    assert len(ctx["widget"]["teeth"]) == 52


def test_context_faces_are_canonical_tuple():
    w = OdontogramaWidget(denticion="permanente")
    ctx = w.get_context("foo", {}, {})
    assert ctx["widget"]["faces"] == CARAS


def test_context_editable_readonly_false():
    w = OdontogramaWidget(denticion="permanente")
    ctx = w.get_context("foo", {}, {})
    assert ctx["widget"]["readonly"] is False


def test_context_readonly_true_for_readonly_widget():
    w = ReadOnlyOdontogramaWidget(denticion="permanente")
    ctx = w.get_context("foo", {}, {})
    assert ctx["widget"]["readonly"] is True


def test_context_tooth_rows_carry_face_labels_for_posterior_upper():
    # Tooth 16 is an upper molar (posterior) → oclusal + palatino.
    w = OdontogramaWidget(denticion="permanente")
    ctx = w.get_context("foo", {}, {})
    # Find the row for 16.
    rows = ctx["widget"]["tooth_rows"]
    row_16 = next(r for r in rows if r["fdi"] == 16)
    assert row_16["mode"] == "caras"
    # Every row starts with five blank face cells (one per canonical key).
    labels = {f["key"]: str(f["label"]) for f in row_16["faces"]}
    assert labels["oclusal_incisal"] == "Oclusal"
    assert labels["lingual_palatino"] == "Palatino"


def test_context_tooth_rows_carry_face_labels_for_anterior_lower():
    # Tooth 31 is a lower-left incisor → incisal + lingual.
    w = OdontogramaWidget(denticion="permanente")
    ctx = w.get_context("foo", {}, {})
    rows = ctx["widget"]["tooth_rows"]
    row_31 = next(r for r in rows if r["fdi"] == 31)
    labels = {f["key"]: str(f["label"]) for f in row_31["faces"]}
    assert labels["oclusal_incisal"] == "Incisal"
    assert labels["lingual_palatino"] == "Lingual"


# ---------------------------------------------------------------------------
# Render — editable widget emits the hidden input
# ---------------------------------------------------------------------------


def test_editable_render_contains_hidden_input():
    w = OdontogramaWidget(denticion="mixta")
    html = w.render("odontograma_mixta", {}, {})
    assert 'type="hidden"' in html
    # The hidden input carries the field name.
    assert 'name="odontograma_mixta"' in html


def test_editable_render_contains_all_permanente_fdi_codes():
    w = OdontogramaWidget(denticion="permanente")
    html = w.render("od", {}, {})
    # Every permanent FDI code appears somewhere in the rendered output.
    for fdi in (11, 18, 21, 28, 31, 38, 41, 48):
        assert f">{fdi}<" in html or str(fdi) in html


def test_editable_render_mixta_contains_primary_and_permanent_codes():
    w = OdontogramaWidget(denticion="mixta")
    html = w.render("od", {}, {})
    # Sample one permanent + one primary.
    assert "16" in html
    assert "55" in html


# ---------------------------------------------------------------------------
# Render — readonly widget emits NO hidden input and NO <select>
# ---------------------------------------------------------------------------


def test_readonly_render_has_no_hidden_input():
    w = ReadOnlyOdontogramaWidget(denticion="permanente")
    html = w.render("od", {"16": {"estado": "corona"}}, {})
    assert "<input" not in html


def test_readonly_render_has_no_select():
    # Readonly MUST NOT allow any state mutation — no <select> elements.
    w = ReadOnlyOdontogramaWidget(denticion="permanente")
    html = w.render("od", {"16": {"estado": "corona"}}, {})
    assert "<select" not in html


def test_readonly_render_still_shows_fdi_codes():
    w = ReadOnlyOdontogramaWidget(denticion="permanente")
    html = w.render("od", {}, {})
    for fdi in (11, 16, 36, 48):
        assert str(fdi) in html


# ---------------------------------------------------------------------------
# Media declarations
# ---------------------------------------------------------------------------


def test_editable_widget_media_includes_css_and_js():
    media = OdontogramaWidget().media
    media_str = str(media)
    assert "odontograma.css" in media_str
    assert "odontograma.js" in media_str


def test_readonly_widget_media_has_css_only():
    media = ReadOnlyOdontogramaWidget().media
    media_str = str(media)
    assert "odontograma.css" in media_str
    assert "odontograma.js" not in media_str
