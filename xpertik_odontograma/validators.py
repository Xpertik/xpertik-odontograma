"""Odontograma validators: strict-write + tolerant-read.

Two PUBLIC functions per ADR-1:

* :func:`validate_odontograma_strict` — raises :class:`~django.core.exceptions.ValidationError`
  on any invariant violation. Used as the write-path validator (attached to
  :class:`~xpertik_odontograma.fields.OdontogramaField` via
  :class:`_FieldBoundValidator`, and invoked from
  :class:`~xpertik_odontograma.forms.OdontogramaFormField`).

* :func:`sanitize_odontograma_for_render` — NEVER raises. Logs warnings via
  ``xpertik_odontograma.legacy_state`` and returns a dict with the same shape
  (downstream renderer decides how to display unknown values — typically with
  :data:`~xpertik_odontograma.settings.DEFAULT_COLOR_UNKNOWN`).

Design notes:

* Both functions read :data:`~xpertik_odontograma.settings.ESTADOS_CARA` and
  :data:`~xpertik_odontograma.settings.ESTADOS_DIENTE` **at call time** (REQ-6.2)
  so ``@override_settings`` + ``importlib.reload`` in tests takes effect.

* :class:`_FieldBoundValidator` captures the field's ``denticion`` as instance
  state (ADR-1, R3) — Django's validator callable signature only passes
  ``value``, so a bound closure is the cleanest way to keep the denticion
  context per-field.
"""

from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.translation import gettext_lazy as _

from . import settings as package_settings
from .constants import CARAS, CAUSAS_AUSENCIA, dientes_por_denticion

__all__ = [
    "validate_tooth_entry",
    "validate_odontograma_strict",
    "sanitize_odontograma_for_render",
    "_FieldBoundValidator",
]


# Strict-write errors go to this logger; renderers / consumers can filter them.
_strict_logger = logging.getLogger("xpertik_odontograma.validators")

# Tolerant-read warnings go to a dedicated logger so consumers can route them
# separately (e.g. to a migration-assistance dashboard) without noise from the
# strict-write errors.
_legacy_logger = logging.getLogger("xpertik_odontograma.legacy_state")


# ---------------------------------------------------------------------------
# Strict write path
# ---------------------------------------------------------------------------

# Allowed top-level keys per branch.
#
# v0.3.0 additions (additive, v0.2.0 data without ``apice`` stays valid):
#
# * ``apice`` — optional per-tooth object ``{estado, parametros?}`` that
#   captures radicular-zone findings (tratamiento pulpar, remanente
#   radicular). It can coexist with ``caras`` (different anatomical
#   zones) but NOT with the whole-tooth ``estado`` branch (XOR extended).
# * ``parametros`` — optional per-tooth parameters dict (e.g. movilidad
#   grado, corona tipo, restauracion material). Profiles own the schema.
# * ``especificaciones`` — optional per-tooth free-text (peru profile).
_ALLOWED_ESTADO_KEYS: frozenset[str] = frozenset(
    {"estado", "causa", "parametros", "especificaciones"}
)
_ALLOWED_CARAS_KEYS: frozenset[str] = frozenset(
    {"caras", "apice", "parametros", "especificaciones"}
)


def validate_tooth_entry(code: Any, entry: Any, denticion: str) -> None:
    """Validate a single ``(fdi_code, entry)`` pair.

    Raises :class:`ValidationError` with a stable ``code`` string on any
    invariant violation:

    * ``invalid_fdi``, ``invalid_fdi_for_denticion``
    * ``entry_not_dict``, ``both_estado_and_caras``, ``neither_estado_nor_caras``
    * ``unknown_estado``, ``invalid_causa``, ``unexpected_keys``
    * ``caras_not_dict``, ``unknown_face``, ``unknown_face_value``
    * ``apice_not_dict``, ``apice_missing_estado`` (v0.3.0+)

    v0.3.0 schema extensions (additive, backward-compatible with v0.2.0):

    * ``apice: {"estado": <key>, "parametros": {...}?}`` — optional per-tooth
      radicular-zone finding (REQ-4.1). Coexists with ``caras`` (different
      anatomical zones) but mutually excludes the whole-tooth ``estado``
      branch (XOR extended: ``estado`` XOR (``caras`` or ``apice``)).
      The peru profile layer validates that ``apice.estado`` is a
      ``zona=RAIZ`` catalog entry.

    Args:
        code: FDI code as it appeared in the JSON (typically a string — JSON
            keys are always strings). Must be coercible to int.
        entry: The per-tooth dict.
        denticion: ``"permanente" | "temporal" | "mixta"``.
    """
    # --- 1. FDI code shape + range -----------------------------------------
    try:
        fdi_int = int(code)
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            _("FDI code %(code)r is not a valid integer."),
            code="invalid_fdi",
            params={"code": code},
        ) from exc

    allowed = dientes_por_denticion(denticion)
    if fdi_int not in allowed:
        raise ValidationError(
            _("FDI code %(code)s is not valid for denticion %(denticion)r."),
            code="invalid_fdi_for_denticion",
            params={"code": fdi_int, "denticion": denticion},
        )

    # --- 2. Entry must be a dict -------------------------------------------
    if not isinstance(entry, dict):
        raise ValidationError(
            _("Entry for tooth %(code)s must be a dict, got %(type)s."),
            code="entry_not_dict",
            params={"code": fdi_int, "type": type(entry).__name__},
        )

    has_estado = "estado" in entry
    has_caras = "caras" in entry
    has_apice = "apice" in entry

    # --- 3. XOR extended: `estado` XOR (`caras` or `apice`) ----------------
    #
    # v0.3.0 adds `apice` as a sibling of `caras` (different anatomical zone).
    # The whole-tooth `estado` branch still mutually excludes per-zone data:
    # you can't say "this tooth is ausente" AND "it has caries on oclusal" at
    # the same time. But `caras` and `apice` CAN coexist (e.g. caries oclusal
    # + tratamiento pulpar — clinically realistic).
    if has_estado and (has_caras or has_apice):
        raise ValidationError(
            _(
                "Tooth %(code)s has both 'estado' and per-zone data "
                "(caras/apice); exactly one branch is allowed."
            ),
            code="both_estado_and_caras",
            params={"code": fdi_int},
        )
    if not has_estado and not has_caras and not has_apice:
        raise ValidationError(
            _(
                "Tooth %(code)s has neither 'estado' nor 'caras' nor 'apice'; "
                "at least one is required."
            ),
            code="neither_estado_nor_caras",
            params={"code": fdi_int},
        )

    # --- 4a. `estado` branch -----------------------------------------------
    if has_estado:
        extra = set(entry) - _ALLOWED_ESTADO_KEYS
        if extra:
            raise ValidationError(
                _("Tooth %(code)s has unexpected keys %(extra)s under 'estado' branch."),
                code="unexpected_keys",
                params={"code": fdi_int, "extra": sorted(extra)},
            )

        estado = entry["estado"]
        if estado not in package_settings.ESTADOS_DIENTE:
            raise ValidationError(
                _("Unknown tooth-state %(estado)r for tooth %(code)s."),
                code="unknown_estado",
                params={"estado": estado, "code": fdi_int},
            )

        if "causa" in entry:
            if estado != "ausente":
                raise ValidationError(
                    _(
                        "Key 'causa' on tooth %(code)s is only allowed when "
                        "estado == 'ausente'."
                    ),
                    code="invalid_causa",
                    params={"code": fdi_int},
                )
            if entry["causa"] not in CAUSAS_AUSENCIA:
                raise ValidationError(
                    _("Unknown causa %(causa)r on tooth %(code)s."),
                    code="invalid_causa",
                    params={"causa": entry["causa"], "code": fdi_int},
                )
        return

    # --- 4b. `caras` and/or `apice` branch ---------------------------------
    extra = set(entry) - _ALLOWED_CARAS_KEYS
    if extra:
        raise ValidationError(
            _("Tooth %(code)s has unexpected keys %(extra)s under 'caras/apice' branch."),
            code="unexpected_keys",
            params={"code": fdi_int, "extra": sorted(extra)},
        )

    if has_caras:
        caras = entry["caras"]
        if not isinstance(caras, dict):
            raise ValidationError(
                _("'caras' for tooth %(code)s must be a dict, got %(type)s."),
                code="caras_not_dict",
                params={"code": fdi_int, "type": type(caras).__name__},
            )

        for face_key, face_value in caras.items():
            if face_key not in CARAS:
                raise ValidationError(
                    _("Unknown face key %(face)r on tooth %(code)s."),
                    code="unknown_face",
                    params={"face": face_key, "code": fdi_int},
                )
            if face_value is None:
                continue
            if face_value not in package_settings.ESTADOS_CARA:
                raise ValidationError(
                    _("Unknown face-state %(state)r on face %(face)s of tooth %(code)s."),
                    code="unknown_face_value",
                    params={"state": face_value, "face": face_key, "code": fdi_int},
                )

    if has_apice:
        apice = entry["apice"]
        if not isinstance(apice, dict):
            raise ValidationError(
                _("'apice' for tooth %(code)s must be a dict, got %(type)s."),
                code="apice_not_dict",
                params={"code": fdi_int, "type": type(apice).__name__},
            )
        if "estado" not in apice:
            raise ValidationError(
                _("'apice' for tooth %(code)s is missing the required 'estado' key."),
                code="apice_missing_estado",
                params={"code": fdi_int},
            )
        # The specific `estado` value and optional `parametros` are validated
        # by the active profile layer (e.g. peru) — the base validator is
        # profile-agnostic and only enforces shape here.


def validate_odontograma_strict(
    value: Any,
    denticion: str = "permanente",
    *,
    profile: str | None = None,
) -> None:
    """Strict validator for the WRITE path.

    Tolerates ``None`` or an empty dict (greenfield records — JSONField's
    ``default=dict`` produces ``{}``). For any other non-dict payload or any
    invalid tooth entry, a single :class:`ValidationError` is raised whose
    ``.error_list`` aggregates every offense found.

    Args:
        value: The odontograma JSON (already decoded to a Python dict).
        denticion: ``"permanente" | "temporal" | "mixta"``.
        profile: Optional profile name to layer country-/regulation-specific
            constraints on top of the base invariants. ``None`` (the default)
            keeps v0.1.0 behavior byte-identical (REQ-7.1). Unknown profile
            names raise :class:`~django.core.exceptions.ImproperlyConfigured`.

    Raises:
        ValidationError: Collecting every invalid entry.
        ImproperlyConfigured: When ``profile`` is non-None and no hook is
            registered for it.
    """
    # Empty odontograms are valid (JSONField default = dict()).
    if value is None or value == {}:
        if profile is not None:
            _dispatch_profile(profile, value, denticion)
        return

    if not isinstance(value, dict):
        raise ValidationError(
            _("Odontograma value must be a dict, got %(type)s."),
            code="odontograma_not_dict",
            params={"type": type(value).__name__},
        )

    errors: list[ValidationError] = []
    for code, entry in value.items():
        # Top-level profile-owned keys (e.g. especificaciones_generales) are
        # handed off to the profile layer below; the base loop ignores them.
        if code == "especificaciones_generales":
            continue
        try:
            validate_tooth_entry(code, entry, denticion)
        except ValidationError as exc:
            errors.append(exc)

    if errors:
        raise ValidationError(errors)

    if profile is not None:
        _dispatch_profile(profile, value, denticion)


def _dispatch_profile(profile: str, value: Any, denticion: str) -> None:
    """Chain a registered profile validator after the base invariants pass."""
    # Lazy import avoids a circular dependency with the profiles package.
    from .profiles import get as _get_profile

    hook = _get_profile(profile)
    if hook is None:
        raise ImproperlyConfigured(
            f"xpertik_odontograma: profile {profile!r} is not registered. "
            f"Add its app to INSTALLED_APPS (or call profiles.register(...)) "
            f"before validating."
        )
    hook(value, denticion)


# ---------------------------------------------------------------------------
# _FieldBoundValidator — ADR-1 / R3
# ---------------------------------------------------------------------------


class _FieldBoundValidator:
    """Callable wrapper that captures a field's ``denticion`` for ``self.validators``.

    Django's validator contract is ``def __call__(value)`` — a single
    argument — so we bind the denticion as instance state. Instances are
    equal iff their ``denticion`` (and optional ``profile``) match, which
    keeps Django's migration autodetector from flagging spurious field
    changes when the field is re-instantiated with the same parameters.

    The ``profile`` kwarg is strictly additive: when omitted/``None``,
    :meth:`deconstruct`'s kwargs dict stays empty so v0.1.0 migrations
    remain byte-stable after upgrading to v0.2.0 (REQ-7.4 / R4).
    """

    __slots__ = ("denticion", "profile")

    def __init__(self, denticion: str, *, profile: str | None = None) -> None:
        self.denticion = denticion
        self.profile = profile

    def __call__(self, value: Any) -> None:
        validate_odontograma_strict(value, self.denticion, profile=self.profile)

    # --- Equality + hash keep migration autodetect stable ------------------
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _FieldBoundValidator):
            return NotImplemented
        return self.denticion == other.denticion and self.profile == other.profile

    def __hash__(self) -> int:
        return hash(("_FieldBoundValidator", self.denticion, self.profile))

    def __repr__(self) -> str:
        if self.profile is None:
            return f"_FieldBoundValidator(denticion={self.denticion!r})"
        return (
            f"_FieldBoundValidator(denticion={self.denticion!r}, "
            f"profile={self.profile!r})"
        )

    # --- Django migration support ------------------------------------------
    def deconstruct(self) -> tuple[str, tuple, dict]:
        # REQ-7.4 / R4: omit `profile` from kwargs when None so v0.1.0
        # migrations remain byte-identical after upgrading.
        kwargs: dict[str, Any] = {}
        if self.profile is not None:
            kwargs["profile"] = self.profile
        return (
            "xpertik_odontograma.validators._FieldBoundValidator",
            (self.denticion,),
            kwargs,
        )


# ---------------------------------------------------------------------------
# Tolerant read path
# ---------------------------------------------------------------------------


def sanitize_odontograma_for_render(
    value: Any,
    denticion: str = "permanente",
) -> dict:
    """Return a dict safe to hand to the renderer; NEVER raises.

    Unknown values are preserved with a warning logged — the renderer will
    fall back to :data:`~xpertik_odontograma.settings.DEFAULT_COLOR_UNKNOWN`
    for any estado / face-state key it doesn't recognize. The one active
    normalization is the "both estado and caras" tie-breaker (ADR-8): when
    legacy data has both branches set, ``estado`` wins and ``caras`` is
    dropped from the output.

    Args:
        value: Any Python value; non-dict inputs produce an empty dict plus
            a warning.
        denticion: Expected denticion for the consuming field; used to log
            out-of-range FDI codes.

    Returns:
        A fresh dict ready to render.
    """
    if value is None or value == {}:
        return {}

    if not isinstance(value, dict):
        _legacy_logger.warning(
            "odontograma value is not a dict (%r); rendering as empty.",
            type(value).__name__,
        )
        return {}

    try:
        allowed = set(dientes_por_denticion(denticion))
    except ValueError:
        # Unknown denticion — still render, just don't range-check FDI codes.
        allowed = set()
        _legacy_logger.warning(
            "denticion %r is not recognized; skipping FDI-range check while sanitizing.",
            denticion,
        )

    estados_diente = package_settings.ESTADOS_DIENTE
    estados_cara = package_settings.ESTADOS_CARA

    cleaned: dict[str, Any] = {}
    for code, entry in value.items():
        # --- FDI sanity + denticion range --------------------------------
        try:
            fdi_int = int(code)
            if allowed and fdi_int not in allowed:
                _legacy_logger.warning(
                    "FDI code %s is outside the %r denticion set; preserving for display.",
                    code,
                    denticion,
                )
        except (TypeError, ValueError):
            _legacy_logger.warning(
                "FDI key %r is not coercible to int; preserving for display.",
                code,
            )

        if not isinstance(entry, dict):
            _legacy_logger.warning(
                "entry for tooth %r is not a dict (%s); preserving for display.",
                code,
                type(entry).__name__,
            )
            cleaned[code] = entry
            continue

        entry_copy = dict(entry)
        has_estado = "estado" in entry_copy
        has_caras = "caras" in entry_copy

        # --- ADR-8 tie-breaker: both present -> estado wins, caras dropped
        if has_estado and has_caras:
            _legacy_logger.warning(
                "tooth %r has both 'estado' and 'caras'; preferring 'estado' "
                "and dropping 'caras' for render (ADR-8).",
                code,
            )
            entry_copy.pop("caras", None)
            has_caras = False

        # --- estado branch: warn on unknown state key -------------------
        if has_estado:
            estado = entry_copy.get("estado")
            if estado not in estados_diente:
                _legacy_logger.warning(
                    "tooth %r has unknown estado %r; will render as unknown "
                    "(default color %s).",
                    code,
                    estado,
                    package_settings.DEFAULT_COLOR_UNKNOWN,
                )
            causa = entry_copy.get("causa")
            if causa is not None and causa not in CAUSAS_AUSENCIA:
                _legacy_logger.warning(
                    "tooth %r has unknown causa %r; preserving for display.",
                    code,
                    causa,
                )

        # --- caras branch: warn on unknown face key / state -------------
        if has_caras:
            caras = entry_copy.get("caras")
            if not isinstance(caras, dict):
                _legacy_logger.warning(
                    "tooth %r 'caras' is not a dict (%s); preserving for display.",
                    code,
                    type(caras).__name__,
                )
            else:
                for face_key, face_value in caras.items():
                    if face_key not in CARAS:
                        _legacy_logger.warning(
                            "tooth %r has unknown face key %r; preserving.",
                            code,
                            face_key,
                        )
                        continue
                    if face_value is None:
                        continue
                    if face_value not in estados_cara:
                        _legacy_logger.warning(
                            "tooth %r face %r has unknown state %r; will render as unknown.",
                            code,
                            face_key,
                            face_value,
                        )

        cleaned[code] = entry_copy

    return cleaned
