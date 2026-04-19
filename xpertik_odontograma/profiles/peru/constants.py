"""Peru profile constants: normative colors, zones, categories, norm gap flag.

The Norma Técnica del Odontograma del Colegio Odontológico del Perú (Disp. V.7)
restricts the palette to two colors: rojo (for caries, mal estado, tratamientos
temporales) and azul (for buen estado and the rest). This module locks the hex
values for both so the peru profile renders identically across consumers.

See also ``AUSENCIA_NORMATIVA_VI_1_24``: the norm PDF jumps from clause VI.1.23
to VI.1.25 — clause 24 is absent from the source document (ADR-9). We document
the gap explicitly so a future revision of the norm can fill it without silent
drift.
"""

from __future__ import annotations

from enum import Enum

__all__ = [
    "AUSENCIA_NORMATIVA_VI_1_24",
    "AZUL_NORMA",
    "COLOR_SYMBOLIC_TO_HEX",
    "Categoria",
    "ROJO_NORMA",
    "Zona",
]


# D1 locked (exploration decision): keep caries stable (#d32f2f, Material Red
# 700) and use Material Blue 800 (#1565c0) — both legible on paper and screen.
ROJO_NORMA: str = "#d32f2f"
AZUL_NORMA: str = "#1565c0"


#: Symbolic color name → hex lookup. Consumers only declare symbolic names in
#: their ``XPERTIK_ODONTOGRAMA_PROFILE_EXTENSIONS`` entries (D3); hex values
#: are rejected at boot.
COLOR_SYMBOLIC_TO_HEX: dict[str, str] = {
    "rojo": ROJO_NORMA,
    "azul": AZUL_NORMA,
}


#: ADR-9: the norm PDF has no entry at clause VI.1.24. This sentinel flags the
#: gap so tests can assert it and a future norm update can fill it deliberately.
AUSENCIA_NORMATIVA_VI_1_24: bool = True


class Zona(str, Enum):
    """Anatomical zone where a nomenclatura's graphical representation lives.

    Matches Anexo II of the norm: recuadros (above/below the arcade hold siglas),
    corona (the tooth crown), raíz (the apical zone), entre piezas (cross-teeth
    findings like diastema, supernumerario), sobre ápices (apparatus drawn at
    the apex level like aparato ortodóntico fijo).
    """

    CORONA = "corona"
    RAIZ = "raiz"
    ENTRE_PIEZAS = "entre_piezas"
    RECUADRO = "recuadro"
    SOBRE_APICES = "sobre_apices"


class Categoria(str, Enum):
    """Clinical category grouping for the 33 nomenclaturas.

    * ``HALLAZGO`` — observed finding (caries, fractura, ausente, …).
    * ``TRATAMIENTO`` — executed treatment (corona, restauración, …).
    * ``ANOMALIA`` — developmental/positional anomaly (movilidad, microdoncia, …).
    * ``ORTODONTICO`` — orthodontic apparatus (cross-teeth).
    """

    HALLAZGO = "hallazgo"
    TRATAMIENTO = "tratamiento"
    ANOMALIA = "anomalia"
    ORTODONTICO = "ortodontico"
