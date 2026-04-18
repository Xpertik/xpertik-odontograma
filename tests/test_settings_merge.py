"""Tests for :mod:`xpertik_odontograma.settings` consumer-override merge.

The package's effective catalogs (``ESTADOS_CARA``/``ESTADOS_DIENTE``) are
evaluated at **module-import time** (design R5), so ``@override_settings``
alone is NOT enough — the test must also ``importlib.reload`` the settings
module so the new Django settings reach the merge expression. Each test
restores the pristine defaults via a final reload in a try/finally-equivalent
structure (Django's ``override_settings`` context manager pops the override
on exit, and the outer reload puts the module back to the original state).
"""

from __future__ import annotations

import importlib

import pytest
from django.test import override_settings

from xpertik_odontograma import settings as pkg_settings


@pytest.fixture(autouse=True)
def _restore_settings_module():
    """Ensure every test leaves :mod:`xpertik_odontograma.settings` pristine."""
    yield
    importlib.reload(pkg_settings)


# ---------------------------------------------------------------------------
# Defaults alone
# ---------------------------------------------------------------------------


def test_default_merge_has_all_package_estados_cara():
    importlib.reload(pkg_settings)
    # All six shipped defaults must be present.
    for key in (
        "sano",
        "caries",
        "obturacion_amalgama",
        "obturacion_resina",
        "sellante",
        "fractura",
    ):
        assert key in pkg_settings.ESTADOS_CARA


def test_default_merge_has_all_package_estados_diente():
    importlib.reload(pkg_settings)
    for key in (
        "no_erupcionado",
        "ausente",
        "corona",
        "implante",
        "protesis_fija",
    ):
        assert key in pkg_settings.ESTADOS_DIENTE


def test_default_color_unknown_present():
    importlib.reload(pkg_settings)
    assert pkg_settings.DEFAULT_COLOR_UNKNOWN.startswith("#")


# ---------------------------------------------------------------------------
# Consumer ADDS a new key
# ---------------------------------------------------------------------------


def test_override_adds_new_estados_cara_key():
    with override_settings(
        XPERTIK_ODONTOGRAMA_ESTADOS_CARA={
            "custom_state": {"label": "Custom", "color": "#123456"},
        }
    ):
        importlib.reload(pkg_settings)
        assert "custom_state" in pkg_settings.ESTADOS_CARA
        # Defaults are still present (shallow merge with consumer on top).
        assert "sano" in pkg_settings.ESTADOS_CARA
        assert pkg_settings.ESTADOS_CARA["custom_state"]["label"] == "Custom"


def test_override_adds_new_estados_diente_key():
    with override_settings(
        XPERTIK_ODONTOGRAMA_ESTADOS_DIENTE={
            "tratamiento_endo": {"label": "Endodoncia", "color": "#abcdef"},
        }
    ):
        importlib.reload(pkg_settings)
        assert "tratamiento_endo" in pkg_settings.ESTADOS_DIENTE
        assert "corona" in pkg_settings.ESTADOS_DIENTE


# ---------------------------------------------------------------------------
# Consumer REPLACES an existing key
# ---------------------------------------------------------------------------


def test_override_replaces_existing_estados_cara_key():
    with override_settings(
        XPERTIK_ODONTOGRAMA_ESTADOS_CARA={
            "sano": {"label": "Healthy", "color": "#ffffff"},
        }
    ):
        importlib.reload(pkg_settings)
        # Override wins.
        assert pkg_settings.ESTADOS_CARA["sano"]["label"] == "Healthy"
        # Other defaults are still present.
        assert "caries" in pkg_settings.ESTADOS_CARA
        assert "fractura" in pkg_settings.ESTADOS_CARA


# ---------------------------------------------------------------------------
# Restoration: after the override is popped, defaults come back
# ---------------------------------------------------------------------------


def test_defaults_restore_after_override_exits():
    with override_settings(
        XPERTIK_ODONTOGRAMA_ESTADOS_CARA={
            "custom": {"label": "Custom", "color": "#000000"},
        }
    ):
        importlib.reload(pkg_settings)
        assert "custom" in pkg_settings.ESTADOS_CARA
    # Fixture reloads after the test, but we also do so explicitly here to
    # make the restoration step observable inside the test itself.
    importlib.reload(pkg_settings)
    assert "custom" not in pkg_settings.ESTADOS_CARA
    assert "sano" in pkg_settings.ESTADOS_CARA
