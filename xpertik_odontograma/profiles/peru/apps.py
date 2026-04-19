"""Django AppConfig for the Peru profile.

Adding ``"xpertik_odontograma.profiles.peru"`` to ``INSTALLED_APPS`` triggers
two phases at boot:

1. At ``apps.py`` module import time (during ``apps.populate``, BEFORE any
   app's ``models.py`` is loaded), the peru validator hook is registered
   with the base-package registry. This guarantees that downstream apps
   which declare :class:`OdontogramaPeruInicialField` at model-class-body
   time can look up the ``"peru"`` profile successfully (REQ-7.3).
2. In :meth:`PeruAppConfig.ready` (after all apps are populated), the
   consumer-side ``XPERTIK_ODONTOGRAMA_PROFILE_EXTENSIONS`` dict is
   HARD-validated (ADR-3, ADR-10, ADR-11) and each accepted extension is
   merged into :data:`EXTENDED_CATALOG`. Any violation raises
   :class:`~django.core.exceptions.ImproperlyConfigured` before Django
   finishes booting.

Lazy imports keep this file import-safe outside of Django setup (e.g. in
unit tests that import the validators module directly).
"""

from __future__ import annotations

import logging

from django.apps import AppConfig

logger = logging.getLogger("xpertik_odontograma.profiles.peru.apps")


def _register_hook_idempotent() -> None:
    """Register ``validate_peru_strict`` with the base registry (idempotent).

    Called at ``apps.py`` import time so the profile is resolvable before any
    app's ``models.py`` declares an :class:`OdontogramaPeruInicialField`.
    """
    from xpertik_odontograma.profiles import get as registry_get
    from xpertik_odontograma.profiles import register as registry_register

    from .validators import validate_peru_strict

    if registry_get("peru") is None:
        try:
            registry_register("peru", validate_peru_strict)
        except ValueError:  # pragma: no cover — race with another thread
            logger.debug("peru profile already registered; skipping.")


# Register at module import time — Django imports all AppConfig modules during
# apps.populate() BEFORE any app's models.py loads. Model fields of type
# OdontogramaPeruInicialField would otherwise fail to resolve "peru" at class
# body time (REQ-7.3 would raise ImproperlyConfigured during models import).
_register_hook_idempotent()


class PeruAppConfig(AppConfig):
    name = "xpertik_odontograma.profiles.peru"
    label = "xpertik_odontograma_peru"
    verbose_name = "Xpertik Odontograma — perfil Perú"

    def ready(self) -> None:  # noqa: D401 — Django AppConfig hook
        # Lazy imports keep ready() safe to call from tests that tweak
        # XPERTIK_ODONTOGRAMA_PROFILE_EXTENSIONS and re-trigger the hook.
        from django.conf import settings

        from .states import _add_extension, _reset_extended_catalog
        from .validators import validate_extension_dict

        # R3: tests may fire ready() multiple times. Reset EXTENDED_CATALOG
        # from CATALOG so each run starts from the same baseline before
        # merging extensions.
        _reset_extended_catalog()

        extensions = getattr(settings, "XPERTIK_ODONTOGRAMA_PROFILE_EXTENSIONS", {})
        for nom in validate_extension_dict(extensions):
            _add_extension(nom)

        # Belt-and-suspenders: ensure the hook is registered even if module
        # import order surprises us (e.g. under a custom AppConfig loader).
        _register_hook_idempotent()
