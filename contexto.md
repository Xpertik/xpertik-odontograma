# Contexto de inicialización — xpertik-odontograma

## Qué es el proyecto

Un paquete Python distribuible vía PyPI (`pip install xpertik-odontograma`) que
provee un **custom Django Field + Widget** para capturar odontogramas
directamente desde el Django admin (y desde cualquier ModelForm).

Es un paquete de la organización **Xpertik**.

## Motivación

Hace tiempo quise desarrollar algo así para guardar odontogramas desde el
Django admin. La idea es que un dentista pueda, en el admin de Django, hacer
click en cada cara de cada diente y que el estado se guarde automáticamente en
la base de datos como JSON, sin backend extra.

## Decisiones de diseño ya tomadas

### Nomenclatura dental

- **FDI / ISO 3950** (dos dígitos). Estándar internacional de la WDF, adoptado
  por la OMS. Es el que se enseña y usa en Latinoamérica, Europa y
  específicamente en Perú.
- No soportar Universal (EEUU) ni Palmer (en desuso) en v1.

### Soporte de dentición

El paquete debe soportar las tres modalidades desde v1:

- **Permanente** (adulta, 32 dientes): cuadrantes 1–4, posiciones 11–48.
- **Temporal / decidua** (de leche, 20 dientes): cuadrantes 5–8, posiciones 51–85.
- **Mixta** (pediatría 6–12 años): ambas denticiones coexisten en el mismo
  registro. Este es el caso real más común en odontopediatría y no puede
  resolverse como "una o la otra".

Configurable por campo:

    odontograma = OdontogramaField(denticion='mixta', default=dict)

Opciones: `'permanente'` (default), `'temporal'`, `'mixta'`.

### Estructura del JSON guardado — por cara, no solo por diente

El JSON se estructura **por diente y por cara**. Cinco caras por diente
(oclusal/incisal, mesial, distal, vestibular/bucal, lingual/palatino). Esto es
lo que pide la práctica clínica real — un dentista no marca "el diente 16 tiene
caries", marca "la cara oclusal del 16 tiene caries y la mesial tiene amalgama".

Ejemplo de JSON guardado:

    {
      "16": {
        "caras": {
          "oclusal": "caries",
          "mesial": "obturacion_amalgama",
          "distal": null,
          "vestibular": null,
          "lingual": null
        }
      },
      "36": {"estado": "ausente", "causa": "extraccion"},
      "21": {"estado": "no_erupcionado"}
    }

Un diente puede tener o bien un `estado` global (ausente, corona, implante,
etc.) o bien `caras` con hallazgos individuales por superficie — nunca ambos.

Causas de ausencia: `extraccion` | `exfoliacion` | `agenesia`.

### Estados configurables vía settings.py (NO hardcodeados)

Los estados (tanto a nivel diente como a nivel cara) **NO deben estar
hardcodeados** en el paquete. Deben ser **extensibles sin forkear**: el
proyecto que instala `xpertik-odontograma` debe poder agregar, quitar o
renombrar estados desde su propio `settings.py`.

Patrón: `xpertik_odontograma/settings.py` lee del `settings.py` del proyecto
consumidor con defaults razonables y los fusiona:

    # xpertik_odontograma/settings.py
    from django.conf import settings

    DEFAULT_ESTADOS_CARA = {
        'sano':                  {'label': 'Sano',                  'color': '#ffffff'},
        'caries':                {'label': 'Caries',                'color': '#e53935'},
        'obturacion_amalgama':   {'label': 'Obturación amalgama',   'color': '#37474f'},
        'obturacion_resina':     {'label': 'Obturación resina',     'color': '#1e88e5'},
        'sellante':              {'label': 'Sellante',              'color': '#43a047'},
        'fractura':              {'label': 'Fractura',              'color': '#ff9800'},
    }

    DEFAULT_ESTADOS_DIENTE = {
        'no_erupcionado':  {'label': 'No erupcionado',  'color': '#bdbdbd'},
        'ausente':         {'label': 'Ausente',         'color': '#000000'},
        'corona':          {'label': 'Corona',          'color': '#ffd600'},
        'implante':        {'label': 'Implante',        'color': '#8e24aa'},
        'protesis_fija':   {'label': 'Prótesis fija',   'color': '#6d4c41'},
    }

    ESTADOS_CARA = {
        **DEFAULT_ESTADOS_CARA,
        **getattr(settings, 'XPERTIK_ODONTOGRAMA_ESTADOS_CARA', {}),
    }

    ESTADOS_DIENTE = {
        **DEFAULT_ESTADOS_DIENTE,
        **getattr(settings, 'XPERTIK_ODONTOGRAMA_ESTADOS_DIENTE', {}),
    }

Así un proyecto consumidor puede, en su propio `settings.py`:

    XPERTIK_ODONTOGRAMA_ESTADOS_CARA = {
        'obturacion_ionomero': {'label': 'Obturación ionómero', 'color': '#00acc1'},
        'caries_profunda':     {'label': 'Caries profunda',     'color': '#b71c1c'},
    }

…y esos estados aparecen automáticamente en el selector del widget, se validan
al guardar, y se renderizan con el color indicado. Sin forkear, sin tocar el
paquete.

Los validadores (`validators.py`) deben leer de `ESTADOS_CARA` y
`ESTADOS_DIENTE` **dinámicamente**, no de constantes hardcodeadas.

**Tolerancia a datos legacy**: si un registro guardado en la DB contiene un
estado que ya no existe en la configuración actual (porque el dentista lo
eliminó después), el validador no debe crashear al leer. Debe loguear un
warning y renderizar el valor tal cual (con color por defecto gris). Esto se
aprende a la mala en producción.

### Arquitectura

- **Custom Field** heredando de `models.JSONField` (Django ≥ 3.1), override de
  `formfield()` para inyectar el widget custom.
- **Custom Widget** (`OdontogramaWidget`) heredando de `forms.Widget` con:
  - `template_name` apuntando a un HTML con SVG interactivo.
  - `Media` declarando CSS y JS estáticos.
  - `value_from_datadict()` y `format_value()` para serializar a/desde JSON.
- **`ReadOnlyOdontogramaWidget`** aparte (hereda del anterior pero renderiza un
  template distinto sin interactividad). Para vistas de solo lectura: listados
  del admin, detalles no editables, reportes PDF, dashboards. Mismo SVG y mismos
  colores que el editable para consistencia visual, pero sin handlers de click
  ni `<input>` oculto.
- Interacción en el front: SVG con los dientes, click en cara abre selector de
  estado, un `<input type="hidden">` mantiene el JSON serializado que se envía
  en el submit normal del form. Nada de AJAX ni endpoints extra — todo vive
  dentro del ciclo de vida normal de un ModelForm.

## Estructura de archivos esperada

    xpertik-odontograma/
    ├── pyproject.toml
    ├── README.md
    ├── LICENSE                    (MIT)
    ├── MANIFEST.in
    ├── .gitignore
    ├── CHANGELOG.md
    └── xpertik_odontograma/
        ├── __init__.py            (version, default_app_config)
        ├── apps.py
        ├── constants.py           (DIENTES_PERMANENTES, DIENTES_TEMPORALES, CARAS)
        ├── settings.py            (lee overrides del proyecto consumidor, expone ESTADOS_CARA y ESTADOS_DIENTE)
        ├── fields.py              (OdontogramaField)
        ├── forms.py               (OdontogramaFormField)
        ├── widgets.py             (OdontogramaWidget, ReadOnlyOdontogramaWidget)
        ├── validators.py          (validar estructura del JSON, tolerante a estados legacy)
        ├── static/
        │   └── xpertik_odontograma/
        │       ├── css/odontograma.css
        │       └── js/odontograma.js
        └── templates/
            └── xpertik_odontograma/
                ├── widget.html
                └── widget_readonly.html

## Convenciones

- **Nombre PyPI**: `xpertik-odontograma` (con guion).
- **Nombre import Python**: `xpertik_odontograma` (con guion bajo).
- **Versionado**: semver, empezar en `0.1.0`.
- **Compatibilidad**: Django ≥ 4.2 LTS, Python ≥ 3.10.
- **Build system**: `hatchling` (preferido) o `setuptools`.
- **Licencia**: MIT.
- **Publicar primero a TestPyPI** antes de PyPI real.
- **CI sugerido**: GitHub Actions corriendo tests en Python 3.10/3.11/3.12 ×
  Django 4.2/5.0/5.2.

## Qué quiero que hagas como primer paso

1. Crear la estructura de carpetas y archivos vacíos/con stubs.
2. `pyproject.toml` completo con metadata Xpertik, classifiers de Django,
   dependencias mínimas (`Django>=4.2`) y build-system.
3. `constants.py` con las listas completas de dientes permanentes y temporales
   en FDI, y las 5 caras.
4. `settings.py` del paquete con los defaults de `ESTADOS_CARA` y
   `ESTADOS_DIENTE` y el merge con los overrides del proyecto consumidor.
5. Esqueleto funcional mínimo de `fields.py` + `forms.py` + `widgets.py`
   (incluyendo `ReadOnlyOdontogramaWidget`) que ya se pueda instalar con
   `pip install -e .` y registrar en `INSTALLED_APPS` aunque el SVG todavía
   sea placeholder.
6. `validators.py` con validación básica tolerante a estados legacy.
7. Un `README.md` inicial con ejemplo de uso que muestre:
   - Instalación.
   - Uso básico en un modelo.
   - Cómo extender estados desde settings.
   - Uso del widget readonly.
8. No implementar aún el SVG interactivo complejo — dejar un `widget.html`
   mínimo que muestre los números FDI en una grilla y un input hidden con el
   JSON. El diseño visual fino viene en iteraciones posteriores.

Cuando termines, dime qué falta para el primer `pip install -e .` funcional y
cómo probarlo en un proyecto Django de prueba.
