# Historias de Usuario — Módulo Motor de Análisis de Sentimiento (EPIC-SENT, Sprint 2)
 
**Proyecto:** HumWorld — Equipo 3
**Origen:** PDF de especificaciones (`0 PROYECTO_FINAL_HUMWORLD 260714.pdf`), secciones 4.2.2 (Diccionario de palabras evaluables), 4.2.4 (Procesado de la información), 10.2 (Endpoints mínimos obligatorios: `/dictionary`, `/sentiment`) y 10.4 (Posible algoritmo para cálculo del humor). Algoritmo de agregación decidido y justificado en `ADR-03-eleccion-algoritmo-agregacion-sentimiento.md`, conforme a la sección 11 de las instrucciones del proyecto.
**Estado general:** Propuesto — historias generadas a partir de los títulos ya oficializados en la hoja "Backlog" de `HumWorld_Anexo_I_Planificacion_actualizado.xlsx` (entregable P3) y de la estimación en puntos ya realizada en Planning Poker (P3, `Anexo-I-Planificacion-entregado-P3.md`, Sprint 2 = 18 puntos). Pendiente de revisión crítica del equipo antes de iniciar Sprint 2.
**Versión del documento:** v1.5. Ver la Tabla de control de versiones al final del documento para el historial completo.
 
> **Nota de grounding general:** el PDF exige un algoritmo de análisis de sentimiento "basado en diccionario, LLM u otro método justificado" (Objetivos específicos, punto 2) y ofrece un algoritmo posible (§10.4) como referencia no vinculante ("Esta es solo una posible solución. Cada equipo puede determinar otra manera"). El backlog ya oficializado por el equipo (hoja Excel) eligió un enfoque **híbrido diccionario + ML** (HU-SENT-002-v2, HU-SENT-006, HU-SENT-007). Este documento formaliza esa elección ya tomada por el equipo; no la introduce de nuevo. La parte de diccionario está completamente grounded en el PDF y en la sección 11 de las instrucciones del proyecto (ver `ADR-03-eleccion-algoritmo-agregacion-sentimiento.md`); la parte de ML no estaba especificada en ningún documento fuente más allá del título de la historia — el equipo definió esa arquitectura, documentada en `ADR-04-arquitectura-modelo-ml-sentimiento.md`.
 
---
 
## HU-SENT-001 — Gestión CRUD del diccionario de términos
 
**Tipo:** Historia de Usuario
**Como** administrador del sistema,
**quiero** dar de alta, consultar, modificar y eliminar términos del diccionario de sentimiento (palabra, idioma, valor numérico),
**para** mantener actualizado el vocabulario que el sistema usa para calcular el humor de las noticias.
 
**Prioridad:** Alta
**Estimación (Planning Poker P3):** 5 puntos *(ya estimado formalmente en el Planning Poker de la Práctica P3 — ver `Anexo-I-Planificacion-entregado-P3.md`; no es un valor definitivo si el alcance cambia, debe revalidarse con el equipo)*
**Depende de contrato de API:** Sí — `GET /api/v1/dictionary`, `GET /api/v1/dictionary/{id}`, `POST /api/v1/dictionary`, `PUT /api/v1/dictionary/{id}`, `PATCH /api/v1/dictionary/{id}`, `DELETE /api/v1/dictionary/{id}` — ver `contrato-sentimiento-diccionario.openapi.yaml`, tag `dictionary`
 
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
**Estimación (Planning Poker P3):** 5 puntos *(ya estimado en P3; dado que el alcance se detalló después con mayor profundidad, el equipo debería revalidar si 5 puntos sigue siendo representativo)*
**Depende de contrato de API:** No expone endpoint propio — es un servicio interno, disparado automáticamente tras cada captura exitosa de una noticia (ver HU-RSS-006/HU-RSS-008, `captura_service.py`).
 
**Mecanismo de disparo:** síncrono, con un timeout explícito sobre la llamada al modelo de ML y fallback automático al método de diccionario (HU-SENT-007) si se excede ese timeout — reutilizando el mismo patrón de resiliencia ya exigido como regla para las fuentes RSS en `docs/architecture.md`, sección 8 (Timeout explícito, sección 13 de las instrucciones del proyecto). Si el modelo de ML no responde a tiempo, el sistema no espera más y cae automáticamente al diccionario, que es instantáneo, garantizando que la captura nunca queda bloqueada esperando indefinidamente a un modelo de ML lento.
 
Como red de seguridad adicional, se reutiliza el mismo scheduler interno ya usado por EPIC-RSS (`APScheduler`/`AsyncIOScheduler`) para un job de barrido que recorre periódicamente las noticias con `valor_humor IS NULL` y les calcula el humor, cubriendo cualquier noticia que haya quedado sin valor por una causa no capturada por el fallback anterior (p. ej. un reinicio del sistema a mitad de cálculo). No requiere tabla de estado de trabajos ni endpoint nuevo: `valor_humor = NULL` (ya definido en HU-SENT-003) funciona como el indicador de "pendiente de cálculo". Se evaluó y descartó una cola de mensajes real (Celery/RQ + Redis/RabbitMQ) por el mismo motivo que ya se descartó para la captura RSS (criterio de proporcionalidad recogido en `docs/architecture.md`): introduce infraestructura no contemplada en el stack del proyecto (sección 8 de las instrucciones), un contenedor Docker adicional, una tabla de estado de trabajos y un endpoint nuevo de consulta de estado — sobre-ingeniería no justificada para el alcance de un prototipo de curso.
 
Con la arquitectura de `HU-SENT-006` ya definida (`ADR-04-arquitectura-modelo-ml-sentimiento.md`), el camino de ML de esta historia llama a un servicio externo real en cada cálculo: antes de usar el regresor propio, el sistema debe generar el vector de embeddings de la noticia llamando a la API de Google Gemini Embedding. El Timeout explícito y el fallback a diccionario descritos arriba son, por lo tanto, el mecanismo que efectivamente protege cada captura de la latencia y disponibilidad de ese servicio externo, aplicando los mismos patrones de resiliencia (Timeout, Retry acotado, Circuit Breaker) evaluados en detalle en `ADR-04`, sección "Patrones de resiliencia".
 
**Valores propuestos, pendientes de validación del equipo** (heurísticas de ingeniería general, no cifras tomadas del PDF — deben ajustarse con mediciones reales una vez integrado el servicio):
- Timeout de la llamada a Google Gemini Embedding: **3 segundos**.
- Periodicidad del job de barrido: **cada 30 minutos**.
### Criterios de aceptación (Gherkin)
 
```gherkin
Escenario: Cálculo con modelo de ML disponible
  Dado que existe un modelo de ML entrenado y versionado (ver HU-SENT-006)
  Cuando se captura una noticia nueva
  Entonces el sistema calcula su valor de humor usando ese modelo, dentro del timeout configurado
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
 
Escenario: Timeout excedido durante el cálculo con ML
  Dado que existe un modelo de ML disponible pero no responde dentro del timeout configurado
  Cuando el sistema intenta calcular el humor de una noticia con ese modelo
  Entonces el sistema no espera más allá del timeout configurado
  Y recae automáticamente en el método de diccionario para esa noticia, igual que en un fallo explícito
  Y el incidente (timeout excedido) queda registrado en el log del sistema
 
Escenario: Barrido de respaldo sobre noticias sin humor calculado
  Dado que existe al menos 1 noticia con valor_humor = NULL desde hace más tiempo del esperado (p. ej. por un reinicio del sistema durante el cálculo)
  Cuando se ejecuta el job periódico de barrido
  Entonces el sistema calcula y persiste el humor de esa noticia (usando ML si está disponible, o diccionario en caso contrario)
  Y ninguna noticia queda con valor_humor = NULL de forma indefinida por esta causa
```
 
**Nota de grounding (secuencia diccionario → ML):** la secuencia "diccionario primero, ML después" está grounded en la propia planificación oficial de Sprint 2 a 5 (`Anexo-I-Planificacion-entregado-P3.md` / hoja Historias-Estimacion): HU-SENT-006 (entrenamiento del modelo) recién se ubica en Sprint 4 "con data ya acumulada", y Sprint 5 registra explícitamente "cierre de HU-SENT-002-v2 (activar camino del modelo)" — confirmando que el camino de diccionario es el que se activa primero (Sprint 2) y el camino ML se activa más tarde, no al revés.
 
### Definition of Done
(Bloque general DoD, sección 14.) Adicionalmente:
- Pruebas unitarias del mecanismo de fallback con el modelo de ML **mockeado** (nunca cargar un modelo real en pruebas unitarias) — incluye el caso de fallo forzado del mock y el caso de timeout forzado (mock que no responde dentro del plazo simulado).
- Prueba de que, con el modelo de ML deshabilitado/ausente (estado esperado hasta Sprint 4), el 100% de las noticias capturadas terminan con un `metodo_calculo` registrado (diccionario o ml), nunca vacío.
- Prueba del job de barrido: dado un fixture con noticias `valor_humor = NULL`, tras ejecutar el job todas quedan con un valor calculado (mock del método de cálculo, sin llamadas reales).
---
 
## HU-SENT-003 — Persistencia del resultado de humor y polarización
 
**Tipo:** Historia Técnica / Enabler Story *(el actor es el propio sistema)*
**Como** sistema HumWorld,
**quiero** persistir el valor de humor calculado y un indicador de polarización junto a cada noticia,
**para** que ambos valores estén disponibles para consultas agregadas y dashboards sin tener que recalcularlos en cada lectura.
 
**Prioridad:** Alta
**Estimación (Planning Poker P3):** 3 puntos
**Depende de contrato de API:** No expone endpoint propio — extiende el modelo de datos `Noticia` ya definido en `diagrama-clases.md` (EPIC-RSS). El campo `valor_humor` (float, nullable) **ya existe** en ese diagrama, dejado explícitamente reservado para este módulo. **Pendiente:** agregar un nuevo campo para el indicador de polarización (nombre y tipo de dato a definir — ver `ADR-03-eleccion-algoritmo-agregacion-sentimiento.md`, que propone `polarizacion_terminos` como desviación estándar de los términos coincidentes) y actualizar `diagrama-clases.md` en consecuencia.
 
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
 
**Nota de uso adicional:** `valor_humor = NULL` no solo representa "noticia sin términos evaluables" (este escenario) — también se usa como indicador de "pendiente de cálculo" para el job de barrido de respaldo definido en HU-SENT-002-v2. Ambos casos son indistinguibles a nivel de dato (`NULL`); si en el futuro el equipo necesita diferenciarlos, requeriría un campo adicional de estado — no contemplado por ahora, para no sobre-diseñar sin una necesidad concreta identificada.
 
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
**Depende de contrato de API:** Sí — `GET /api/v1/sentiment` con parámetros de query `continente`, `pais`, `desde`, `hasta` (PDF, §10.2: "GET (global, por continente, por país, timeline, detalle noticia)") — ver `contrato-sentimiento-diccionario.openapi.yaml`, tag `sentiment`
 
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
 
**Nota de grounding:** esta historia reutiliza el modelo `CanalNoticias.continente`/`CanalNoticias.pais` ya definido en EPIC-RSS (`ADR-02-relacion-composicion-canal-fuente.md`) en vez de duplicar esos campos en `Noticia` — la agregación por continente/país se resuelve mediante el join `Noticia → FuenteRSS → CanalNoticias` ya existente.
 
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
**Depende de contrato de API:** Sí — `POST /api/v1/sentiment` con body `{"texto": "..."}` (PDF, §10.2: "POST (para analizar un texto en concreto, devuelve su valor de humor)") — ver `contrato-sentimiento-diccionario.openapi.yaml`, tag `sentiment` (comparte tag con HU-SENT-004)
 
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
 
**Tipo:** Historia de Usuario *(el entrenamiento se dispara manualmente por el administrador del sistema, no automáticamente — por lo que no se clasifica como Enabler Story, mismo criterio aplicado en HU-RSS-009)*
**Como** administrador del sistema,
**quiero** disparar manualmente el entrenamiento de una nueva versión del modelo de aprendizaje automático para el cálculo de humor, usando como datos de entrenamiento el histórico de noticias ya evaluadas por el método de diccionario,
**para** mejorar progresivamente la precisión del cálculo de humor más allá del método determinista de diccionario (HU-SENT-007), cuando el equipo considere que hay suficientes datos acumulados.
 
**Prioridad:** Media
**Estimación (Planning Poker P3):** 5 puntos *(estimado en P3 antes de que existiera este detalle — con la arquitectura ya resuelta, el equipo debería revalidar este número con Planning Poker real; sigue siendo un punto de partida, no un valor definitivo)*
**Depende de contrato de API:** Sí — `POST /api/v1/trainings` (sustantivo en plural sin verbo en la URL, sección 6 de las instrucciones del proyecto) — ver `contrato-sentimiento-diccionario.openapi.yaml`, tag `trainings`
 
La arquitectura del modelo de ML está definida en `ADR-04-arquitectura-modelo-ml-sentimiento.md`, que incluye el detalle completo de las alternativas evaluadas y sus trade-offs. En resumen:
 
- **Tipo de modelo y features:** embeddings externos + regresor propio entrenado localmente. El texto de cada noticia (título + contenido) se convierte en un vector numérico llamando a la API de Google Gemini Embedding (servicio externo); con esos vectores como entrada, se entrena localmente un regresor de `scikit-learn` (p. ej. `Ridge`) que predice `valor_humor` (-10 a +10). El modelo entrenado es un artefacto propio del equipo — coherente con el título "entrenamiento y versionado" de esta historia — no una llamada directa a un LLM en cada noticia.
- **Proveedor de embeddings:** Google Gemini Embedding, elegido por tener free tier permanente sin tarjeta de crédito (1.500 solicitudes/día, 10M tokens/min), a diferencia de OpenAI (crédito gratis que expira a los 3 meses) o Cohere (solo crédito de prueba). Verificado por búsqueda web — las condiciones de cuota/precio deben reconfirmarse antes de implementar, ya que pueden cambiar con el tiempo.
- **Mecanismo de disparo:** manual, vía `POST /api/v1/trainings` — el administrador decide cuándo reentrenar, evitando entrenamientos automáticos innecesarios o en mal momento.
- **Umbral mínimo de datos:** parámetro configurable del sistema. **Valor propuesto, pendiente de validación del equipo: 1.000 noticias evaluadas por diccionario** — con la estimación de ~50 fuentes RSS activas y un volumen típico de 500-1.000 noticias/día para ese número de fuentes, este umbral se alcanzaría en menos de una semana de captura real (ver `ADR-04` para la justificación completa).
- **Versionado:** tabla de metadatos en MySQL (`modelos_sentimiento`: id, versión/timestamp, ruta del archivo del regresor serializado, nombre y versión del modelo de embeddings usado al entrenar, métricas de evaluación, fecha de entrenamiento, `activo` booleano) + el archivo del regresor entrenado (`.joblib`) en disco/volumen Docker.
- **Criterio de evaluación:** comparación contra el método de diccionario (HU-SENT-007) en un conjunto de validación, usando **MAE** (error absoluto medio) como métrica. Limitación metodológica documentada en `ADR-04`: el diccionario es la única referencia de verdad disponible (no hay etiquetado humano de noticias en este proyecto), por lo que el modelo, en el mejor de los casos, aprende a generalizar el mismo tipo de señal que el diccionario — no puede conceptualmente "superarlo" con este criterio de evaluación.
- **Patrones de resiliencia:** al depender de un servicio externo real (Google Gemini Embedding), aplican Timeout explícito, Retry acotado con backoff exponencial y Circuit Breaker — evaluados en detalle en `ADR-04`, reutilizando los mismos patrones ya exigidos como regla para las fuentes RSS en `docs/architecture.md`, sección 8.
### Criterios de aceptación (Gherkin)
 
```gherkin
Escenario: Entrenamiento exitoso con datos suficientes
  Dado que existe un volumen mínimo de noticias ya evaluadas por el método de diccionario (umbral configurable — valor propuesto: 1.000 noticias, pendiente de validación por el equipo)
  Cuando el administrador envía POST a /api/v1/trainings
  Entonces el sistema responde con código HTTP 201
  Y el sistema genera los embeddings de las noticias de entrenamiento (Google Gemini Embedding), entrena el regresor localmente y genera una nueva versión del modelo
  Y esa versión queda registrada en la tabla de metadatos con un identificador único, la fecha de entrenamiento y las métricas de evaluación (MAE contra diccionario)
 
Escenario: Entrenamiento con datos insuficientes
  Dado que el volumen de noticias evaluadas no alcanza el umbral mínimo configurado
  Cuando el administrador envía POST a /api/v1/trainings
  Entonces el sistema responde con código HTTP 409
  Y el modelo de ML activo (si existe una versión previa) no se ve afectado
 
Escenario: Fallo del servicio externo de embeddings durante el entrenamiento
  Dado que el servicio de Google Gemini Embedding no responde o falla durante el proceso de entrenamiento
  Cuando el sistema intenta generar los vectores de embeddings para el conjunto de entrenamiento
  Entonces el sistema aplica Retry acotado con backoff exponencial (ver ADR-04)
  Y si el fallo persiste tras agotar los reintentos, el entrenamiento se cancela sin afectar el modelo activo previo
  Y el sistema responde con un código de error apropiado (p. ej. 502 o 503) indicando que el entrenamiento no pudo completarse
  Y el incidente queda registrado en el log del sistema
```
 
**Nota de grounding:** el PDF no exige ni describe un modelo de ML en ningún punto; solo lo permite como una de las opciones válidas para el algoritmo de sentimiento ("basado en diccionario, LLM u otro método justificado", Objetivos específicos punto 2). La arquitectura completa de esta historia fue decidida por el equipo, con el detalle completo de alternativas evaluadas y trade-offs en `ADR-04-arquitectura-modelo-ml-sentimiento.md`.
 
### Definition of Done
(Bloque general DoD, sección 14.) Adicionalmente:
- Pruebas unitarias del entrenamiento usando un dataset de fixture pequeño y determinista, con el servicio de embeddings **mockeado** (nunca llamadas reales a Google Gemini Embedding ni entrenamiento con datos reales de producción en el pipeline de CI) — incluye el caso de fallo/timeout del servicio de embeddings mockeado.
- Documentación del criterio de evaluación (MAE contra diccionario) y de su limitación metodológica en el resultado de cada entrenamiento.
- Prueba de que un entrenamiento con datos insuficientes no afecta al modelo activo previo.
---
 
## HU-SENT-007 — Fallback determinista con diccionario
 
**Tipo:** Historia Técnica / Enabler Story *(el actor es el propio sistema)*
**Como** sistema HumWorld,
**quiero** calcular el humor de una noticia mediante el método determinista de diccionario — promedio simple de los valores de los términos evaluables coincidentes, más un indicador de polarización — según lo definido en `ADR-03-eleccion-algoritmo-agregacion-sentimiento.md`,
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
 
Escenario: Término que aparece más de una vez en el mismo texto
  Dado que el diccionario contiene el término "crisis" con valor -6
  Y una noticia cuyo texto contiene la palabra "crisis" tres veces y ningún otro término evaluable
  Cuando el sistema calcula su humor
  Entonces el término "crisis" se cuenta una única vez para el promedio (n=1), no tres
  Y valor_humor = -6.0 (no se pondera por la cantidad de apariciones en el texto)
```
 
**Nota de grounding (algoritmo):** la fórmula (promedio simple, no suma) y el indicador complementario de polarización (desviación estándar) están decididos y justificados en detalle en `ADR-03-eleccion-algoritmo-agregacion-sentimiento.md`, conforme a la sección 11 de las instrucciones del proyecto.
 
**Divisor "n" del promedio:** `n` cuenta **términos únicos distintos** del diccionario que aparecen en el texto, no cada aparición individual. Justificación: contar apariciones repetidas dejaría que una noticia que menciona muchas veces la misma palabra (algo común por estilo de redacción periodística, no necesariamente porque el evento sea más intenso) pesara desproporcionadamente en el promedio, distorsionando el resultado por frecuencia de mención en vez de por contenido real evaluado.
 
### Definition of Done
(Bloque general DoD, sección 14.) Adicionalmente:
- Prueba unitaria que reproduce exactamente el escenario numérico documentado (valor_humor=-1.0, polarizacion_terminos=7.0) — determinista, sin mocks de red ni de modelo ML, 100% verificable.
- Prueba del caso de cero términos coincidentes (valor_humor=NULL).
- Prueba del caso de término repetido varias veces en el mismo texto (ver Escenario 4): confirma que se cuenta como término único (n=1), no por cantidad de apariciones.
---
 
## Resumen de trazabilidad
 
| ID | Tipo | Prioridad | Puntos (P3) | Endpoint / mecanismo | Referencia PDF |
|---|---|---|---|---|---|
| HU-SENT-001 | Historia de Usuario | Alta | 5 | `/api/v1/dictionary` (CRUD) — ver `contrato-sentimiento-diccionario.openapi.yaml` | §4.2.2, §10.2 |
| HU-SENT-002-v2 | Enabler Story | Alta | 5 | Interno — síncrono + Timeout explícito (propuesto: 3s) + fallback a diccionario + job de barrido de respaldo (propuesto: cada 30 min) | §4.2.4, Objetivos específicos #2 |
| HU-SENT-003 | Enabler Story | Alta | 3 | Extiende modelo `Noticia` | §4.2.4 |
| HU-SENT-004 | Historia de Usuario | Alta | 1 | `GET /api/v1/sentiment` — ver `contrato-sentimiento-diccionario.openapi.yaml` | §4.1, §10.2 |
| HU-SENT-005 | Historia de Usuario | Media | 2 | `POST /api/v1/sentiment` — ver `contrato-sentimiento-diccionario.openapi.yaml` | §10.2 |
| HU-SENT-006 | Historia de Usuario | Media | 5 | `POST /api/v1/trainings` — ver `contrato-sentimiento-diccionario.openapi.yaml` — embeddings externos (Google Gemini Embedding) + regresor local scikit-learn, disparo manual, umbral propuesto: 1.000 noticias (ver ADR-04) | Objetivos específicos #2 (no detallado) |
| HU-SENT-007 | Enabler Story | Alta | 2 | Interno (servicio compartido) — n = términos únicos | §10.4, sección 11 instrucciones proyecto |
 
## Tabla de control de versiones
 
| ID | Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|---|
| HU-SENT-001 a 007 | v1.0 | 2026-09-28 | Primera formalización detallada de las 7 historias de EPIC-SENT, a partir de los títulos ya oficializados en la hoja Backlog del Excel y de la estimación ya realizada en Planning Poker de P3. Se agregan Gherkin, DoD, contrato de API propuesto y notas de grounding para cada una. Se identifican y documentan explícitamente los puntos pendientes de decisión del equipo, en particular para HU-SENT-002-v2 y, sobre todo, HU-SENT-006 (arquitectura de ML no especificada en ningún documento fuente). |
| HU-SENT-002-v2, HU-SENT-007 | v1.1 | 2026-09-28 (segunda sesión del día) | Se cierran 2 de los puntos pendientes de v1.0: **HU-SENT-002-v2** queda con mecanismo de disparo confirmado (síncrono + Timeout explícito con fallback automático a diccionario + job de barrido de respaldo, reutilizando el scheduler ya usado por EPIC-RSS, sin infraestructura de cola de mensajes nueva) y nuevos escenarios Gherkin de timeout y de barrido; **HU-SENT-007** queda con el divisor "n" del promedio confirmado como términos únicos distintos, con nuevo escenario Gherkin de término repetido. HU-SENT-006 queda explícitamente fuera de esta sesión de cierre — sus 7 puntos abiertos requieren su propio ADR. |
| HU-SENT-006, HU-SENT-002-v2 | v1.2 | 2026-09-28 (tercera sesión del día) | Se cierra el último punto pendiente de EPIC-SENT: **HU-SENT-006** queda completamente resuelta en sesión de trabajo dedicada — se reclasifica de Enabler Story a Historia de Usuario (actor = administrador, disparo manual), se define el contrato `POST /api/v1/trainings`, y se documentan las 7 decisiones de arquitectura del modelo de ML (embeddings externos vía Google Gemini Embedding + regresor local scikit-learn, umbral de datos configurable, versionado en MySQL, evaluación por MAE contra diccionario, patrones de resiliencia) en el nuevo `ADR-04-arquitectura-modelo-ml-sentimiento.md`, con sus alternativas y trade-offs. Se actualiza **HU-SENT-002-v2** en consecuencia: el camino de ML ahora invoca un servicio externo real, por lo que el Timeout/fallback ya definido en v1.1 pasa de ser una salvaguarda preventiva a ser el mecanismo de protección efectivo. Con esto, las 7 historias de EPIC-SENT quedan sin puntos de decisión arquitectónica abiertos (quedan solo parámetros de configuración a fijar con datos reales: timeout exacto, periodicidad del barrido, umbral mínimo de entrenamiento). |
| HU-SENT-002-v2, HU-SENT-006 | v1.3 | 2026-09-28 (cuarta sesión del día) | Se fijan **valores propuestos** (no definitivos) para los 3 parámetros de configuración que quedaban abiertos desde v1.2, a partir de la estimación del equipo de ~50 fuentes RSS activas y de heurísticas generales de ingeniería (no de ningún dato del PDF): **HU-SENT-002-v2** → timeout de la llamada a Google Gemini Embedding = 3 segundos, periodicidad del job de barrido = cada 30 minutos; **HU-SENT-006** → umbral mínimo de entrenamiento = 1.000 noticias evaluadas por diccionario. Los tres valores quedan pendientes de ratificación por el equipo, con el mismo tratamiento que una estimación de Planning Poker (punto de partida, no valor definitivo). Actualizados en espejo en `ADR-04-arquitectura-modelo-ml-sentimiento.md` (v1.1) y `HU-RSS-captura.md` (v1.9, periodicidad del cron de captura). |
| Todas (HU-SENT-002-v2, HU-SENT-003, HU-SENT-006, HU-SENT-007) | v1.4 (editorial) | 2026-09-29 | Limpieza editorial: se retiran los bloques de comentario en formato cita ("— CONFIRMADO/A (decisión del equipo, sesión...)", "Valores propuestos (PO/Arquitecto, sesión..., pendientes de ratificación)", "Actualización (sesión...)") y se integra su contenido técnico como texto normal del documento, sin narrar el proceso de decisión turno a turno. No cambia ninguna decisión, valor propuesto, criterio de aceptación ni alcance — solo la forma en que se presenta. El historial de sesiones/fechas queda concentrado en esta tabla, que es donde la sección 3 de las instrucciones del proyecto exige la trazabilidad. |
| HU-SENT-001, HU-SENT-004, HU-SENT-005, HU-SENT-006 | v1.5 | 2026-09-29 | Se crea `contrato-sentimiento-diccionario.openapi.yaml` (v1.0.0), el primer contrato OpenSpec de EPIC-SENT. Se actualizan los campos "Depende de contrato de API" de estas 4 historias y la tabla de "Resumen de trazabilidad", que dejan de decir "recurso nuevo, no existe todavía en ningún contrato" y pasan a referenciar el contrato ya creado. Sin cambios en el alcance, los criterios de aceptación ni los valores propuestos de ninguna historia. |
