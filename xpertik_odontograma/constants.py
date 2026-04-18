"""FDI tooth codes, canonical face keys, absence causes, and face-label resolution.

All tooth code sequences follow FDI / ISO 3950 nomenclature
(cuadrante × posición). Face keys are the five canonical
combined keys (D1): the UI resolves the correct label per tooth
(incisors show "Incisal", molars show "Oclusal"; upper teeth show
"Palatino", lower teeth show "Lingual"; `vestibular_bucal` renders
as "Vestibular" in v0.1.0 — the "bucal" synonym is documented as a
simplification and does not change clinical meaning).
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

__all__ = [
    "DIENTES_PERMANENTES",
    "DIENTES_TEMPORALES",
    "CARAS",
    "CAUSAS_AUSENCIA",
    "DIENTES_POR_DENTICION",
    "dientes_por_denticion",
    "face_label",
]


# ---------------------------------------------------------------------------
# FDI tooth codes
# ---------------------------------------------------------------------------

# Permanent dentition: 32 codes — quadrants 1, 2, 3, 4 × positions 1..8.
DIENTES_PERMANENTES: tuple[int, ...] = (
    11, 12, 13, 14, 15, 16, 17, 18,
    21, 22, 23, 24, 25, 26, 27, 28,
    31, 32, 33, 34, 35, 36, 37, 38,
    41, 42, 43, 44, 45, 46, 47, 48,
)

# Primary dentition: 20 codes — quadrants 5, 6, 7, 8 × positions 1..5.
DIENTES_TEMPORALES: tuple[int, ...] = (
    51, 52, 53, 54, 55,
    61, 62, 63, 64, 65,
    71, 72, 73, 74, 75,
    81, 82, 83, 84, 85,
)


# ---------------------------------------------------------------------------
# Canonical face keys (D1: single schema, UI resolves labels per tooth)
# ---------------------------------------------------------------------------

CARAS: tuple[str, ...] = (
    "oclusal_incisal",
    "mesial",
    "distal",
    "vestibular_bucal",
    "lingual_palatino",
)


# ---------------------------------------------------------------------------
# Absence causes
# ---------------------------------------------------------------------------

CAUSAS_AUSENCIA: tuple[str, ...] = (
    "extraccion",
    "exfoliacion",
    "agenesia",
)


# ---------------------------------------------------------------------------
# Helper: denticion -> allowed FDI codes
# ---------------------------------------------------------------------------

DIENTES_POR_DENTICION: dict[str, tuple[int, ...]] = {
    "permanente": DIENTES_PERMANENTES,
    "temporal": DIENTES_TEMPORALES,
    "mixta": DIENTES_PERMANENTES + DIENTES_TEMPORALES,
}


def dientes_por_denticion(denticion: str) -> tuple[int, ...]:
    """Return the tuple of allowed FDI codes for the given denticion mode.

    Args:
        denticion: One of ``"permanente"``, ``"temporal"``, ``"mixta"``.

    Returns:
        The tuple of integer FDI codes valid for that mode.

    Raises:
        ValueError: If ``denticion`` is not one of the three recognized values.
    """
    try:
        return DIENTES_POR_DENTICION[denticion]
    except KeyError as exc:
        raise ValueError(
            f"denticion must be one of {tuple(DIENTES_POR_DENTICION)!r}, got {denticion!r}"
        ) from exc


# ---------------------------------------------------------------------------
# Helper: per-tooth face label (ADR-11)
# ---------------------------------------------------------------------------

# Anterior teeth (incisors + canines) in both dentitions — positions 1..3.
# Used to decide incisal vs oclusal for the `oclusal_incisal` face key.
_ANTERIOR_CODES: frozenset[int] = frozenset(
    {11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43}  # permanent anteriors
    | {51, 52, 53, 61, 62, 63, 71, 72, 73, 81, 82, 83}  # primary anteriors
)

# Upper teeth — quadrants 1, 2 (permanent) and 5, 6 (primary).
# Used to decide palatino vs lingual for the `lingual_palatino` face key.
_UPPER_CODES: frozenset[int] = frozenset(
    tuple(range(11, 19)) + tuple(range(21, 29)) + tuple(range(51, 56)) + tuple(range(61, 66))
)


def face_label(fdi_code: int, face_key: str) -> str:
    """Resolve the human-readable label for ``face_key`` on the tooth ``fdi_code``.

    Per D1 the 5 canonical face keys are shared across all teeth and the UI
    picks the correct label. v0.1.0 simplifies ``vestibular_bucal`` to always
    render as "Vestibular" (the "bucal" synonym does not alter clinical
    meaning and is a documented simplification).

    Args:
        fdi_code: FDI / ISO 3950 tooth code (e.g. ``11``, ``36``, ``55``).
        face_key: One of :data:`CARAS`.

    Returns:
        A ``gettext_lazy`` proxy with the localized label.

    Raises:
        ValueError: If ``face_key`` is not in :data:`CARAS`.
    """
    if face_key not in CARAS:
        raise ValueError(
            f"face_key must be one of {CARAS!r}, got {face_key!r}"
        )

    if face_key == "mesial":
        return _("Mesial")
    if face_key == "distal":
        return _("Distal")
    if face_key == "oclusal_incisal":
        return _("Incisal") if fdi_code in _ANTERIOR_CODES else _("Oclusal")
    if face_key == "vestibular_bucal":
        # v0.1.0 simplification — see module docstring.
        return _("Vestibular")
    # face_key == "lingual_palatino"
    return _("Palatino") if fdi_code in _UPPER_CODES else _("Lingual")
