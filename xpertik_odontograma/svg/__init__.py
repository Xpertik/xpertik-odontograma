"""SVG rendering for xpertik_odontograma widgets.

Server-side SVG renderer (ADR-U1) + reusable tooth silhouettes as
``<symbol>`` defs (ADR-U2/U3). The widget layer composes these into a
single self-contained ``<svg>`` per chart; no build step, no AJAX, no
extra runtime deps.

Public API:

* :func:`render_chart` — top-level renderer ``(value, denticion, ...) -> str``.
* :func:`render_tooth` — per-tooth ``<g>`` builder.
* :func:`sigla_for_tooth` — Anexo II recuadro text auto-derived (D2).
* :func:`build_catalog_by_zona` — group catalog entries by zona for popover.
* :data:`SILHOUETTES_SVG` — embeddable ``<svg><defs>…</defs></svg>`` blob.
* :func:`silhouette_id_for_tooth` — FDI → symbol id mapping.
* :func:`is_superior` / :func:`is_inferior` — arcada helpers.
"""

from __future__ import annotations

from .renderer import (
    build_catalog_by_zona,
    render_chart,
    render_tooth,
    sigla_for_tooth,
)
from .silhouettes import (
    SILHOUETTES_SVG,
    is_inferior,
    is_superior,
    silhouette_id_for_tooth,
)

__all__ = [
    "SILHOUETTES_SVG",
    "build_catalog_by_zona",
    "is_inferior",
    "is_superior",
    "render_chart",
    "render_tooth",
    "sigla_for_tooth",
    "silhouette_id_for_tooth",
]
