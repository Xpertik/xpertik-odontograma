# Caso clínico — Carlos Mendoza (67 años)

> **Propósito**: este documento describe el caso clínico sembrado por
> `manage.py seed_demo` en el paciente `Carlos Mendoza (67 años) — Adulto
> mayor complejo` para que el odontólogo valide si la representación
> gráfica del widget coincide con la **Norma Técnica del Odontograma**
> emitida por el Colegio Odontológico del Perú.
>
> **Versión del paquete**: `xpertik-odontograma==0.3.0a1`
> **Fecha de seed**: 2026-04-24

---

## Perfil del paciente

Adulto mayor con múltiples extracciones previas, restauración protésica
parcial, periodoncia incipiente y patología endodóntica.

---

## Cuadrante 1 — Maxilar superior derecho

| Pieza | Hallazgo | Nomenclatura (cláusula norma) | Cómo DEBE verse |
| --- | --- | --- | --- |
| **11** | Fractura en cara vestibular | **Fractura** (VI.1.15) | Línea recta **roja** sobre la cara vestibular del incisivo central |
| **14** | Movilidad grado 1 | **Movilidad** (VI.1.23) | "M1" en **azul** dentro del recuadro superior |
| **15** | Movilidad grado 2 | **Movilidad** (VI.1.23) | "M2" en **azul** dentro del recuadro superior |
| **16** | Ausente por extracción | **Diente Ausente** (VI.1.8) | **Aspa (X) azul** sobre la silueta del primer molar |
| **17** | Ausente por extracción | **Diente Ausente** (VI.1.8) | **Aspa azul** sobre la silueta del segundo molar |
| 12, 13, 18 | Sin hallazgo | — | Silueta limpia |

## Cuadrante 2 — Maxilar superior izquierdo

| Pieza | Hallazgo | Nomenclatura (cláusula norma) | Cómo DEBE verse |
| --- | --- | --- | --- |
| **21** | Fractura en cara vestibular | **Fractura** (VI.1.15) | Línea recta **roja** en cara vestibular del incisivo central izquierdo |
| **25** | Corona definitiva metálica completa | **Corona Definitiva CC** (VI.1.4) | **Circunferencia azul** que rodea la corona del segundo premolar + "**CC**" en **azul** dentro del recuadro superior |
| **26** | Ausente por extracción | **Diente Ausente** (VI.1.8) | **Aspa azul** sobre la silueta del primer molar |
| **27** | Ausente por extracción | **Diente Ausente** (VI.1.8) | **Aspa azul** sobre la silueta del segundo molar |
| 22, 23, 24, 28 | Sin hallazgo | — | Silueta limpia |

## Cuadrante 3 — Mandíbula inferior izquierda

| Pieza | Hallazgo | Nomenclatura (cláusula norma) | Cómo DEBE verse |
| --- | --- | --- | --- |
| **36** | **Caries** en oclusal + **Tratamiento de Conducto** previo | **Caries** (VI.1.3) + **Tratamiento Pulpar TC** (VI.1.33) | Cara oclusal pintada en **rojo** (caries activa/recidivante) + **línea vertical azul** sobre la raíz + "**TC**" en **azul** dentro del recuadro inferior |
| **37** | Ausente por extracción | **Diente Ausente** (VI.1.8) | **Aspa azul** sobre la silueta |
| 31, 32, 33, 34, 35, 38 | Sin hallazgo | — | Silueta limpia |

## Cuadrante 4 — Mandíbula inferior derecha

| Pieza | Hallazgo | Nomenclatura (cláusula norma) | Cómo DEBE verse |
| --- | --- | --- | --- |
| **46** | Remanente radicular (raíz remanente) | **Remanente Radicular RR** (VI.1.27) | "**RR**" en **rojo** sobre la raíz del primer molar inferior |
| **47** | Ausente por extracción | **Diente Ausente** (VI.1.8) | **Aspa azul** sobre la silueta |
| 41, 42, 43, 44, 45, 48 | Sin hallazgo | — | Silueta limpia |

---

## Especificaciones generales (campo de texto del odontograma)

> *"Paciente adulto mayor. Múltiples ausencias dentarias por extracciones
> previas. Recomendado: prótesis parcial removible. Tratamiento
> endodóntico previo en pieza 36 con caries recidivante."*

---

## Síntesis clínica

**Lo que está pasando con este paciente:**

- **6 dientes ausentes** (16, 17, 26, 27, 37, 47) — todos posteriores;
  indicación clara de prótesis parcial removible o rehabilitación sobre
  implantes.
- **2 fracturas** en incisivos centrales superiores (11, 21) — probablemente
  trauma previo.
- **Movilidad incipiente** en sector premolar superior derecho (14 grado 1,
  15 grado 2) — sugiere periodontitis localizada.
- **Pieza 36** con tratamiento de conducto antiguo + caries recidivante —
  necesita reevaluación endodóntica.
- **Pieza 46** con remanente radicular — requiere extracción quirúrgica.

---

## Validación:

1. ✅ **Nomenclaturas y cláusulas correctas** — ¿la cita de la cláusula
   VI.1.N en la norma técnica del Colegio Odontológico es correcta para
   cada hallazgo de este caso?

2. ✅ **Representación visual coherente con la norma** — ¿lo que muestra el
   software (aspa azul, línea vertical, "TC" en recuadro, "RR" rojo, etc.)
   coincide con lo que esperaría ver un profesional al leer un odontograma
   conforme a la norma peruana?

3. ✅ **Coherencia clínica del caso** — ¿el conjunto de hallazgos es
   plausible en un paciente real de 67 años? ¿La síntesis clínica refleja
   correctamente lo que se ve en el chart?

4. ✅ **Completitud informativa** — ¿debería haber siglas adicionales en
   los recuadros de los dientes ausentes para indicar el tipo de ausencia
   (extracción / exfoliación / agenesia)? ¿O esa información va únicamente
   en el campo de especificaciones?

5. ✅ **Lo que falta** — ¿qué nomenclaturas o información clínica relevante
   no está representada en este caso y debería estar en alpha.2 o alpha.3?

---

## feedback

observaciones en `docs/feedback/alpha1.md`
