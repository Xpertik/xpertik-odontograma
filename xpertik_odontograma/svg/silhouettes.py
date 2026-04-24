"""Tooth silhouette ``<symbol>`` definitions — v0.3.0-alpha.1 rough first pass.

Per design ADR-U2/U3 and domain decision D1 (see
``sdd/v0-3-0-peru-ui/domain-decisions`` and the norm PDF at
``docs/norms/norma-tecnica-odontograma-peru.pdf`` Anexo II, pages 5-6),
silhouettes are stored as Python string literals wrapped in ``<symbol>``
elements. The renderer embeds them inline via
:data:`SILHOUETTES_SVG` so the chart is a single self-contained document.

alpha.1 ships **6 core silhouettes** with rough geometric approximations
(D1: "rough-first-pass, polish in alpha.2"). The 6 IDs are:

* ``xp-incisivo`` — anterior, tapered crown, single root
* ``xp-canino`` — anterior, pointed crown, single root
* ``xp-premolar`` — transitional, small rectangular crown, 1-2 roots
* ``xp-molar`` — posterior, large rectangular crown with cusps, 2-3 roots
* ``xp-temporal-anterior`` — smaller anterior (temporal dentition)
* ``xp-temporal-posterior`` — smaller posterior (temporal dentition)

Per ADR-U3 the same ``<symbol>`` is reused for superior/inferior via CSS
rotation (``transform: rotate(180deg)``) at the ``<g>`` level so the raíz
points up for maxilar and down for mandíbula — the view convention is
"from inside the mouth looking outward" per clinical convention.

Canonical ``viewBox="0 0 40 80"`` — width 40, height 80. The corona lives
in the top half (y: 0–40) and the raíz in the bottom half (y: 40–80).

Adding silhouettes (for alpha.2 polish):

1. Open ``docs/norms/norma-tecnica-odontograma-peru.pdf`` at Anexo II.
2. Inkscape: import PDF page, rasterize, Path > Trace Bitmap.
3. Reduce to 2-3 paths per silhouette (corona, raíz, optional cusp lines).
4. Normalize to the ``viewBox="0 0 40 80"`` coordinate space above.
5. Replace the literal below with the traced paths.
"""

from __future__ import annotations

__all__ = [
    "SILHOUETTES",
    "SILHOUETTES_SVG",
    "is_inferior",
    "is_superior",
    "silhouette_id_for_tooth",
]


# ---------------------------------------------------------------------------
# Individual silhouette <symbol> literals.
# ---------------------------------------------------------------------------
#
# Each symbol carries ONLY the outline — the clickable face ``<path>`` regions
# are painted on top by ``renderer.render_tooth``; the symbol is a pure visual
# template reused via ``<use xlink:href="#xp-<id>"/>``.


_INCISIVO = """\
<symbol id="xp-incisivo" viewBox="0 0 40 80">
  <!-- Corona: tapered/rectangular with incisal edge -->
  <path d="M 10 30 L 10 10 L 16 4 L 24 4 L 30 10 L 30 30 Z"
        fill="white" stroke="#333" stroke-width="1"/>
  <!-- Incisal edge line -->
  <path d="M 14 6 L 26 6" fill="none" stroke="#333" stroke-width="0.5"/>
  <!-- Raíz (single, conical) -->
  <path d="M 10 30 L 14 70 L 20 78 L 26 70 L 30 30"
        fill="white" stroke="#333" stroke-width="1"/>
</symbol>"""


_CANINO = """\
<symbol id="xp-canino" viewBox="0 0 40 80">
  <!-- Corona: pointed (triangular) crown -->
  <path d="M 10 30 L 10 12 L 20 2 L 30 12 L 30 30 Z"
        fill="white" stroke="#333" stroke-width="1"/>
  <!-- Cusp-tip highlight -->
  <path d="M 16 10 L 20 4 L 24 10" fill="none" stroke="#333" stroke-width="0.5"/>
  <!-- Raíz (single, long and conical — canines have the longest root) -->
  <path d="M 10 30 L 13 72 L 20 78 L 27 72 L 30 30"
        fill="white" stroke="#333" stroke-width="1"/>
</symbol>"""


_PREMOLAR = """\
<symbol id="xp-premolar" viewBox="0 0 40 80">
  <!-- Corona: small rectangular with two cusps -->
  <path d="M 8 30 L 8 10 L 14 4 L 20 2 L 26 4 L 32 10 L 32 30 Z"
        fill="white" stroke="#333" stroke-width="1"/>
  <!-- Two cusps -->
  <path d="M 14 6 L 14 30 M 26 6 L 26 30"
        fill="none" stroke="#333" stroke-width="0.5"/>
  <!-- Raíz: can be single or bifurcated; render slightly bifurcated -->
  <path d="M 8 30 L 12 70 L 16 78" fill="none" stroke="#333" stroke-width="1"/>
  <path d="M 32 30 L 28 70 L 24 78" fill="none" stroke="#333" stroke-width="1"/>
  <!-- Apical floor connecting the bifurcation -->
  <path d="M 16 78 L 24 78" fill="none" stroke="#333" stroke-width="1"/>
</symbol>"""


_MOLAR = """\
<symbol id="xp-molar" viewBox="0 0 40 80">
  <!-- Corona: rectangular with cusps -->
  <path d="M 4 30 L 4 8 L 10 2 L 20 0 L 30 2 L 36 8 L 36 30 Z"
        fill="white" stroke="#333" stroke-width="1"/>
  <!-- Cusp lines -->
  <path d="M 12 6 L 12 30 M 28 6 L 28 30"
        fill="none" stroke="#333" stroke-width="0.5"/>
  <path d="M 20 2 L 20 30" fill="none" stroke="#333" stroke-width="0.5"/>
  <!-- Raíz (2 roots, curving toward apex) -->
  <path d="M 8 30 Q 8 60 12 78" fill="none" stroke="#333" stroke-width="1"/>
  <path d="M 32 30 Q 32 60 28 78" fill="none" stroke="#333" stroke-width="1"/>
  <!-- Cervical line connecting roots at the CEJ -->
  <path d="M 4 30 L 36 30" fill="none" stroke="#333" stroke-width="1"/>
</symbol>"""


_TEMPORAL_ANTERIOR = """\
<symbol id="xp-temporal-anterior" viewBox="0 0 40 80">
  <!-- Smaller anterior crown (temporal teeth are smaller than permanents) -->
  <path d="M 12 32 L 12 14 L 18 8 L 22 8 L 28 14 L 28 32 Z"
        fill="white" stroke="#333" stroke-width="1"/>
  <!-- Incisal edge -->
  <path d="M 16 10 L 24 10" fill="none" stroke="#333" stroke-width="0.5"/>
  <!-- Short conical root (temporal roots resorb) -->
  <path d="M 12 32 L 16 64 L 20 72 L 24 64 L 28 32"
        fill="white" stroke="#333" stroke-width="1"/>
</symbol>"""


_TEMPORAL_POSTERIOR = """\
<symbol id="xp-temporal-posterior" viewBox="0 0 40 80">
  <!-- Smaller posterior crown with cusps -->
  <path d="M 8 32 L 8 12 L 12 6 L 20 4 L 28 6 L 32 12 L 32 32 Z"
        fill="white" stroke="#333" stroke-width="1"/>
  <!-- Cusp lines -->
  <path d="M 14 10 L 14 32 M 26 10 L 26 32"
        fill="none" stroke="#333" stroke-width="0.5"/>
  <!-- Bifurcated short roots -->
  <path d="M 10 32 Q 10 52 14 70" fill="none" stroke="#333" stroke-width="1"/>
  <path d="M 30 32 Q 30 52 26 70" fill="none" stroke="#333" stroke-width="1"/>
  <!-- CEJ line -->
  <path d="M 8 32 L 32 32" fill="none" stroke="#333" stroke-width="1"/>
</symbol>"""


#: Mapping of symbol id → inline ``<symbol>`` literal. Callers that want to
#: embed the defs at the top of their own markup should prefer
#: :data:`SILHOUETTES_SVG` which wraps these in a hidden ``<svg>`` host.
SILHOUETTES: dict[str, str] = {
    "xp-incisivo": _INCISIVO,
    "xp-canino": _CANINO,
    "xp-premolar": _PREMOLAR,
    "xp-molar": _MOLAR,
    "xp-temporal-anterior": _TEMPORAL_ANTERIOR,
    "xp-temporal-posterior": _TEMPORAL_POSTERIOR,
}


#: A single hidden ``<svg>`` host containing all silhouette ``<symbol>`` defs.
#: Consumers can inject this once at the top of a page and reuse via ``<use>``
#: from any downstream chart on the same page.
SILHOUETTES_SVG: str = (
    '<svg xmlns="http://www.w3.org/2000/svg" '
    'style="display:none" aria-hidden="true">'
    "<defs>"
    + "".join(SILHOUETTES.values())
    + "</defs></svg>"
)


# ---------------------------------------------------------------------------
# FDI → silhouette-id mapping.
# ---------------------------------------------------------------------------


def silhouette_id_for_tooth(fdi_code: int) -> str:
    """Return the ``<symbol>`` id that should render the given FDI tooth.

    FDI code layout: first digit = quadrant (1–8), second digit = position.

    Mapping rules:

    * Quadrants 1-4 are permanent; 5-8 are temporal.
    * Positions 1-2 → incisivo (central/lateral).
    * Position 3 → canino.
    * Positions 4-5 → premolar (permanent) / temporal-posterior (temporal —
      temporal dentition has no premolars, so the 2 primary molars live at
      positions 4-5).
    * Positions 6-8 → molar.
    * Temporal teeth (quadrants 5-8) map anterior positions (1-3) to
      ``xp-temporal-anterior`` and posterior positions (4-5) to
      ``xp-temporal-posterior``.

    Args:
        fdi_code: FDI / ISO 3950 tooth code.

    Returns:
        A string id matching one of the keys in :data:`SILHOUETTES`.
    """
    quadrant, position = divmod(fdi_code, 10)
    temporal = quadrant in (5, 6, 7, 8)

    if temporal:
        if position in (1, 2, 3):
            return "xp-temporal-anterior"
        # positions 4 and 5 are the temporal molars
        return "xp-temporal-posterior"

    # Permanent dentition
    if position in (1, 2):
        return "xp-incisivo"
    if position == 3:
        return "xp-canino"
    if position in (4, 5):
        return "xp-premolar"
    # positions 6, 7, 8
    return "xp-molar"


# ---------------------------------------------------------------------------
# Arcada helpers (for rendering orientation).
# ---------------------------------------------------------------------------


def is_superior(fdi_code: int) -> bool:
    """Return ``True`` when the FDI code belongs to a maxillary (upper) tooth.

    Maxilar: quadrants 1, 2 (permanent) and 5, 6 (temporal).
    """
    quadrant = fdi_code // 10
    return quadrant in (1, 2, 5, 6)


def is_inferior(fdi_code: int) -> bool:
    """Return ``True`` when the FDI code belongs to a mandibular (lower) tooth.

    Mandíbula: quadrants 3, 4 (permanent) and 7, 8 (temporal).
    """
    quadrant = fdi_code // 10
    return quadrant in (3, 4, 7, 8)
