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

1. Update version in `pyproject.toml` (`[project] version = "X.Y.Z"`).
2. Update `CHANGELOG.md` with the new entry.
3. Commit: `chore(release): X.Y.Z`
4. Tag: `git tag vX.Y.Z && git push --tags`
5. GitHub Actions `release-testpypi.yml` runs automatically. Watch https://github.com/xpertik/xpertik-odontograma/actions.
6. Verify publication: https://test.pypi.org/project/xpertik-odontograma/
7. Test install from TestPyPI in a clean venv:
   ```
   pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ xpertik-odontograma==X.Y.Z
   ```

## v0.1.0 -> v0.2.0 roadmap

- v0.1.0 publishes to **TestPyPI only**. Real PyPI publishing is deferred to v0.2.0 after clinical feedback validates the JSON schema and UX.
- v0.2.0 will require a second Trusted Publisher entry on https://pypi.org/ (real PyPI) with the same config pattern.
