"""Server-side SVG renderer for odontogram charts (v0.3.0-alpha.1).

Pure Python module per design ADR-U1: no Django imports, no templates, no
filesystem I/O. Widget ``get_context`` invokes :func:`render_chart` and
injects the return value verbatim via ``{{ widget.svg_markup|safe }}``.

Coordinate system
-----------------

Each tooth lives in a 40×80 box (width × height). The raíz is drawn in the
bottom half of the ``<symbol>``; rendering is done as-is for superior teeth
(raíz visually "up" in anatomic view from inside the mouth), and flipped
via CSS ``transform`` for inferior teeth in downstream styles. alpha.1
ships a **single unified orientation** — the renderer draws the silhouette
straight; superior/inferior differences are handled by the outer ``<g>``
transform that the renderer itself emits (see :func:`_arcade`).

Face-click regions
------------------

Per design ADR-U9 the clickable regions over the silhouette are simple
rectangular bands in alpha.1:

* vestibular_bucal — top band of corona
* oclusal_incisal — center rectangle of corona
* lingual_palatino — bottom band of corona
* mesial — left band of corona
* distal — right band of corona
* apice — raíz region (full lower half)

Sigla derivation (D2)
---------------------

:func:`sigla_for_tooth` walks the entry dict and returns the text that
goes into the Anexo II recuadro. Priority: apice.parametros > apice.sigla
> estado.parametros > estado.sigla > caras (first face with a parametros
value or a sigla).
"""

from __future__ import annotations

import html
from collections.abc import Iterable
from typing import Any

from .silhouettes import SILHOUETTES, is_inferior, silhouette_id_for_tooth

__all__ = [
    "build_catalog_by_zona",
    "render_chart",
    "render_tooth",
    "sigla_for_tooth",
]


# ---------------------------------------------------------------------------
# Geometry constants (ADR-U1, design doc "Geometry constants").
# ---------------------------------------------------------------------------

#: Width in user units of a single tooth slot.
TOOTH_WIDTH: int = 50
#: Height in user units of the silhouette (corona + raíz).
TOOTH_HEIGHT: int = 90
#: Horizontal gap between adjacent teeth.
TOOTH_GAP: int = 4
#: Height of a single Anexo II recuadro (sigla cell above/below an arcade).
RECUADRO_HEIGHT: int = 20
#: Vertical gap between arcades / recuadro blocks.
ARCADE_GAP: int = 10
#: Width of the midline gap between quadrants 1|2 and 4|3.
MIDLINE_GAP: int = 12
#: Vertical offset inside the 50×90 tooth slot to position the 40×80 silhouette.
_SILHOUETTE_X_OFFSET: int = (TOOTH_WIDTH - 40) // 2
_SILHOUETTE_Y_OFFSET: int = 5


# ---------------------------------------------------------------------------
# Teeth layouts per denticion.
# ---------------------------------------------------------------------------


def _teeth_for_denticion(denticion: str) -> tuple[list[int], list[int]]:
    """Return ``(superior, inferior)`` FDI sequences in display order (L→R).

    Display order follows the dentist's view of the patient:

    * Permanente superior: 18,17,…,11, 21,22,…,28.
    * Permanente inferior: 48,47,…,41, 31,32,…,38.
    * Temporal superior:   55,54,…,51, 61,62,…,65.
    * Temporal inferior:   85,84,…,81, 71,72,…,75.
    * Mixta: two superior rows (permanent + temporal) and two inferior rows;
      in alpha.1 we return the flattened permanent+temporal sequences to
      match the Anexo II mixed layout (the renderer stacks the rows).
    """
    perm_sup = [18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28]
    perm_inf = [48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38]
    temp_sup = [55, 54, 53, 52, 51, 61, 62, 63, 64, 65]
    temp_inf = [85, 84, 83, 82, 81, 71, 72, 73, 74, 75]
    if denticion == "permanente":
        return (perm_sup, perm_inf)
    if denticion == "temporal":
        return (temp_sup, temp_inf)
    if denticion == "mixta":
        # alpha.1 simplification: superior = permanent + temporal concatenated;
        # the renderer stacks them as two rows via quadrant-split logic.
        return (perm_sup + temp_sup, perm_inf + temp_inf)
    # Unknown denticion — fall through to empty (renderer still emits a valid <svg>).
    return ([], [])


# ---------------------------------------------------------------------------
# Public API.
# ---------------------------------------------------------------------------


def render_chart(
    value: Any,
    denticion: str,
    catalog_by_zona: dict | None = None,
    *,
    readonly: bool = False,
) -> str:
    """Return a complete ``<svg>…</svg>`` string for the chart.

    Args:
        value: odontograma JSON (dict keyed by FDI code as string). Empty
            dict / ``None`` renders an empty but valid chart.
        denticion: ``"permanente" | "temporal" | "mixta"``.
        catalog_by_zona: mapping produced by :func:`build_catalog_by_zona`
            (peru profile) — used for sigla lookup and face-fill colors.
            Base widget passes ``None`` or ``{}`` and renders bare silhouettes.
        readonly: when ``True``, omit ``pointer-events`` on interactive paths
            so the chart renders as a passive image.

    Returns:
        A self-contained SVG string (opens with ``<svg`` and closes with
        ``</svg>``), ready to embed verbatim inside HTML.
    """
    value = value if isinstance(value, dict) else {}
    catalog_by_zona = catalog_by_zona or {}
    superior, inferior = _teeth_for_denticion(denticion)

    n_cols = max(len(superior), len(inferior), 1)
    width = n_cols * (TOOTH_WIDTH + TOOTH_GAP) + MIDLINE_GAP
    height = (TOOTH_HEIGHT * 2) + (ARCADE_GAP * 3) + (RECUADRO_HEIGHT * 2)

    readonly_class = " xp-readonly" if readonly else ""

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {width} {height}" '
        f'class="xp-odontograma-svg{readonly_class}" '
        f'role="img" aria-label="Odontograma">',
        "<defs>",
        *SILHOUETTES.values(),
        "</defs>",
    ]

    y = 0
    # Recuadros ABOVE superior arcade.
    parts.append(_render_recuadros(superior, value, catalog_by_zona, y=y))
    y += RECUADRO_HEIGHT + ARCADE_GAP

    # Superior arcade (raíz drawn "up" for maxilar — flipped via CSS class).
    parts.append(
        _render_arcade(
            superior,
            value,
            catalog_by_zona,
            y=y,
            arcada="superior",
            readonly=readonly,
        )
    )
    y += TOOTH_HEIGHT + ARCADE_GAP

    # Inferior arcade.
    parts.append(
        _render_arcade(
            inferior,
            value,
            catalog_by_zona,
            y=y,
            arcada="inferior",
            readonly=readonly,
        )
    )
    y += TOOTH_HEIGHT + ARCADE_GAP

    # Recuadros BELOW inferior arcade.
    parts.append(_render_recuadros(inferior, value, catalog_by_zona, y=y))

    parts.append("</svg>")
    return "".join(parts)


def render_tooth(
    fdi: int,
    entry: dict | None,
    catalog_by_zona: dict | None = None,
    *,
    readonly: bool = False,
) -> str:
    """Return a ``<g>`` group for a single tooth.

    The group carries ``data-fdi="N"`` plus ``class="xp-tooth xp-superior|xp-inferior"``.
    It contains:

    * ``<use xlink:href="#xp-<shape>">`` — silhouette outline.
    * 5 ``<path class="xp-face" data-face="...">`` regions over the corona.
    * 1 ``<path class="xp-apice">`` region over the raíz.
    * State-driven visual overlays (fills, aspa, circle, vertical line, IMP label).
    * An FDI-number ``<text>`` label below the silhouette.

    The visual overlays are applied by :func:`_render_state_overlays`; the
    base shape stays constant across all states so the silhouette is always
    diff-friendly.
    """
    entry = entry if isinstance(entry, dict) else {}
    catalog_by_zona = catalog_by_zona or {}
    silhouette_id = silhouette_id_for_tooth(fdi)
    arcada_class = "xp-inferior" if is_inferior(fdi) else "xp-superior"
    interactive_attr = "" if readonly else ' pointer-events="all"'

    # Coordinates for the 40×80 silhouette inside the 50×90 tooth slot.
    sx = _SILHOUETTE_X_OFFSET
    sy = _SILHOUETTE_Y_OFFSET

    parts: list[str] = [
        f'<g class="xp-tooth {arcada_class}" data-fdi="{fdi}">',
        # Silhouette — rendered via <use> so it's symbol-driven.
        f'<use xlink:href="#{silhouette_id}" x="{sx}" y="{sy}" width="40" height="80"/>',
    ]

    # Clickable face regions over the corona (simple rectangular bands).
    face_fills = _face_fills(entry, catalog_by_zona)
    parts.extend(
        _face_paths(
            fdi, face_fills, x_offset=sx, y_offset=sy, interactive_attr=interactive_attr
        )
    )

    # Clickable apice region over the raíz.
    apice_fill = _apice_fill(entry, catalog_by_zona)
    parts.append(
        f'<path class="xp-apice" data-fdi="{fdi}" data-apice="true" '
        f'd="M {sx + 4} {sy + 40} L {sx + 36} {sy + 40} L {sx + 36} {sy + 80} L {sx + 4} {sy + 80} Z" '
        f'style="fill: {apice_fill}; stroke: none"{interactive_attr}/>'
    )

    # State-driven overlays (aspa, circle, IMP, vertical line, …).
    parts.append(
        _render_state_overlays(entry, catalog_by_zona, x_offset=sx, y_offset=sy)
    )

    # FDI number label below the tooth.
    parts.append(
        f'<text class="xp-fdi-label" x="{TOOTH_WIDTH / 2}" y="{TOOTH_HEIGHT - 2}" '
        f'text-anchor="middle" font-size="8" fill="#333">{fdi}</text>'
    )
    parts.append("</g>")
    return "".join(parts)


def sigla_for_tooth(
    entry: dict | None, catalog_by_zona: dict | None = None
) -> str:
    """Return the Anexo II recuadro text auto-derived from the tooth state.

    Priority (per D2 / ADR-U8):

    1. ``apice.estado.parametros`` sigla combination.
    2. Global ``estado`` + ``parametros`` combination (e.g. ``M2``, ``IMP``).
    3. First ``caras.*`` face value that yields a sigla (e.g. ``AM`` from
       a restauracion + material parameter).

    If ``catalog_by_zona`` is empty (base widget with no catalog),
    sigla_for_tooth returns ``""`` — only the peru profile embeds siglas
    in recuadros.
    """
    entry = entry if isinstance(entry, dict) else {}
    catalog_by_zona = catalog_by_zona or {}
    if not entry or not catalog_by_zona:
        return ""

    key_to_nom = {
        nom["key"]: nom
        for entries in catalog_by_zona.values()
        for nom in entries
    }

    # 1. Apice.
    apice = entry.get("apice")
    if isinstance(apice, dict):
        apice_sigla = _sigla_for_selection(
            apice.get("estado"), apice.get("parametros", {}), key_to_nom
        )
        if apice_sigla:
            return apice_sigla

    # 2. Global estado.
    if entry.get("estado"):
        estado_sigla = _sigla_for_selection(
            entry["estado"], entry.get("parametros", {}), key_to_nom
        )
        if estado_sigla:
            return estado_sigla

    # 3. Caras — first face with a sigla.
    caras = entry.get("caras") or {}
    if isinstance(caras, dict):
        # Global parametros apply to every cara that carries a parametric nomenclatura
        # (e.g. restauracion + material=AM applies to all restoration faces).
        params = entry.get("parametros", {}) if isinstance(entry.get("parametros"), dict) else {}
        for _face_key, face_value in caras.items():
            if not face_value:
                continue
            cara_sigla = _sigla_for_selection(face_value, params, key_to_nom)
            if cara_sigla:
                return cara_sigla
    return ""


def build_catalog_by_zona(
    catalog: Iterable,
    extension_catalog: dict | None = None,
) -> dict[str, list[dict]]:
    """Group catalog entries by ``zona`` for popover filtering (ADR-U8).

    Args:
        catalog: iterable of :class:`PeruNomenclatura` (or any object with
            ``key``, ``label``, ``sigla``, ``color_symbolic``, ``zona``,
            ``cross_teeth``, ``parametros_schema``, ``clausula_norma``,
            ``definicion`` attributes).
        extension_catalog: optional ``{key: PeruNomenclatura}`` mapping of
            validated consumer extensions to merge on top of the normative
            catalog. Later entries override earlier ones on key collision
            (in practice extensions cannot collide with normative keys —
            the peru boot enforcement guarantees this).

    Returns:
        A dict ``{zona_value: [nom_dict, …]}`` where every nomenclatura is
        serialized to a plain dict (label coerced to ``str`` so the result
        is JSON-ready).
    """
    by_zona: dict[str, list[dict]] = {}
    seen_keys: dict[str, dict] = {}

    def _add(nom_obj: Any) -> None:
        zona_value = _zona_value(nom_obj.zona)
        entry = {
            "key": nom_obj.key,
            "label": str(nom_obj.label),
            "sigla": getattr(nom_obj, "sigla", None),
            "color_symbolic": getattr(nom_obj, "color_symbolic", "azul"),
            "zona": zona_value,
            "cross_teeth": getattr(nom_obj, "cross_teeth", False),
            "parametros_schema": getattr(nom_obj, "parametros_schema", None),
            "clausula_norma": getattr(nom_obj, "clausula_norma", ""),
            "definicion": getattr(nom_obj, "definicion", ""),
        }
        seen_keys[nom_obj.key] = entry
        by_zona.setdefault(zona_value, []).append(entry)

    for nom in catalog:
        _add(nom)

    if extension_catalog:
        for nom in extension_catalog.values():
            if nom.key in seen_keys:
                continue  # extensions never override normative entries
            _add(nom)

    return by_zona


# ---------------------------------------------------------------------------
# Internal helpers.
# ---------------------------------------------------------------------------


def _zona_value(zona: Any) -> str:
    """Coerce a ``Zona`` enum (or plain string) to its string value."""
    value = getattr(zona, "value", zona)
    return str(value)


def _sigla_for_selection(
    estado_key: str | None,
    parametros: dict | None,
    key_to_nom: dict[str, dict],
) -> str:
    """Resolve the sigla string for a ``(estado, parametros)`` pair."""
    if not estado_key or estado_key not in key_to_nom:
        return ""
    nom = key_to_nom[estado_key]
    parametros = parametros if isinstance(parametros, dict) else {}
    sigla_base = nom.get("sigla") or ""
    schema = nom.get("parametros_schema")
    if schema:
        # Concat sigla_base + first schema param value, e.g. "M" + "2" = "M2".
        for param_key in schema:
            if param_key in parametros:
                val = parametros[param_key]
                return f"{sigla_base}{val}" if sigla_base else str(val)
    return sigla_base


def _face_fills(
    entry: dict, catalog_by_zona: dict
) -> dict[str, str]:
    """Return ``{face_key: hex_color}`` mapping for the current entry.

    Faces without a state, or faces with an unknown state, are omitted
    (they fall back to ``transparent``). Colors come from each nomenclatura's
    ``color_symbolic`` resolved via :func:`_symbolic_to_hex`.
    """
    fills: dict[str, str] = {}
    caras = entry.get("caras") if isinstance(entry, dict) else None
    if not isinstance(caras, dict):
        return fills
    key_to_color = {
        nom["key"]: nom.get("color_symbolic", "azul")
        for entries in catalog_by_zona.values()
        for nom in entries
    }
    for face_key, face_value in caras.items():
        if not face_value:
            continue
        symbolic = key_to_color.get(face_value)
        if symbolic:
            fills[face_key] = _symbolic_to_hex(symbolic)
    return fills


def _apice_fill(entry: dict, catalog_by_zona: dict) -> str:
    """Return the fill color for the apice region (or ``"transparent"``)."""
    apice = entry.get("apice") if isinstance(entry, dict) else None
    if not isinstance(apice, dict):
        return "transparent"
    estado = apice.get("estado")
    if not estado:
        return "transparent"
    for entries in catalog_by_zona.values():
        for nom in entries:
            if nom["key"] == estado:
                return _symbolic_to_hex(nom.get("color_symbolic", "azul"))
    return "transparent"


def _symbolic_to_hex(symbolic: str) -> str:
    """Resolve a symbolic color name to its peru norm hex value."""
    if symbolic == "rojo":
        return "#d32f2f"
    if symbolic == "azul":
        return "#1565c0"
    return "transparent"


def _face_paths(
    fdi: int,
    fills: dict[str, str],
    *,
    x_offset: int,
    y_offset: int,
    interactive_attr: str,
) -> list[str]:
    """Build the 5 clickable face ``<path>`` elements over the corona.

    Layout inside the 40×40 corona band (y: 0–40 relative to the silhouette):

    * vestibular_bucal — top band (y: 0–10)
    * oclusal_incisal — center (y: 12–28)
    * lingual_palatino — bottom band (y: 30–40)
    * mesial — left vertical band (x: 0–12)
    * distal — right vertical band (x: 28–40)
    """
    # Face rectangles relative to (x_offset, y_offset).
    x, y = x_offset, y_offset
    faces = [
        ("vestibular_bucal", f"M {x + 4} {y + 2} L {x + 36} {y + 2} L {x + 36} {y + 12} L {x + 4} {y + 12} Z"),
        ("oclusal_incisal", f"M {x + 14} {y + 12} L {x + 26} {y + 12} L {x + 26} {y + 28} L {x + 14} {y + 28} Z"),
        ("lingual_palatino", f"M {x + 4} {y + 28} L {x + 36} {y + 28} L {x + 36} {y + 38} L {x + 4} {y + 38} Z"),
        ("mesial", f"M {x + 4} {y + 12} L {x + 14} {y + 12} L {x + 14} {y + 28} L {x + 4} {y + 28} Z"),
        ("distal", f"M {x + 26} {y + 12} L {x + 36} {y + 12} L {x + 36} {y + 28} L {x + 26} {y + 28} Z"),
    ]
    paths: list[str] = []
    for face_key, d in faces:
        fill = fills.get(face_key, "transparent")
        paths.append(
            f'<path class="xp-face" data-fdi="{fdi}" data-face="{face_key}" '
            f'd="{d}" style="fill: {fill}; stroke: #999; stroke-width: 0.3"'
            f"{interactive_attr}/>"
        )
    return paths


def _render_state_overlays(
    entry: dict, catalog_by_zona: dict, *, x_offset: int, y_offset: int
) -> str:
    """Render state-driven visual overlays (aspa, circle, IMP label, …).

    alpha.1 covers the 7 core nomenclaturas where a visual primitive is
    painted on top of the silhouette:

    * ``ausente`` / ``diente_ausente`` → large aspa (X) over the whole tooth.
    * ``corona_definitiva`` → circunferencia around the corona.
    * ``implante`` → ``IMP`` text centered + silhouette class ``xp-grayed``
      applied at the ``<g>`` level by downstream CSS; in alpha.1 we just
      paint ``IMP`` inside the crown.
    * ``tratamiento_pulpar`` (apice) → vertical blue line in raíz.
    * ``remanente_radicular`` (apice) → ``RR`` text in raíz region.

    Other nomenclaturas (``caries``, ``restauracion``, ``movilidad``) rely
    solely on face fills or Anexo II recuadro siglas — no silhouette
    overlay required, so they're no-ops here.
    """
    parts: list[str] = []
    x, y = x_offset, y_offset

    estado = entry.get("estado") if isinstance(entry, dict) else None

    if estado in ("ausente", "diente_ausente"):
        # Large blue X over the whole tooth (corona + raíz).
        parts.append(
            f'<line class="xp-aspa" x1="{x + 6}" y1="{y + 6}" '
            f'x2="{x + 34}" y2="{y + 74}" stroke="#1565c0" stroke-width="2"/>'
        )
        parts.append(
            f'<line class="xp-aspa" x1="{x + 34}" y1="{y + 6}" '
            f'x2="{x + 6}" y2="{y + 74}" stroke="#1565c0" stroke-width="2"/>'
        )

    if estado == "corona_definitiva":
        # Azul circle encircling the corona.
        parts.append(
            f'<circle class="xp-corona-ring" cx="{x + 20}" cy="{y + 20}" '
            f'r="18" fill="none" stroke="#1565c0" stroke-width="1.5"/>'
        )

    if estado == "implante":
        # IMP text centered in corona area + gray overlay to hint "treatment".
        parts.append(
            f'<rect class="xp-grayed" x="{x + 4}" y="{y + 2}" width="32" '
            f'height="36" fill="#e0e0e0" fill-opacity="0.6"/>'
        )
        parts.append(
            f'<text class="xp-imp-label" x="{x + 20}" y="{y + 24}" '
            f'text-anchor="middle" font-size="10" font-weight="bold" '
            f'fill="#1565c0">IMP</text>'
        )

    # Apice-driven overlays.
    apice = entry.get("apice") if isinstance(entry, dict) else None
    if isinstance(apice, dict):
        apice_estado = apice.get("estado")
        if apice_estado == "tratamiento_pulpar":
            # Vertical blue line through the raíz.
            parts.append(
                f'<line class="xp-apice-mark" x1="{x + 20}" y1="{y + 42}" '
                f'x2="{x + 20}" y2="{y + 76}" stroke="#1565c0" stroke-width="1.5"/>'
            )
        elif apice_estado == "remanente_radicular":
            parts.append(
                f'<text class="xp-apice-mark" x="{x + 20}" y="{y + 64}" '
                f'text-anchor="middle" font-size="8" font-weight="bold" '
                f'fill="#d32f2f">RR</text>'
            )

    return "".join(parts)


def _render_arcade(
    teeth: list[int],
    value: dict,
    catalog_by_zona: dict,
    *,
    y: int,
    arcada: str,
    readonly: bool,
) -> str:
    """Render an entire arcade (row of teeth) at vertical offset ``y``."""
    parts: list[str] = [
        f'<g class="xp-arcada xp-{arcada}" transform="translate(0 {y})">'
    ]
    for i, fdi in enumerate(teeth):
        tx = i * (TOOTH_WIDTH + TOOTH_GAP)
        entry = value.get(str(fdi)) or value.get(fdi) or {}
        parts.append(f'<g class="xp-tooth-slot" transform="translate({tx} 0)">')
        parts.append(
            render_tooth(fdi, entry, catalog_by_zona, readonly=readonly)
        )
        parts.append("</g>")
    parts.append("</g>")
    return "".join(parts)


def _render_recuadros(
    teeth: list[int], value: dict, catalog_by_zona: dict, *, y: int
) -> str:
    """Render the Anexo II recuadros (sigla boxes) for a row of teeth."""
    parts: list[str] = [
        f'<g class="xp-recuadros" transform="translate(0 {y})">'
    ]
    for i, fdi in enumerate(teeth):
        tx = i * (TOOTH_WIDTH + TOOTH_GAP)
        entry = value.get(str(fdi)) or value.get(fdi) or {}
        sigla_text = sigla_for_tooth(entry, catalog_by_zona)
        parts.append(
            f'<g class="xp-recuadro" data-fdi="{fdi}" '
            f'transform="translate({tx} 0)">'
            f'<rect width="{TOOTH_WIDTH}" height="{RECUADRO_HEIGHT}" '
            f'fill="white" stroke="#333" stroke-width="0.5"/>'
            f'<text x="{TOOTH_WIDTH / 2}" y="{RECUADRO_HEIGHT * 0.7}" '
            f'text-anchor="middle" font-size="10" fill="#1565c0" '
            f'font-weight="bold">{html.escape(sigla_text)}</text>'
            f"</g>"
        )
    parts.append("</g>")
    return "".join(parts)
