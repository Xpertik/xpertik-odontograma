"""Django AppConfig for the Peru profile.

Adding ``"xpertik_odontograma.profiles.peru"`` to ``INSTALLED_APPS`` triggers
three actions at boot (ADR-3, ADR-10, ADR-11):

1. Reset :data:`EXTENDED_CATALOG` from the frozen ``CATALOG`` (idempotent
   across test teardown cycles — R3).
2. Validate every entry in ``XPERTIK_ODONTOGRAMA_PROFILE_EXTENSIONS``. Any
   violation raises :class:`~django.core.exceptions.ImproperlyConfigured`
   BEFORE the app registry finishes loading — HARD per D2.
3. Register the peru validator hook with
   :mod:`xpertik_odontograma.profiles.registry`.

Lazy imports keep this file import-safe outside of Django setup (e.g. in
unit tests that import the validators module directly).
"""

from __future__ import annotations

import logging

from django.apps import AppConfig

logger = logging.getLogger("xpertik_odontograma.profiles.peru.apps")


class PeruAppConfig(AppConfig):
    name = "xpertik_odontograma.profiles.peru"
    label = "xpertik_odontograma_peru"
    verbose_name = "Xpertik Odontograma — perfil Perú"

    def ready(self) -> None:  # noqa: D401 — Django AppConfig hook
        # Lazy imports: avoid executing the profile at module import time —
        # Django calls ready() after the app registry is populated, which is
        # the safe point to touch settings + the base-package registry.
        from django.conf import settings

        from xpertik_odontograma.profiles import get as registry_get
        from xpertik_odontograma.profiles import register as registry_register

        from .states import _add_extension, _reset_extended_catalog
        from .validators import validate_extension_dict, validate_peru_strict

        # R3: tests may fire ready() multiple times. Reset EXTENDED_CATALOG
        # from CATALOG so each run starts from the same baseline before
        # merging extensions.
        _reset_extended_catalog()

        extensions = getattr(settings, "XPERTIK_ODONTOGRAMA_PROFILE_EXTENSIONS", {})
        for nom in validate_extension_dict(extensions):
            _add_extension(nom)

        # Register the peru validator. Idempotent: swallow duplicate-
        # registration errors on test re-entry.
        if registry_get("peru") is None:
            try:
                registry_register("peru", validate_peru_strict)
            except ValueError:  # pragma: no cover — race with another thread
                logger.debug("peru profile already registered; skipping.")
