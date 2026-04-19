"""Peru profile for xpertik_odontograma — Colegio Odontológico del Perú norm.

Activation:

1. Add ``"xpertik_odontograma.profiles.peru"`` to your Django
   ``INSTALLED_APPS``. This triggers :class:`PeruAppConfig.ready` which
   validates any consumer extensions, populates the runtime catalog, and
   registers the peru validator hook.

2. (Optional) set ``XPERTIK_ODONTOGRAMA_PROFILE = "peru"`` so every bare
   :class:`~xpertik_odontograma.fields.OdontogramaField` picks up peru
   validation by default.

3. (Recommended) declare fields via
   :class:`OdontogramaPeruInicialField` so the profile is locked by class
   identity and admin discovery works without extra wiring.

This module intentionally keeps imports lazy — eagerly importing Django
settings or the base registry here would crash when the package is
inspected outside a Django setup (e.g. by a docs builder).
"""

default_app_config = "xpertik_odontograma.profiles.peru.apps.PeruAppConfig"

__all__ = ["default_app_config"]
