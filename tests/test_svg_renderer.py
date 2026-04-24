"""Phase 7 — renderer module pure-function tests (v0.3.0-alpha.1).

Locks the public contract of :mod:`xpertik_odontograma.svg.renderer`:

* :func:`render_chart` returns a valid ``<svg>…</svg>`` string for each
  denticion with the expected number of ``<g class="xp-tooth">`` groups,
  silhouette defs, and Anexo II recuadros.
* :func:`render_tooth` emits a single tooth group referencing the right
  silhouette via ``<use xlink:href>``.
* :func:`sigla_for_tooth` auto-derives the Anexo II recuadro text from the
  entry + catalog per D2 priorities (apice > estado > caras).
* :func:`build_catalog_by_zona` groups catalog entries by their zona and
  preserves the ``cross_teeth`` boolean so the client JS can disable them.
* ``readonly=True`` suppresses ``pointer-events="all"`` on interactive
  paths.
"""

from __future__ import annotations

import pytest

from xpertik_odontograma.profiles.peru.states import get_extended_catalog
from xpertik_odontograma.svg.renderer import (
    build_catalog_by_zona,
    render_chart,
    render_tooth,
    sigla_for_tooth,
)


@pytest.fixture(scope="module")
def catalog() -> dict:
    return build_catalog_by_zona(get_extended_catalog().values())


# ---------------------------------------------------------------------------
# render_chart shape
# ---------------------------------------------------------------------------


def test_render_chart_returns_valid_svg_document() -> None:
    svg = render_chart({}, "permanente")
    assert svg.startswith("<svg")
    assert svg.rstrip().endswith("</svg>")


def test_render_chart_declares_xmlns_and_xlink() -> None:
    svg = render_chart({}, "permanente")
    assert 'xmlns="http://www.w3.org/2000/svg"' in svg
    assert 'xmlns:xlink="http://www.w3.org/1999/xlink"' in svg


def test_render_chart_advertises_img_role_and_aria_label() -> None:
    svg = render_chart({}, "permanente")
    assert 'role="img"' in svg
    assert 'aria-label="Odontograma"' in svg


def test_render_chart_embeds_silhouette_defs() -> None:
    svg = render_chart({}, "permanente")
    assert "<defs>" in svg
    # Every silhouette id should appear inside the defs.
    for sil_id in ("xp-incisivo", "xp-canino", "xp-premolar", "xp-molar"):
        assert f'id="{sil_id}"' in svg


def test_render_chart_permanente_has_32_tooth_groups() -> None:
    svg = render_chart({}, "permanente")
    # Count only ``<g class="xp-tooth xp-...">`` (the tooth groups) — the
    # ``xp-tooth-slot`` wrapper is the per-position translate container.
    assert svg.count('<g class="xp-tooth ') == 32


def test_render_chart_temporal_has_20_tooth_groups() -> None:
    svg = render_chart({}, "temporal")
    assert svg.count('<g class="xp-tooth ') == 20


def test_render_chart_mixta_has_52_tooth_groups() -> None:
    svg = render_chart({}, "mixta")
    # 32 permanent + 20 temporal.
    assert svg.count('<g class="xp-tooth ') == 52


def test_render_chart_unknown_denticion_returns_empty_but_valid_svg() -> None:
    svg = render_chart({}, "made_up")
    assert svg.startswith("<svg")
    assert svg.rstrip().endswith("</svg>")
    # No tooth groups produced — helper returned empty arcades.
    assert svg.count('<g class="xp-tooth ') == 0


def test_render_chart_readonly_tags_svg_class() -> None:
    svg = render_chart({}, "permanente", readonly=True)
    assert "xp-readonly" in svg


def test_render_chart_editable_has_pointer_events_on_faces() -> None:
    svg = render_chart({}, "permanente", readonly=False)
    # Interactive overlay — required so JS click delegation works.
    assert 'pointer-events="all"' in svg


def test_render_chart_readonly_drops_pointer_events() -> None:
    svg = render_chart({}, "permanente", readonly=True)
    assert 'pointer-events="all"' not in svg


def test_render_chart_emits_fdi_labels_for_each_tooth() -> None:
    svg = render_chart({}, "permanente")
    # Sample one FDI per quadrant.
    for fdi in (18, 11, 21, 28, 48, 41, 31, 38):
        assert f">{fdi}<" in svg


def test_render_chart_emits_recuadros_above_and_below() -> None:
    svg = render_chart({}, "permanente")
    # Two recuadro groups — one above superior arcade, one below inferior.
    assert svg.count('class="xp-recuadros"') == 2


# ---------------------------------------------------------------------------
# render_tooth
# ---------------------------------------------------------------------------


def test_render_tooth_uses_symbol_reference(catalog: dict) -> None:
    svg = render_tooth(16, {}, catalog)
    assert '<use xlink:href="#xp-molar"' in svg


def test_render_tooth_carries_data_fdi(catalog: dict) -> None:
    svg = render_tooth(16, {}, catalog)
    assert 'data-fdi="16"' in svg


def test_render_tooth_emits_all_five_face_paths(catalog: dict) -> None:
    svg = render_tooth(16, {}, catalog)
    for face in (
        "oclusal_incisal",
        "mesial",
        "distal",
        "vestibular_bucal",
        "lingual_palatino",
    ):
        assert f'data-face="{face}"' in svg


def test_render_tooth_emits_apice_region(catalog: dict) -> None:
    svg = render_tooth(16, {}, catalog)
    assert '<path class="xp-apice"' in svg
    assert 'data-apice="true"' in svg


def test_render_tooth_emits_fdi_label(catalog: dict) -> None:
    svg = render_tooth(16, {}, catalog)
    assert 'class="xp-fdi-label"' in svg
    assert ">16<" in svg


def test_render_tooth_marks_arcada_class(catalog: dict) -> None:
    # Superior quadrant (1) uses xp-superior; inferior (3) uses xp-inferior.
    assert "xp-superior" in render_tooth(16, {}, catalog)
    assert "xp-inferior" in render_tooth(36, {}, catalog)


def test_render_tooth_none_entry_is_treated_as_empty(catalog: dict) -> None:
    # Defensive: renderer should not crash on None.
    svg = render_tooth(16, None, catalog)
    assert '<use xlink:href="#xp-molar"' in svg


# ---------------------------------------------------------------------------
# sigla_for_tooth
# ---------------------------------------------------------------------------


def test_sigla_for_empty_entry_returns_empty_string(catalog: dict) -> None:
    assert sigla_for_tooth({}, catalog) == ""


def test_sigla_for_tooth_without_catalog_returns_empty() -> None:
    # Base widget has no catalog — sigla is silenced.
    assert sigla_for_tooth({"estado": "implante"}, {}) == ""


def test_sigla_for_implante_returns_IMP(catalog: dict) -> None:
    assert sigla_for_tooth({"estado": "implante"}, catalog) == "IMP"


def test_sigla_for_movilidad_combines_sigla_and_grado(catalog: dict) -> None:
    sigla = sigla_for_tooth(
        {"estado": "movilidad", "parametros": {"grado": 2}}, catalog
    )
    assert sigla == "M2"


def test_sigla_for_apice_tratamiento_pulpar_TC(catalog: dict) -> None:
    # The apice.estado path has highest priority (D2).
    sigla = sigla_for_tooth(
        {"apice": {"estado": "tratamiento_pulpar", "parametros": {"tipo": "TC"}}},
        catalog,
    )
    assert sigla == "TC"


def test_sigla_apice_wins_over_caras(catalog: dict) -> None:
    # apice has priority 1; caras sit at priority 3 per the renderer docstring.
    entry = {
        "apice": {"estado": "tratamiento_pulpar", "parametros": {"tipo": "TC"}},
        "caras": {"oclusal_incisal": "restauracion"},
        "parametros": {"material": "AM"},
    }
    assert sigla_for_tooth(entry, catalog) == "TC"


def test_sigla_for_restauracion_material(catalog: dict) -> None:
    # Falls back to caras — the shared parametros dict supplies material.
    entry = {
        "caras": {"oclusal_incisal": "restauracion"},
        "parametros": {"material": "R"},
    }
    assert sigla_for_tooth(entry, catalog) == "R"


# ---------------------------------------------------------------------------
# build_catalog_by_zona
# ---------------------------------------------------------------------------


def test_build_catalog_by_zona_groups_by_zona_value() -> None:
    by_zona = build_catalog_by_zona(get_extended_catalog().values())
    # Every bucket must be a list of dicts (JSON-ready).
    for zona, entries in by_zona.items():
        assert isinstance(zona, str)
        assert isinstance(entries, list)
        for entry in entries:
            assert isinstance(entry, dict)


def test_build_catalog_by_zona_preserves_cross_teeth_flag() -> None:
    by_zona = build_catalog_by_zona(get_extended_catalog().values())
    all_entries = {e["key"]: e for bucket in by_zona.values() for e in bucket}
    # caries is non-cross-teeth, diastema is cross-teeth.
    assert all_entries["caries"]["cross_teeth"] is False
    assert all_entries["diastema"]["cross_teeth"] is True


def test_build_catalog_by_zona_resolves_gettext_labels_to_strings() -> None:
    by_zona = build_catalog_by_zona(get_extended_catalog().values())
    for bucket in by_zona.values():
        for entry in bucket:
            # gettext_lazy proxies get coerced — otherwise JSON blows up.
            assert isinstance(entry["label"], str)


def test_build_catalog_by_zona_has_raiz_bucket_for_apice_entries() -> None:
    by_zona = build_catalog_by_zona(get_extended_catalog().values())
    raiz_keys = {e["key"] for e in by_zona.get("raiz", [])}
    assert {"tratamiento_pulpar", "remanente_radicular"} <= raiz_keys
