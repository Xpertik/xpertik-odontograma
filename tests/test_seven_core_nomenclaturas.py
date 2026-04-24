"""Phase 4 — 7 core nomenclaturas render assertions (v0.3.0-alpha.1).

Per spec REQ-5.1 through REQ-5.7, each of the 7 core nomenclaturas must
produce the norm-mandated SVG primitive with the correct colour. These
tests lock the contract between ``svg/renderer.render_tooth`` +
``sigla_for_tooth`` and the Anexo II visual language.

Primitive matrix (from spec C5):

+---------------------+------------------------------------+---------+
| Key                 | Primitive                          | Color   |
+=====================+====================================+=========+
| caries              | face fill on cara path             | #d32f2f |
| restauracion        | face fill + material sigla recuadro| #1565c0 |
| ausente             | aspa X over silhouette             | #1565c0 |
| corona_definitiva   | circle around corona + tipo sigla  | #1565c0 |
| implante            | "IMP" + grayed silhouette          | #1565c0 |
| movilidad           | "M{grado}" sigla in recuadro       | #1565c0 |
| tratamiento_pulpar  | vertical line in raíz + tipo sigla | #1565c0 |
+---------------------+------------------------------------+---------+

All colours are peru-norm constants (``ROJO_NORMA = #d32f2f``,
``AZUL_NORMA = #1565c0``) per INV-4.
"""

from __future__ import annotations

import pytest

from xpertik_odontograma.profiles.peru.states import get_extended_catalog
from xpertik_odontograma.svg.renderer import (
    build_catalog_by_zona,
    render_tooth,
    sigla_for_tooth,
)


ROJO_NORMA = "#d32f2f"
AZUL_NORMA = "#1565c0"


@pytest.fixture(scope="module")
def catalog() -> dict:
    """Return the full Peru catalog grouped by zona (shared across tests)."""
    return build_catalog_by_zona(get_extended_catalog().values())


# ---------------------------------------------------------------------------
# REQ-5.1 — caries (rojo, face fill)
# ---------------------------------------------------------------------------


def test_caries_paints_face_with_rojo_norma(catalog):
    entry = {"caras": {"oclusal_incisal": "caries"}}
    svg = render_tooth(16, entry, catalog)
    # The oclusal face path carries the rojo norma fill attribute.
    assert 'data-face="oclusal_incisal"' in svg
    assert f'fill="{ROJO_NORMA}"' in svg
    # No overlay primitives for caries (face fill only).
    assert "xp-aspa" not in svg
    assert "xp-corona-ring" not in svg
    assert "xp-imp-label" not in svg


def test_caries_emits_no_recuadro_sigla(catalog):
    # caries has no sigla of its own (face fill carries the information).
    assert sigla_for_tooth({"caras": {"oclusal_incisal": "caries"}}, catalog) == ""


# ---------------------------------------------------------------------------
# REQ-5.2 — restauracion (azul, face fill + material sigla)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "material", ["AM", "R", "IV", "IM", "IE"]
)
def test_restauracion_paints_face_azul_and_propagates_material_sigla(
    catalog, material
):
    entry = {
        "caras": {"oclusal_incisal": "restauracion"},
        "parametros": {"material": material},
    }
    svg = render_tooth(16, entry, catalog)
    assert 'data-face="oclusal_incisal"' in svg
    assert f'fill="{AZUL_NORMA}"' in svg
    # Sigla derivation returns the material code for recuadro.
    assert sigla_for_tooth(entry, catalog) == material


# ---------------------------------------------------------------------------
# REQ-5.3 — ausente / diente_ausente (aspa X over silhouette)
# ---------------------------------------------------------------------------


def test_ausente_renders_aspa_in_azul(catalog):
    entry = {"estado": "ausente"}
    svg = render_tooth(16, entry, catalog)
    # Two aspa <line> elements crossing the tooth, stroked azul norma.
    assert svg.count('class="xp-aspa"') == 2
    assert f'stroke="{AZUL_NORMA}"' in svg


def test_diente_ausente_alias_also_renders_aspa(catalog):
    # ``diente_ausente`` is a legacy alias accepted by the renderer overlay.
    entry = {"estado": "diente_ausente"}
    svg = render_tooth(16, entry, catalog)
    assert svg.count('class="xp-aspa"') == 2


# ---------------------------------------------------------------------------
# REQ-5.4 — corona_definitiva (azul circle around corona + tipo sigla)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tipo", ["CC", "CF", "CMC", "CV", "CJ", "3-4", "4-5", "7-8"])
def test_corona_definitiva_renders_ring_and_propagates_tipo_sigla(
    catalog, tipo
):
    entry = {"estado": "corona_definitiva", "parametros": {"tipo": tipo}}
    svg = render_tooth(16, entry, catalog)
    assert 'class="xp-corona-ring"' in svg
    assert f'stroke="{AZUL_NORMA}"' in svg
    # Sigla lookup surfaces the tipo value for the Anexo II recuadro.
    assert sigla_for_tooth(entry, catalog) == tipo


# ---------------------------------------------------------------------------
# REQ-5.5 — implante (IMP sigla + grayed silhouette)
# ---------------------------------------------------------------------------


def test_implante_renders_imp_label_and_grayed_overlay(catalog):
    entry = {"estado": "implante"}
    svg = render_tooth(16, entry, catalog)
    assert 'class="xp-imp-label"' in svg
    assert ">IMP<" in svg
    assert 'class="xp-grayed"' in svg
    # Sigla derivation propagates IMP to the recuadro.
    assert sigla_for_tooth(entry, catalog) == "IMP"


# ---------------------------------------------------------------------------
# REQ-5.6 — movilidad (M{grado} sigla in recuadro; no silhouette overlay)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("grado", [1, 2, 3])
def test_movilidad_derives_M_grado_sigla(catalog, grado):
    entry = {"estado": "movilidad", "parametros": {"grado": grado}}
    svg = render_tooth(16, entry, catalog)
    # Movilidad is sigla-only — no corona primitive on the silhouette.
    assert "xp-corona-ring" not in svg
    assert "xp-aspa" not in svg
    assert sigla_for_tooth(entry, catalog) == f"M{grado}"


# ---------------------------------------------------------------------------
# REQ-5.7 — tratamiento_pulpar (vertical line in raíz + tipo sigla)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tipo", ["TC", "PC", "PP"])
def test_tratamiento_pulpar_renders_vertical_line_and_tipo_sigla(
    catalog, tipo
):
    entry = {"apice": {"estado": "tratamiento_pulpar", "parametros": {"tipo": tipo}}}
    svg = render_tooth(16, entry, catalog)
    # The vertical line marker lives in the raíz region.
    assert 'class="xp-apice-mark"' in svg
    assert f'stroke="{AZUL_NORMA}"' in svg
    # Sigla derivation surfaces the tipo in the recuadro.
    assert sigla_for_tooth(entry, catalog) == tipo


# ---------------------------------------------------------------------------
# Colour integrity — rojo vs azul norma
# ---------------------------------------------------------------------------


def test_caries_uses_rojo_not_azul(catalog):
    svg = render_tooth(16, {"caras": {"oclusal_incisal": "caries"}}, catalog)
    # The oclusal face must not be azul (that's restauracion's colour).
    assert f'data-face="oclusal_incisal" d="M 19 17 L 31 17 L 31 33 L 19 33 Z" fill="{AZUL_NORMA}"' not in svg


def test_restauracion_uses_azul_not_rojo(catalog):
    svg = render_tooth(
        16,
        {"caras": {"oclusal_incisal": "restauracion"}, "parametros": {"material": "R"}},
        catalog,
    )
    # The face must not be rojo (that's caries' colour).
    assert f'data-face="oclusal_incisal" d="M 19 17 L 31 17 L 31 33 L 19 33 Z" fill="{ROJO_NORMA}"' not in svg
