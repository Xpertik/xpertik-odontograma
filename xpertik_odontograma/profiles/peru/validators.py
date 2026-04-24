"""Peru profile validators (strict-write) and extension enforcement (boot-time).

Two public callables:

* :func:`validate_peru_strict` — chained after the base
  :func:`xpertik_odontograma.validators.validate_odontograma_strict`; it
  rejects unknown nomenclaturas, cross-teeth nomenclaturas (deferred to
  v0.3.0 per ADR-7), out-of-schema ``parametros``, and mal-shaped
  ``especificaciones`` / ``especificaciones_generales`` strings.

* :func:`validate_extension_dict` — called ONCE at boot by
  :meth:`PeruAppConfig.ready` to vet ``XPERTIK_ODONTOGRAMA_PROFILE_EXTENSIONS``.
  Any violation raises :class:`~django.core.exceptions.ImproperlyConfigured`
  BEFORE Django finishes the app registry load (HARD enforcement per D2).

Helper :func:`resolve_color` resolves symbolic colors (``"rojo" | "azul"``)
to their hex values (Disp. V.7). Hex strings or any other symbolic name
raise :class:`ValueError`.
"""

from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.translation import gettext_lazy as _

from .constants import AZUL_NORMA, ROJO_NORMA, Categoria, Zona
from .specifications import validate_especificaciones_shape
from .states import (
    NORMATIVE_KEYS,
    PeruNomenclatura,
    get_extended_catalog,
)

__all__ = [
    "resolve_color",
    "sanitize_peru",
    "validate_extension_dict",
    "validate_peru_strict",
]


# Strict-write violations log here; renderers and tests can filter.
_strict_logger = logging.getLogger("xpertik_odontograma.profiles.peru.validators")
# Tolerant-read path (sanitize) logs to a dedicated channel — mirrors the
# v0.1.0 split between strict and legacy_state loggers.
_legacy_logger = logging.getLogger("xpertik_odontograma.profiles.peru.legacy_state")


# ---------------------------------------------------------------------------
# Color resolver
# ---------------------------------------------------------------------------


def resolve_color(symbolic: str) -> str:
    """Return the hex value for a symbolic color name.

    Raises :class:`ValueError` on any value other than ``"rojo"`` or
    ``"azul"`` — including hex strings (Disp. V.7, D3).
    """
    if symbolic == "rojo":
        return ROJO_NORMA
    if symbolic == "azul":
        return AZUL_NORMA
    raise ValueError(
        f"color simbólico {symbolic!r} inválido; sólo 'rojo' o 'azul' (Disp. V.7)"
    )


# ---------------------------------------------------------------------------
# Strict write-path validator
# ---------------------------------------------------------------------------


def _validate_parametros(
    nom: PeruNomenclatura,
    fdi_code: str,
    parametros: Any,
) -> None:
    """Cross-check ``parametros`` against a catalog entry's ``parametros_schema``.

    The schema is a ``{param_key: [allowed_values]}`` map. Missing any
    required key, providing a value outside the allowed list, or passing
    a non-dict ``parametros`` all raise :class:`ValidationError`.
    """
    schema = nom.parametros_schema
    if schema is None:
        return  # no schema → nothing to validate

    if not isinstance(parametros, dict):
        raise ValidationError(
            _("Pieza %(code)s: 'parametros' debe ser un dict."),
            code="parametros_not_dict",
            params={"code": fdi_code},
        )

    for param_key, allowed in schema.items():
        if param_key not in parametros:
            raise ValidationError(
                _(
                    "Pieza %(code)s: nomenclatura '%(key)s' requiere parámetro "
                    "'%(param)s' (permitidos: %(allowed)s)."
                ),
                code="missing_parametro",
                params={
                    "code": fdi_code,
                    "key": nom.key,
                    "param": param_key,
                    "allowed": list(allowed),
                },
            )
        if parametros[param_key] not in allowed:
            raise ValidationError(
                _(
                    "Pieza %(code)s: parámetro '%(param)s'=%(got)r no válido para "
                    "'%(key)s' (permitidos: %(allowed)s)."
                ),
                code="invalid_parametro",
                params={
                    "code": fdi_code,
                    "param": param_key,
                    "got": parametros[param_key],
                    "key": nom.key,
                    "allowed": list(allowed),
                },
            )


def _reject_cross_teeth(nom: PeruNomenclatura, fdi_code: str) -> ValidationError:
    """Build a ``ValidationError`` for a cross-teeth nomenclatura (ADR-7)."""
    return ValidationError(
        _(
            "Pieza %(code)s: nomenclatura '%(key)s' (anomalía entre piezas, "
            "cláusula %(clausula)s) no soportada en v0.2.0; implementación "
            "v0.3.0."
        ),
        code="cross_teeth_deferred_peru",
        params={
            "code": fdi_code,
            "key": nom.key,
            "clausula": nom.clausula_norma,
        },
    )


def _validate_tooth_entry_peru(
    fdi_code: str,
    entry: dict,
    catalog: dict[str, PeruNomenclatura],
) -> list[ValidationError]:
    """Run peru-specific checks on one tooth entry. Returns a list of errors."""
    errors: list[ValidationError] = []

    # Per-tooth especificaciones (optional).
    if "especificaciones" in entry:
        try:
            validate_especificaciones_shape(
                entry["especificaciones"], field=f"{fdi_code}.especificaciones"
            )
        except ValidationError as exc:
            errors.append(exc)

    if "estado" in entry:
        estado = entry["estado"]
        if estado not in catalog:
            errors.append(
                ValidationError(
                    _("Pieza %(code)s: nomenclatura '%(key)s' desconocida en el catálogo del perfil Perú."),
                    code="unknown_nomenclatura_peru",
                    params={"code": fdi_code, "key": estado},
                )
            )
            return errors

        nom = catalog[estado]
        if nom.cross_teeth:
            errors.append(_reject_cross_teeth(nom, fdi_code))
            return errors

        try:
            _validate_parametros(nom, fdi_code, entry.get("parametros", {}))
        except ValidationError as exc:
            errors.append(exc)

    if "caras" in entry:
        caras = entry["caras"]
        if isinstance(caras, dict):
            for face_key, face_value in caras.items():
                if face_value is None:
                    continue
                if face_value not in catalog:
                    errors.append(
                        ValidationError(
                            _(
                                "Pieza %(code)s cara %(face)s: nomenclatura "
                                "'%(key)s' desconocida en el catálogo del perfil "
                                "Perú."
                            ),
                            code="unknown_nomenclatura_peru",
                            params={
                                "code": fdi_code,
                                "face": face_key,
                                "key": face_value,
                            },
                        )
                    )
                    continue
                nom = catalog[face_value]
                if nom.cross_teeth:
                    errors.append(_reject_cross_teeth(nom, fdi_code))

    # --- apice branch (v0.3.0 — REQ-4.3, REQ-4.4) --------------------------
    #
    # The base validator (validate_tooth_entry) already enforces that `apice`
    # is a dict with a required `estado` key. Here the peru layer validates
    # that the specific nomenclatura is catalog-known AND lives in `zona=RAIZ`
    # (the anatomical zone that the apice data slot represents). Coronal
    # entries (zona=CORONA) in apice are rejected with code
    # `wrong_zone_for_apice`. Cross-teeth in apice are impossible under the
    # shipped catalog (cross_teeth entries are zona=ENTRE_PIEZAS or
    # SOBRE_APICES, not RAIZ) — the defensive check catches pathological
    # consumer extensions.
    if "apice" in entry:
        apice = entry["apice"]
        if isinstance(apice, dict):
            apice_estado = apice.get("estado")
            if apice_estado:
                if apice_estado not in catalog:
                    errors.append(
                        ValidationError(
                            _(
                                "Pieza %(code)s apice: nomenclatura '%(key)s' "
                                "desconocida en el catálogo del perfil Perú."
                            ),
                            code="unknown_nomenclatura_peru",
                            params={"code": fdi_code, "key": apice_estado},
                        )
                    )
                else:
                    nom = catalog[apice_estado]
                    if nom.cross_teeth:
                        errors.append(_reject_cross_teeth(nom, fdi_code))
                    elif nom.zona != Zona.RAIZ:
                        errors.append(
                            ValidationError(
                                _(
                                    "Pieza %(code)s apice: nomenclatura "
                                    "'%(key)s' pertenece a la zona "
                                    "'%(zona)s'; sólo nomenclaturas con "
                                    "zona=RAIZ son admisibles en 'apice'."
                                ),
                                code="wrong_zone_for_apice",
                                params={
                                    "code": fdi_code,
                                    "key": apice_estado,
                                    "zona": nom.zona.value,
                                },
                            )
                        )
                    else:
                        try:
                            _validate_parametros(
                                nom, fdi_code, apice.get("parametros", {})
                            )
                        except ValidationError as exc:
                            errors.append(exc)

    return errors


def validate_peru_strict(value: Any, denticion: str = "permanente") -> None:
    """Strict peru validator — run AFTER the base validator succeeds (REQ-4.7).

    Rejects:

    * unknown nomenclaturas (``unknown_nomenclatura_peru``, REQ-4.3)
    * cross-teeth nomenclaturas (``cross_teeth_deferred_peru``, REQ-4.4,
      with an error message naming v0.3.0 so the user knows where support
      is headed)
    * out-of-schema ``parametros`` for nomenclaturas that accept variants
    * non-string ``especificaciones`` / ``especificaciones_generales``
      (``especificaciones_not_str``, REQ-8.1/8.2)

    All offenses in a single call are aggregated into one
    :class:`ValidationError` whose ``.error_list`` contains every failure.
    """
    if value is None or value == {}:
        return
    if not isinstance(value, dict):
        # Base validator already rejects non-dict top-level; keep defensive.
        return

    catalog = get_extended_catalog()
    errors: list[ValidationError] = []

    # Top-level especificaciones_generales (optional).
    if "especificaciones_generales" in value:
        try:
            validate_especificaciones_shape(
                value["especificaciones_generales"],
                field="especificaciones_generales",
            )
        except ValidationError as exc:
            errors.append(exc)

    for fdi_code, entry in value.items():
        if fdi_code == "especificaciones_generales":
            continue
        if not isinstance(entry, dict):
            # Base validator already caught this.
            continue
        errors.extend(_validate_tooth_entry_peru(fdi_code, entry, catalog))

    if errors:
        for err in errors:
            # Surface each failure for ops (REQ-4.8); aggregate still raises below.
            _strict_logger.warning(
                "peru strict rejection: code=%s, params=%r",
                getattr(err, "code", "<no-code>"),
                getattr(err, "params", {}),
            )
        raise ValidationError(errors)


# ---------------------------------------------------------------------------
# Tolerant read path (symmetry with base sanitize — never raises).
# ---------------------------------------------------------------------------


def sanitize_peru(value: Any, denticion: str = "permanente") -> dict:
    """Tolerant peru reader — NEVER raises, logs unknown keys.

    Returned dict mirrors the input shape with unknown nomenclaturas
    preserved (the renderer falls back to a gray default). This mirrors
    the v0.1.0 strict/sanitize split so the widget can render legacy data
    after a consumer enables the peru profile without a crash.
    """
    if not isinstance(value, dict):
        return {}

    catalog = get_extended_catalog()
    cleaned: dict[str, Any] = {}

    for fdi_code, entry in value.items():
        if fdi_code == "especificaciones_generales":
            if isinstance(entry, str):
                cleaned[fdi_code] = entry
            else:
                _legacy_logger.warning(
                    "especificaciones_generales no es str (%s); se descarta.",
                    type(entry).__name__,
                )
            continue

        if not isinstance(entry, dict):
            cleaned[fdi_code] = entry
            continue

        entry_copy = dict(entry)

        estado = entry_copy.get("estado")
        if estado is not None and estado not in catalog:
            _legacy_logger.warning(
                "pieza %r tiene estado peru desconocido %r; se renderiza como gris.",
                fdi_code,
                estado,
            )

        caras = entry_copy.get("caras")
        if isinstance(caras, dict):
            for face_key, face_value in caras.items():
                if face_value is None:
                    continue
                if face_value not in catalog:
                    _legacy_logger.warning(
                        "pieza %r cara %r tiene estado peru desconocido %r.",
                        fdi_code,
                        face_key,
                        face_value,
                    )

        cleaned[fdi_code] = entry_copy

    return cleaned


# ---------------------------------------------------------------------------
# Boot-time extension enforcement (HARD — D2).
# ---------------------------------------------------------------------------


_REQUIRED_EXTENSION_FIELDS: frozenset[str] = frozenset(
    {"label", "color", "zona", "categoria"}
)


def validate_extension_dict(extensions: Any) -> list[PeruNomenclatura]:
    """Validate ``XPERTIK_ODONTOGRAMA_PROFILE_EXTENSIONS`` at Django startup.

    Any violation raises :class:`~django.core.exceptions.ImproperlyConfigured`
    — Django's app-registry loader surfaces the error with a clear boot
    failure (ADR-3, D2 HARD).

    Accepted shapes:

    * Top-level dict keyed by profile name, e.g.
      ``{"peru": {"implante_corto": {...}}}``. Only the ``"peru"`` key is
      considered by this validator; other profiles are ignored here.
    * A flat ``{key: spec}`` dict (no profile wrapper) is also accepted for
      backward compatibility with early docs. In that case every entry is
      treated as a peru extension.

    Returns a list of fully-validated :class:`PeruNomenclatura` instances
    ready for insertion into :data:`EXTENDED_CATALOG`.
    """
    if not extensions:
        return []

    if not isinstance(extensions, dict):
        raise ImproperlyConfigured(
            "XPERTIK_ODONTOGRAMA_PROFILE_EXTENSIONS debe ser un diccionario "
            f"(recibido: {type(extensions).__name__})."
        )

    # Support both shapes: {"peru": {...}} or flat {key: spec}.
    if "peru" in extensions and isinstance(extensions["peru"], dict):
        peru_extensions = extensions["peru"]
    else:
        peru_extensions = extensions

    results: list[PeruNomenclatura] = []
    for key, spec in peru_extensions.items():
        results.append(_validate_one_extension(key, spec))
    return results


def _validate_one_extension(key: str, spec: Any) -> PeruNomenclatura:
    """Validate a single extension spec; raise ``ImproperlyConfigured`` on any flaw."""
    # V.14: normative keys cannot be overridden.
    if key in NORMATIVE_KEYS:
        raise ImproperlyConfigured(
            f"extensión '{key}' colisiona con nomenclatura normativa; "
            f"Disp. V.14 — las especialidades pueden ADICIONAR, no MODIFICAR. "
            f"Remediación: renombrá la extensión a una key nueva."
        )

    if not isinstance(spec, dict):
        raise ImproperlyConfigured(
            f"extensión '{key}' debe ser un dict, no {type(spec).__name__}. "
            f"Remediación: envolvelo en {{label, color, zona, categoria, ...}}."
        )

    missing = _REQUIRED_EXTENSION_FIELDS - set(spec.keys())
    if missing:
        raise ImproperlyConfigured(
            f"extensión '{key}' falta campos obligatorios: {sorted(missing)}. "
            f"Remediación: agregá {sorted(missing)} al spec."
        )

    color = spec["color"]
    if color not in ("rojo", "azul"):
        raise ImproperlyConfigured(
            f"extensión '{key}' color inválido {color!r}; debe ser 'rojo' o "
            f"'azul' (Disp. V.7). Remediación: usá colores simbólicos, no hex."
        )

    try:
        zona = Zona(spec["zona"])
    except ValueError as exc:
        raise ImproperlyConfigured(
            f"extensión '{key}' zona inválida {spec['zona']!r}. Remediación: "
            f"elegí una de {[z.value for z in Zona]}."
        ) from exc

    try:
        categoria = Categoria(spec["categoria"])
    except ValueError as exc:
        raise ImproperlyConfigured(
            f"extensión '{key}' categoria inválida {spec['categoria']!r}. "
            f"Remediación: elegí una de {[c.value for c in Categoria]}."
        ) from exc

    return PeruNomenclatura(
        key=key,
        label=spec["label"],
        sigla=spec.get("sigla"),
        color_symbolic=color,
        zona=zona,
        categoria=categoria,
        clausula_norma=spec.get("clausula_norma", "extension"),
        cross_teeth=False,  # v0.2.0: extensions cannot be cross-teeth
        parametros_schema=spec.get("parametros_schema"),
        definicion=spec.get("definicion", ""),
    )
