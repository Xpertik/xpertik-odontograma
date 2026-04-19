# Releasing xpertik-odontograma

## One-time setup: Configure Trusted Publisher on TestPyPI

Before the first tag push, a repo admin MUST configure a Trusted Publisher on TestPyPI so the GitHub Actions release workflow can authenticate without API tokens.

### Steps

1. Log into https://test.pypi.org/ with the Xpertik account.
2. Navigate to https://test.pypi.org/manage/account/publishing/.
3. Click **"Add a new pending publisher"**.
4. Fill in:
   - **PyPI Project Name**: `xpertik-odontograma`
   - **Owner**: `xpertik`
   - **Repository name**: `xpertik-odontograma`
   - **Workflow name**: `release-testpypi.yml`
   - **Environment name**: `testpypi`
5. Click **"Add"**.

After this, pushing a tag matching `v*.*.*` (or manually dispatching the workflow) will trigger a build and publish to TestPyPI without needing any secrets in the GitHub repo settings.

## Cutting a release

1. Update version in `pyproject.toml` (`[project] version = "X.Y.Z"`) AND in `xpertik_odontograma/__init__.py` (`__version__ = "X.Y.Z"`).
2. Update `CHANGELOG.md` with the new entry — for the release commit, swap the `[X.Y.Z] - Unreleased` header for `[X.Y.Z] - YYYY-MM-DD`.
3. Commit: `chore(release): X.Y.Z` (conventional commits; NO Co-Authored-By per project convention).
4. Tag: `git tag -a vX.Y.Z -m "Release X.Y.Z — <short summary>"` then `git push origin vX.Y.Z`.
5. GitHub Actions `release-testpypi.yml` runs automatically on the tag push. Watch https://github.com/xpertik/xpertik-odontograma/actions.
6. Verify publication: https://test.pypi.org/project/xpertik-odontograma/
7. Test install from TestPyPI in a clean venv:
   ```
   pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ xpertik-odontograma==X.Y.Z
   ```

## v0.2.0 release notes

- NO additional Trusted Publisher config is required for `v0.2.0`: the v0.1.0 setup on this GitHub repo remains valid.
- The release commit bumps `pyproject.toml` AND `xpertik_odontograma/__init__.py` to `0.2.0`.
- Before tagging, `CHANGELOG.md`'s `## [0.2.0] - Unreleased` header MUST be updated to `## [0.2.0] - YYYY-MM-DD` (the tag workflow does not auto-rewrite the changelog).
- Tag command (human action — do NOT automate from a sub-agent):
  ```
  git tag -a v0.2.0 -m "Release 0.2.0 — Peru profile (data layer)"
  git push origin v0.2.0
  ```
- The sdist/wheel built by `python -m build` include the full `xpertik_odontograma/profiles/peru/` tree (7 modules — `apps.py`, `constants.py`, `fields.py`, `__init__.py`, `specifications.py`, `states.py`, `validators.py`) plus the unchanged templates and static assets from v0.1.0.

### Known limitations v0.2.0 → v0.3.0

What is NOT shipped in v0.2.0 (deferred to v0.3.0 — consumers should be warned before upgrading):

- **UI conformance**: the placeholder grid UI is unchanged. The SVG-based interactive chart required by the Norma (representación gráfica) lands in v0.3.0.
- **Cross-teeth nomenclaturas rejected**: the 6 Peru entries that span multiple pieces are accepted in the catalog metadata but rejected by `validate_peru_strict` with code `cross_teeth_deferred_peru` and an error message pointing to v0.3.0:
  - `diastema` (VI.1.7)
  - `geminacion_fusion` (VI.1.12)
  - `transposicion` (VI.1.30)
  - `supernumerario` (VI.1.28)
  - `aparato_orto_fijo` (VI.1.1)
  - `aparato_orto_removible` (VI.1.2)
- **Evolución field**: only the initial field (`OdontogramaPeruInicialField`) ships. `OdontogramaPeruEvolucionField` and the planned audit trail are v0.3.0.
- **Apical zone rendering + radiographic-findings field + B&W print CSS**: all v0.3.0.
- **`AUSENCIA_NORMATIVA_VI_1_24`**: the catalog has 32 entries (not 33) because clause VI.1.24 is intentionally absent from the norm PDF. Of the 32, 26 are usable write-path; 6 are cross-teeth (rejected until v0.3.0).

### Pre-tag verification checklist (v0.2.0)

Run these BEFORE pushing the `v0.2.0` tag — the tag triggers the publish workflow:

1. `pytest tests/ -q` → 259 passing, 0 failing.
2. `.venv/bin/ruff check .` → `All checks passed!`.
3. `python -m build` → `dist/xpertik_odontograma-0.2.0-py3-none-any.whl` + `dist/xpertik_odontograma-0.2.0.tar.gz` produced.
4. `unzip -l dist/xpertik_odontograma-0.2.0-py3-none-any.whl | grep profiles/peru` → 7 entries (apps, constants, fields, __init__, specifications, states, validators).
5. `unzip -l dist/xpertik_odontograma-0.2.0-py3-none-any.whl | grep -E "(templates|static)"` → templates + static assets still present.
6. Demo-project smoke test: install editable, add `xpertik_odontograma.profiles.peru` to `INSTALLED_APPS`, declare a model with `OdontogramaPeruInicialField`, `manage.py check` + `makemigrations` + `migrate` all clean.
7. `makemigrations --dry-run` twice consecutively in the demo project → both print `No changes detected` (proves `deconstruct()` is stable; REQ-6.4).

## v0.2.0 → v0.3.0 roadmap

- v0.2.0 remains **TestPyPI only** (no real PyPI publish). Real PyPI publishing is still gated on v0.3.0 UI conformance + clinical sign-off.
- v0.3.0 will require a second Trusted Publisher entry on https://pypi.org/ (real PyPI) with the same config pattern.
