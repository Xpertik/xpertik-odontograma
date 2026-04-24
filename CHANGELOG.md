# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0-alpha.1] - 2026-04-24

### Added

- **SVG interactive chart** replacing the HTML placeholder widget (v0.1.0/v0.2.0).
- **Tooth silhouettes** — 6 SVG `<symbol>` definitions for incisivo, canino, premolar, molar, temporal-anterior, temporal-posterior. Reused via `<use xlink:href="">`. Traced approximations based on Anexo II of the Peruvian norm (polish planned for alpha.2).
- **Apical zone** as a first-class data model zone: per-tooth optional `apice` key alongside `caras`. Nomenclaturas with `zona=RAIZ` (tratamiento_pulpar, remanente_radicular) register here.
- **Anexo II layout** — 3 rows of recuadros above superior teeth + 3 rows below inferior teeth. Siglas auto-derived from tooth state (read-only computed).
- **Contextual popover** (`<dialog>`) — click on any face/apice opens filtered list of catalog nomenclaturas valid for that zona. Parametros sub-selector for movilidad (grado), corona_definitiva (tipo), restauracion (material), tratamiento_pulpar (tipo).
- **Cross-teeth nomenclaturas** visible in selector but disabled with tooltip `Disponible en v0.4.0` (diastema, geminación, transposición, supernumerario, aparato ortodóntico fijo/removible).
- **7 core nomenclaturas** rendered with their normative graphical representations: caries (rojo fill), restauracion (azul fill + material sigla), diente_ausente (aspa azul), corona_definitiva (circunferencia azul + tipo sigla), implante (IMP en recuadro + silueta grayed), movilidad (M{grado} en recuadro), tratamiento_pulpar (línea vertical azul en raíz + tipo sigla).
- **Print CSS** — A4 landscape @page, color preservation via print-color-adjust, popover/selector chrome hidden.
- **Keyboard navigation** — Tab cycles through zones, Enter/Space activates, ESC dismisses popover. ARIA labels on every interactive element.
- New `xpertik_odontograma/svg/` package with `silhouettes.py` + `renderer.py`.
- New `xpertik_odontograma.profiles.peru.widgets.PeruOdontogramaWidget` + readonly variant.
- Backward-compat aliases: `OdontogramaWidget` and `ReadOnlyOdontogramaWidget` still importable (now point to SVG versions).
- 128 new tests (444 total) across new test files: `test_svg_silhouettes.py`, `test_svg_renderer.py`, `test_apice_roundtrip.py`, `test_backward_compat_v0_2.py`, `test_seven_core_nomenclaturas.py`, `test_cross_teeth_disabled.py`, `test_svg_print_layout.py`, `test_profile_peru_widget.py`.

### Changed

- **`OdontogramaPeruInicialField.formfield()`** now binds `PeruOdontogramaWidget` by default for peru-profiled fields.
- **Base `OdontogramaWidget`** now produces SVG output instead of HTML placeholder. Consumers using `widget.render(...)` directly will see SVG markup.
- **JSON schema** extended (additive): per-tooth `apice: {estado, parametros?}` optional key. XOR invariant extended: `estado` (global) XOR (`caras` or `apice`).

### Known limitations (v0.3.0-alpha.1)

- **Partial client-side re-render**: selecting a face nomenclatura updates the face fill color live. Other overlays (aspa, corona ring, tratamiento_pulpar line, auto-derived siglas in recuadros) remain stale until form submit + reload. Full reactive rendering lands in alpha.2.
- **Silhouettes are geometric approximations**. Dentist review drives polish in alpha.2.
- **Alpha.1 covers 7 core nomenclaturas**. The remaining 19 catalog entries (desgaste_oclusal_incisal, discromico, ectopico, clavija, extruido, intruido, edentulo_total, fractura, giroversion, impactacion, macrodoncia, microdoncia, migracion, protesis_removible, protesis_total, remanente_radicular, restauracion_temporal, semi_impactacion, corona_temporal) are in the catalog but not yet rendered with their specific SVG primitives — they appear in the popover but render as plain state color. Full rendering ships in alpha.3.
- **`<dialog>` element**: modern browsers supported. Safari < 15.4 uses the `setAttribute('open')` fallback path in `peru-chart.js`; full manual-focus-trap `<div>` polyfill evaluated for alpha.2 if NVDA/VoiceOver smoke reports gaps.
- **Cross-teeth nomenclaturas** (6 entries) still REJECTED by the strict validator. Visible as disabled in popover with v0.4.0 pointer.

### BREAKING CHANGES

- **Legacy HTML templates DELETED**: `_tooth_cell.html`, `_tooth_grid.html`, `widget.html`, `widget_readonly.html` are no longer present. Consumers who extended these templates must migrate to the new SVG structure.
- **Legacy static files DELETED**: `odontograma.css` and `odontograma.js` replaced by `odontograma-svg.css` and `odontograma-svg.js`. Consumers who referenced the old paths directly must update.
- **Base widget output change**: `OdontogramaWidget.render(...)` now returns SVG markup instead of HTML grid. API-level: `.get_context()` has new keys (`svg_markup`, `value_json`, `catalog_by_zona_json`); old keys (`tooth_rows`, `sections`) removed.

### Backward compatibility

- v0.2.0 data (without `apice` key) validates + renders without migration.
- `OdontogramaField(profile=None)` behavior unchanged from v0.2.0.
- The 89 v0.1.0 tests + 170 v0.2.0 tests + 185 v0.3.0-alpha.1 tests = 444 total, all green.

## [0.2.0] - 2026-04-19

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

[0.3.0-alpha.1]: https://github.com/xpertik/xpertik-odontograma/releases/tag/v0.3.0a1
[0.2.0]: https://github.com/xpertik/xpertik-odontograma/releases/tag/v0.2.0
[0.1.0]: https://github.com/xpertik/xpertik-odontograma/releases/tag/v0.1.0
