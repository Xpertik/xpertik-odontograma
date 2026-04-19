# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - Unreleased

### Added

- **Peru profile** (`xpertik_odontograma.profiles.peru`) — opt-in data layer that enforces the Norma Técnica del Odontograma del Colegio Odontológico del Perú.
- Profile registry system (`xpertik_odontograma.profiles.registry`) — minimal ≤30-LOC registry for country/regulatory profiles.
- `OdontogramaPeruInicialField` — model field locked to the Peru profile, rejects `profile=` kwarg.
- Peru catalog with **32 nomenclaturas** from clause VI.1 of the norm (26 usable in v0.2.0 + 6 cross-teeth deferred to v0.3.0). Each entry carries its `clausula_norma` for traceability.
- `validate_peru_strict` — strict validator that rejects unknown nomenclaturas, cross-teeth anomalies (with v0.3.0 pointer), invalid parametros, and non-conformant colors.
- HARD extension enforcement via `PeruAppConfig.ready()` — consumer `XPERTIK_ODONTOGRAMA_PROFILE_EXTENSIONS` is validated at Django startup; violations raise `ImproperlyConfigured` with Disp. V.14 citation.
- Symbolic color system — extensions declare `color: "rojo"` or `color: "azul"`, never hex (centralizes normative values).
- `especificaciones` JSON schema additions — per-tooth text field + top-level `especificaciones_generales` (Disp. V.9, V.10, V.11). Helpers in `xpertik_odontograma.profiles.peru.specifications`.
- `XPERTIK_ODONTOGRAMA_PROFILE` setting — activates a profile globally for newly-declared fields (default None).
- `XPERTIK_ODONTOGRAMA_PROFILE_EXTENSIONS` setting — dict of consumer extensions (default {}).
- 170 new tests across 7 test files; total suite now 259 tests.
- README section "Using the Peru profile" with activation, extension, and especificaciones examples.

### Changed

- `OdontogramaField` now accepts an opt-in `profile=` kwarg. When set, chains to the registered profile validator. Default `None` preserves v0.1.0 behavior byte-identically (backward compat verified by 16 dedicated regression tests).
- `validate_odontograma_strict` accepts a keyword-only `profile=` param that dispatches via registry. Existing call sites unchanged.

### Known limitations (v0.2.0 data layer, not full conformance)

- UI is still the v0.1.0 placeholder grid — does not render normative graphic representations (aspas, triángulos, flechas, siglas en recuadros). Full UI conformance ships in v0.3.0.
- Corona vs raíz not separated in the data model — still 5 caras per tooth. v0.3.0.
- Odontograma paralela de evolución (Disp. V.4) not implemented — v0.3.0.
- Inalterabilidad / audit trail (Disp. V.3, V.13) not implemented — v0.3.0.
- 6 cross-teeth anomalies rejected with explicit error pointing to v0.3.0: diastema, geminación/fusión, transposición, supernumerario, aparato ortodóntico fijo/removible.
- VI.1.24 is absent from the norm PDF (discontinuity from 1.23 to 1.25) — documented as `AUSENCIA_NORMATIVA_VI_1_24` constant.

### Backward compatibility

- v0.1.0 consumers NOT activating the Peru profile see ZERO behavior change. The 89 v0.1.0 tests all pass unchanged. Installing v0.2.0 over v0.1.0 requires no migrations.
- Existing DB data under the v0.1.0 schema remains valid when no profile is active.
- Upgrading to activate the Peru profile requires the consumer to map their v0.1.0 state keys to the Peru catalog; this is a DATA migration, documented in the Peru profile section of README.

## [0.1.0] - Unreleased

### Added

- `OdontogramaField`: custom Django model field inheriting from `JSONField`, accepts `denticion` kwarg (`permanente` | `temporal` | `mixta`), preserves kwarg via `deconstruct()` for migrations, honors caller-passed `widget=` in `formfield()`.
- `OdontogramaFormField`: form field subclass routing to `OdontogramaWidget` by default.
- `OdontogramaWidget`: interactive placeholder widget rendering an FDI grid with per-face state selectors. Serializes state to a hidden JSON input on change. Declares `Media` for CSS + JS placeholders.
- `ReadOnlyOdontogramaWidget`: display-only variant. Same grid and colors, no form interaction, no JavaScript.
- `BaseOdontogramaWidget`: shared context builder used by both concrete widgets. Pre-computes face labels per tooth so templates don't need template tags.
- Shared `_tooth_grid.html` partial to avoid markup duplication between editable and readonly templates.
- Redesigned placeholder widget UI as a clinical dental-chart grid (5 faces per tooth, colors from settings, quadrant layout, mode toggle). Still a placeholder — interactive SVG is scheduled for v0.2.0.
- Extensible state palettes via `XPERTIK_ODONTOGRAMA_ESTADOS_CARA` and `XPERTIK_ODONTOGRAMA_ESTADOS_DIENTE` in consumer's `settings.py`. Package defaults wrapped in `gettext_lazy`.
- Write-strict / read-tolerant validation split:
  - `validate_odontograma_strict`: raises `ValidationError` on invalid FDI, XOR violation (`estado` vs `caras`), unknown state keys, invalid `causa`.
  - `sanitize_odontograma_for_render`: never raises; logs warnings to `xpertik_odontograma.legacy_state` for legacy/unknown values, preserves shape for rendering.
- `_FieldBoundValidator` pattern: captures `denticion` per-field instance without class-attribute pollution.
- Canonical face keys: `oclusal_incisal`, `mesial`, `distal`, `vestibular_bucal`, `lingual_palatino`. UI labels resolve dynamically per tooth (anterior vs posterior, superior vs inferior).
- FDI tooth sets as module-level tuples: `DIENTES_PERMANENTES` (32 codes), `DIENTES_TEMPORALES` (20 codes).
- `dientes_por_denticion(denticion)` helper returning the allowed FDI set for each mode.
- `face_label(fdi_code, face_key)` pure function for UI label resolution.
- Test suite: 89 tests covering constants, settings merge (with `@override_settings` + `importlib.reload` pattern), strict + tolerant validators, field roundtrip (with DB integration via `pytest.mark.django_db`), widget context and render.
- `tests/testproject/` minimal Django project for pytest-django.
- CI on GitHub Actions: lint (ruff) gate + 3×3 matrix (Python 3.10/3.11/3.12 × Django 4.2/5.0/5.2), `fail-fast: false`, concurrency cancellation on same-ref pushes.
- TestPyPI release workflow with OIDC Trusted Publisher authentication (no API tokens). Includes mandatory wheel-asset verification step that fails closed if `templates/` or `static/` are missing from the built wheel.
- Hatchling build backend with explicit non-Python asset inclusion (`[tool.hatch.build.targets.wheel]`).
- Ruff config with `E, W, F, I, UP, B` rule set.
- `RELEASING.md` documenting manual Trusted Publisher setup and release cadence.

### Fixed

- Compacted placeholder widget tooth sizing from ~220px to ~85px per tooth so a permanent-dentition row fits in the Django admin viewport without clipping. Face labels abbreviated to single letters (V/M/O/I/D/L/P) with full names preserved as hover tooltips and `aria-label`. Chart containers also get `overflow-x: auto` as a safety net on narrower consumers; print CSS bumps teeth back up for paper legibility.
  - Added `min-width: 0` to chart/row/half flex items and `box-sizing: border-box` + `white-space: nowrap` to the inline `<select>` elements so the native select's intrinsic width (dominated by long option labels like "— sin hallazgo —") can no longer push grid cells past their declared `1fr` share.

### Known limitations (intentional for v0.1.0)

- Widget UI is an HTML placeholder (FDI grid + `<select>` per face). The interactive SVG is planned for v0.2.0 after clinical feedback.
- Published to TestPyPI only. Real PyPI publishing deferred to v0.2.0.
- `OdontogramaField.check()` does not currently emit the originally-specified warning code `xpertik_odontograma.W001` for dentition downgrades. Data-orphan detection requires a DB probe beyond what Django system checks can do statically; will ship as a management command in v0.2.0.
- `vestibular_bucal` face key always labels as "Vestibular" in the UI. The "bucal" synonym distinction for anteriores is under clinical review for v0.2.0.
- No `.po` translation catalogs shipped. Package defaults use `gettext_lazy`; consumer projects that need Spanish-to-another-language translation can generate catalogs themselves.

[0.2.0]: https://github.com/xpertik/xpertik-odontograma/releases/tag/v0.2.0
[0.1.0]: https://github.com/xpertik/xpertik-odontograma/releases/tag/v0.1.0
