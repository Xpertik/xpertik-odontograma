# Catálogo de nomenclaturas — perfil Perú v0.3.0-alpha.1

> **Propósito**: lo que el `OdontogramaPeruInicialField` contempla
> **actualmente** (con representación gráfica conforme a la norma) y, al
> final, lo que **no está contemplado todavía** (en catálogo pero
> pendiente de implementación, o diferido a versiones posteriores).
>
> **Versión del paquete**: `xpertik-odontograma==0.3.0a1`
> **Generado desde**: `xpertik_odontograma.profiles.peru.states.CATALOG`
> **Norma fuente**: `docs/norms/norma-tecnica-odontograma-peru.pdf`

---

## Resumen ejecutivo

| Estado | Cantidad |
| --- | --- |
| ✅ **Implementado en alpha.1 — conforme a la norma** | **8** |
| ⏳ Pendiente para alpha.3 (en catálogo, sin primitiva gráfica específica) | 18 |
| 🔒 Diferido a v0.4.0 (cross-teeth + aparatos ortodónticos) | 6 |
| **Total catálogo** | **32** |

---

# ✅ Contemplado actualmente (alpha.1)

Lo que el odontograma **muestra correctamente** y el field valida según
la norma. **Estas 8 nomenclaturas son las que el odontólogo puede usar
hoy con representación gráfica conforme a la Norma Técnica del Colegio
Odontológico del Perú.**

## Hallazgos

| # | Cláusula | Key | Sigla | Color | Zona | Descripción y representación gráfica |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **VI.1.3** | `caries` | — | rojo | corona | Lesión cariosa pintada en **rojo** sobre las superficies (caras) comprometidas |
| 2 | **VI.1.8** | `ausente` | — | azul | corona | **Aspa (X) azul** sobre la silueta del diente |
| 3 | **VI.1.27** | `remanente_radicular` | RR | rojo | raíz | Siglas "**RR**" en **rojo** sobre la raíz |

## Tratamientos

| # | Cláusula | Key | Sigla | Color | Zona | Descripción y representación gráfica |
| --- | --- | --- | --- | --- | --- | --- |
| 4 | **VI.1.4** | `corona_definitiva` | (tipo) | azul | recuadro | **Circunferencia azul** alrededor de la corona + sigla del tipo en recuadro |
| 5 | **VI.1.19** | `implante` | IMP | azul | recuadro | Silueta **grayed** + "**IMP**" en recuadro superior |
| 6 | **VI.1.28** | `restauracion` | (material) | azul | corona | Cara afectada pintada en **azul** + sigla del material en recuadro |
| 7 | **VI.1.33** | `tratamiento_pulpar` | (tipo) | azul | raíz | **Línea vertical azul** sobre la raíz + sigla del tipo en recuadro |

## Anomalías

| # | Cláusula | Key | Sigla | Color | Zona | Descripción y representación gráfica |
| --- | --- | --- | --- | --- | --- | --- |
| 8 | **VI.1.23** | `movilidad` | M + grado | azul | recuadro | "**M**" + grado (1, 2 o 3) en **azul** dentro del recuadro |

## Parámetros disponibles

### Tipos de Corona Definitiva (`corona_definitiva.parametros.tipo`)

| Sigla | Significado |
| --- | --- |
| **CC** | Corona completa metálica |
| **CF** | Corona fenestrada |
| **CMC** | Corona metal-cerámica |
| **CV** | Corona veneer (frente estético) |
| **CJ** | Corona jacket (estética libre de metal) |
| **3-4** / **4-5** / **7-8** | Corona parcial metálica |

### Materiales de Restauración (`restauracion.parametros.material`)

| Sigla | Significado |
| --- | --- |
| **AM** | Amalgama |
| **R** | Resina |
| **IV** | Ionómero de vidrio |
| **IM** | Incrustación metálica |
| **IE** | Incrustación estética |

### Tipos de Tratamiento Pulpar (`tratamiento_pulpar.parametros.tipo`)

| Sigla | Significado |
| --- | --- |
| **TC** | Tratamiento de conductos |
| **PC** | Pulpectomía |
| **PP** | Pulpotomía |

### Grados de Movilidad (`movilidad.parametros.grado`)

| Valor | Significado |
| --- | --- |
| **1** | Movilidad horizontal grado I |
| **2** | Movilidad horizontal grado II |
| **3** | Movilidad horizontal y vertical (grado III) |

### Causas de Ausencia (cuando `estado = ausente`)

| Valor | Significado |
| --- | --- |
| `extraccion` | Pieza extraída |
| `exfoliacion` | Pieza exfoliada (caída fisiológica de pieza temporal) |
| `agenesia` | Pieza nunca formada |

---

# Pendiente — NO contemplado todavía

Las siguientes nomenclaturas **están en el catálogo y se pueden guardar y
validar**, pero **el render todavía no muestra su primitiva gráfica
específica conforme a la norma**. Aparecen en el popover y se aceptan en
formularios pero se ven como color plano de cara o sigla genérica en
recuadro.

## ⏳ alpha.3 — Pendiente representación gráfica específica

### Hallazgos

| # | Cláusula | Key | Sigla | Color | Zona | Representación que falta |
| --- | --- | --- | --- | --- | --- | --- |
| — | VI.1.6 | `desgaste_oclusal_incisal` | DES | azul | recuadro | "DES" en azul en recuadro |
| — | VI.1.14 | `edentulo_total` | — | azul | corona | Línea horizontal azul sobre coronas del maxilar edéntulo |
| — | VI.1.15 | `fractura` | — | rojo | corona | Línea recta roja en sentido de la fractura |

### Tratamientos

| # | Cláusula | Key | Sigla | Color | Zona | Representación que falta |
| --- | --- | --- | --- | --- | --- | --- |
| — | VI.1.5 | `corona_temporal` | — | rojo | corona | Circunferencia roja alrededor de la corona |
| — | VI.1.25 | `protesis_removible` | — | azul | sobre ápices | Dos líneas paralelas azul a nivel de los ápices |
| — | VI.1.26 | `protesis_total` | — | azul | corona | Dos líneas paralelas azul sobre las coronas del maxilar |
| — | VI.1.29 | `restauracion_temporal` | — | rojo | corona | Contorno rojo siguiendo forma de las superficies |

### Anomalías por pieza

| # | Cláusula | Key | Sigla | Color | Zona | Representación que falta |
| --- | --- | --- | --- | --- | --- | --- |
| — | VI.1.9 | `discromico` | DIS | azul | recuadro | "DIS" en azul en recuadro |
| — | VI.1.10 | `ectopico` | E | azul | recuadro | "E" en azul en recuadro |
| — | VI.1.11 | `clavija` | — | azul | recuadro | Triángulo azul circunscribiendo el número de la pieza |
| — | VI.1.12 | `extruido` | — | azul | corona | Flecha azul dirigida hacia el plano oclusal |
| — | VI.1.13 | `intruido` | — | azul | corona | Flecha vertical azul dirigida al ápice |
| — | VI.1.17 | `giroversion` | — | azul | corona | Flecha curva azul siguiendo el sentido de la rotación |
| — | VI.1.18 | `impactacion` | I | azul | recuadro | "I" en azul en recuadro |
| — | VI.1.20 | `macrodoncia` | MAC | azul | recuadro | "MAC" en azul en recuadro |
| — | VI.1.21 | `microdoncia` | MIC | azul | recuadro | "MIC" en azul en recuadro |
| — | VI.1.22 | `migracion` | — | azul | corona | Flecha horizontal azul siguiendo el sentido de la migración |
| — | VI.1.30 | `semi_impactacion` | SI | azul | recuadro | "SI" en azul en recuadro |

## 🔒 v0.4.0 — Diferido (anomalías cross-teeth y aparatos ortodónticos)

Estas nomenclaturas requieren un modelo de datos extendido (relaciones
**entre piezas**) que llega en v0.4.0. Hoy el catálogo las marca como
deshabilitadas con tooltip "Disponible en v0.4.0".

### Anomalías entre piezas

| # | Cláusula | Key | Sigla | Color | Descripción norma |
| --- | --- | --- | --- | --- | --- |
| — | VI.1.7 | `diastema` | — | azul | Paréntesis invertido azul entre las piezas dentarias |
| — | VI.1.16 | `geminacion_fusion` | — | azul | Dos circunferencias azules interceptadas encerrando los números de las piezas involucradas |
| — | VI.1.31 | `supernumerario` | S | azul | Letra "S" mayúscula encerrada en circunferencia azul, entre los ápices de las piezas adyacentes |
| — | VI.1.32 | `transposicion` | — | azul | Dos flechas curvas azul entrecruzadas a la altura de los números de las piezas involucradas |

### Aparatos ortodónticos

| # | Cláusula | Key | Sigla | Color | Descripción norma |
| --- | --- | --- | --- | --- | --- |
| — | VI.1.1 | `aparato_orto_fijo` | — | azul | Cuadrados con cruz a nivel de los ápices, unidos con línea recta. Azul (buen estado) o rojo (mal estado) |
| — | VI.1.2 | `aparato_orto_removible` | — | azul | Línea en zig-zag a la altura de los ápices del maxilar en tratamiento. Azul (buen estado) o rojo (mal estado) |

## Nota sobre VI.1.24

VI.1.24 está **ausente del PDF oficial** (la numeración salta de 1.23 a
1.25). Documentado como `AUSENCIA_NORMATIVA_VI_1_24` en código.
Pendiente confirmación con el Colegio Odontológico — ¿es errata o se
omitió a propósito?

---

## Validación con el odontólogo

1. **De las 8 implementadas hoy**: ¿la representación gráfica matchea lo
   que un profesional espera ver al leer un odontograma conforme a la
   norma peruana? Probar cada una en el admin con un caso clínico.

2. **De las 18 pendientes (alpha.3)**: ¿cuáles son las **5 más usadas en
   la práctica clínica diaria** y deberían entrar primero?

3. **Cross-teeth (v0.4.0)**: ¿el diastema y supernumerario se usan
   frecuentemente? ¿Geminación / fusión / transposición son raras?

4. **Cláusula VI.1.24 ausente**: ¿el odontólogo conoce qué nomenclatura
   iba a estar ahí?

5. **Lo que falta**: ¿hay algo crítico que NO esté en el catálogo de 32?

---

## feedback

observaciones en `docs/feedback/alpha1.md`
