"""Tests for :mod:`xpertik_odontograma.profiles.peru.states` (REQ-2.x).

Pin the catalog's shape:

* Length is 32 — the norm PDF documents only 32 nomenclaturas (VI.1.1 through
  VI.1.33 with VI.1.24 absent). Phase 2 correctly produced 32 entries and
  flagged the ambiguity with spec REQ-2.1's "33". Tests follow ground truth,
  not the doc typo; the corresponding 27/26 arithmetic flips accordingly.
* All entries cite a ``VI.1.N`` clause (REQ-2.5).
* No entry occupies clause ``VI.1.24`` (REQ-2.6 + ADR-9).
* Exactly 6 entries are cross-teeth (REQ-2.3) — the 6 spec'd keys exactly.
* ``PeruNomenclatura`` is frozen (REQ-2.4).
* Known entries expose the colors, zonas, categorias, and ``parametros_schema``
  the spec locks down (REQ-2.7).
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from xpertik_odontograma.profiles.peru.constants import (
    AUSENCIA_NORMATIVA_VI_1_24,
    Categoria,
    Zona,
)
from xpertik_odontograma.profiles.peru.states import (
    CATALOG,
    EXTENDED_CATALOG,
    NORMATIVE_KEYS,
    PeruNomenclatura,
)

# The 6 cross-teeth nomenclaturas per Phase 2 finding + spec REQ-2.3.
EXPECTED_CROSS_TEETH_KEYS: frozenset[str] = frozenset(
    {
        "aparato_orto_fijo",
        "aparato_orto_removible",
        "diastema",
        "geminacion_fusion",
        "transposicion",
        "supernumerario",
    }
)


# ---------------------------------------------------------------------------
# Shape, size, gap
# ---------------------------------------------------------------------------


def test_catalog_has_32_entries():
    # The PDF documents 32 nomenclaturas; VI.1.24 is intentionally absent.
    # Spec REQ-2.1 says "33" but REQ-2.6 forbids VI.1.24 — 32 is the only
    # count consistent with the norm itself. See Phase 2 apply-progress.
    assert len(CATALOG) == 32


def test_catalog_is_a_tuple_not_list():
    # Immutability at language level (ADR-2): tuples have no `.append`.
    assert isinstance(CATALOG, tuple)
    with pytest.raises(AttributeError):
        CATALOG.append("foo")  # type: ignore[attr-defined]


def test_ausencia_normativa_vi_1_24_flag_set():
    assert AUSENCIA_NORMATIVA_VI_1_24 is True


def test_no_entry_occupies_clause_vi_1_24():
    # REQ-2.6: the norm PDF has no entry at VI.1.24 (jumps from 1.23 to 1.25).
    clauses = {n.clausula_norma for n in CATALOG}
    assert "VI.1.24" not in clauses


# ---------------------------------------------------------------------------
# Clause citations (REQ-2.5)
# ---------------------------------------------------------------------------


def test_every_entry_cites_a_clause():
    for nom in CATALOG:
        assert nom.clausula_norma, f"{nom.key!r} has empty clausula_norma"


def test_every_clause_starts_with_vi_1():
    for nom in CATALOG:
        assert nom.clausula_norma.startswith("VI.1."), (
            f"{nom.key!r} clause {nom.clausula_norma!r} does not start with 'VI.1.'"
        )


# ---------------------------------------------------------------------------
# Uniqueness
# ---------------------------------------------------------------------------


def test_no_duplicate_keys():
    keys = [n.key for n in CATALOG]
    assert len(keys) == len(set(keys))


def test_normative_keys_is_frozenset_matching_catalog():
    assert isinstance(NORMATIVE_KEYS, frozenset)
    assert NORMATIVE_KEYS == {n.key for n in CATALOG}
    assert len(NORMATIVE_KEYS) == 32


# ---------------------------------------------------------------------------
# Cross-teeth marking (REQ-2.3)
# ---------------------------------------------------------------------------


def test_exactly_six_cross_teeth_entries():
    cross = {n.key for n in CATALOG if n.cross_teeth}
    assert len(cross) == 6


def test_cross_teeth_keys_match_spec():
    cross = {n.key for n in CATALOG if n.cross_teeth}
    assert cross == EXPECTED_CROSS_TEETH_KEYS


def test_usable_catalog_size_is_26():
    # 32 total − 6 cross-teeth (deferred to v0.3.0) = 26 usable nomenclaturas.
    # Spec scenario arithmetic ("33 − 6 = 27") is based on the doc typo; real
    # ground truth is 32 − 6 = 26.
    usable = sum(1 for n in CATALOG if not n.cross_teeth)
    assert usable == 26


@pytest.mark.parametrize("expected_key", sorted(EXPECTED_CROSS_TEETH_KEYS))
def test_each_expected_cross_teeth_key_is_flagged(expected_key):
    # Look up by key; raise if missing from CATALOG.
    entry = next((n for n in CATALOG if n.key == expected_key), None)
    assert entry is not None, f"expected cross-teeth key {expected_key!r} missing"
    assert entry.cross_teeth is True


# ---------------------------------------------------------------------------
# Frozen dataclass (REQ-2.4)
# ---------------------------------------------------------------------------


def test_peru_nomenclatura_is_frozen():
    entry = CATALOG[0]
    with pytest.raises(FrozenInstanceError):
        entry.label = "hacked"  # type: ignore[misc]


def test_peru_nomenclatura_rejects_new_attrs():
    entry = CATALOG[0]
    # frozen + slots combined raise FrozenInstanceError, AttributeError, or
    # TypeError depending on the code path — what we care about is that the
    # instance refuses any attribute change.
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        entry.new_attribute = "x"  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Known entries — specific properties (REQ-2.7 + spec-locked colors/zones)
# ---------------------------------------------------------------------------


def _by_key(key: str) -> PeruNomenclatura:
    entry = next((n for n in CATALOG if n.key == key), None)
    assert entry is not None, f"expected key {key!r} in CATALOG"
    return entry


def test_caries_is_rojo_corona_hallazgo():
    nom = _by_key("caries")
    assert nom.color_symbolic == "rojo"
    assert nom.zona == Zona.CORONA
    assert nom.categoria == Categoria.HALLAZGO


def test_fractura_is_rojo():
    nom = _by_key("fractura")
    assert nom.color_symbolic == "rojo"


def test_ausente_is_azul():
    # Norm calls it "Diente Ausente"; key is `ausente` in the catalog.
    nom = _by_key("ausente")
    assert nom.color_symbolic == "azul"


def test_corona_definitiva_has_tipo_parametros_schema():
    nom = _by_key("corona_definitiva")
    assert nom.color_symbolic == "azul"
    assert nom.parametros_schema is not None
    assert "tipo" in nom.parametros_schema
    allowed = nom.parametros_schema["tipo"]
    # Must include the canonical codes from spec REQ-2.7.
    for code in ("CC", "CF", "CMC", "CV", "CJ"):
        assert code in allowed, f"{code!r} missing from corona_definitiva.tipo"


def test_movilidad_has_grado_parametros_schema():
    nom = _by_key("movilidad")
    assert nom.parametros_schema is not None
    assert "grado" in nom.parametros_schema
    grados = nom.parametros_schema["grado"]
    # Values may be stored as int or str; accept either but the three canonical
    # grades must all be present.
    coerced = {str(g) for g in grados}
    assert coerced == {"1", "2", "3"}


def test_restauracion_has_material_parametros_schema():
    nom = _by_key("restauracion")
    assert nom.parametros_schema is not None
    assert "material" in nom.parametros_schema
    mats = set(nom.parametros_schema["material"])
    assert {"AM", "R", "IV", "IM", "IE"}.issubset(mats)


def test_tratamiento_pulpar_has_tipo_parametros_schema():
    nom = _by_key("tratamiento_pulpar")
    assert nom.parametros_schema is not None
    assert "tipo" in nom.parametros_schema
    tipos = set(nom.parametros_schema["tipo"])
    assert {"TC", "PC", "PP"}.issubset(tipos)


# ---------------------------------------------------------------------------
# EXTENDED_CATALOG sanity
# ---------------------------------------------------------------------------


def test_extended_catalog_is_a_dict():
    # ADR-11: mutable dict, rebuilt by PeruAppConfig.ready from CATALOG.
    assert isinstance(EXTENDED_CATALOG, dict)


def test_extended_catalog_contains_every_normative_key():
    # After PeruAppConfig.ready() fires (which it has, in the test runner),
    # every CATALOG entry is reachable via EXTENDED_CATALOG.
    for key in NORMATIVE_KEYS:
        assert key in EXTENDED_CATALOG


# ---------------------------------------------------------------------------
# Every color is 'rojo' or 'azul' (Disp. V.7 — D3)
# ---------------------------------------------------------------------------


def test_all_colors_are_symbolic_rojo_or_azul():
    for nom in CATALOG:
        assert nom.color_symbolic in ("rojo", "azul"), (
            f"{nom.key!r} color {nom.color_symbolic!r} breaks Disp. V.7 — only "
            f"'rojo' or 'azul' symbolic allowed."
        )
