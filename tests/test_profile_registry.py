"""Tests for :mod:`xpertik_odontograma.profiles.registry` (REQ-1.1–1.4).

The registry is deliberately minimal (≤30 executable LOC). These tests pin
its public API and guarantee:

* ``register(name, hook)`` + ``get(name)`` round-trip preserves the hook.
* Double-registration with the same name raises :class:`ValueError`.
* ``get("unknown")`` returns ``None`` (spec REQ-1.4 is authoritative — the
  design skeleton's ``KeyError`` path was overridden by spec).
* ``clear()`` wipes all registrations.

A fixture isolates tests by snapshotting the registry before each test and
restoring it afterwards — the peru profile registers itself at Django boot
via :mod:`xpertik_odontograma.profiles.peru.apps`, so we MUST NOT leave the
registry empty after teardown.
"""

from __future__ import annotations

import pytest

from xpertik_odontograma.profiles import registry


@pytest.fixture
def isolated_registry():
    """Snapshot + restore the registry around each test.

    The peru profile self-registers at Django boot; wiping it would break
    every subsequent test that touches the peru validator.
    """
    snapshot = dict(registry._REGISTRY)
    registry.clear()
    yield registry
    registry.clear()
    registry._REGISTRY.update(snapshot)


# ---------------------------------------------------------------------------
# register + get
# ---------------------------------------------------------------------------


def test_register_then_get_returns_same_hook(isolated_registry):
    def hook(value, denticion):
        return None

    isolated_registry.register("foo", hook)
    assert isolated_registry.get("foo") is hook


def test_register_preserves_callable_identity(isolated_registry):
    sentinel = object()

    def hook(value, denticion):
        hook.sentinel = sentinel

    isolated_registry.register("marker", hook)
    resolved = isolated_registry.get("marker")
    resolved("v", "permanente")
    assert hook.sentinel is sentinel


# ---------------------------------------------------------------------------
# get — unknown lookup returns None (REQ-1.4, NOT KeyError)
# ---------------------------------------------------------------------------


def test_get_unknown_returns_none(isolated_registry):
    # Authoritative behavior per REQ-1.4: the registry is a lookup table and
    # never raises on miss. The field layer is the one that turns an unknown
    # profile into ImproperlyConfigured (REQ-7.3).
    assert isolated_registry.get("unknown") is None


def test_get_unknown_does_not_raise(isolated_registry):
    # No exception type — positive assertion that the call returns.
    result = isolated_registry.get("still-unknown")
    assert result is None


# ---------------------------------------------------------------------------
# register — double-registration rejected (REQ-1.3)
# ---------------------------------------------------------------------------


def test_double_register_raises_value_error(isolated_registry):
    def hook_a(value, denticion):
        return None

    def hook_b(value, denticion):
        return None

    isolated_registry.register("foo", hook_a)
    with pytest.raises(ValueError) as excinfo:
        isolated_registry.register("foo", hook_b)

    # Error message MUST name the duplicate key (spec REQ-1.3).
    assert "foo" in str(excinfo.value)


def test_double_register_preserves_original_hook(isolated_registry):
    def hook_a(value, denticion):
        return None

    def hook_b(value, denticion):
        return None

    isolated_registry.register("foo", hook_a)
    with pytest.raises(ValueError):
        isolated_registry.register("foo", hook_b)

    # The first-registered hook stays wired (REQ-1.3 scenario).
    assert isolated_registry.get("foo") is hook_a


# ---------------------------------------------------------------------------
# clear — test-fixture support
# ---------------------------------------------------------------------------


def test_clear_wipes_registrations(isolated_registry):
    isolated_registry.register("foo", lambda v, d: None)
    isolated_registry.register("bar", lambda v, d: None)

    isolated_registry.clear()

    assert isolated_registry.get("foo") is None
    assert isolated_registry.get("bar") is None


def test_register_works_after_clear(isolated_registry):
    def hook(value, denticion):
        return None

    isolated_registry.register("foo", hook)
    isolated_registry.clear()
    # After clear, foo is free to be re-registered without ValueError.
    isolated_registry.register("foo", hook)
    assert isolated_registry.get("foo") is hook


# ---------------------------------------------------------------------------
# Invariants
# ---------------------------------------------------------------------------


def test_register_multiple_profiles_independently(isolated_registry):
    def hook_es(value, denticion):
        return None

    def hook_pe(value, denticion):
        return None

    isolated_registry.register("es", hook_es)
    isolated_registry.register("pe", hook_pe)

    assert isolated_registry.get("es") is hook_es
    assert isolated_registry.get("pe") is hook_pe
    # Cross-talk check: registering `es` MUST NOT poison `pe`.
    assert isolated_registry.get("pe") is not hook_es
