# Catálogo de nomenclaturas — perfil Perú v0.3.0-alpha.1

> **Propósito**: listado completo de las **32 nomenclaturas** del catálogo
> VI.1 de la **Norma Técnica del Odontograma** (Colegio Odontológico del
> Perú) que el paquete `xpertik-odontograma` implementa actualmente.
>
> Para validar con el odontólogo: ¿están todas las nomenclaturas? ¿alguna
> falta o sobra? ¿el matching key/sigla/cláusula es correcto?
>
> **Versión del paquete**: `xpertik-odontograma==0.3.0a1`
> **Generado desde**: `xpertik_odontograma.profiles.peru.states.CATALOG`
> **Fuente normativa**: `docs/norms/norma-tecnica-odontograma-peru.pdf`

---

## Resumen

| Métrica | Cantidad |
| --- | --- |
| Entries totales en catálogo | **32** |
| Disponibles para uso clínico (no cross-teeth) | **26** |
| Diferidas a v0.4.0 (cross-teeth, anomalías entre piezas o aparatos) | **6** |
| Con representación gráfica específica conforme a la norma (alpha.1) | **8** |
| En catálogo con sigla pero sin primitiva gráfica específica (alpha.3) | **18** |

**Nota**: VI.1.24 está ausente del PDF oficial (la numeración salta de 1.23
a 1.25). Documentado como `AUSENCIA_NORMATIVA_VI_1_24` en código —
pendiente confirmación con el Colegio Odontológico.

## Leyenda de status

- ✅ **Conforme alpha.1** — la representación gráfica específica de la
  norma está implementada (aspa, círculo, línea, sigla en recuadro, etc.).
- ⏳ **alpha.3** — la nomenclatura está en el catálogo, valida correctamente,
  pero el render todavía es genérico (color plano de cara). La primitiva
  específica se implementa en alpha.3.
- 🔒 **v0.4.0** — diferida; nomenclatura entre piezas (cross-teeth) o
  aparato ortodóntico que requiere modelo de datos extendido.

---

## Hallazgos (categoría: hallazgo)

| # | Cláusula | Key | Sigla | Color | Zona | Descripción norma | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | VI.1.3 | `caries` | — | rojo | corona | Lesión cariosa siguiendo su forma en las superficies dentarias comprometidas, totalmente pintada en rojo | ✅ |
| 2 | VI.1.6 | `desgaste_oclusal_incisal` | DES | azul | recuadro | Siglas "DES" en mayúsculas azul en el recuadro | ⏳ |
| 3 | VI.1.8 | `ausente` | — | azul | corona | Aspa (X) azul sobre la figura de la pieza dentaria | ✅ |
| 4 | VI.1.14 | `edentulo_total` | — | azul | corona | Línea recta horizontal azul sobre las coronas de las piezas ausentes del maxilar edéntulo | ⏳ |
| 5 | VI.1.15 | `fractura` | — | rojo | corona | Línea recta roja, en el sentido de la fractura, sobre corona y/o raíz | ⏳ |
| 6 | VI.1.27 | `remanente_radicular` | RR | rojo | raíz | Siglas "RR" en mayúsculas rojo sobre la raíz | ✅ |

## Tratamientos (categoría: tratamiento)

| # | Cláusula | Key | Sigla | Color | Zona | Descripción norma | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 7 | VI.1.4 | `corona_definitiva` | — | azul | recuadro | Circunferencia azul encerrando la corona; siglas del tipo en recuadro | ✅ |
| 8 | VI.1.5 | `corona_temporal` | — | rojo | corona | Circunferencia roja encerrando la corona | ⏳ |
| 9 | VI.1.19 | `implante` | IMP | azul | recuadro | Siglas "IMP" en mayúsculas azul en el recuadro de la pieza reemplazada | ✅ |
| 10 | VI.1.25 | `protesis_removible` | — | azul | sobre ápices | Dos líneas horizontales paralelas azul a nivel de los ápices (rojo si mal estado) | ⏳ |
| 11 | VI.1.26 | `protesis_total` | — | azul | corona | Dos líneas paralelas horizontales azul sobre las coronas (rojo si mal estado) | ⏳ |
| 12 | VI.1.28 | `restauracion` | — | azul | corona | Restauración pintada azul siguiendo forma en superficies; sigla material en recuadro | ✅ |
| 13 | VI.1.29 | `restauracion_temporal` | — | rojo | corona | Contorno en rojo siguiendo la forma en las superficies comprometidas | ⏳ |
| 14 | VI.1.33 | `tratamiento_pulpar` | — | azul | raíz | Línea recta vertical azul en la raíz; siglas del tipo en recuadro | ✅ |

### Tipos de Corona Definitiva (parámetros de VI.1.4)

| Sigla | Significado |
| --- | --- |
| CC | Corona completa metálica |
| CF | Corona fenestrada |
| CMC | Corona metal-cerámica |
| CV | Corona veneer (frente estético) |
| CJ | Corona jacket (estética libre de metal) |
| 3-4, 4-5, 7-8 | Corona parcial metálica (porción del diente cubierta) |

### Materiales de Restauración (parámetros de VI.1.28)

| Sigla | Significado |
| --- | --- |
| AM | Amalgama |
| R | Resina |
| IV | Ionómero de vidrio |
| IM | Incrustación metálica |
| IE | Incrustación estética |

### Tipos de Tratamiento Pulpar (parámetros de VI.1.33)

| Sigla | Significado |
| --- | --- |
| TC | Tratamiento de conductos |
| PC | Pulpectomía |
| PP | Pulpotomía |

## Anomalías (categoría: anomalía)

### Por pieza (sin cross-teeth)

| # | Cláusula | Key | Sigla | Color | Zona | Descripción norma | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 15 | VI.1.9 | `discromico` | DIS | azul | recuadro | Siglas "DIS" en mayúsculas azul en recuadro | ⏳ |
| 16 | VI.1.10 | `ectopico` | E | azul | recuadro | Letra "E" mayúscula azul en recuadro | ⏳ |
| 17 | VI.1.11 | `clavija` | — | azul | recuadro | Triángulo azul circunscribiendo el número de la pieza | ⏳ |
| 18 | VI.1.12 | `extruido` | — | azul | corona | Flecha azul dirigida hacia el plano oclusal | ⏳ |
| 19 | VI.1.13 | `intruido` | — | azul | corona | Flecha recta vertical azul dirigida hacia el ápice | ⏳ |
| 20 | VI.1.17 | `giroversion` | — | azul | corona | Flecha curva azul siguiendo el sentido de la giroversión a nivel oclusal | ⏳ |
| 21 | VI.1.18 | `impactacion` | I | azul | recuadro | Letra "I" mayúscula azul en recuadro | ⏳ |
| 22 | VI.1.20 | `macrodoncia` | MAC | azul | recuadro | Siglas "MAC" en mayúsculas azul en recuadro | ⏳ |
| 23 | VI.1.21 | `microdoncia` | MIC | azul | recuadro | Siglas "MIC" en mayúsculas azul en recuadro | ⏳ |
| 24 | VI.1.22 | `migracion` | — | azul | corona | Flecha recta horizontal azul siguiendo el sentido de la migración a nivel oclusal | ⏳ |
| 25 | VI.1.23 | `movilidad` | M + grado | azul | recuadro | "M" + grado (1/2/3) azul en recuadro. Clasificación en especificaciones | ✅ |
| 26 | VI.1.30 | `semi_impactacion` | SI | azul | recuadro | Siglas "SI" en mayúsculas azul en recuadro | ⏳ |

### Entre piezas (cross-teeth — diferidas a v0.4.0)

| # | Cláusula | Key | Sigla | Color | Zona | Descripción norma | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 27 | VI.1.7 | `diastema` | — | azul | entre piezas | Paréntesis invertido azul entre las piezas dentarias | 🔒 |
| 28 | VI.1.16 | `geminacion_fusion` | — | azul | entre piezas | Dos circunferencias azules interceptadas encerrando los números de las piezas involucradas | 🔒 |
| 29 | VI.1.31 | `supernumerario` | S | azul | entre piezas | Letra "S" mayúscula encerrada en circunferencia azul, entre los ápices de las piezas adyacentes | 🔒 |
| 30 | VI.1.32 | `transposicion` | — | azul | entre piezas | Dos flechas curvas azul entrecruzadas, a la altura de los números de las piezas involucradas | 🔒 |

## Ortodónticos (categoría: ortodóntico — diferidos a v0.4.0)

| # | Cláusula | Key | Sigla | Color | Zona | Descripción norma | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 31 | VI.1.1 | `aparato_orto_fijo` | — | azul | sobre ápices | Cuadrados con cruz en su interior a nivel de los ápices, unidos con línea recta. Azul (buen estado) o rojo (mal estado) | 🔒 |
| 32 | VI.1.2 | `aparato_orto_removible` | — | azul | sobre ápices | Línea en zig-zag a la altura de los ápices del maxilar en tratamiento. Azul (buen estado) o rojo (mal estado) | 🔒 |

---

## Causas de ausencia (cuando `estado = ausente`)

Cuando una pieza tiene estado `ausente`, opcionalmente se registra la
**causa**:

| Sigla / valor | Significado |
| --- | --- |
| `extraccion` | Pieza extraída |
| `exfoliacion` | Pieza exfoliada (caída fisiológica de pieza temporal) |
| `agenesia` | Pieza nunca formada |

---

## Validación clínica con el odontólogo

Pasarle este documento al profesional clínico junto con la sesión en el
admin de Django. Preguntarle específicamente:

1. **Completitud** — ¿el catálogo tiene las 32 nomenclaturas que prescribe
   la norma? ¿falta alguna? ¿sobra alguna?

2. **Cláusulas** — ¿la cita de la cláusula VI.1.N está correcta para cada
   nomenclatura?

3. **Siglas** — ¿las siglas (DES, DIS, E, IMP, MAC, MIC, RR, SI, S, AM, R,
   IV, IM, IE, TC, PC, PP, CC, CF, CMC, CV, CJ, 3-4, 4-5, 7-8) están bien
   interpretadas? ¿Faltan otros tipos comunes en la práctica?

4. **Priorización para alpha.3** — de las 18 nomenclaturas marcadas como
   ⏳, ¿cuáles son las 5 más usadas clínicamente y deberían entrar primero
   en alpha.3?

5. **Cross-teeth (v0.4.0)** — ¿cuáles de las 6 cross-teeth son
   imprescindibles en la práctica diaria? ¿el diastema y supernumerario
   son comunes? ¿geminación/fusión y transposición son raras?

6. **Cláusula VI.1.24 ausente del PDF** — ¿el odontólogo conoce qué
   nomenclatura iba a estar ahí? ¿Es errata del documento del Colegio o
   omisión intencional?

---

## Referencias técnicas

- Catálogo en código: `xpertik_odontograma/profiles/peru/states.py` — clase
  `PeruNomenclatura` (frozen dataclass) + tupla `CATALOG`
- Validador estricto: `xpertik_odontograma/profiles/peru/validators.py` —
  función `validate_peru_strict`
- Render gráfico: `xpertik_odontograma/svg/renderer.py` — funciones
  `_render_state_overlays`, `_face_fills`, `sigla_for_tooth`
- Norma fuente: `docs/norms/norma-tecnica-odontograma-peru.pdf`
- Análisis de conformidad completo: `NORMA_CUMPLIMIENTO.md`
