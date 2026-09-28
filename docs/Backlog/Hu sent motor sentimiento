# Historias de Usuario — Módulo Motor de Análisis de Sentimiento (EPIC-SENT, Sprint 2)

**Proyecto:** HumWorld — Equipo 3
**Origen:** PDF de especificaciones (`0 PROYECTO_FINAL_HUMWORLD 260714.pdf`), secciones 4.2.2 (Diccionario de palabras evaluables), 4.2.4 (Procesado de la información), 10.2 (Endpoints mínimos obligatorios: `/dictionary`, `/sentiment`) y 10.4 (Posible algoritmo para cálculo del humor). Algoritmo de agregación decidido y justificado en `ADR-003-algoritmo-sentimiento.md`, conforme a la sección 11 de las instrucciones del proyecto.
**Estado general:** Propuesto — historias generadas a partir de los títulos ya oficializados en la hoja "Backlog" de `HumWorld_Anexo_I_Planificacion_actualizado.xlsx` (entregable P3) y de la estimación en puntos ya realizada en Planning Poker (P3, `Anexo-I-Planificacion-entregado-P3.md`, Sprint 2 = 18 puntos). Pendiente de revisión crítica del equipo antes de iniciar Sprint 2.
**Versión del documento:** v1.0 — Sesión 2026-09-28. Primera formalización detallada de HU-SENT-001 a 007 (antes solo existían como títulos de una línea en la hoja Backlog del Excel; no existía Gherkin, DoD ni contrato de API para ninguna de las 7).

> **Nota de grounding general:** el PDF exige un algoritmo de análisis de sentimiento "basado en diccionario, LLM u otro método justificado" (Objetivos específicos, punto 2) y ofrece un algoritmo posible (§10.4) como referencia no vinculante ("Esta es solo una posible solución. Cada equipo puede determinar otra manera"). El backlog ya oficializado por el equipo (hoja Excel) eligió un enfoque **híbrido diccionario + ML** (HU-SENT-002-v2, HU-SENT-006, HU-SENT-007). Este documento formaliza esa elección ya tomada por el equipo; no la introduce de nuevo. La parte de diccionario está completamente grounded en el PDF y en la sección 11 de las instrucciones del proyecto; la parte de ML **no está especificada en ningún documento fuente** más allá del título de la historia, por lo que HU-SENT-002-v2 y, especialmente, HU-SENT-006 quedan con puntos explícitamente marcados como pendientes de decisión del equipo, en vez de inventar una arquitectura de ML no acordada.

---

## HU-SENT-001 — Gestión CRUD del diccionario de términos

**Tipo:** Historia de Usuario
**Como** administrador del sistema,
**quiero** dar de alta, consultar, modificar y eliminar términos del diccionario de sentimiento (palabra, idioma, valor numérico),
**para** mantener actualizado el vocabulario que el sistema usa para calcular el humor de las noticias.

**Prioridad:** Alta
**Estimación (Planning Poker P3):** 5 puntos *(ya estimado formalmente en el Planning Poker de la Práctica P3 — ver `Anexo-I-Planificacion-entregado-P3.md`; no es un valor definitivo si el alcance cambia, debe revalidarse con el equipo)*
**Depende de contrato de API:** Sí — `GET /api/v1/dictionary`, `GET /api/v1/dictionary/{id}`, `POST /api/v1/dictionary`, `PUT /api/v1/dictionary/{id}`, `PATCH /api/v1/dictionary/{id}`, `DELETE /api/v1/dictionary/{id}` *(recurso nuevo — no existe todavía en `contrato-canales-fuentes-rss.openapi.yaml`; requiere su propio contrato o una extensión del existente, a definir)*

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Alta exitosa de un término
  Dado que no existe un término con la misma palabra y el mismo idioma en el diccionario
  Cuando se envía POST a /api/v1/dictionary con palabra="guerra", idioma="es", valor=-8
  Entonces el sistema responde con código HTTP 201
  Y el término queda disponible en el diccionario con esos datos

Escenario: Rechazo por valor fuera de rango
  Dado que el diccionario usa una escala de -10 a +10 (instrucciones del proyecto, sección 11)
  Cuando se envía POST a /api/v1/dictionary con valor=11 o valor=-11
  Entonces el sistema responde con código HTTP 400
  Y no se crea ningún término

Escenario: Rechazo por término duplicado
  Dado que ya existe un término con palabra="guerra" e idioma="es"
  Cuando se envía POST a /api/v1/dictionary con la misma palabra="guerra" e idioma="es"
  Entonces el sistema responde con código HTTP 409

Escenario: Búsqueda de términos por palabra
  Dado que existen términos registrados
  Cuando se envía GET a /api/v1/dictionary?busqueda=guerr
  Entonces el sistema responde con código HTTP 200
  Y la lista incluye únicamente términos cuya palabra contiene "guerr"

Escenario: Eliminación de un término inexistente
  Cuando se envía DELETE a /api/v1/dictionary/{id} con un id que no existe
  Entonces el sistema responde con código HTTP 404
```

**Nota de grounding (idiomas):** el PDF (sección 3, Alcance, punto 2) exige que los idiomas soportados para el análisis sean **inglés y español** — el campo `idioma` del término es obligatorio por ese motivo, no es una adición arbitraria.

**Nota de grounding (escala):** el rango -10 a +10 proviene directamente de la sección 11 de las instrucciones del proyecto y coincide con el ejemplo del PDF (§10.4: "-10 palabra que indica mal humor, +10 palabra que indica muy buen humor").

### Definition of Done
(Bloque general DoD, sección 14 de las instrucciones del proyecto — código revisado, pruebas con mocks, cobertura ≥80%, SonarQube sin críticos, Swagger actualizado, build/deploy con `needs: [test, sonarqube]`.) Adicionalmente:
- Prueba unitaria específica de los valores límite de la escala: -10, 0, +10 aceptados; -11 y +11 rechazados con 400.
- Prueba del criterio de unicidad compuesta (palabra + idioma), no solo palabra.

---

## HU-SENT-002-v2 — Cálculo híbrido de humor (diccionario + ML)

**Tipo:** Historia Técnica / Enabler Story *(el actor es el propio sistema, según sección 4 de las instrucciones del proyecto)*
**Como** sistema HumWorld,
**quiero** calcular el valor de humor de cada noticia capturada usando el modelo de ML entrenado y versionado (HU-SENT-006) cuando esté disponible, o el método determinista de diccionario (HU-SENT-007) en caso contrario,
**para** asignar automáticamente un valor de sentimiento a toda noticia nueva sin intervención manual, mejorando progresivamente la precisión a medida que el modelo de ML esté disponible.

**Prioridad:** Alta
**Estimación (Planning Poker P3):** 5 puntos *(ya estimado en P3; ver nota — el alcance de esta historia se ha detallado recién en esta sesión, por lo que el equipo debería revalidar si 5 puntos sigue siendo representativo una vez fijados los puntos pendientes de abajo)*
**Depende de contrato de API:** No expone endpoint propio — es un servicio interno, disparado automáticamente tras cada captura exitosa de una noticia (ver HU-RSS-006/HU-RSS-008, `captura_service.py`). **Mecanismo exacto de disparo pendiente de decisión del equipo:** ¿síncrono dentro del propio flujo de captura (el cálculo de humor bloquea la respuesta/el job de captura hasta terminar), o asíncrono como paso posterior independiente? Esto determina si el cálculo puede degradar el tiempo total del cron (HU-RSS-006) o de la captura manual (HU-RSS-008).

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Cálculo con modelo de ML disponible
  Dado que existe un modelo de ML entrenado y versionado (ver HU-SENT-006)
  Cuando se captura una noticia nueva
  Entonces el sistema calcula su valor de humor usando ese modelo
  Y persiste el resultado (HU-SENT-003) con metodo_calculo="ml" y el identificador de versión del modelo usado

Escenario: Cálculo sin modelo de ML disponible (fallback)
  Dado que no existe todavía un modelo de ML entrenado (estado inicial del proyecto, antes de Sprint 4)
  Cuando se captura una noticia nueva
  Entonces el sistema calcula su valor de humor usando el método determinista de diccionario (HU-SENT-007)
  Y persiste el resultado con metodo_calculo="diccionario"

Escenario: Fallo del modelo de ML durante el cálculo
  Dado que existe un modelo de ML disponible pero su ejecución lanza un error
  Cuando el sistema intenta calcular el humor de una noticia con ese modelo
  Entonces el sistema recae automáticamente en el método de diccionario para esa noticia
  Y la noticia no queda nunca sin un valor de humor calculado por causa de ese fallo
  Y el incidente queda registrado en el log del sistema
```

**Nota de grounding:** la secuencia "diccionario primero, ML después" está grounded en la propia planificación oficial de Sprint 2 a 5 (`Anexo-I-Planificacion-entregado-P3.md` / hoja Historias-Estimacion): HU-SENT-006 (entrenamiento del modelo) recién se ubica en Sprint 4 "con data ya acumulada", y Sprint 5 registra explícitamente "cierre de HU-SENT-002-v2 (activar camino del modelo)" — confirmando que el camino de diccionario es el que se activa primero (Sprint 2) y el camino ML se activa más tarde, no al revés.

### Definition of Done
(Bloque general DoD, sección 14.) Adicionalmente:
- Pruebas unitarias del mecanismo de fallback con el modelo de ML **mockeado** (nunca cargar un modelo real en pruebas unitarias) — incluye el caso de fallo forzado del mock.
- Prueba de que, con el modelo de ML deshabilitado/ausente (estado esperado hasta Sprint 4), el 100% de las noticias capturadas terminan con un `metodo_calculo` registrado (diccionario o ml), nunca vacío.

---

## HU-SENT-003 — Persistencia del resultado de humor y polarización

**Tipo:** Historia Técnica / Enabler Story *(el actor es el propio sistema)*
**Como** sistema HumWorld,
**quiero** persistir el valor de humor calculado y un indicador de polarización junto a cada noticia,
**para** que ambos valores estén disponibles para consultas agregadas y dashboards sin tener que recalcularlos en cada lectura.

**Prioridad:** Alta
**Estimación (Planning Poker P3):** 3 puntos
**Depende de contrato de API:** No expone endpoint propio — extiende el modelo de datos `Noticia` ya definido en `diagrama-clases.md` (EPIC-RSS). El campo `valor_humor` (float, nullable) **ya existe** en ese diagrama, dejado explícitamente reservado para este módulo. **Pendiente:** agregar un nuevo campo para el indicador de polarización (nombre y tipo de dato a definir — ver `ADR-003-algoritmo-sentimiento.md`, que propone `polarizacion_terminos` como desviación estándar de los términos coincidentes) y actualizar `diagrama-clases.md` en consecuencia — no se modifica ese diagrama en esta sesión, solo se deja documentada la necesidad.

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Persistencia exitosa tras el cálculo
  Dado que HU-SENT-002-v2 calculó un valor de humor y un valor de polarización para una noticia
  Cuando el sistema persiste el resultado
  Entonces el valor_humor almacenado coincide exactamente con el valor calculado
  Y el indicador de polarización almacenado coincide exactamente con el valor calculado
  Y se registra el metodo_calculo usado ("diccionario" o "ml")

Escenario: Noticia sin términos evaluables coincidentes
  Dado que una noticia no contiene ningún término del diccionario (método diccionario, HU-SENT-007)
  Cuando el sistema intenta calcular y persistir su humor
  Entonces valor_humor se persiste como NULL (no como 0)
  Y esto permite distinguir "sin datos suficientes para evaluar" de "evaluado y resultó neutro" en las consultas agregadas (HU-SENT-004)
```

**Nota de grounding:** el PDF (sección 4.2.4) exige explícitamente que "la información de valor de 'humor' de cada RSS se persistirá junto con el propio RSS" — esta historia formaliza ese requisito para el caso de diccionario ("En el caso de utilizar diccionario de palabras", texto literal del PDF).

### Definition of Done
(Bloque general DoD, sección 14.) Adicionalmente:
- Prueba de round-trip: calcular → persistir → leer, verificando que ambos valores (humor y polarización) sobreviven sin pérdida de precisión.
- Migración de base de datos (MySQL) documentada para el nuevo campo de polarización, revisada por el equipo antes de mergear.

---

## HU-SENT-004 — Consulta de análisis de sentimiento (global/continente/país/timeline)

**Tipo:** Historia de Usuario
**Como** analista de medios o usuario interesado en la evolución del sentimiento global *(PDF, sección 4.1: "el sistema está pensado para ser utilizado por analistas de medios, investigadores o cualquier usuario interesado en la evolución del sentimiento global")*,
**quiero** consultar el valor de humor agregado a nivel global, por continente, por país, y su evolución en el tiempo,
**para** analizar cómo cambia el estado de ánimo del mundo y de sus regiones.

**Prioridad:** Alta *(aunque su estimación es la más baja de Sprint 2, es la historia que las dashboards de EPIC-DASH consumen directamente — bloquea el Sprint 3 si no está lista)*
**Estimación (Planning Poker P3):** 1 punto
**Depende de contrato de API:** Sí — `GET /api/v1/sentiment` con parámetros de query `continente`, `pais`, `desde`, `hasta` (PDF, §10.2: "GET (global, por continente, por país, timeline, detalle noticia)") *(recurso nuevo, no existe todavía en ningún contrato OpenAPI del Proyecto)*

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Consulta del humor global
  Cuando se envía GET a /api/v1/sentiment sin parámetros
  Entonces el sistema responde con código HTTP 200
  Y el cuerpo incluye el humor agregado (promedio de valor_humor) de todas las noticias con valor_humor no nulo

Escenario: Consulta filtrada por continente
  Dado que existen noticias asociadas (vía FuenteRSS → CanalNoticias) a canales de distintos continentes
  Cuando se envía GET a /api/v1/sentiment?continente=Europa
  Entonces el sistema responde con código HTTP 200
  Y el agregado incluye únicamente noticias cuyo canal tiene continente="Europa"

Escenario: Consulta de timeline en un rango de fechas
  Cuando se envía GET a /api/v1/sentiment?desde=2026-09-01&hasta=2026-09-30
  Entonces el sistema responde con código HTTP 200
  Y el cuerpo incluye una serie de valores agregados por fecha dentro de ese rango

Escenario: Filtro sin datos disponibles
  Dado un continente o país sin ninguna noticia con valor_humor calculado
  Cuando se consulta /api/v1/sentiment con ese filtro
  Entonces el sistema responde con código HTTP 200 y un resultado vacío o nulo
  Y nunca responde con código HTTP 500 por ausencia de datos
```

**Nota de grounding:** esta historia reutiliza el modelo `CanalNoticias.continente`/`CanalNoticias.pais` ya definido en EPIC-RSS (`ADR-002-arquitectura-captura-rss.md`) en vez de duplicar esos campos en `Noticia` — la agregación por continente/país se resuelve mediante el join `Noticia → FuenteRSS → CanalNoticias` ya existente.

### Definition of Done
(Bloque general DoD, sección 14.) Adicionalmente:
- Pruebas de agregación con datos fixture (no reales) cubriendo al menos dos continentes y un rango de fechas.

---

## HU-SENT-005 — Análisis de sentimiento de un texto arbitrario (endpoint)

**Tipo:** Historia de Usuario
**Como** analista de medios o usuario del sistema,
**quiero** enviar un texto arbitrario a la API y recibir su valor de humor calculado,
**para** probar el análisis de sentimiento sin depender de que el texto provenga de una noticia ya capturada.

**Prioridad:** Media
**Estimación (Planning Poker P3):** 2 puntos
**Depende de contrato de API:** Sí — `POST /api/v1/sentiment` con body `{"texto": "..."}` (PDF, §10.2: "POST (para analizar un texto en concreto, devuelve su valor de humor)") *(recurso nuevo, comparte tag `sentiment` con HU-SENT-004)*

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Análisis exitoso de un texto con términos del diccionario
  Cuando se envía POST a /api/v1/sentiment con texto="Gran victoria, aunque hubo momentos de guerra"
  Entonces el sistema responde con código HTTP 200
  Y el cuerpo incluye un valor_humor calculado según el método determinista de diccionario (HU-SENT-007)

Escenario: Rechazo de texto vacío
  Cuando se envía POST a /api/v1/sentiment con texto=""
  Entonces el sistema responde con código HTTP 400

Escenario: Texto sin términos del diccionario coincidentes
  Cuando se envía POST a /api/v1/sentiment con un texto que no contiene ningún término del diccionario
  Entonces el sistema responde con código HTTP 200
  Y el valor_humor devuelto es NULL, con un indicador explícito de "0 términos evaluados" en la respuesta
```

**Nota de grounding (alcance del método):** a diferencia de HU-SENT-002-v2 (que puede usar ML), este endpoint de análisis puntual usa siempre el método determinista de diccionario (HU-SENT-007) — el PDF no exige que el análisis de texto arbitrario pase por el camino de ML, y usar siempre diccionario aquí da una respuesta instantánea y 100% reproducible para pruebas. **Esto es una propuesta del agente PO/Arquitecto, no una decisión ya tomada por el equipo — a confirmar.**

### Definition of Done
(Bloque general DoD, sección 14.)

---

## HU-SENT-006 — Entrenamiento y versionado del modelo de ML

**Tipo:** Historia Técnica / Enabler Story *(el actor es el propio sistema o un proceso de datos — ver nota de grounding, actor exacto pendiente de decisión del equipo, análogo a lo resuelto para HU-RSS-009)*
**Como** sistema HumWorld (o administrador del sistema, según se decida el mecanismo de disparo — ver más abajo),
**quiero** entrenar y versionar un modelo de aprendizaje automático para el cálculo de humor, usando como datos de entrenamiento el histórico de noticias ya evaluadas por el método de diccionario,
**para** mejorar progresivamente la precisión del cálculo de humor más allá del método determinista de diccionario (HU-SENT-007).

**Prioridad:** Media
**Estimación (Planning Poker P3):** 5 puntos *(estimado en P3 antes de que existiera este detalle — dado el volumen de puntos abiertos listados abajo, el equipo debería tratar este número como aún más provisional que el resto y revalidarlo con Planning Poker real una vez resueltos)*
**Depende de contrato de API:** Ninguno definido todavía — **completamente pendiente de decisión del equipo** (ver nota de grounding).

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Entrenamiento exitoso con datos suficientes
  Dado que existe un volumen mínimo de noticias ya evaluadas por el método de diccionario (umbral exacto — PENDIENTE, ver nota)
  Cuando se dispara el proceso de entrenamiento
  Entonces el sistema genera una nueva versión del modelo
  Y esa versión queda registrada con un identificador único y la fecha de entrenamiento

Escenario: Entrenamiento con datos insuficientes
  Dado que el volumen de noticias evaluadas no alcanza el umbral mínimo definido
  Cuando se intenta disparar el entrenamiento
  Entonces el sistema rechaza la operación
  Y el modelo de ML activo (si existe una versión previa) no se ve afectado
```

**Nota de grounding (alcance MUY abierto — a diferencia del resto de historias de este documento, el PDF NO exige ni describe un modelo de ML en ningún punto; solo lo permite como una de las opciones válidas para el algoritmo de sentimiento, "basado en diccionario, LLM u otro método justificado", Objetivos específicos punto 2). Quedan pendientes de decisión del equipo, sin los cuales esta historia no puede pasar a Planning Poker real ni a implementación:**
1. **Tipo de modelo y librería** (p. ej. un clasificador/regresor clásico tipo scikit-learn entrenado sobre features léxicas, un modelo de embeddings, un fine-tuning de un modelo pequeño, etc.) — no hay ninguna decisión de arquitectura tomada todavía; requeriría su propio ADR antes de implementarse.
2. **Features de entrada** al modelo (¿texto crudo, bag-of-words, embeddings, features derivadas del propio diccionario?).
3. **Mecanismo de disparo del entrenamiento**: ¿manual, vía un endpoint administrativo (análogo a la decisión ya tomada en HU-RSS-009 de exponer `POST /api/v1/seeds`), o programado automáticamente (p. ej. un cron adicional, análogo a HU-RSS-006)? Esto determina si el actor de esta historia es "sistema" (Enabler puro) o "administrador del sistema" (Historia de Usuario clásica, como terminó siendo HU-RSS-009 tras la decisión del equipo del 2026-09-10).
4. **Umbral mínimo de datos** para entrenar (el Gherkin de arriba lo deja como placeholder sin cifra, precisamente para no inventar un número sin respaldo).
5. **Mecanismo y esquema de versionado** del modelo (¿archivo con timestamp, tabla de metadatos en MySQL, ambos?).
6. **Criterio de evaluación/validación** del modelo antes de promoverlo a producción (¿se compara contra el método de diccionario en un conjunto de validación? ¿con qué métrica?).
7. **Si el entrenamiento o la inferencia dependen de un servicio externo** (p. ej. una API de terceros para embeddings o LLM): de ser así, aplicarían los patrones de resiliencia de la sección 13 del proyecto (Circuit Breaker/Timeout/Retry), análogos a los ya definidos en `ADR-002` para las fuentes RSS — hoy no se puede evaluar esto porque no existe todavía una decisión de si el modelo se aloja localmente o se consume externamente.

**Recomendación del agente PO/Arquitecto:** antes de estimar esta historia con Planning Poker real o de tocar código, el equipo debería resolver los 7 puntos de arriba — posiblemente amerite su propio ADR ("Elección de arquitectura del modelo de ML de humor"), separado de `ADR-003` (que cubre solo el algoritmo determinista de diccionario).

### Definition of Done
(Bloque general DoD, sección 14.) Adicionalmente (una vez resueltos los puntos pendientes):
- Pruebas unitarias del entrenamiento usando un dataset de fixture pequeño y determinista (nunca entrenar con datos reales de producción en el pipeline de CI).
- Documentación del criterio de evaluación/validación usado para promover una versión del modelo.

---

## HU-SENT-007 — Fallback determinista con diccionario

**Tipo:** Historia Técnica / Enabler Story *(el actor es el propio sistema)*
**Como** sistema HumWorld,
**quiero** calcular el humor de una noticia mediante el método determinista de diccionario — promedio simple de los valores de los términos evaluables coincidentes, más un indicador de polarización — según lo definido en `ADR-003-algoritmo-sentimiento.md`,
**para** disponer siempre de un valor de humor calculable, incluso cuando el modelo de ML no esté disponible, no esté entrenado todavía, o falle (ver HU-SENT-002-v2).

**Prioridad:** Alta
**Estimación (Planning Poker P3):** 2 puntos
**Depende de contrato de API:** No expone endpoint propio — es un servicio interno invocado por HU-SENT-002-v2 (cálculo automático tras captura) y por HU-SENT-005 (endpoint de análisis de texto arbitrario).

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Cálculo con dos términos de signos opuestos (ilustra la limitación conocida del promedio simple)
  Dado que el diccionario contiene el término "guerra" con valor -8 y el término "victoria" con valor +6
  Y una noticia cuyo texto contiene exactamente esos dos términos evaluables y ningún otro
  Cuando el sistema calcula su humor
  Entonces valor_humor = (-8 + 6) / 2 = -1.0
  Y polarizacion_terminos = desviación estándar de [-8, 6] = 7.0
  Y este resultado documenta explícitamente la limitación conocida (instrucciones del proyecto, sección 11): un promedio casi neutro (-1.0) puede ocultar una noticia con términos fuertemente opuestos, señal que solo queda visible a través de polarizacion_terminos

Escenario: Noticia sin términos evaluables coincidentes
  Dado una noticia cuyo texto no contiene ningún término del diccionario
  Cuando el sistema calcula su humor
  Entonces valor_humor se registra como NULL
  Y cantidad_terminos_evaluados = 0

Escenario: Coincidencia de un único término
  Dado una noticia cuyo texto contiene exactamente el término "victoria" con valor +6 y ningún otro término evaluable
  Cuando el sistema calcula su humor
  Entonces valor_humor = 6.0
  Y polarizacion_terminos = 0.0 (desviación estándar de un único valor)
```

**Nota de grounding (algoritmo):** la fórmula (promedio simple, no suma) y el indicador complementario de polarización (desviación estándar) están decididos y justificados en detalle en `ADR-003-algoritmo-sentimiento.md`, conforme a la sección 11 de las instrucciones del proyecto. **Pendiente de decisión del equipo:** si `n` (el divisor del promedio) cuenta cada aparición del término en el texto o solo términos únicos distintos — el ejemplo de arriba asume términos únicos, pero no está confirmado.

### Definition of Done
(Bloque general DoD, sección 14.) Adicionalmente:
- Prueba unitaria que reproduce exactamente el escenario numérico de arriba (valor_humor=-1.0, polarizacion_terminos=7.0) — determinista, sin mocks de red ni de modelo ML, 100% verificable.
- Prueba del caso de cero términos coincidentes (valor_humor=NULL).

---

## Resumen de trazabilidad

| ID | Tipo | Prioridad | Puntos (P3) | Endpoint / mecanismo | Referencia PDF |
|---|---|---|---|---|---|
| HU-SENT-001 | Historia de Usuario | Alta | 5 | `/api/v1/dictionary` (CRUD, propuesto) | §4.2.2, §10.2 |
| HU-SENT-002-v2 | Enabler Story | Alta | 5 | Interno (hook tras captura) | §4.2.4, Objetivos específicos #2 |
| HU-SENT-003 | Enabler Story | Alta | 3 | Extiende modelo `Noticia` | §4.2.4 |
| HU-SENT-004 | Historia de Usuario | Alta | 1 | `GET /api/v1/sentiment` (propuesto) | §4.1, §10.2 |
| HU-SENT-005 | Historia de Usuario | Media | 2 | `POST /api/v1/sentiment` (propuesto) | §10.2 |
| HU-SENT-006 | Enabler Story *(actor a confirmar)* | Media | 5 | Sin definir — muy pendiente | Objetivos específicos #2 (no detallado) |
| HU-SENT-007 | Enabler Story | Alta | 2 | Interno (servicio compartido) | §10.4, sección 11 instrucciones proyecto |

## Tabla de control de versiones

| ID | Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|---|
| HU-SENT-001 a 007 | v1.0 | 2026-09-28 | Primera formalización detallada de las 7 historias de EPIC-SENT, a partir de los títulos ya oficializados en la hoja Backlog del Excel y de la estimación ya realizada en Planning Poker de P3. Se agregan Gherkin, DoD, contrato de API propuesto y notas de grounding para cada una. Se identifican y documentan explícitamente los puntos pendientes de decisión del equipo, en particular para HU-SENT-002-v2 y, sobre todo, HU-SENT-006 (arquitectura de ML no especificada en ningún documento fuente). |
