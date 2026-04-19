"""Peru nomenclaturas catalog — section VI.1 of the Colegio Odontológico del Perú norm.

Each entry cites its norm clause inline (format ``# VI.1.N``). The catalog
covers 33 entries: VI.1.1 through VI.1.33, **skipping VI.1.24** — the source
PDF jumps from clause VI.1.23 (Movilidad) directly to VI.1.25 (Prótesis
Removible). That gap is documented in
:data:`xpertik_odontograma.profiles.peru.constants.AUSENCIA_NORMATIVA_VI_1_24`
so a future revision of the norm can fill it deliberately (ADR-9).

Six entries are **cross-teeth** (anomalías entre piezas): ``aparato_orto_fijo``,
``aparato_orto_removible``, ``diastema``, ``geminacion_fusion``,
``supernumerario`` and ``transposicion``. They are included in the catalog for
completeness, marked ``cross_teeth=True``, and rejected by the v0.2.0 strict
validator with an actionable error pointing to v0.3.0 (ADR-7).

The catalog is a frozen tuple of immutable dataclass instances (ADR-2). A
parallel mutable mapping, :data:`EXTENDED_CATALOG`, is rebuilt from ``CATALOG``
at boot by :class:`PeruAppConfig.ready` after merging validated consumer
extensions (ADR-11). The normative ``CATALOG`` itself is never mutated.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.utils.translation import gettext_lazy as _

from .constants import Categoria, Zona

__all__ = [
    "CATALOG",
    "EXTENDED_CATALOG",
    "NORMATIVE_KEYS",
    "PeruNomenclatura",
    "get_extended_catalog",
]


@dataclass(frozen=True, slots=True)
class PeruNomenclatura:
    """One entry of the Peru norm catalog.

    Attributes:
        key: snake_case identifier used in the odontograma JSON.
        label: ``gettext_lazy`` proxy for user-facing labels.
        sigla: letters drawn in the recuadro (``"CC"``, ``"IMP"``, …). ``None``
            when the nomenclatura has no sigla of its own; for entries with
            variant-specific siglas (e.g. ``corona_definitiva.tipo="CC"``), the
            sigla lives in ``parametros_schema`` instead.
        color_symbolic: ``"rojo"`` (Disp. V.7 — mal estado / caries / temporal)
            or ``"azul"`` (buen estado / rest of catalog).
        zona: anatomical zone where the representation lives (Anexo II).
        categoria: clinical grouping.
        clausula_norma: exact clause cite, format ``"VI.1.N"``.
        cross_teeth: ``True`` when the nomenclatura spans two or more pieces
            (diastema, supernumerario, aparatos …). Rejected by the v0.2.0
            strict validator (deferred to v0.3.0 — ADR-7).
        parametros_schema: optional ``{param_key: allowed_values}`` schema for
            nomenclaturas with variants (corona tipo, movilidad grado, …).
        definicion: short description lifted from Anexo I, for UI tooltips.
    """

    key: str
    label: Any                              # gettext_lazy proxy
    sigla: str | None = None
    color_symbolic: str = "azul"
    zona: Zona = Zona.RECUADRO
    categoria: Categoria = Categoria.HALLAZGO
    clausula_norma: str = ""
    cross_teeth: bool = False
    parametros_schema: dict | None = None
    definicion: str = ""


# ---------------------------------------------------------------------------
# CATALOG — 33 normative entries (VI.1.1–VI.1.33, skipping VI.1.24 per ADR-9).
# ---------------------------------------------------------------------------

CATALOG: tuple[PeruNomenclatura, ...] = (
    # VI.1.1 — Aparato Ortodóntico Fijo (cross-teeth — v0.3.0)
    PeruNomenclatura(
        key="aparato_orto_fijo",
        label=_("Aparato ortodóntico fijo"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.SOBRE_APICES,
        categoria=Categoria.ORTODONTICO,
        clausula_norma="VI.1.1",
        cross_teeth=True,
        definicion=(
            "Cuadrados con cruz en su interior, a nivel de los ápices de las "
            "piezas dentarias extremas, unidos con una línea recta. Azul en "
            "buen estado, rojo en mal estado."
        ),
    ),
    # VI.1.2 — Aparato Ortodóntico Removible (cross-teeth — v0.3.0)
    PeruNomenclatura(
        key="aparato_orto_removible",
        label=_("Aparato ortodóntico removible"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.SOBRE_APICES,
        categoria=Categoria.ORTODONTICO,
        clausula_norma="VI.1.2",
        cross_teeth=True,
        definicion=(
            "Línea en zig-zag a la altura de los ápices del maxilar en "
            "tratamiento. Azul en buen estado, rojo en mal estado."
        ),
    ),
    # VI.1.3 — Caries
    PeruNomenclatura(
        key="caries",
        label=_("Caries"),
        sigla=None,
        color_symbolic="rojo",
        zona=Zona.CORONA,
        categoria=Categoria.HALLAZGO,
        clausula_norma="VI.1.3",
        definicion=(
            "Lesión cariosa siguiendo su forma en las superficies dentarias "
            "comprometidas, totalmente pintada en rojo."
        ),
    ),
    # VI.1.4 — Corona Definitiva (tipos: CC, CF, CMC, CV, CJ, 3-4, 4-5, 7-8)
    PeruNomenclatura(
        key="corona_definitiva",
        label=_("Corona definitiva"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.RECUADRO,
        categoria=Categoria.TRATAMIENTO,
        clausula_norma="VI.1.4",
        parametros_schema={
            "tipo": ["CC", "CF", "CMC", "CV", "CJ", "3-4", "4-5", "7-8"],
        },
        definicion=(
            "Circunferencia azul encerrando la corona; siglas en recuadro "
            "superior. CC=completa metálica, CF=fenestrada, CMC=metal-cerámica, "
            "CV=veneer, CJ=jacket, 3-4/4-5/7-8=parciales."
        ),
    ),
    # VI.1.5 — Corona Temporal
    PeruNomenclatura(
        key="corona_temporal",
        label=_("Corona temporal"),
        sigla=None,
        color_symbolic="rojo",
        zona=Zona.CORONA,
        categoria=Categoria.TRATAMIENTO,
        clausula_norma="VI.1.5",
        definicion="Circunferencia de color rojo encerrando la corona.",
    ),
    # VI.1.6 — Desgaste Oclusal / Incisal
    PeruNomenclatura(
        key="desgaste_oclusal_incisal",
        label=_("Desgaste oclusal/incisal"),
        sigla="DES",
        color_symbolic="azul",
        zona=Zona.RECUADRO,
        categoria=Categoria.HALLAZGO,
        clausula_norma="VI.1.6",
        definicion="Siglas DES en mayúsculas azul en el recuadro de la pieza.",
    ),
    # VI.1.7 — Diastema (cross-teeth — v0.3.0)
    PeruNomenclatura(
        key="diastema",
        label=_("Diastema"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.ENTRE_PIEZAS,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.7",
        cross_teeth=True,
        definicion="Paréntesis invertido azul entre las piezas dentarias.",
    ),
    # VI.1.8 — Diente Ausente
    PeruNomenclatura(
        key="ausente",
        label=_("Diente ausente"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.CORONA,
        categoria=Categoria.HALLAZGO,
        clausula_norma="VI.1.8",
        definicion="Aspa (X) azul sobre la figura de la pieza dentaria.",
    ),
    # VI.1.9 — Diente Discrómico
    PeruNomenclatura(
        key="discromico",
        label=_("Diente discrómico"),
        sigla="DIS",
        color_symbolic="azul",
        zona=Zona.RECUADRO,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.9",
        definicion="Siglas DIS en mayúsculas azul en recuadro.",
    ),
    # VI.1.10 — Diente Ectópico
    PeruNomenclatura(
        key="ectopico",
        label=_("Diente ectópico"),
        sigla="E",
        color_symbolic="azul",
        zona=Zona.RECUADRO,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.10",
        definicion="Letra E mayúscula azul en recuadro.",
    ),
    # VI.1.11 — Diente en Clavija
    PeruNomenclatura(
        key="clavija",
        label=_("Diente en clavija"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.RECUADRO,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.11",
        definicion="Triángulo azul circunscribiendo el número de la pieza.",
    ),
    # VI.1.12 — Diente Extruido
    PeruNomenclatura(
        key="extruido",
        label=_("Diente extruido"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.CORONA,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.12",
        definicion="Flecha azul dirigida hacia el plano oclusal.",
    ),
    # VI.1.13 — Diente Intruido
    PeruNomenclatura(
        key="intruido",
        label=_("Diente intruido"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.CORONA,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.13",
        definicion="Flecha recta vertical azul dirigida hacia el ápice.",
    ),
    # VI.1.14 — Edéntulo Total
    PeruNomenclatura(
        key="edentulo_total",
        label=_("Edéntulo total"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.CORONA,
        categoria=Categoria.HALLAZGO,
        clausula_norma="VI.1.14",
        definicion=(
            "Línea recta horizontal azul sobre las coronas de las piezas "
            "ausentes del maxilar edéntulo."
        ),
    ),
    # VI.1.15 — Fractura
    PeruNomenclatura(
        key="fractura",
        label=_("Fractura"),
        sigla=None,
        color_symbolic="rojo",
        zona=Zona.CORONA,
        categoria=Categoria.HALLAZGO,
        clausula_norma="VI.1.15",
        definicion=(
            "Línea recta roja, en el sentido de la fractura, sobre la figura "
            "de la corona y/o raíz."
        ),
    ),
    # VI.1.16 — Geminación / Fusión (cross-teeth — v0.3.0)
    PeruNomenclatura(
        key="geminacion_fusion",
        label=_("Geminación / fusión"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.ENTRE_PIEZAS,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.16",
        cross_teeth=True,
        definicion=(
            "Dos circunferencias azules interceptadas encerrando los números "
            "de las piezas involucradas."
        ),
    ),
    # VI.1.17 — Giroversión
    PeruNomenclatura(
        key="giroversion",
        label=_("Giroversión"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.CORONA,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.17",
        definicion=(
            "Flecha curva azul siguiendo el sentido de la giroversión a "
            "nivel oclusal."
        ),
    ),
    # VI.1.18 — Impactación
    PeruNomenclatura(
        key="impactacion",
        label=_("Impactación"),
        sigla="I",
        color_symbolic="azul",
        zona=Zona.RECUADRO,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.18",
        definicion="Letra I mayúscula azul en recuadro.",
    ),
    # VI.1.19 — Implante
    PeruNomenclatura(
        key="implante",
        label=_("Implante"),
        sigla="IMP",
        color_symbolic="azul",
        zona=Zona.RECUADRO,
        categoria=Categoria.TRATAMIENTO,
        clausula_norma="VI.1.19",
        definicion=(
            "Siglas IMP en mayúsculas azul en el recuadro de la pieza "
            "reemplazada."
        ),
    ),
    # VI.1.20 — Macrodoncia
    PeruNomenclatura(
        key="macrodoncia",
        label=_("Macrodoncia"),
        sigla="MAC",
        color_symbolic="azul",
        zona=Zona.RECUADRO,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.20",
        definicion="Siglas MAC en mayúsculas azul en recuadro.",
    ),
    # VI.1.21 — Microdoncia
    PeruNomenclatura(
        key="microdoncia",
        label=_("Microdoncia"),
        sigla="MIC",
        color_symbolic="azul",
        zona=Zona.RECUADRO,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.21",
        definicion="Siglas MIC en mayúsculas azul en recuadro.",
    ),
    # VI.1.22 — Migración
    PeruNomenclatura(
        key="migracion",
        label=_("Migración"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.CORONA,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.22",
        definicion=(
            "Flecha recta horizontal azul siguiendo el sentido de la "
            "migración a nivel oclusal."
        ),
    ),
    # VI.1.23 — Movilidad (grados 1, 2, 3)
    PeruNomenclatura(
        key="movilidad",
        label=_("Movilidad"),
        sigla="M",
        color_symbolic="azul",
        zona=Zona.RECUADRO,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.23",
        parametros_schema={"grado": [1, 2, 3]},
        definicion=(
            "Letra M mayúscula azul seguida del grado (1, 2 o 3) en el "
            "recuadro. Tipo de clasificación en especificaciones."
        ),
    ),
    # VI.1.24 — INTENTIONALLY ABSENT.
    # The source PDF jumps from VI.1.23 (Movilidad) directly to VI.1.25
    # (Prótesis Removible). See constants.AUSENCIA_NORMATIVA_VI_1_24.
    # A future revision of the norm may fill this clause; we leave the gap
    # explicit so we don't silently renumber other entries (ADR-9).
    #
    # VI.1.25 — Prótesis Removible
    PeruNomenclatura(
        key="protesis_removible",
        label=_("Prótesis removible"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.SOBRE_APICES,
        categoria=Categoria.TRATAMIENTO,
        clausula_norma="VI.1.25",
        definicion=(
            "Dos líneas horizontales paralelas azul (rojo si mal estado) a "
            "nivel de los ápices de las piezas reemplazadas."
        ),
    ),
    # VI.1.26 — Prótesis Total
    PeruNomenclatura(
        key="protesis_total",
        label=_("Prótesis total"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.CORONA,
        categoria=Categoria.TRATAMIENTO,
        clausula_norma="VI.1.26",
        definicion=(
            "Dos líneas rectas paralelas horizontales azul (rojo si mal "
            "estado) sobre las coronas de las piezas del maxilar."
        ),
    ),
    # VI.1.27 — Remanente Radicular
    PeruNomenclatura(
        key="remanente_radicular",
        label=_("Remanente radicular"),
        sigla="RR",
        color_symbolic="rojo",
        zona=Zona.RAIZ,
        categoria=Categoria.HALLAZGO,
        clausula_norma="VI.1.27",
        definicion="Siglas RR en mayúsculas rojo sobre la raíz.",
    ),
    # VI.1.28 — Restauración (materiales: AM, R, IV, IM, IE)
    PeruNomenclatura(
        key="restauracion",
        label=_("Restauración"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.CORONA,
        categoria=Categoria.TRATAMIENTO,
        clausula_norma="VI.1.28",
        parametros_schema={
            "material": ["AM", "R", "IV", "IM", "IE"],
        },
        definicion=(
            "Restauración siguiendo forma en superficies comprometidas, "
            "pintada totalmente azul. Sigla del material en recuadro: "
            "AM=amalgama, R=resina, IV=ionómero, IM=incrustación metálica, "
            "IE=incrustación estética."
        ),
    ),
    # VI.1.29 — Restauración Temporal
    PeruNomenclatura(
        key="restauracion_temporal",
        label=_("Restauración temporal"),
        sigla=None,
        color_symbolic="rojo",
        zona=Zona.CORONA,
        categoria=Categoria.TRATAMIENTO,
        clausula_norma="VI.1.29",
        definicion=(
            "Contorno en rojo siguiendo la forma en las superficies "
            "comprometidas."
        ),
    ),
    # VI.1.30 — Semi-Impactación
    PeruNomenclatura(
        key="semi_impactacion",
        label=_("Semi-impactación"),
        sigla="SI",
        color_symbolic="azul",
        zona=Zona.RECUADRO,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.30",
        definicion="Siglas SI en mayúsculas azul en recuadro.",
    ),
    # VI.1.31 — Supernumerario (cross-teeth — v0.3.0)
    PeruNomenclatura(
        key="supernumerario",
        label=_("Supernumerario"),
        sigla="S",
        color_symbolic="azul",
        zona=Zona.ENTRE_PIEZAS,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.31",
        cross_teeth=True,
        definicion=(
            "Letra S mayúscula encerrada en circunferencia azul, entre los "
            "ápices de las piezas adyacentes al supernumerario."
        ),
    ),
    # VI.1.32 — Transposición (cross-teeth — v0.3.0)
    PeruNomenclatura(
        key="transposicion",
        label=_("Transposición"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.ENTRE_PIEZAS,
        categoria=Categoria.ANOMALIA,
        clausula_norma="VI.1.32",
        cross_teeth=True,
        definicion=(
            "Dos flechas curvas azul entrecruzadas, a la altura de los "
            "números de las piezas involucradas."
        ),
    ),
    # VI.1.33 — Tratamiento Pulpar (tipos: TC, PC, PP)
    PeruNomenclatura(
        key="tratamiento_pulpar",
        label=_("Tratamiento pulpar"),
        sigla=None,
        color_symbolic="azul",
        zona=Zona.RAIZ,
        categoria=Categoria.TRATAMIENTO,
        clausula_norma="VI.1.33",
        parametros_schema={"tipo": ["TC", "PC", "PP"]},
        definicion=(
            "Línea recta vertical azul en la raíz; siglas del tipo en "
            "recuadro: TC=tratamiento de conductos, PC=pulpectomía, "
            "PP=pulpotomía."
        ),
    ),
)


#: Immutable set of normative keys. Consumer extensions cannot collide
#: with these (Disp. V.14 enforced at boot by :class:`PeruAppConfig`).
NORMATIVE_KEYS: frozenset[str] = frozenset(n.key for n in CATALOG)


# ---------------------------------------------------------------------------
# EXTENDED_CATALOG — runtime mapping (CATALOG ∪ validated extensions).
# ---------------------------------------------------------------------------

#: Runtime mapping rebuilt by :meth:`PeruAppConfig.ready` (ADR-11).
#: The frozen ``CATALOG`` tuple is never mutated; only ``EXTENDED_CATALOG``
#: sees consumer extensions. Tests may call :func:`_reset_extended_catalog`
#: to restore a clean state between runs (R3 — idempotent ready()).
EXTENDED_CATALOG: dict[str, PeruNomenclatura] = {n.key: n for n in CATALOG}


def get_extended_catalog() -> dict[str, PeruNomenclatura]:
    """Return the current runtime catalog (CATALOG ∪ validated extensions).

    The returned dict is the same object each call — callers must not mutate
    it. :meth:`PeruAppConfig.ready` is the only sanctioned writer.
    """
    return EXTENDED_CATALOG


def _add_extension(nomenclatura: PeruNomenclatura) -> None:
    """Register a validated consumer extension. Called only by :class:`PeruAppConfig.ready`."""
    EXTENDED_CATALOG[nomenclatura.key] = nomenclatura


def _reset_extended_catalog() -> None:
    """Reset ``EXTENDED_CATALOG`` to just the normative ``CATALOG``.

    Used by :meth:`PeruAppConfig.ready` (idempotent re-entry — R3) and by
    test fixtures that tweak ``XPERTIK_ODONTOGRAMA_PROFILE_EXTENSIONS``.
    """
    EXTENDED_CATALOG.clear()
    EXTENDED_CATALOG.update({n.key: n for n in CATALOG})
