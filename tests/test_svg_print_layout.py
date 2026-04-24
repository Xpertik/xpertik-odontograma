"""Phase 6 — Print CSS rules (v0.3.0-alpha.1).

The spec REQ-9 demands:

* A ``@media print`` block in the base widget stylesheet.
* Popovers, selects, and buttons are hidden on print.
* Silhouettes, faces, and recuadros keep their colour
  (``print-color-adjust: exact``).
* A4 landscape page size via ``@page``.

These tests verify the declared rules exist in the shipped CSS file so
regressions show up in CI rather than dentist-facing print previews.
"""

from __future__ import annotations

from pathlib import Path

import pytest

CSS_PATH = (
    Path(__file__).resolve().parent.parent
    / "xpertik_odontograma"
    / "static"
    / "xpertik_odontograma"
    / "css"
    / "odontograma-svg.css"
)


@pytest.fixture(scope="module")
def css() -> str:
    assert CSS_PATH.exists(), f"CSS file missing: {CSS_PATH}"
    return CSS_PATH.read_text(encoding="utf-8")


def test_css_contains_media_print_block(css: str) -> None:
    assert "@media print" in css


def test_print_hides_popover(css: str) -> None:
    # Popover dialog must not appear on paper.
    assert ".xp-popover" in css
    # And within the @media print block.
    print_block = css.split("@media print", 1)[1]
    assert ".xp-popover" in print_block
    assert "display: none" in print_block


def test_print_hides_selects_and_buttons(css: str) -> None:
    print_block = css.split("@media print", 1)[1]
    assert "select:not(.xp-keep-in-print)" in print_block
    assert "button" in print_block


def test_print_preserves_colour_on_faces(css: str) -> None:
    # print-color-adjust: exact must be declared for face / apice / recuadro.
    print_block = css.split("@media print", 1)[1]
    assert "print-color-adjust: exact" in print_block
    assert "-webkit-print-color-adjust: exact" in print_block
    # Ensure each key selector is covered.
    for selector in (".xp-face", ".xp-apice", ".xp-recuadro", ".xp-tooth"):
        assert selector in print_block, f"Missing {selector} in @media print"


def test_print_sets_page_landscape_a4(css: str) -> None:
    print_block = css.split("@media print", 1)[1]
    assert "@page" in print_block
    assert "A4 landscape" in print_block
    assert "margin: 1cm" in print_block


def test_print_makes_svg_fill_page_width(css: str) -> None:
    print_block = css.split("@media print", 1)[1]
    # The SVG must not keep its 800px min-width which would overflow A4.
    assert "min-width: 100%" in print_block
    assert "max-width: 100%" in print_block


def test_placeholder_note_hidden_in_print(css: str) -> None:
    print_block = css.split("@media print", 1)[1]
    assert ".xp-odontograma-placeholder-note" in print_block
