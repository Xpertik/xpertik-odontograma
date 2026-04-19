# Análisis de Conformidad — Norma Técnica del Odontograma (Perú)

**Paquete**: `xpertik-odontograma`
**Versión analizada**: v0.1.0
**Norma de referencia**: Norma Técnica del Odontograma — Colegio Odontológico del Perú, Consejo Administrativo Nacional ([Norma Técnica](docs/norms/norma-tecnica-odontograma-peru.pdf))
**Fecha de análisis**: 2026-04-19
**Estado general**: ⚠️ **NO CONFORME** — cimiento técnico correcto (FDI, dentición, estructura por pieza) pero faltan ≥80% de las nomenclaturas normativas, sistema de colores no conforme, ausencia de odontograma de evolución e inalterabilidad, campo de especificaciones no implementado.

**Este documento es la fuente de verdad del scope v0.2.0 "perfil Perú"** — todo cambio registrado aquí como "Plan v0.2.0" se consolidará en el change `v0-2-0-peru-profile`.

---

## Shipped in v0.2.0 (2026-04-19)

El change `v0-2-0-peru-profile` cerró la **capa de datos** del perfil Perú. El análisis original de este documento se escribió contra v0.1.0; las secciones siguientes permanecen como registro histórico, pero los siguientes deltas aplican a v0.2.0:

**Deltas implementados (capa de datos)**:

- ✅ Perfil Perú opt-in (`xpertik_odontograma.profiles.peru`): se activa agregando `"xpertik_odontograma.profiles.peru"` a `INSTALLED_APPS` + declarando un `OdontogramaPeruInicialField` en el modelo.
- ✅ Sistema de colores normativo: constantes `ROJO_NORMA = "#d32f2f"` y `AZUL_NORMA = "#1565c0"` + sistema simbólico (`"rojo"` / `"azul"`); rechazo duro de hex en extensiones (V.7 en la capa de datos).
- ✅ Catálogo de **32 nomenclaturas** (VI.1.1–VI.1.33 menos VI.1.24, documentada como `AUSENCIA_NORMATIVA_VI_1_24`). Cada entrada lleva `clausula_norma` para trazabilidad (VI.1 en la capa de datos).
- ✅ **26 usables en v0.2.0**; 6 cross-teeth (aparato orto fijo/removible, diastema, geminación/fusión, transposición, supernumerario) RECHAZADAS con mensaje explícito apuntando a v0.3.0.
- ✅ `validate_peru_strict`: validador opt-in que dispatcha por registry; rechaza nomenclaturas desconocidas, colores hex, parametros inválidos.
- ✅ Campo `especificaciones` por pieza + top-level `especificaciones_generales` (Disp. V.9, V.10, V.11 en la capa de datos). Helpers en `profiles.peru.specifications`.
- ✅ HARD enforcement de extensiones vía `PeruAppConfig.ready()` — cualquier intento del consumidor de sobrescribir una key normativa o usar hex hace fallar el arranque de Django con `ImproperlyConfigured` (V.14).
- ✅ Backward compat byte-a-byte: los 89 tests de v0.1.0 siguen en verde sin cambios; ninguna migración requerida al subir de v0.1.0 → v0.2.0 siempre que no se active el perfil.
- ✅ 170 tests nuevos (total 259) pinean: tamaño del catálogo, las 6 keys cross-teeth, aritmética "26 usables", inmutabilidad del dataclass frozen, rechazo de cada una de las 6 cross-teeth con texto literal "v0.3.0", 16 regresiones v0.1.

**Lo que NO cambió en v0.2.0 (queda pendiente para v0.3.0)**:

- ⏳ Widget / UI: sigue siendo el grid HTML placeholder de v0.1.0. No renderiza las representaciones gráficas normativas (aspas, triángulos, flechas, siglas en recuadros).
- ⏳ Zona apical separada de la coronal (Anexo II 5.4).
- ⏳ Recuadros superiores/inferiores para siglas (Anexo II 5.1).
- ⏳ `OdontogramaPeruEvolucionField` / odontograma paralela de evolución (Disp. V.4).
- ⏳ Inalterabilidad + audit trail (Disp. V.3, V.13).
- ⏳ CSS `@media print` B/N (Disp. V.12).
- ⏳ Hallazgos radiográficos como sub-clave estructurada (Disp. V.11).
- ⏳ Cross-teeth anomalies (6 nomenclaturas).
- ⏳ Distinción semántica hallazgos vs plan (Disp. V.5) — se tipifica la `categoria` en el catálogo pero no hay enforcement semántico.

El roadmap actualizado está en la Sección 6.

---

## Sección 1 — Resumen ejecutivo

| Eje | Status | Severidad | Notas |
|-----|--------|-----------|-------|
| Nomenclatura FDI / ISO 3950 | ✅ CONFORME | — | V.2 cumplida — `DIENTES_PERMANENTES` y `DIENTES_TEMPORALES` usan codificación digito-2 |
| Dentición permanente / temporal / mixta | ✅ CONFORME | — | Configurable vía `denticion=` kwarg en `OdontogramaField` |
| Línea central entre lados | ✅ CONFORME | — | Midline CSS en el widget placeholder |
| Sistema de colores (solo rojo y azul) | ✅ CONFORME (en perfil Perú v0.2.0) / ⚠️ OPT-IN | CRÍTICO | `profiles.peru` fija `#d32f2f`/`#1565c0`; paquete base conserva paleta v0.1.0 para uso genérico no-Perú |
| 33 nomenclaturas específicas (VI.1) | ⚠️ PARCIAL v0.2.0 — 26/32 usables en datos | CRÍTICO | Catálogo de datos completo (32 entradas, VI.1.24 ausente en norma). 6 cross-teeth rechazadas apuntando a v0.3.0. Representación gráfica normativa: ⏳ v0.3.0. |
| Representación gráfica por nomenclatura | ❌ NO CONFORME (UI intacta en v0.2.0) | CRÍTICO | UI sigue el placeholder de v0.1.0; SVG interactivo normativo llega en v0.3.0 |
| Inalterabilidad (V.3 y V.13) | ❌ NO CONFORME (⏳ v0.3.0) | ALTO | Edición libre actual, sin audit trail, sin firma de modificación |
| Odontograma paralelo de evolución (V.4) | ❌ NO IMPLEMENTADA (⏳ v0.3.0) | ALTO | Falta segundo field / modelo paralelo para evolución de tratamientos |
| Distinción hallazgos vs plan (V.5) | ⚠️ PARCIAL v0.2.0 — categoría tipificada | MEDIO | `categoria` se tipifica en el catálogo (hallazgo/tratamiento/anomalia/ortodontico); enforcement semántico ⏳ v0.3.0 |
| Campo de especificaciones (V.9, V.10, V.11) | ✅ CONFORME v0.2.0 (per-tooth + global) | ALTO | `especificaciones` por pieza + `especificaciones_generales` top-level + helpers |
| Zona Apical diferenciada (Anexo II) | ❌ NO IMPLEMENTADA (⏳ v0.3.0) | ALTO | Solo hay 5 caras coronales, sin separar corona / raíz |
| Recuadros encima/debajo para siglas (Anexo II) | ❌ NO IMPLEMENTADO (⏳ v0.3.0) | ALTO | UI placeholder no renderiza los 3 recuadros superiores + 3 inferiores por cuadrante |
| Impresión en negro (V.12) | ⚠️ PARCIAL (⏳ v0.3.0) | MEDIO | Print CSS actual mantiene colores; falta `@media print` que convierta a B/N |
| Corona ≥ 1 cm² impresa (V.12) | ⚠️ PARCIAL (⏳ v0.3.0) | BAJO | Tamaño CSS relativo — se respeta en pantalla pero no validado en impresión |
| Extensibilidad por especialidad (V.14) | ✅ CONFORME v0.2.0 (HARD enforcement) | MEDIO | `PeruAppConfig.ready()` rechaza override de keys normativas + hex; `ImproperlyConfigured` al arranque |
| Tiempo máximo 10 min (V.15) | N/A | — | Requisito operativo humano, no técnico del paquete |

**Veredicto**: el paquete v0.1.0 es un buen cimiento técnico-estructural pero funcionalmente sirve como odontograma genérico; para cumplir la Norma Técnica del Perú se requiere un **perfil específico** (`xpertik_odontograma.profiles.peru`) con las 33 nomenclaturas, paleta binaria rojo/azul, zona apical, recuadros de siglas, item especificaciones, evolución paralela e inalterabilidad.

---

## Sección 2 — Análisis por Disposición General (V. del PDF, 15 items)

#### V.1 — La odontograma debe formar parte de la Ficha Estomatológica y de la Historia Clínica

**Enunciado normativo**: "La odontograma debe formar parte de la Ficha Estomatológica y de la Historia Clínica."

**Status actual en v0.1.0**: ✅ CONFORME (por diseño de integración)

**Evidencia**:
- `xpertik_odontograma/fields.py` — `OdontogramaField` hereda de `JSONField` y se instala en el modelo consumidor (típicamente la Historia Clínica o Ficha Estomatológica del proyecto host).
- La README documenta este patrón de integración.

**Brecha**: ninguna a nivel de paquete. La integración correcta queda bajo la responsabilidad del consumidor.

**Plan v0.2.0**: documentar explícitamente en README que el campo debe vivir en el modelo Ficha Estomatológica / Historia Clínica del consumidor, y no como modelo standalone.

---

#### V.2 — Sistema numérico dígito-2 FDI / OMS

**Enunciado normativo**: "El sistema numérico para la odontograma debe ser el sistema digito dos o binario propuesto por la Federación Dental Internacional y aceptada por la Organización Mundial de la Salud."

**Status actual en v0.1.0**: ✅ CONFORME

**Evidencia**:
- `xpertik_odontograma/constants.py:32-45` — `DIENTES_PERMANENTES` (11-48) y `DIENTES_TEMPORALES` (51-85) siguen exactamente FDI / ISO 3950.
- `validators.py:82-98` — validación estricta de `invalid_fdi` y `invalid_fdi_for_denticion`.

**Brecha**: ninguna.

**Plan v0.2.0**: n/a.

---

#### V.3 — Desarrollo individual en primera cita; inalterable

**Enunciado normativo**: "La odontograma se debe desarrollar individualmente para cada paciente, durante la primera cita odontológica y será inalterable."

**Status actual en v0.1.0**: ❌ NO CONFORME

**Evidencia**:
- `OdontogramaField` hoy es un `JSONField` estándar: cualquier `save()` puede sobreescribirlo libremente.
- No hay audit trail, ni append-only, ni bloqueo post-creación.
- `admin.py` expone el campo editable en el `ModelAdmin` por defecto.

**Brecha**: no existe mecanismo que impida modificar el odontograma inicial tras la primera cita.

**Plan v0.2.0**:
- Separar el modelo en dos fields conceptuales: `odontograma_inicial` (frozen tras `created`) y `odontograma_evolucion` (mutable, ver V.4).
- Implementar `OdontogramaInicialField` con hook `pre_save` que levante `ValidationError` si el valor previo existe y difiere (excepto vía flujo firmado, ver V.13).
- Opcional (perfil estricto): integrar `django-simple-history` o tabla de audit propia para mantener trail inmutable.

---

#### V.4 — Odontograma paralela de evolución de tratamientos

**Enunciado normativo**: "Paralelamente se debe desarrollar una odontograma que registre la evolución de los tratamientos dentales."

**Status actual en v0.1.0**: ❌ NO IMPLEMENTADA

**Evidencia**: solo existe un `OdontogramaField` — no hay separación entre odontograma inicial (diagnóstico) y odontograma evolutivo (seguimiento).

**Brecha**: arquitectura de un solo campo. No se puede registrar el avance del tratamiento sin sobreescribir el inicial (violando V.3).

**Plan v0.2.0**:
- Agregar `OdontogramaEvolucionField` (alias semántico del `OdontogramaField`, mismo schema, pero mutable).
- Recomendación al consumidor: `odontograma_inicial = OdontogramaInicialField()` + `odontograma_evolucion = OdontogramaEvolucionField(default=dict)` (el segundo se actualiza en cada cita).
- **Decisión abierta** (ver Sección 7): ¿un `JSONField` secundario o un modelo `OdontogramaEvolucion` separado con FK al paciente y un `fecha_evolucion`? La norma sólo pide "paralela"; un modelo separado con historial temporal es la lectura más útil.

---

#### V.5 — Odontograma inicial registra solo lo observado

**Enunciado normativo**: "En la odontograma inicial sólo se debe registrar lo observado en el momento del examen y no debe registrarse el plan de tratamiento."

**Status actual en v0.1.0**: ⚠️ NO SEMÁNTICO

**Evidencia**: el schema JSON no distingue entre "hallazgo observado" y "plan de tratamiento" — un estado `obturacion_resina` puede significar tanto "obturación existente (hallazgo)" como "obturación planificada (plan)".

**Brecha**: falta dimensión semántica en el schema para diferenciar hallazgo vs plan. Esto es indirectamente necesario para V.4/V.5: el inicial contiene hallazgos, la evolución contiene tratamientos ejecutados.

**Plan v0.2.0**:
- Establecer la convención explícita: `odontograma_inicial` → solo hallazgos; `odontograma_evolucion` → tratamientos ejecutados + fecha.
- Documentar que el plan de tratamiento vive en otro campo del modelo consumidor (no en el odontograma normativo).

---

#### V.6 — Tamaño, ubicación y forma proporcional de los hallazgos

**Enunciado normativo**: "Cada registro que se haga en la odontograma debe respetar proporcionalmente el tamaño, ubicación y forma de los hallazgos."

**Status actual en v0.1.0**: ⚠️ PARCIAL

**Evidencia**: el widget placeholder actual pinta cada cara/pieza con color de fondo uniforme; no respeta "forma del hallazgo" (ej. la norma exige dibujar la caries "siguiendo su forma" sobre las superficies comprometidas).

**Brecha**: la representación es puramente topológica (qué cara) y no geométrica (qué forma dentro de la cara).

**Plan v0.2.0**:
- Ampliar el widget a SVG con regiones por cara que acepten máscara / forma adicional (subset de la cara coloreado).
- **Tradeoff aceptable**: en el perfil Perú v0.2.0 se puede partir con pintado de cara completa (como hoy) y dejar formas libres sobre cara como enhancement v0.3.x.

---

#### V.7 — Solo colores rojo y azul

**Enunciado normativo**: "Para el registro de hallazgos en la odontograma solo se utilizará los colores rojo y azul."

**Status actual en v0.1.0**: ❌ NO CONFORME

**Evidencia**: `settings.py:33-81` usa la siguiente paleta:
- `caries`: `#d32f2f` (rojo — OK)
- `obturacion_amalgama`: `#424242` (gris oscuro — ❌)
- `obturacion_resina`: `#1976d2` (azul — OK)
- `sellante`: `#81c784` (verde — ❌)
- `fractura`: `#ff9800` (naranja — ❌; la norma exige rojo)
- `no_erupcionado`: `#e0e0e0` (gris — ❌)
- `ausente`: `#757575` (gris — ❌; la norma exige aspa azul)
- `corona`: `#ffb300` (ámbar — ❌; la norma exige circunferencia azul para definitiva, roja para temporal)
- `implante`: `#6a1b9a` (violeta — ❌; la norma exige siglas "IMP" azul)
- `protesis_fija`: `#00838f` (cian — ❌)

**Brecha**: 8 de 11 estados usan colores fuera de la paleta rojo/azul.

**Plan v0.2.0**:
- Nuevo catálogo `profiles/peru/states.py` que SOLO use `#0040ff` (azul normativo) y `#d32f2f` (rojo normativo).
- Validador `validate_color_palette_peru` que rechace cualquier color fuera de esa dupla cuando el perfil Perú esté activo.
- Semántica por estado: buen estado → azul; mal estado / caries / lesión / remanente / temporal → rojo (ver V.8).

---

#### V.8 — Azul = buen estado; rojo = mal estado; tratamientos temporales en rojo

**Enunciado normativo**: "En los recuadros correspondientes a las piezas dentarias en donde se especifique el tipo de tratamiento se registrará las siglas en color azul cuando el tratamiento se encuentre en buen estado y en color rojo cuando se encuentra en mal estado. Asimismo, los tratamientos temporales se registrarán de color rojo."

**Status actual en v0.1.0**: ❌ NO CONFORME

**Evidencia**: ningún estado del catálogo actual tiene una dimensión "bueno / malo" que cambie color dinámicamente.

**Brecha**: falta modelado de la condición del tratamiento existente.

**Plan v0.2.0**:
- Cada estado del perfil Perú con siglas (CC, CF, CMC, AM, R, IV, IM, IE, TC, PC, PP, IMP, etc.) admitirá sub-clave `{"condicion": "bueno" | "malo"}` que determina el color.
- Los estados marcados como "temporal" (ej. `corona_temporal`, `restauracion_temporal`) forzarán rojo.
- Validación estricta: `condicion` es requerida cuando el estado es un tratamiento existente.

---

#### V.9 — Campo de especificaciones para hallazgos no graficables

**Enunciado normativo**: "En el rubro de especificaciones se debe explicar, determinar, aclarar con individualidad los hallazgos que no pueden ser registrados gráficamente."

**Status actual en v0.1.0**: ❌ NO IMPLEMENTADO

**Evidencia**: no existe `TextField` normativo asociado al odontograma.

**Brecha**: no hay lugar oficial para las notas de texto libre que la norma pide al pie del odontograma.

**Plan v0.2.0**:
- Agregar al schema JSON una clave top-level `especificaciones: str` (max 2000 chars, opcional).
- Renderizar textarea debajo del grid en el widget.
- Alternativa más limpia: `OdontogramaPeruField` expone un método `.especificaciones` y obliga al consumidor a declarar `especificaciones = models.TextField(blank=True)` en el mismo modelo (documentado en la guía de integración del perfil).

---

#### V.10 — Anomalías múltiples en especificaciones

**Enunciado normativo**: "En el caso de que una pieza dentaria presente más de una anomalía, estas se deben registrar en el ítem de especificaciones."

**Status actual en v0.1.0**: ❌ NO IMPLEMENTADO

**Evidencia**: el schema actual permite exactamente UN `estado` O UN set de `caras` por pieza (validator XOR en `validators.py:111-123`). Una pieza con múltiples anomalías (ej. microdoncia + giroversión + caries) no se puede representar.

**Brecha**: el schema es "un hallazgo por pieza". Norma exige que el resto vaya al item especificaciones.

**Plan v0.2.0**:
- Permitir que una pieza tenga un `estado` primario (la anomalía "dominante" a graficar) + una referencia textual a `especificaciones` con las restantes.
- Alternativa más expresiva: convertir `estado` en lista (`estados: list[str]`) y renderizar la primera; el resto se auto-anexa al item especificaciones.

---

#### V.11 — Hallazgos radiográficos consignados

**Enunciado normativo**: "Los hallazgos radiográficos deben ser consignados en la odontograma."

**Status actual en v0.1.0**: ❌ NO IMPLEMENTADO

**Evidencia**: no hay distinción entre hallazgo clínico y radiográfico.

**Brecha**: campo libre + flag.

**Plan v0.2.0**:
- Sub-clave `origen: "clinico" | "radiografico"` a nivel de entry (default `clinico`).
- Bloque de texto en `especificaciones` claramente marcado como "Hallazgos radiográficos".

---

#### V.12 — Gráfico único, impreso en negro, corona ≥ 1 cm²

**Enunciado normativo**: "El gráfico de la odontograma establecida en la presente norma será único, y debe ser impreso en color negro. La corona debe tener como mínimo un centímetro cuadrado y la raíz será proporcional a esta. (ver anexo II)."

**Status actual en v0.1.0**: ⚠️ PARCIAL

**Evidencia**:
- Gráfico único: ✅ el widget placeholder tiene layout maxila/mandíbula separado por línea central, consistente con Anexo II.
- Impresión en negro: ❌ no hay regla `@media print` que fuerce B/N.
- Corona ≥ 1 cm²: ⚠️ sin validación de tamaño de impresión.

**Brecha**:
- CSS print-specific que elimine colores (salvo rojo/azul que según la norma se permite en pantalla y debe imprimirse NEGRO — interpretación: la norma exige impresión BN, la visualización en pantalla admite rojo/azul).
- ⚠️ AMBIGÜEDAD NORMATIVA: la norma dice "impreso en color negro" pero VI.1 usa rojo/azul en todos los diagramas de ejemplo. Interpretación razonable: los DIAGRAMAS del Anexo II están en negro; los HALLAZGOS se marcan en rojo/azul en papel pero el SUSTRATO del odontograma imprime en negro. Se asume: elementos de base (marco, siglas FDI, dientes esquemáticos) en negro, hallazgos en rojo/azul.

**Plan v0.2.0**:
- CSS `@media print { @page { size: A4; } .odontograma-base { filter: grayscale(1); } .odontograma-hallazgo { /* preserva color */ } }`.
- Unidades absolutas (`mm`) en el CSS de impresión para garantizar corona ≥ 10 mm × 10 mm.

---

#### V.13 — Sin enmendaduras ni tachaduras; modificación firmada

**Enunciado normativo**: "La odontograma debe ser llenado sin enmendaduras ni tachaduras. En el caso que se produjera alguna modificación por tratamiento el profesional responsable debe registrar y firmar la modificación realizada en el ítem de especificaciones."

**Status actual en v0.1.0**: ❌ NO CONFORME

**Evidencia**: sin audit trail, sin firma, sin registro de modificaciones.

**Brecha**: derivada directa de V.3.

**Plan v0.2.0**:
- Acoplado con V.3: toda modificación del odontograma inicial debe:
  1. Requerir `usuario` + `fecha` + `motivo` (firma técnica).
  2. Append al `especificaciones` un bloque con "Modificación <fecha> por <usuario>: <motivo>".
  3. Persistir en tabla de audit (`OdontogramaAuditEntry`).
- API: `odontograma_field.modificar(cambios, usuario, motivo)` en vez de `instance.odontograma = nuevo; instance.save()`.

---

#### V.14 — Especialidades pueden adicionar nomenclaturas, no modificarlas

**Enunciado normativo**: "Las especialidades odontológicas podrán adicionar otras nomenclaturas relacionadas a su campo, mas no así modificar o contradecir las establecidas por la presente norma."

**Status actual en v0.1.0**: ⚠️ PARCIAL

**Evidencia**: `settings.py:92-99` hace `{**DEFAULT_ESTADOS_*, **override}` — el override del consumidor PUEDE sobreescribir una key por defecto (ej. redefinir `caries` con otro color). Esto viola V.14.

**Brecha**: el merge no protege el catálogo normativo.

**Plan v0.2.0**:
- En perfil Perú, las 33 nomenclaturas normativas son un `frozenset` de keys protegidas.
- Merge con override: si override redefine una key protegida → `ImproperlyConfigured`.
- El consumidor puede **agregar** keys (ej. `caries_recidivante` como extensión propia) pero no redefinir `caries`.

---

#### V.15 — Tiempo máximo 10 minutos

**Enunciado normativo**: "La odontograma debe ser desarrollado en un tiempo máximo de 10 minutos."

**Status actual en v0.1.0**: N/A

**Evidencia**: requisito operativo sobre el profesional, no sobre el software.

**Brecha**: ninguna a nivel de paquete.

**Plan v0.2.0**: el widget debe ser eficiente en entrada de datos (atajos de teclado, click-to-set, estado por defecto "sano"). Meta de UX: carga completa en < 10 min por un odontólogo entrenado.

---

## Sección 3 — Análisis por Nomenclatura Específica (VI.1 del PDF, 33 items)

Las 33 nomenclaturas normativas están definidas en VI.1 del PDF. El paquete v0.1.0 NO cubre ninguna de ellas con fidelidad gráfica (forma + color + ubicación + sigla). A lo sumo tiene keys semánticamente cercanas que hoy se pintan con color de fondo. Detalle:

### Tabla resumen

| # | Nomenclatura | Key v0.1.0 (si existe) | Color norma | Forma norma | Status |
|---|---|---|---|---|---|
| 1.1 | Aparato Ortodóntico Fijo | — | azul/rojo | cuadrados + cruz + línea recta entre ápices | ❌ |
| 1.2 | Aparato Ortodóntico Removible | — | azul/rojo | línea zig-zag en ápices | ❌ |
| 1.3 | Caries | `caries` | rojo | forma de lesión pintada en superficie | ⚠️ parcial (color OK, forma no) |
| 1.4 | Corona Definitiva | `corona` (color ámbar) | azul | circunferencia + siglas CC/CF/CMC/3-4/4-5/7-8/CV/CJ en recuadro | ❌ |
| 1.5 | Corona Temporal | — | rojo | circunferencia roja | ❌ |
| 1.6 | Desgaste Oclusal/Incisal | — | azul | siglas "DES" en recuadro | ❌ |
| 1.7 | Diastema | — | azul | paréntesis invertido entre piezas | ❌ |
| 1.8 | Diente Ausente | `ausente` (gris) | azul | aspa / X sobre pieza | ❌ |
| 1.9 | Diente Discromico | — | azul | siglas "DIS" en recuadro | ❌ |
| 1.10 | Diente Ectópico | — | azul | letra "E" en recuadro | ❌ |
| 1.11 | Diente en Clavija | — | azul | triángulo circunscribiendo el número | ❌ |
| 1.12 | Diente Extruido | — | azul | flecha hacia plano oclusal | ❌ |
| 1.13 | Diente Intruido | — | azul | flecha recta vertical hacia ápice | ❌ |
| 1.14 | Edéntulo Total | — | azul | línea recta horizontal sobre coronas | ❌ |
| 1.15 | Fractura | `fractura` (naranja) | rojo | línea recta en sentido de fractura | ❌ |
| 1.16 | Geminación / Fusión | — | azul | dos circunferencias interceptadas | ❌ |
| 1.17 | Giroversión | — | azul | flecha curva en plano oclusal | ❌ |
| 1.18 | Impactación | — | azul | letra "I" en recuadro | ❌ |
| 1.19 | Implante | `implante` (violeta) | azul | siglas "IMP" en recuadro | ❌ |
| 1.20 | Macrodoncia | — | azul | siglas "MAC" en recuadro | ❌ |
| 1.21 | Microdoncia | — | azul | siglas "MIC" en recuadro | ❌ |
| 1.22 | Migración | — | azul | flecha recta horizontal en plano oclusal | ❌ |
| 1.23 | Movilidad | — | azul | "M" + grado (arábigo) en recuadro | ❌ |
| 1.24 | (AUSENCIA NORMATIVA) | — | — | — | ⚠️ el PDF salta de 1.23 a 1.25 |
| 1.25 | Prótesis Removible | — | azul/rojo | dos líneas paralelas horizontales en ápices | ❌ |
| 1.26 | Prótesis Total | — | azul/rojo | dos líneas paralelas horizontales sobre coronas | ❌ |
| 1.27 | Remanente Radicular | — | rojo | siglas "RR" sobre la raíz | ❌ |
| 1.28 | Restauración | `obturacion_amalgama` / `obturacion_resina` | azul | superficie pintada + siglas AM/R/IV/IM/IE en recuadro | ⚠️ parcial |
| 1.29 | Restauración Temporal | — | rojo | contorno en rojo siguiendo forma | ❌ |
| 1.30 | Semi-Impactación | — | azul | siglas "SI" en recuadro | ❌ |
| 1.31 | Supernumerario | — | azul | "S" mayúscula dentro de circunferencia entre ápices | ❌ |
| 1.32 | Transposición | — | azul | dos flechas curvas entrecruzadas entre piezas | ❌ |
| 1.33 | Tratamiento Pulpar | — | azul | línea recta vertical en raíz + siglas TC/PC/PP | ❌ |

**Cobertura**: 6 keys v0.1.0 (`caries`, `fractura`, `ausente`, `corona`, `implante`, `obturacion_amalgama` / `obturacion_resina` → restauración) tienen mapeo semántico parcial a 5 de 33 nomenclaturas. **Ninguna** renderiza la forma normativa ni las siglas. El color es correcto solo en `caries`.

### Detalle por nomenclatura

#### VI.1.1 — Aparato Ortodóntico Fijo

**Representación normativa**: cuadrados con cruz en su interior, a nivel de los ápices de las piezas dentarias extremas, unidos con una línea recta.

**Color normado**: AZUL (buen estado) / ROJO (mal estado).

**Ubicación**: sobre ápices + línea entre ellos.

**Siglas**: —

**Estado actual en v0.1.0**: no existe. Status: ❌ NO CONFORME.

**Brecha**: nomenclatura inter-piezas (no por diente), requiere representación de "rango" de piezas. Schema actual es flat por FDI.

**Plan v0.2.0**: nuevo estado top-level `hallazgos_inter_piezas: list[{tipo, fdi_inicio, fdi_fin, condicion}]` con render SVG correspondiente. Ver Sección 7 (decisión abierta).

---

#### VI.1.2 — Aparato Ortodóntico Removible

**Representación normativa**: línea zig-zag a la altura de los ápices del maxilar en tratamiento.

**Color normado**: AZUL / ROJO según condición.

**Ubicación**: ápices del maxilar (toda la arcada).

**Estado actual**: ❌ NO CONFORME.

**Plan v0.2.0**: estado por arcada (no por pieza). Clave top-level `aparato_ortodontico_removible: {arcada: "superior" | "inferior", condicion: "bueno" | "malo"}`.

---

#### VI.1.3 — Caries

**Representación normativa**: dibujar lesión siguiendo su forma en las superficies dentarias comprometidas, totalmente pintada con color rojo.

**Color normado**: ROJO.

**Ubicación**: CORONA, por cara.

**Estado actual**: `caras.caries` con color `#d32f2f`. Status: ⚠️ PARCIAL (color OK, forma no).

**Brecha**: el widget pinta la cara completa; la norma pide "forma de la lesión" (subset de la cara).

**Plan v0.2.0**: aceptar v0.2.0 con "cara completa pintada" como compromiso; forma libre queda para v0.3.x (requiere SVG editable).

---

#### VI.1.4 — Corona Definitiva

**Representación normativa**: circunferencia de color azul encerrando la corona; en el recuadro correspondiente se anotan siglas en mayúsculas azules.

**Color normado**: AZUL.

**Ubicación**: contorno de la corona + recuadro superior con sigla.

**Siglas**: CC (Corona Completa metálica), CF (Corona Fenestrada), CMC (Corona Metal Cerámica), 3/4, 4/5, 7/8 (Corona Parcial metálica), CV (Corona Veneer), CJ (Corona Jacket).

**Nota**: en `especificaciones` debe registrarse color del metal (dorada o plateada).

**Estado actual**: `corona` con color `#ffb300` (ámbar), sin sigla, sin recuadro. Status: ❌ NO CONFORME.

**Plan v0.2.0**:
- Renombrar key a `corona_definitiva`.
- Sub-campo `tipo: "CC" | "CF" | "CMC" | "3/4" | "4/5" | "7/8" | "CV" | "CJ"`.
- Sub-campo `condicion: "bueno" | "malo"` (norma V.8).
- Sub-campo `material_color: "dorada" | "plateada"` que auto-flush a `especificaciones`.
- Render: SVG con circunferencia azul + sigla en recuadro superior.

---

#### VI.1.5 — Corona Temporal

**Representación normativa**: circunferencia de color rojo encerrando la corona.

**Color normado**: ROJO.

**Ubicación**: contorno corona.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: nueva key `corona_temporal` con render circunferencia roja.

---

#### VI.1.6 — Desgaste Oclusal / Incisal

**Representación normativa**: siglas "DES" en mayúsculas de color azul, en el recuadro que corresponde a la pieza.

**Color normado**: AZUL.

**Ubicación**: RECUADRO superior.

**Siglas**: DES.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `desgaste_oclusal_incisal`, render sigla DES en recuadro superior.

---

#### VI.1.7 — Diastema

**Representación normativa**: paréntesis invertido de color azul ENTRE las piezas dentarias.

**Color normado**: AZUL.

**Ubicación**: ENTRE piezas (coronal).

**Estado actual**: no existe, schema no soporta inter-piezas. Status: ❌ NO CONFORME.

**Plan v0.2.0**: `hallazgos_inter_piezas` top-level con tipo `diastema` + par de FDI adyacentes.

---

#### VI.1.8 — Diente Ausente

**Representación normativa**: aspa (X) de color azul sobre la figura de la pieza dentaria.

**Color normado**: AZUL.

**Ubicación**: sobre corona + raíz.

**Estado actual**: `ausente` con color `#757575` (gris). Status: ❌ NO CONFORME (color erróneo, forma faltante).

**Plan v0.2.0**: mantener key `ausente`, restringir color a azul, render SVG con aspa sobre toda la pieza. Sub-clave `causa` ya existe (`extraccion`/`exfoliacion`/`agenesia`) y se mantiene.

---

#### VI.1.9 — Diente Discromico

**Representación normativa**: siglas "DIS" en mayúsculas azul en recuadro.

**Color normado**: AZUL.

**Siglas**: DIS.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `discromico`, render sigla DIS.

---

#### VI.1.10 — Diente Ectópico

**Representación normativa**: letra "E" mayúscula azul en recuadro.

**Color normado**: AZUL.

**Siglas**: E.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `ectopico`.

---

#### VI.1.11 — Diente en Clavija

**Representación normativa**: triángulo de color azul circunscribiendo el número de la pieza.

**Color normado**: AZUL.

**Ubicación**: alrededor del número FDI.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `clavija`, render triángulo SVG alrededor del código FDI.

---

#### VI.1.12 — Diente Extruido

**Representación normativa**: flecha de color azul dirigida hacia el plano oclusal.

**Color normado**: AZUL.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `extruido`, render flecha SVG apuntando al plano oclusal (según arcada).

---

#### VI.1.13 — Diente Intruido

**Representación normativa**: flecha recta vertical azul dirigida hacia el ápice.

**Color normado**: AZUL.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `intruido`, render flecha SVG hacia el ápice.

---

#### VI.1.14 — Edéntulo Total

**Representación normativa**: línea recta horizontal azul sobre las coronas de las piezas ausentes del maxilar edéntulo.

**Color normado**: AZUL.

**Ubicación**: arcada completa.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: clave por arcada `edentulo_total: {arcada: "superior" | "inferior"}`. Mutuamente excluyente con estados individuales en esa arcada (validador).

---

#### VI.1.15 — Fractura

**Representación normativa**: línea recta de color rojo, en el sentido de la fractura, sobre la figura de la corona y/o raíz.

**Color normado**: ROJO.

**Estado actual**: `fractura` con color `#ff9800` (naranja). Status: ❌ NO CONFORME (color erróneo).

**Plan v0.2.0**: mantener key, cambiar color a rojo normativo, render línea SVG.

---

#### VI.1.16 — Geminación / Fusión

**Representación normativa**: dos circunferencias interceptadas de color azul encerrando los números de las piezas involucradas.

**Color normado**: AZUL.

**Ubicación**: alrededor de dos códigos FDI adyacentes.

**Estado actual**: no existe, schema no soporta par de piezas. Status: ❌ NO CONFORME.

**Plan v0.2.0**: `hallazgos_inter_piezas` tipo `geminacion_fusion` + par FDI.

---

#### VI.1.17 — Giroversión

**Representación normativa**: flecha curva azul siguiendo el sentido de la giroversión a nivel oclusal.

**Color normado**: AZUL.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `giroversion: {sentido: "horario" | "antihorario"}`.

---

#### VI.1.18 — Impactación

**Representación normativa**: letra "I" mayúscula azul en recuadro.

**Color normado**: AZUL.

**Siglas**: I.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `impactacion`. Nota: distinto de `semi_impactacion` (VI.1.30).

---

#### VI.1.19 — Implante

**Representación normativa**: siglas "IMP" mayúsculas azul en recuadro de la pieza reemplazada.

**Color normado**: AZUL.

**Siglas**: IMP.

**Estado actual**: `implante` con color `#6a1b9a` (violeta), sin sigla, sin recuadro. Status: ❌ NO CONFORME.

**Plan v0.2.0**: mantener key, cambiar a azul, render sigla IMP en recuadro superior.

---

#### VI.1.20 — Macrodoncia

**Representación normativa**: siglas "MAC" mayúsculas azul en recuadro.

**Siglas**: MAC.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `macrodoncia`.

---

#### VI.1.21 — Microdoncia

**Representación normativa**: siglas "MIC" mayúsculas azul en recuadro.

**Siglas**: MIC.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `microdoncia`.

---

#### VI.1.22 — Migración

**Representación normativa**: flecha recta horizontal azul siguiendo el sentido de la migración a nivel oclusal.

**Color normado**: AZUL.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `migracion: {sentido: "mesial" | "distal"}`.

---

#### VI.1.23 — Movilidad

**Representación normativa**: letra "M" mayúscula azul + número arábigo (grado) en recuadro. Tipo de clasificación en especificaciones.

**Color normado**: AZUL.

**Siglas**: M + grado (1, 2, 3).

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `movilidad: {grado: 1 | 2 | 3, clasificacion: str}` (la clasificación se deriva a `especificaciones`).

---

#### VI.1.24 — AUSENCIA EN LA NORMA

⚠️ **AMBIGÜEDAD NORMATIVA**: el PDF salta de 1.23 (Movilidad) directamente a 1.25 (Prótesis Removible). No existe nomenclatura 1.24 en el documento fuente. Se documenta esta ausencia para futuras revisiones con el Colegio Odontológico del Perú. No hay acción en v0.2.0.

---

#### VI.1.25 — Prótesis Removible

**Representación normativa**: dos líneas horizontales paralelas azul (o rojo si mal estado) a nivel de los ápices de las piezas reemplazadas. Tipo de material en especificaciones.

**Color normado**: AZUL / ROJO según condición.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: clave por rango de piezas `protesis_removible: {fdi_range: [a,b], condicion, material}`.

---

#### VI.1.26 — Prótesis Total

**Representación normativa**: dos líneas rectas paralelas y horizontales azul (o rojo si mal estado) sobre las coronas de las piezas del maxilar.

**Color normado**: AZUL / ROJO.

**Estado actual**: `protesis_fija` (clave actual es "fija", no "total"). Status: ❌ NO CONFORME.

**Plan v0.2.0**: renombrar / reemplazar por `protesis_total: {arcada, condicion, material}`. Nota: la norma no tiene explícitamente "prótesis fija" como nomenclatura separada — la prótesis fija se materializa como corona definitiva (VI.1.4) sobre pilares.

---

#### VI.1.27 — Remanente Radicular

**Representación normativa**: siglas "RR" mayúsculas ROJO sobre la raíz.

**Color normado**: ROJO.

**Ubicación**: zona apical (raíz).

**Siglas**: RR.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `remanente_radicular`, render sigla RR en zona apical (requiere zona apical — ver Sección 5).

---

#### VI.1.28 — Restauración

**Representación normativa**: restauración siguiendo forma en superficies comprometidas, pintada totalmente de AZUL. Siglas del material en recuadro correspondiente, mayúsculas azul.

**Color normado**: AZUL.

**Siglas**: AM (Amalgama), R (Resina), IV (Ionómero de Vidrio), IM (Incrustación Metálica), IE (Incrustación Estética).

**Estado actual**: `obturacion_amalgama` (color gris oscuro `#424242` — ❌), `obturacion_resina` (azul `#1976d2` — OK). Sin siglas. Sin recuadro. Status: ⚠️ PARCIAL.

**Plan v0.2.0**:
- Consolidar en un solo estado `restauracion: {material: "AM" | "R" | "IV" | "IM" | "IE"}` por cara.
- Todos renderizan azul (color de la norma).
- Sigla en recuadro superior según material.
- Desaparecen `obturacion_amalgama`, `obturacion_resina`, `sellante` del catálogo Perú (el sellante no es nomenclatura normativa — podría ir en especificaciones).

---

#### VI.1.29 — Restauración Temporal

**Representación normativa**: contorno en rojo siguiendo la forma en las superficies comprometidas.

**Color normado**: ROJO.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `restauracion_temporal` por cara, render contorno rojo.

---

#### VI.1.30 — Semi-Impactación

**Representación normativa**: siglas "SI" mayúsculas azul en recuadro.

**Siglas**: SI.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `semi_impactacion`.

---

#### VI.1.31 — Supernumerario

**Representación normativa**: letra "S" mayúscula encerrada en circunferencia azul, localizada ENTRE los ápices de las piezas adyacentes al supernumerario.

**Color normado**: AZUL.

**Ubicación**: entre piezas (zona apical).

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: `hallazgos_inter_piezas` tipo `supernumerario` + par FDI adyacente.

---

#### VI.1.32 — Transposición

**Representación normativa**: dos flechas curvas azul entrecruzadas, a la altura de los números de las piezas involucradas.

**Color normado**: AZUL.

**Ubicación**: entre dos piezas.

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: `hallazgos_inter_piezas` tipo `transposicion` + par FDI.

---

#### VI.1.33 — Tratamiento Pulpar

**Representación normativa**: línea recta vertical azul en la representación gráfica de la raíz; siglas del tipo de tratamiento en recuadro correspondiente, mayúsculas azul.

**Color normado**: AZUL.

**Ubicación**: raíz (zona apical) + recuadro.

**Siglas**: TC (Tratamiento de Conductos), PC (Pulpectomía), PP (Pulpotomía).

**Estado actual**: no existe. Status: ❌ NO CONFORME.

**Plan v0.2.0**: key `tratamiento_pulpar: {tipo: "TC" | "PC" | "PP"}`, render línea azul en raíz + sigla en recuadro.

---

## Sección 4 — Análisis Anexo I (Glosario de Términos)

El Anexo I define los términos clínicos normativos. La siguiente tabla mapea cada término al estado del paquete (si existe) y marca los huérfanos que requieren creación en v0.2.0.

| Término del Anexo I | Definición (resumen) | Key v0.1.0 | Estado v0.2.0 Perú |
|---|---|---|---|
| AMALGAMA | Aleación de mercurio para restauración | `obturacion_amalgama` | `restauracion.material="AM"` |
| ANOMALÍAS | Estado contrario a lo natural | — | concepto transversal |
| CARIES | Enfermedad destructiva | `caries` ✅ | `caries` (color rojo norma) |
| CORONAS | Fundas que recubren los dientes | `corona` | `corona_definitiva` |
| CORONA COMPLETA (CC) | Cubre completamente el muñón (sólo metálica) | — | `corona_definitiva.tipo="CC"` |
| CORONA FENESTRADA (CF) | Metálica con ventana vestibular | — | `corona_definitiva.tipo="CF"` |
| CORONA JACKET (CJ) | Estética libre de metal | — | `corona_definitiva.tipo="CJ"` |
| CORONA METAL CERÁMICA (CMC) | Núcleo metálico revestido de estético | — | `corona_definitiva.tipo="CMC"` |
| CORONA PARCIAL | 3/4, 4/5, 7/8 | — | `corona_definitiva.tipo="3/4"|"4/5"|"7/8"` |
| CORONA TEMPORAL | Provisoria | — | `corona_temporal` |
| CORONA VENEER (CV) | Completa con frente estético | — | `corona_definitiva.tipo="CV"` |
| DESGASTE OCLUSAL/INCISAL | Pérdida de estructura a nivel oclusal/incisal | — | `desgaste_oclusal_incisal` |
| DIASTEMA | Separación entre piezas correlativas | — | `hallazgos_inter_piezas` tipo `diastema` |
| DIENTE AUSENTE | Pieza no presente (extraída, agenesia, impactada) | `ausente` ✅ | `ausente` (color azul, aspa) |
| DIENTE ECTÓPICO | Erupcionado fuera del lugar | — | `ectopico` |
| DISCROMIA DENTARIA | Alteraciones de color | — | `discromico` |
| DENTULO (Desdentado) | Ausencia parcial o total | — | `edentulo_total` (caso arcada) |
| ESPECIFICAR | Explicar con individualidad | — | top-level `especificaciones: str` |
| EXTRUSIÓN | Sobre erupción hacia arco antagonista | — | `extruido` |
| FRACTURA | Ruptura | `fractura` | `fractura` (color rojo norma) |
| FUSIÓN | Unión de dos piezas en desarrollo | — | `hallazgos_inter_piezas` tipo `geminacion_fusion` |
| GEMINACIÓN | Un órgano del esmalte forma dos piezas | — | `hallazgos_inter_piezas` tipo `geminacion_fusion` |
| GIROVERSIÓN | Rotación sobre eje longitudinal | — | `giroversion` |
| IMPACTACIÓN | No erupcionó por barrera física, sin comunicación bucal | — | `impactacion` |
| IMPLANTE | Dispositivo que sustituye raíz | `implante` | `implante` (siglas IMP, color azul) |
| INCRUSTACIÓN | Restauración que reemplaza corona parcialmente | — | `restauracion.material="IM"|"IE"` |
| INTRUSIÓN | Pieza que alcanzó plano oclusal y quedó por debajo | — | `intruido` |
| MACRODONCIA | Volumen aumentado | — | `macrodoncia` |
| MICRODONCIA | Volumen disminuido | — | `microdoncia` |
| MIGRACIÓN | Desplazamiento horizontal espontáneo | — | `migracion` |
| MOVILIDAD PATOLÓGICA | Desplazamiento en alveolo | — | `movilidad` |
| PULPECTOMÍA | Remoción de pulpa coronal+radicular infectada | — | `tratamiento_pulpar.tipo="PC"` |
| PULPOTOMÍA | Extirpación de pulpa cameral en pieza caduca | — | `tratamiento_pulpar.tipo="PP"` |
| PRÓTESIS FIJA | Restituye piezas por restauraciones cementadas sobre pilares | `protesis_fija` | (concepto — NO es nomenclatura VI.1 directa; se materializa como `corona_definitiva` sobre pilares) |
| PRÓTESIS REMOVIBLE | Retirable de su lugar | — | `protesis_removible` |
| REMANENTE RADICULAR | Fragmento radicular en alveolo | — | `remanente_radicular` (siglas RR rojo) |
| RESINA COMPUESTA | Material estético | `obturacion_resina` | `restauracion.material="R"` |
| RESTAURACIÓN | Reconstrucción de la corona | — | `restauracion` |
| SEMI-IMPACTACIÓN | No erupcionó totalmente por barrera física | — | `semi_impactacion` |
| SUPERNUMERARIO | Número aumentado | — | `hallazgos_inter_piezas` tipo `supernumerario` |
| TRANSPOSICIÓN DENTARIA | Cambio de piezas que erupcionan en sitio del otro | — | `hallazgos_inter_piezas` tipo `transposicion` |
| TRATAMIENTO PULPAR | Terapia de toda o parte de la pulpa | — | `tratamiento_pulpar` |
| TRATAMIENTO DE CONDUCTO | Pulpar en piezas permanentes | — | `tratamiento_pulpar.tipo="TC"` |

**Términos huérfanos actuales en v0.1.0** que se eliminarán del perfil Perú: `sellante` (no aparece en Anexo I ni en VI.1).

**Términos presentes en Anexo I pero sin nomenclatura VI.1 dedicada**: `ANOMALÍAS` (concepto), `ESPECIFICAR` (concepto → campo), `PRÓTESIS FIJA` (concepto, se modela como corona).

---

## Sección 5 — Análisis Anexo II (Partes del Odontograma)

El Anexo II del PDF identifica cinco zonas del gráfico:

### 5.1. Recuadro de piezas dentarias

**Descripción normativa**: filas de recuadros arriba y abajo de cada hemiarcada para anotar siglas por pieza (DES, DIS, E, I, IMP, MAC, MIC, M+grado, SI, CC/CF/CMC/..., AM/R/IV/IM/IE, TC/PC/PP).

**Estado v0.1.0**: ❌ NO IMPLEMENTADO. El widget placeholder solo renderiza las caras + número FDI.

**Plan v0.2.0**: agregar en el widget tres filas de recuadros encima de cada arcada superior y tres filas debajo de cada arcada inferior (el PDF muestra exactamente 3 filas arriba + 3 filas abajo). Cada recuadro se liga a una sigla del estado correspondiente.

### 5.2. Número de piezas dentarias

**Descripción normativa**: el código FDI visible sobre cada pieza.

**Estado v0.1.0**: ✅ CONFORME (el widget placeholder los renderiza).

**Plan v0.2.0**: ajustar tipografía/tamaño para que cumpla la proporción del Anexo II (legibilidad al imprimir).

### 5.3. Zona Oclusal

**Descripción normativa**: cara masticatoria del diente (corona).

**Estado v0.1.0**: ✅ CONFORME parcialmente. La corona se representa con sus 5 caras (oclusal/incisal, mesial, distal, vestibular, lingual/palatino).

**Plan v0.2.0**: validar que las caras solo admitan estados de tipo "cara" (caries, restauración, restauración temporal), no estados de pieza completa.

### 5.4. Zona Apical

**Descripción normativa**: raíz del diente, representada separada de la corona. Se usa para ubicar hallazgos como remanente radicular (RR), tratamiento pulpar (línea vertical), implante, supernumerario (entre ápices), aparato ortodóntico fijo/removible (a la altura de los ápices), prótesis removible.

**Estado v0.1.0**: ❌ NO IMPLEMENTADA. El schema solo tiene 5 caras coronales; no hay representación de la raíz.

**Plan v0.2.0**:
- Ampliar el schema por pieza para incluir zona radicular: `{"caras": {...coronales...}, "raiz": {"estado": "remanente_radicular" | "tratamiento_pulpar", ...}}`.
- Render SVG de la raíz debajo de la corona para cada pieza.

### 5.5. Item Especificaciones

**Descripción normativa**: campo de texto libre al pie del odontograma para los hallazgos no graficables, anomalías múltiples, tipo de aparatología, color del metal de la corona, hallazgos radiográficos, tipo de clasificación de movilidad, firmas de modificación.

**Estado v0.1.0**: ❌ NO IMPLEMENTADO.

**Plan v0.2.0**: clave top-level en el JSON `especificaciones: str` (max 5000 chars); widget renderiza `<textarea>` con label "ESPECIFICACIONES:" al pie. Validador requiere que esté presente (aunque sea string vacío) en el perfil Perú.

---

## Sección 6 — Roadmap v0.2.0 — Perfil Perú (Resumen accionable)

### P0 (bloqueantes — sin esto el paquete NO cumple la norma)

- [x] ✅ **v0.2.0** — Crear módulo `xpertik_odontograma.profiles.peru` con `states.py`, `validators.py`, `fields.py`, `apps.py`, `specifications.py`, `constants.py`.
- [x] ✅ **v0.2.0** (en perfil Perú) — Restringir paleta de colores a rojo (`#d32f2f`) y azul (`#1565c0`); sistema simbólico + rechazo de hex en extensiones.
- [ ] ⚠️ PARCIAL **v0.2.0** — Catálogo de datos de las 32 nomenclaturas VI.1 (26 usables + 6 cross-teeth rechazadas con pointer a v0.3.0). Representación gráfica normativa: ⏳ v0.3.0.
- [ ] ⏳ **v0.3.0** — Implementar representaciones gráficas SVG: aspa, X, circunferencia, triángulo, flechas rectas/curvas, líneas paralelas, paréntesis invertido, siglas en recuadro.
- [ ] ⏳ **v0.3.0** — Zona apical separada de la coronal en el schema (`{caras: {...}, raiz: {...}}`).
- [ ] ⏳ **v0.3.0** — Recuadros superiores e inferiores en el widget para alojar siglas (3 filas arriba, 3 filas abajo por arcada, como Anexo II).
- [x] ✅ **v0.2.0** — Clave top-level `especificaciones_generales: str` + `especificaciones: str` por pieza en el schema JSON (helpers en `profiles.peru.specifications`). Textarea en widget: ⏳ v0.3.0 junto a la UI normativa.
- [ ] ⏳ **v0.3.0** — Campo `odontograma_evolucion` paralelo al `odontograma_inicial` (V.4).
- [ ] ⏳ **v0.3.0** — Inalterabilidad del inicial: bloqueo en `pre_save` + audit trail apendeable (V.3, V.13).
- [ ] ⏳ **v0.3.0** — Soporte de nomenclaturas inter-piezas (`hallazgos_inter_piezas: list[...]`) para diastema, geminación/fusión, supernumerario, transposición, aparato ortodóntico fijo/removible, prótesis removible/total. (v0.2.0 rechaza estas 6 con error explícito.)

### P1 (conformidad completa)

- [ ] ⚠️ PARCIAL **v0.2.0** — `categoria` (hallazgo/tratamiento/anomalia/ortodontico) se tipifica en el catálogo. Enforcement semántico hallazgos-vs-plan: ⏳ v0.3.0 (V.5).
- [ ] ⏳ **v0.3.0** — Sub-clave `origen: "clinico" | "radiografico"` por entry (V.11). Por ahora el texto libre en `especificaciones` es la vía de registro.
- [ ] ⏳ **v0.3.0** — CSS `@media print` que convierte base del gráfico a B/N conservando rojo/azul de los hallazgos; tamaño de corona ≥ 10 mm × 10 mm absolutos (V.12).
- [x] ✅ **v0.2.0** — HARD lock de nomenclaturas normativas: `PeruAppConfig.ready()` rechaza overrides sobre las 32 keys del catálogo, permite agregar extensiones (V.14). `ImproperlyConfigured` al arranque.
- [x] ✅ **v0.2.0** — Validación de causas coherente con Anexo I (definiciones en el catálogo; `extraccion | exfoliacion | agenesia` preservadas desde v0.1.0).
- [ ] ⏳ **v0.3.0** — API `instance.modificar_odontograma(cambios, usuario, motivo)` con firma automática en `especificaciones` (V.13).
- [ ] ⏳ **v0.3.0** — Validador "anomalías múltiples" (V.10): si `estados` tiene >1 entrada por pieza, auto-anexar resto a `especificaciones`.

### P2 (mejoras post-norma)

- [ ] SVG totalmente interactivo (click-to-set por cara/zona/recuadro) — original de v0.2.0 pre-análisis.
- [ ] Management command `odontograma_reconcile_denticion` para migrar odontogramas de paciente pediátrico → adulto.
- [ ] Traducciones `.po` (ES-PE completa, PT-BR para expansión regional).
- [ ] Validador de tiempo de registro (alerta si `created_at → updated_at` > 10 min) — V.15 operativo.

### Arquitectura propuesta

- El paquete base `xpertik-odontograma` se mantiene **GENÉRICO**: FDI, dentición, 5 caras, estados extensibles vía `XPERTIK_ODONTOGRAMA_ESTADOS_*`.
- Nuevo sub-paquete `xpertik_odontograma.profiles.peru`:
  - `states.py` — las 33 nomenclaturas normativas con sus siglas y condiciones.
  - `validators.py` — invariantes específicos: paleta rojo/azul, aspa obligatoria para ausente, condición obligatoria en tratamientos existentes, inalterabilidad del inicial, lock de keys protegidas.
  - `widgets.py` — widgets SVG que respetan las representaciones gráficas del Anexo II (recuadros, zona apical, línea central) y rinden las formas normadas (aspa, triángulo, flechas, etc.).
  - `models.py` — `OdontogramaPeruInicialField`, `OdontogramaPeruEvolucionField` que extienden `OdontogramaField` con los constraints específicos.
  - `audit.py` — `OdontogramaAuditEntry` append-only + helper `modificar()`.
- Activación por el consumidor:
  - En `settings.py` del proyecto host: `XPERTIK_ODONTOGRAMA_PROFILE = "peru"` fuerza validaciones estrictas.
  - En el modelo: `odontograma_inicial = OdontogramaPeruInicialField()` + `odontograma_evolucion = OdontogramaPeruEvolucionField(default=dict)` + `especificaciones = models.TextField(blank=True)`.
- Compatibilidad: el perfil por defecto (`"generic"`) mantiene el comportamiento v0.1.0 para no romper consumidores existentes.

---

## Sección 7 — Decisiones abiertas (entradas para el `sdd-explore` de v0.2.0)

1. **¿Modelo separado o `JSONField` paralelo para la evolución?**
   - Opción A: segundo `JSONField` (`odontograma_evolucion`) en el mismo modelo — simple, una fila por paciente.
   - Opción B: modelo `OdontogramaEvolucion` con FK a paciente y `fecha_evolucion` — permite historial temporal granular.
   - Recomendación preliminar: B (más fiel a la norma V.4 "registre la evolución de los tratamientos" implica secuencia temporal).

2. **Inalterabilidad: Django-level vs audit completo?**
   - Opción A: `ModelAdmin.readonly_fields` + `pre_save` hook — simple, sin historial profundo.
   - Opción B: `django-simple-history` o tabla `OdontogramaAuditEntry` propia — trail completo, revisable, más pesado.
   - Recomendación preliminar: B en perfil estricto; A aceptable en perfil "soft".

3. **Nomenclaturas con siglas: ¿un estado genérico con sub-tipo o N estados distintos?**
   - Opción A: `restauracion: {material: "AM" | "R" | ...}` — schema compacto, fácil de validar.
   - Opción B: `restauracion_amalgama`, `restauracion_resina`, ... — más explícito pero ruidoso.
   - Recomendación preliminar: A (consistente con cómo la norma agrupa por concepto en VI.1.28).

4. **Hallazgos inter-piezas: ¿lista top-level o sub-clave por pieza?**
   - Opción A: top-level `hallazgos_inter_piezas: list[{tipo, fdi_pair, ...}]` — limpio, sin duplicación.
   - Opción B: sub-clave en cada pieza del par con referencia cruzada — más verboso, riesgo de desincronización.
   - Recomendación preliminar: A.

5. **Paleta de azul normativo: ¿`#0040ff` puro, `#1976d2` Material, u otro?**
   - La norma dice "azul" sin especificar hex. Hay que decidir un azul legible tanto en pantalla como impreso.
   - Recomendación preliminar: `#1565c0` (Material Blue 700 — bien impreso, buen contraste sobre blanco, compatible con lectura diaria).

6. **Firma de modificación: ¿username / full name / ID profesional del odontólogo?**
   - V.13 dice "el profesional responsable debe registrar y firmar". Decidir qué identificador persistir.
   - Recomendación preliminar: `user_id` + nombre de auditoría + número de colegiatura (si está en el modelo del consumidor).

7. **Widget SVG: ¿construir in-house o adoptar librería dental existente?**
   - Ver si existe alguna librería OSS con los pictogramas del Anexo II ya en SVG.
   - Recomendación preliminar: construir in-house, control total, sin dependencias externas con licencias inciertas.

8. **¿Cómo representamos "edéntulo total" sin chocar con estados individuales por pieza?**
   - Validador MUTEX: si `edentulo_total.arcada == "superior"`, rechazar cualquier estado en FDI 11-18 / 21-28 / 51-55 / 61-65.

9. **⚠️ AMBIGÜEDAD NORMATIVA ítem 1.24**: el PDF salta de 1.23 a 1.25. Confirmar con el Colegio si es errata o nomenclatura reservada. No bloquea v0.2.0.

---

**Cierre**: este documento debe leerse junto al PDF fuente ([Norma Técnica](docs/norms/norma-tecnica-odontograma-peru.pdf)) y es la entrada directa para el change SDD `v0-2-0-peru-profile`. Cada ítem marcado como "Plan v0.2.0" se convertirá en una task del breakdown de ese change.
