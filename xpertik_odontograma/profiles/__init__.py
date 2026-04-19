"""Profile registry for xpertik_odontograma.

Profiles impose country-specific or regulatory constraints on top of the
base package. See ``xpertik_odontograma.profiles.peru`` for the Peru norm.
"""

from .registry import clear, get, register

__all__ = ["clear", "get", "register"]
