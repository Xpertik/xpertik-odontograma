# xpertik-odontograma

[![tests](https://github.com/xpertik/xpertik-odontograma/actions/workflows/tests.yml/badge.svg)](https://github.com/xpertik/xpertik-odontograma/actions/workflows/tests.yml)
[![python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://pypi.org/project/xpertik-odontograma/)
[![django](https://img.shields.io/badge/django-4.2%20%7C%205.0%20%7C%205.2-green.svg)](https://pypi.org/project/xpertik-odontograma/)
[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](./LICENSE)

A distributable Django package that provides a custom `OdontogramaField` + `OdontogramaWidget` to record dental odontograms directly from the Django admin — or from any `ModelForm`. No extra backend, no AJAX — state is serialized as JSON in a single hidden input within the normal form submit cycle.

Built around the **FDI / ISO 3950** dental notation standard, with configurable state palettes, support for permanent / primary / mixed dentition, and a per-face (not just per-tooth) data model that matches real clinical workflow.

## Status

**v0.1.0 — early release.** Shipped to [TestPyPI](https://test.pypi.org/project/xpertik-odontograma/) for clinical validation. The widget UI in this release is an HTML placeholder (functional grid with state selectors). The interactive SVG is planned for v0.2.0 after feedback from a practicing odontologist.

Use it if you want to:

- Validate the data model in your own Django project before v0.2.0 lands.
- Build integrations that write/read odontogram JSON.
- Contribute clinical feedback on state names, face keys, or dentition semantics.

## Installation

```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ xpertik-odontograma
```

Or from source (development install):

```bash
git clone https://github.com/xpertik/xpertik-odontograma.git
cd xpertik-odontograma
pip install -e .
```

### Add to your Django project

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "django.contrib.staticfiles",   # REQUIRED — the widget ships CSS/JS as static files
    "xpertik_odontograma",
    # ...
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,   # REQUIRED — widget templates live inside the package
        # ...
    }
]
```

Run `python manage.py collectstatic` in production, or rely on `runserver`'s static-file handling in development.

## Quickstart

### 1. Declare a model field

```python
from django.db import models
from xpertik_odontograma.fields import OdontogramaField


class Patient(models.Model):
    name = models.CharField(max_length=100)
    odontograma = OdontogramaField(denticion="mixta", default=dict)
```

`denticion` accepts three values:

- `"permanente"` (default) — 32 adult teeth, FDI codes 11–48.
- `"temporal"` — 20 primary teeth, FDI codes 51–85.
- `"mixta"` — both sets, for pediatric records during tooth eruption.

`default=dict` is REQUIRED. Django's JSONField requires a callable, not a literal `{}` — the package follows this convention.

### 2. Register in admin

```python
from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    fields = ["name", "odontograma"]
```

That's it. The admin edit form renders the odontogram grid with a state selector per face. Data persists as JSON on form submit.

### 3. Read odontogram data

```python
patient = Patient.objects.get(pk=1)
patient.odontograma
# → {"16": {"caras": {"oclusal_incisal": "caries", "mesial": "obturacion_resina", ...}}, "36": {"estado": "ausente", "causa": "extraccion"}}
```

## JSON schema

The persisted format uses FDI codes as keys. Each tooth entry has EXACTLY ONE of:

```json
{
  "<fdi_code>": {
    "estado": "ausente | corona | implante | ...",
    "causa": "extraccion | exfoliacion | agenesia"
  }
}
```

OR:

```json
{
  "<fdi_code>": {
    "caras": {
      "oclusal_incisal":  "<state_key> | null",
      "mesial":           "<state_key> | null",
      "distal":           "<state_key> | null",
      "vestibular_bucal": "<state_key> | null",
      "lingual_palatino": "<state_key> | null"
    }
  }
}
```

### Face keys

Five canonical keys shared across all teeth. The UI label is resolved dynamically per tooth:

| Key                | Posterior label | Anterior label  |
|--------------------|-----------------|-----------------|
| `oclusal_incisal`  | Oclusal         | Incisal         |
| `mesial`           | Mesial          | Mesial          |
| `distal`           | Distal          | Distal          |
| `vestibular_bucal` | Vestibular      | Vestibular      |
| `lingual_palatino` | Palatino (superior) / Lingual (inferior) | Palatino (superior) / Lingual (inferior) |

This simplification keeps the stored data compact (5 fixed keys) while letting the UI present clinically-correct labels.

## Extending states

State palettes are NOT hardcoded in the package. Override them from your project's `settings.py`:

```python
# settings.py
from django.utils.translation import gettext_lazy as _

XPERTIK_ODONTOGRAMA_ESTADOS_CARA = {
    "obturacion_ionomero": {"label": _("Obturación ionómero"), "color": "#00acc1"},
    "caries_profunda":     {"label": _("Caries profunda"),     "color": "#b71c1c"},
}

XPERTIK_ODONTOGRAMA_ESTADOS_DIENTE = {
    "endodoncia": {"label": _("Endodoncia"), "color": "#5e35b1"},
}
```

These merge WITH the package defaults — you extend, you don't replace. If you want to shadow a default, use the same key:

```python
XPERTIK_ODONTOGRAMA_ESTADOS_CARA = {
    "sano": {"label": _("Healthy"), "color": "#ffffff"},  # overrides default "Sano"
}
```

**i18n note**: the package's own default labels are wrapped in `gettext_lazy`. If your consumer overrides need translation, wrap them yourself — the package does not touch your dict values.

## Peru profile (Norma Técnica del Colegio Odontológico)

`xpertik-odontograma` ships an optional **Peru profile** that enforces the Norma Técnica del Odontograma issued by the Colegio Odontológico del Perú. When activated, the profile:

- Restricts colors to the two normative values (**red** `#d32f2f` / **blue** `#1565c0`) — Disposición V.7.
- Validates each tooth entry against a **catalog of 32 normative nomenclaturas** (VI.1 of the norm). 6 are cross-teeth anomalies (diastema, geminación/fusión, transposición, supernumerario, ortodonticos fijo/removible) and are REJECTED in v0.2.0 with a clear error pointing to v0.3.0. **26 usable** in v0.2.0.
- Adds `especificaciones` fields (per-tooth and global) for findings that cannot be registered graphically (Disp. V.9, V.10, V.11).
- Enforces extensions STRICTLY via `AppConfig.ready()` — any consumer attempting to override a normative key or use a hex color will see Django fail to start with a clear error (Disp. V.14).

### Activation

1. Add the profile to `INSTALLED_APPS`:

   ```python
   INSTALLED_APPS = [
       # ...
       "xpertik_odontograma",
       "xpertik_odontograma.profiles.peru",  # <-- add this
       # ...
   ]
   ```

2. Declare a field in your model:

   ```python
   from xpertik_odontograma.profiles.peru.fields import OdontogramaPeruInicialField

   class Paciente(models.Model):
       nombre = models.CharField(max_length=150)
       odontograma = OdontogramaPeruInicialField(default=dict, blank=True)
   ```

   The profile is locked to `"peru"` on this field class. Passing `profile=` as a kwarg raises `TypeError`.

### Extending the catalog

Especialidades may ADD new nomenclaturas without modifying the base catalog (Disp. V.14):

```python
# settings.py
XPERTIK_ODONTOGRAMA_PROFILE_EXTENSIONS = {
    "implante_corto": {
        "label": _("Implante corto"),
        "color": "azul",               # symbolic only — never hex
        "zona": "corona",              # corona | raiz | entre_piezas | recuadro | sobre_apices
        "categoria": "tratamiento",    # hallazgo | tratamiento | anomalia | ortodontico
        "sigla": "IMP-C",
    },
}
```

HARD rules (violation → `ImproperlyConfigured` at Django startup):

- Extension key MUST NOT collide with any key in the normative catalog.
- `color` MUST be `"rojo"` or `"azul"` (symbolic). Hex values are rejected.
- `zona` and `categoria` MUST be one of the enum values.
- All required fields (label, color, zona, categoria) MUST be present.

### Especificaciones

The JSON schema is extended with two optional text fields:

```json
{
  "16": {
    "caras": {"oclusal_incisal": "caries"},
    "especificaciones": "Dolor al frío, sensibilidad dentinaria"
  },
  "especificaciones_generales": "Hallazgos radiográficos: dos lesiones periapicales en el cuadrante superior derecho"
}
```

Use the helpers in `xpertik_odontograma.profiles.peru.specifications` to read/write safely.

### What the profile does NOT do (v0.2.0)

- Renders the custom graphical representations per nomenclatura (aspas, triángulos, flechas, siglas en recuadros). The UI stays as the v0.1.0 HTML placeholder. Interactive SVG with normative graphics lands in v0.3.0.
- Does NOT separate corona vs raíz as distinct zones (still 5 caras per tooth). v0.3.0 will model the apical zone as its own entity.
- Does NOT implement the parallel odontograma de evolución (Disp. V.4). v0.3.0.
- Does NOT enforce inalterabilidad / audit trail (Disp. V.3, V.13). v0.3.0.
- Does NOT support cross-teeth anomalies (6 of 32 nomenclaturas). v0.3.0.

For the full conformance analysis and v0.3.0 roadmap, see [NORMA_CUMPLIMIENTO.md](./NORMA_CUMPLIMIENTO.md).

### References

- [Norma Técnica del Odontograma — PDF](./docs/norms/norma-tecnica-odontograma-peru.pdf) (Colegio Odontológico del Perú)
- [Análisis de conformidad](./NORMA_CUMPLIMIENTO.md) (1000+ lines, per-clause + per-nomenclatura analysis)

## Readonly widget

For display-only contexts (report pages, PDF exports, audit logs), use `ReadOnlyOdontogramaWidget`:

```python
from django import forms
from xpertik_odontograma.fields import OdontogramaField
from xpertik_odontograma.widgets import ReadOnlyOdontogramaWidget


class PatientReadonlyForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["odontograma"]
        widgets = {
            "odontograma": ReadOnlyOdontogramaWidget(denticion="mixta"),
        }
```

Same grid, same colors, no editing UI, no JavaScript loaded.

## Validation

The package ships two validation paths:

- **Strict (on write)**: `xpertik_odontograma.validators.validate_odontograma_strict` runs automatically when a model is saved through a form or via `full_clean()`. Rejects invalid FDI codes for the declared dentition, malformed tooth entries, unknown state keys, and invalid `causa` values.
- **Tolerant (on read)**: `xpertik_odontograma.validators.sanitize_odontograma_for_render` is invoked by the widget before rendering. It NEVER raises — if a record contains a state key that was since removed from your config (e.g., a clinic edited their palette), the widget logs a warning and renders the tooth with a neutral gray.

This write-strict / read-tolerant split lets you evolve your state palette without breaking historical records.

## Logger namespaces

| Logger                                    | What it logs                                               |
|-------------------------------------------|------------------------------------------------------------|
| `xpertik_odontograma`                     | Parent — catch-all for all package logs                    |
| `xpertik_odontograma.legacy_state`        | Legacy/unknown state values encountered on read            |
| `xpertik_odontograma.validators`          | Validation details at DEBUG level                          |
| `xpertik_odontograma.widgets`             | Widget rendering diagnostics                               |

Configure in your `LOGGING` dict:

```python
LOGGING = {
    "version": 1,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "xpertik_odontograma.legacy_state": {"handlers": ["console"], "level": "WARNING"},
    },
}
```

## Roadmap

- **v0.1.0**: generic data model, validators, placeholder UI, tests, CI, **TestPyPI only**. Clinical feedback loop with one practicing odontologist.
- **v0.2.0** (shipped with this release): **data-layer Peru profile** — catalog of 32 normative nomenclaturas (26 usable + 6 cross-teeth deferred), symbolic colors, HARD extension enforcement, `especificaciones` per-tooth and global, `OdontogramaPeruInicialField`. Byte-identical backward compat when no profile is active. UI still the v0.1.0 placeholder grid.
- **v0.3.0**: interactive SVG widget with full normative graphical conformance (aspas, triángulos, flechas, siglas en recuadros), apical zone as a distinct entity, cross-teeth anomalies, odontograma paralela de evolución (Disp. V.4), inalterabilidad + audit trail (Disp. V.3, V.13), B&W print CSS, radiographic findings field. Publication to PyPI proper.

## Contributing

This is a Xpertik project. Issues and PRs welcome at https://github.com/xpertik/xpertik-odontograma.

For local development:

```bash
git clone https://github.com/xpertik/xpertik-odontograma.git
cd xpertik-odontograma
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e ".[test]"
pytest
```

Before submitting a PR:

```bash
ruff check .
pytest -ra tests/
```

## License

MIT © 2026 Xpertik. See [LICENSE](./LICENSE).
