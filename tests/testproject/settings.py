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
    "tests",  # our test-only models live here
]

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
