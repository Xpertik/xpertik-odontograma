"""Pytest fixtures & configuration for the xpertik-odontograma test suite.

pytest-django auto-discovers the settings module from ``pyproject.toml``
(``[tool.pytest.ini_options].DJANGO_SETTINGS_MODULE``), so this file only
needs a defensive setdefault in case tests are invoked without pytest-django
in the loop (e.g. direct ``python -m unittest`` runs).
"""

from __future__ import annotations

import os

import django


def pytest_configure(config) -> None:  # noqa: D401 — pytest hook signature
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.testproject.settings")
    django.setup()
