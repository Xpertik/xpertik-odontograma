"""Phase 7 — silhouettes module unit tests (v0.3.0-alpha.1).

Locks the contract of :mod:`xpertik_odontograma.svg.silhouettes`:

* ``SILHOUETTES`` dict has exactly 6 entries with the canonical ids.
* ``SILHOUETTES_SVG`` host element embeds every ``<symbol>`` via a hidden
  ``<svg>`` wrapper.
* Each ``<symbol>`` carries the canonical ``viewBox="0 0 40 80"``.
* :func:`silhouette_id_for_tooth` routes every FDI position to the correct
  silhouette per the table in the module docstring.
* :func:`is_superior` / :func:`is_inferior` classify every quadrant.

The test file is deliberately a thin lock: the module is pure string
literals + FDI arithmetic, so the goal is regression protection against
accidental edits to the ``<symbol>`` ids, the viewBox, or the FDI routing.
"""

from __future__ import annotations

import pytest

from xpertik_odontograma.svg.silhouettes import (
    SILHOUETTES,
    SILHOUETTES_SVG,
    is_inferior,
    is_superior,
    silhouette_id_for_tooth,
)

EXPECTED_IDS = frozenset(
    {
        "xp-incisivo",
        "xp-canino",
        "xp-premolar",
        "xp-molar",
        "xp-temporal-anterior",
        "xp-temporal-posterior",
    }
)


# ---------------------------------------------------------------------------
# SILHOUETTES dict shape
# ---------------------------------------------------------------------------


def test_silhouettes_has_exactly_six_entries() -> None:
    assert len(SILHOUETTES) == 6


def test_silhouettes_ids_match_expected_set() -> None:
    assert frozenset(SILHOUETTES.keys()) == EXPECTED_IDS


@pytest.mark.parametrize("sil_id", sorted(EXPECTED_IDS))
def test_each_symbol_contains_its_id_literal(sil_id: str) -> None:
    # The literal must advertise its own id so <use xlink:href=""> works.
    assert f'id="{sil_id}"' in SILHOUETTES[sil_id]


@pytest.mark.parametrize("sil_id", sorted(EXPECTED_IDS))
def test_each_symbol_uses_canonical_viewbox(sil_id: str) -> None:
    # viewBox is contract per the module docstring.
    assert 'viewBox="0 0 40 80"' in SILHOUETTES[sil_id]


@pytest.mark.parametrize("sil_id", sorted(EXPECTED_IDS))
def test_each_symbol_opens_and_closes_symbol_tag(sil_id: str) -> None:
    svg = SILHOUETTES[sil_id]
    assert svg.startswith("<symbol"), f"{sil_id} does not start with <symbol"
    assert svg.rstrip().endswith("</symbol>"), f"{sil_id} is not </symbol>-closed"


# ---------------------------------------------------------------------------
# SILHOUETTES_SVG host
# ---------------------------------------------------------------------------


def test_silhouettes_svg_is_hidden_host() -> None:
    # The top-level <svg> that ships the defs is style:display:none + aria-hidden
    # so it does not bloat the a11y tree.
    assert 'style="display:none"' in SILHOUETTES_SVG
    assert 'aria-hidden="true"' in SILHOUETTES_SVG


def test_silhouettes_svg_wraps_defs_block() -> None:
    assert "<defs>" in SILHOUETTES_SVG
    assert "</defs>" in SILHOUETTES_SVG


def test_silhouettes_svg_embeds_every_symbol() -> None:
    for sil_id in EXPECTED_IDS:
        assert f'id="{sil_id}"' in SILHOUETTES_SVG


# ---------------------------------------------------------------------------
# silhouette_id_for_tooth routing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fdi, expected",
    [
        # Permanent incisors (positions 1-2) — quadrants 1-4.
        (11, "xp-incisivo"),
        (21, "xp-incisivo"),
        (31, "xp-incisivo"),
        (41, "xp-incisivo"),
        (12, "xp-incisivo"),
        (42, "xp-incisivo"),
        # Permanent canines (position 3).
        (13, "xp-canino"),
        (23, "xp-canino"),
        (33, "xp-canino"),
        (43, "xp-canino"),
        # Permanent premolars (positions 4-5).
        (14, "xp-premolar"),
        (15, "xp-premolar"),
        (24, "xp-premolar"),
        (45, "xp-premolar"),
        # Permanent molars (positions 6-8).
        (16, "xp-molar"),
        (17, "xp-molar"),
        (18, "xp-molar"),
        (26, "xp-molar"),
        (36, "xp-molar"),
        (48, "xp-molar"),
    ],
)
def test_permanent_fdi_routes_to_expected_silhouette(fdi: int, expected: str) -> None:
    assert silhouette_id_for_tooth(fdi) == expected


@pytest.mark.parametrize(
    "fdi, expected",
    [
        # Temporal anteriors (positions 1-3, quadrants 5-8).
        (51, "xp-temporal-anterior"),
        (52, "xp-temporal-anterior"),
        (53, "xp-temporal-anterior"),
        (61, "xp-temporal-anterior"),
        (71, "xp-temporal-anterior"),
        (81, "xp-temporal-anterior"),
        # Temporal posteriors (positions 4-5, quadrants 5-8).
        (54, "xp-temporal-posterior"),
        (55, "xp-temporal-posterior"),
        (64, "xp-temporal-posterior"),
        (75, "xp-temporal-posterior"),
        (85, "xp-temporal-posterior"),
    ],
)
def test_temporal_fdi_routes_to_expected_silhouette(fdi: int, expected: str) -> None:
    assert silhouette_id_for_tooth(fdi) == expected


def test_routing_never_returns_unknown_id() -> None:
    # Every mapping MUST land in SILHOUETTES.
    for fdi in (11, 21, 31, 41, 16, 28, 38, 48, 55, 65, 75, 85, 51, 61, 71, 81, 54):
        assert silhouette_id_for_tooth(fdi) in SILHOUETTES


# ---------------------------------------------------------------------------
# Arcada classification helpers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fdi", [11, 18, 21, 28, 51, 55, 61, 65])
def test_is_superior_classifies_maxillary_quadrants(fdi: int) -> None:
    assert is_superior(fdi) is True
    assert is_inferior(fdi) is False


@pytest.mark.parametrize("fdi", [31, 38, 41, 48, 71, 75, 81, 85])
def test_is_inferior_classifies_mandibular_quadrants(fdi: int) -> None:
    assert is_inferior(fdi) is True
    assert is_superior(fdi) is False
