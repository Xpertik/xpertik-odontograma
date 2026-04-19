# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/xpertik/xpertik-odontograma/releases/tag/v0.1.0
