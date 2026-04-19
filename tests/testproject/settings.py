"""Minimal Django settings used by the pytest-django test runner.

Keep this file tiny and dependency-free: it's imported by every test run and
by the project-level ``manage.py check`` equivalent. Real consumers of the
package ship their own settings — this module only exists to exercise
``xpertik_odontograma`` end-to-end (forms, fields, migrations, templates).
"""

from __future__ import annotations

SECRET_KEY = "test-secret-not-for-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "xpertik_odontograma",
    # v0.2.0: the peru profile registers its validator hook via AppConfig.ready().
    # Adding it here activates OdontogramaPeruInicialField for the `tests` app
    # models without forcing a global XPERTIK_ODONTOGRAMA_PROFILE = "peru" setting
    # (which would affect the v0.1 Patient model's backward-compat tests).
    "xpertik_odontograma.profiles.peru",
    "tests",  # our test-only models live here
]

# Intentionally left unset: keep the global profile default to None so the v0.1.0
# `Patient` model (which uses bare `OdontogramaField`) preserves byte-identical
# v0.1.0 behavior (REQ-7.1). The peru-specific tests use `OdontogramaPeruInicialField`
# which locks `profile="peru"` at the class level.
# XPERTIK_ODONTOGRAMA_PROFILE = "peru"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

USE_TZ = True
STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
ROOT_URLCONF = "tests.testproject.urls"
