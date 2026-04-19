"""Minimal profile registry — module-level dict (ADR-1).

Profiles register their validator hook here at import time. Consumers
activate a profile via ``XPERTIK_ODONTOGRAMA_PROFILE`` setting or per-field
``profile=`` kwarg.

Hard cap: ≤30 LOC of executable code. No ABCs, no entry points, no dynamic
discovery — profiles are package-internal for now.
"""

from __future__ import annotations

from collections.abc import Callable

__all__ = ["clear", "get", "register"]


_REGISTRY: dict[str, Callable] = {}


def register(name: str, hook: Callable) -> None:
    """Register a profile validator hook. Raises on double registration (REQ-1.3)."""
    if name in _REGISTRY:
        raise ValueError(f"profile {name!r} already registered")
    _REGISTRY[name] = hook


def get(name: str) -> Callable | None:
    """Return the validator hook for ``name`` or ``None`` if unregistered (REQ-1.4)."""
    return _REGISTRY.get(name)


def clear() -> None:
    """Clear all registrations. Intended for tests only."""
    _REGISTRY.clear()
