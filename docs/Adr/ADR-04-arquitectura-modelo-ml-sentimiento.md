# ADR-04: Arquitectura del modelo de Machine Learning para el cálculo de humor
 
**Proyecto:** HumWorld — Equipo 3
**Fecha de creación:** 2026-09-28
**Versión del documento:** v1.1 — historial completo en "Historial de revisión de este ADR", al final del documento.
 
---
 
## Estado
 
**Aceptado.**
 
---
 
## Contexto
 
### 1. Origen y por qué este ADR existe
 
El PDF de especificaciones (`0 PROYECTO_FINAL_HUMWORLD 260714.pdf`) exige, en sus Objetivos específicos, un algoritmo de análisis de sentimiento "basado en diccionario, LLM u otro método justificado", dejando expresamente abierta la puerta a un enfoque de Machine Learning como alternativa o complemento al método de diccionario. El backlog ya oficializado por el equipo (hoja "Backlog" del Excel de planificación, entregable P3) incorporó esta posibilidad formalizando dos historias distintas: `HU-SENT-007` (método determinista de diccionario, ya resuelto y documentado en `ADR-03-eleccion-algoritmo-agregacion-sentimiento.md`) y `HU-SENT-006` ("Entrenamiento y versionado del modelo de ML"), cuyo título fue estimado en Planning Poker de P3 (5 puntos) pero **sin que ningún documento fuente especificara la arquitectura concreta del modelo**.
 
Al momento de la sesión de cierre del backlog RSS/SENT del 2026-09-28 (documento de reconciliación de backlog — **referencia pendiente de confirmar por el equipo:** el archivo citado no se encuentra en el repositorio), se identificaron 7 puntos de arquitectura completamente abiertos en `HU-SENT-006`:
 
1. Tipo de modelo y de features a utilizar.
2. Proveedor o mecanismo concreto para obtener esas features (si aplica un servicio externo).
3. Mecanismo de disparo del entrenamiento (manual vs. automático).
4. Umbral mínimo de datos de entrenamiento.
5. Esquema de versionado de los modelos entrenados.
6. Criterio de evaluación de la calidad del modelo.
7. Necesidad (o no) de patrones de resiliencia, dado que podría involucrar un servicio externo.
Dado el volumen y la profundidad de estas decisiones, el equipo decidió explícitamente **no resolverlas mediante preguntas rápidas** (como sí se hizo con puntos más acotados de `HU-SENT-002-v2` y `HU-SENT-007` en la sesión anterior del mismo día), sino dedicar una sesión de trabajo específica, con su propio ADR — precisamente la que da origen a este documento.
 
### 2. Restricciones reales del proyecto
 
* **Curso académico y plazos:** este es un proyecto de la asignatura "Tópico IA en Ingeniería de Software" (Universidad Andrés Bello), desarrollado por un equipo de estudiantes de últimos años de Ingeniería Civil Informática, con entregas por sprint dentro de un semestre académico — no un proyecto comercial con presupuesto ni con tiempo abierto para investigación extensa. Esto descarta de entrada cualquier alternativa que requiera presupuesto (tarjetas de crédito, planes pagos de APIs) o infraestructura de cómputo especializada (entrenamiento de modelos propios de gran escala, GPUs dedicadas).
* **Stack ya definido (sección 8 de las instrucciones del proyecto):** arquitectura distribuida/en capas con API REST documentada en Swagger/OpenAPI, MySQL como base de datos relacional principal, Docker (o entornos virtuales del IDE) para despliegue, GitHub Actions para CI/CD con `needs` entre jobs, SonarQube para calidad. Cualquier tecnología nueva debe encajar en este stack o justificarse explícitamente si lo excede.
* **Precedente directo:** el módulo de captura RSS ya evaluó y rechazó infraestructura de colas de mensajes (Celery/RQ + Redis/RabbitMQ) para la captura RSS, por representar sobre-ingeniería para el alcance de un prototipo de curso (criterio de proporcionalidad recogido como regla en `docs/architecture.md`). Ese mismo criterio se aplica aquí.
* **Ausencia de etiquetado humano:** el proyecto no cuenta con un dataset de noticias etiquetadas manualmente por humanos con su "verdadero" valor de humor. La única fuente de verdad disponible es el propio método de diccionario (`HU-SENT-007`), ya que es determinista y siempre calculable. Esta restricción condiciona directamente el punto 6 (criterio de evaluación) de la Decisión, más abajo.
* **Planificación de sprints ya oficializada (`Anexo-I-Planificacion-entregado-P3.md`):** `HU-SENT-006` se ubica en Sprint 4 ("con data ya acumulada") y Sprint 5 registra el "cierre de HU-SENT-002-v2 (activar camino del modelo)". Esto confirma que el camino de diccionario se activa primero (Sprint 2) y que hay una ventana de tiempo — Sprints 2 y 3 — durante la cual se acumulan noticias evaluadas por diccionario, que son precisamente los datos de entrenamiento del modelo de ML.
* **Historias ya resueltas de las que este ADR depende:** `HU-SENT-002-v2` (mecanismo de cálculo híbrido, con Timeout + fallback a diccionario ya definidos en sesión anterior del mismo día) y `HU-SENT-007` (método de diccionario, fuente de los datos de entrenamiento y de la referencia de evaluación).
---
 
## Decisión
 
Se decide una arquitectura de **embeddings externos + regresor local entrenado por el equipo**, con disparo manual, versionado en MySQL, evaluación por MAE contra el método de diccionario, y aplicación explícita de los patrones de resiliencia ya exigidos como regla para las fuentes RSS en `docs/architecture.md`, sección 8. El detalle de cada punto:
 
### 1. Tipo de modelo y features
 
El texto de cada noticia (título + contenido) se convierte en un **vector de embeddings** (representación numérica densa del significado semántico del texto) mediante una llamada a un servicio externo de embeddings. Ese vector se usa como conjunto de features de entrada para entrenar, **localmente y con librerías del propio proyecto**, un modelo de regresión de `scikit-learn` (candidato inicial: `Ridge`, por ser una regresión lineal regularizada, rápida de entrenar y sin dependencias adicionales de infraestructura) que predice `valor_humor` en la escala -10 a +10 ya definida en `ADR-03`.
 
Esta decisión es deliberada frente a la alternativa de usar un LLM como "juez" directo en cada noticia (ver Alternativa B más abajo): aquí el artefacto que se entrena y versiona es un modelo propio del equipo (el regresor), coherente con el título literal de la historia — "Entrenamiento **y versionado** del modelo de ML" — mientras que un LLM-como-juez no involucra ningún entrenamiento ni versionado real por parte del equipo, solo llamadas a un modelo ya entrenado por un tercero.
 
### 2. Proveedor de embeddings
 
Se elige **Google Gemini Embedding** como proveedor del servicio externo de generación de embeddings, por ofrecer un **free tier permanente sin necesidad de tarjeta de crédito** (1.500 solicitudes/día, 10.000.000 de tokens/minuto), condición decisiva dado que el equipo no cuenta con presupuesto para este proyecto de curso. Esta información fue verificada mediante búsqueda web el 2026-09-28; **debe reconfirmarse por el equipo antes de la implementación real**, ya que las condiciones de cuota y precio de APIs externas pueden cambiar con el tiempo y esta verificación tiene fecha de vencimiento implícita. El equipo es responsable de crear su propia cuenta y gestionar sus propias credenciales de API — el agente PO/Arquitecto no crea cuentas ni maneja credenciales por política de seguridad.
 
### 3. Mecanismo de disparo del entrenamiento
 
**Manual**, mediante el nuevo endpoint `POST /api/v1/trainings`. El administrador del sistema decide cuándo reentrenar el modelo, en vez de que el sistema lo dispare automáticamente por una condición (p. ej. cada N noticias nuevas). Esto evita entrenamientos automáticos en momentos inoportunos (p. ej. durante una ventana de mantenimiento) o con datos todavía insuficientes, y mantiene el control del proceso en manos de una persona — coherente con la naturaleza poco frecuente de un reentrenamiento (a diferencia del cálculo de humor por noticia, que sí es de alta frecuencia y por tanto automático). Esta decisión reclasifica `HU-SENT-006` de "Historia Técnica/Enabler Story" a **Historia de Usuario clásica**, ya que el actor pasa a ser el administrador del sistema (persona), no un proceso automatizado — mismo criterio de clasificación ya aplicado previamente a `HU-RSS-009`.
 
### 4. Umbral mínimo de datos de entrenamiento
 
Se mantiene como **parámetro configurable del sistema** (no una cifra hardcodeada), y se fija un **valor propuesto, pendiente de ratificación formal del equipo**: **1.000 noticias evaluadas por diccionario.**
 
**Justificación del valor propuesto:** el equipo estimó ~50 fuentes RSS activas (ver `HU-RSS-009`). Con un volumen típico de 500-1.000 noticias/día para ese número de fuentes — heurística general de publicación de feeds de noticias, no un dato extraído del PDF ni de ningún documento fuente del proyecto —, el umbral de 1.000 noticias se alcanzaría en menos de una semana de captura real. Esto deja margen técnico de sobra: un regresor `Ridge` regularizado sobre embeddings no requiere mucho más que unos cientos de ejemplos para tener una base razonable, por lo que 1.000 prioriza además la **diversidad temporal/temática** (varios días de captura, no solo una ráfaga inicial) por sobre el volumen puro, sin obligar a esperar hasta el límite de Sprint 3 para el primer entrenamiento de prueba.
 
**Esta cifra no reemplaza la validación del equipo** — sigue el mismo criterio de "Auditoría de estimaciones" (sección 7 de las instrucciones del proyecto) que las estimaciones de Planning Poker: es un punto de partida justificado, no un valor definitivo. Debe confirmarse o ajustarse con el volumen real observado durante los Sprints 2-3, antes de que `HU-SENT-006` se implemente en Sprint 4. Mismo criterio de proporcionalidad ya usado para la periodicidad del cron de captura en `HU-RSS-007` y para el timeout de `HU-SENT-002-v2` (ver punto 7, más abajo).
 
### 5. Esquema de versionado de modelos
 
Se define una tabla de metadatos en MySQL, `modelos_sentimiento`, con (al menos) los siguientes campos:
 
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | INT / BIGINT, PK | Identificador único de la versión del modelo |
| `version` | VARCHAR o TIMESTAMP | Identificador de versión (puede ser el propio timestamp de entrenamiento) |
| `ruta_archivo` | VARCHAR | Ruta al archivo serializado del regresor (`.joblib`) en disco/volumen Docker |
| `modelo_embeddings_usado` | VARCHAR | Nombre y versión del modelo de embeddings de Google usado al entrenar (crítico para detectar incompatibilidad si Google actualiza su modelo) |
| `mae_evaluacion` | FLOAT | Métrica de evaluación (ver punto 6) |
| `fecha_entrenamiento` | DATETIME | Fecha y hora del entrenamiento |
| `activo` | BOOLEAN | Indica si esta es la versión actualmente en uso por `HU-SENT-002-v2` |
 
El regresor entrenado en sí (el objeto `scikit-learn` serializado) se persiste como archivo `.joblib` en disco o en un volumen Docker — **no** en la base de datos relacional, que solo guarda la metadata y la ruta de acceso al archivo. Este esquema es deliberadamente simple (una tabla + archivos), evitando herramientas especializadas de MLOps (p. ej. MLflow, DVC) que excederían el alcance y el stack de un proyecto de curso sin presupuesto ni tiempo para su configuración.
 
### 6. Criterio de evaluación
 
Se evalúa cada modelo entrenado comparando sus predicciones contra los valores calculados por el método de diccionario (`HU-SENT-007`) sobre un conjunto de validación, usando **MAE (Mean Absolute Error / error absoluto medio)** como métrica.
 
**Limitación metodológica documentada explícitamente (no se oculta):** al no existir en este proyecto un conjunto de noticias con valor de humor etiquetado por humanos, el diccionario es la única referencia de "verdad" disponible. Esto implica que el modelo de ML, evaluado de esta manera, en el mejor de los casos aprende a **generalizar el mismo tipo de señal que ya captura el diccionario** — no puede, con este criterio de evaluación, demostrar que "supera" conceptualmente al diccionario en términos de precisión frente a un sentimiento humano real, solo puede demostrar que lo aproxima bien en casos no vistos directamente (generalización) y que puede capturar relaciones semánticas más ricas que un simple conteo de términos (p. ej. sarcasmo, contexto, sinónimos no presentes en el diccionario). El valor real de esta vía de ML no es "ser más preciso que el diccionario" sino **generalizar más allá del vocabulario explícito del diccionario**, algo que el MAE contra diccionario no mide directamente pero que sí es observable cualitativamente revisando casos de desacuerdo entre ambos métodos.
 
### 7. Patrones de resiliencia
 
Al depender de un servicio externo de terceros (Google Gemini Embedding) — con el mismo perfil de riesgo que las fuentes RSS externas (disponibilidad no garantizada, latencia variable, límites de cuota), para las que `docs/architecture.md` sección 8 ya exige resiliencia obligatoria — se evalúan explícitamente los 4 patrones de la sección 13 de las instrucciones del proyecto:
 
* **Timeout explícito:** **Aplica.** Toda llamada a la API de embeddings debe tener un timeout máximo configurado, para no dejar el proceso de entrenamiento (ni, en el camino de `HU-SENT-002-v2`, el cálculo de humor por noticia) esperando indefinidamente. **Valor propuesto (pendiente de ratificación por el equipo): 3 segundos.** Justificación: las llamadas a APIs de embeddings de texto corto suelen responder en menos de 1 segundo; 3 segundos da margen cómodo sin contradecir la prioridad explícita del equipo de que el modelo de ML no sea lento. No es una cifra tomada del PDF — debe ajustarse con mediciones reales (p50/p95/p99) de latencia una vez integrado el servicio, fijando el valor definitivo justo por encima del p95 observado.
* **Retry con backoff exponencial (acotado):** **Aplica.** Ante un fallo transitorio puntual (p. ej. un error 5xx momentáneo de la API), se reintenta un número acotado de veces con backoff exponencial — nunca reintento infinito. Si se agotan los reintentos, el entrenamiento se cancela limpiamente (ver escenario Gherkin en `HU-SENT-006`) sin afectar al modelo activo previo.
* **Circuit Breaker:** **Aplica, con matiz.** Es más relevante en el camino de `HU-SENT-002-v2` (llamadas de alta frecuencia, una por cada noticia capturada) que en el entrenamiento (`HU-SENT-006`, disparo manual, poco frecuente): si el servicio de embeddings empieza a fallar sistemáticamente, un Circuit Breaker evita que cada captura de noticia intente la llamada y bloquee hilos de ejecución esperando timeouts repetidos, "abriendo el circuito" tras un umbral de fallos y cayendo directamente al fallback de diccionario (ya definido en `HU-SENT-002-v2`) sin siquiera intentar la llamada externa durante la ventana en que el circuito está abierto.
* **Bulkhead:** **No se considera necesario para el alcance actual del prototipo.** Este patrón aísla recursos (p. ej. pools de conexión o hilos separados) para que el fallo de un servicio no consuma todos los recursos del sistema — relevante en sistemas con múltiples integraciones externas de alto volumen compitiendo por los mismos recursos. En el alcance actual, el único servicio externo de esta naturaleza es el propio Google Gemini Embedding (las fuentes RSS del módulo de captura son un conjunto de recursos distinto), por lo que no hay múltiples integraciones compitiendo entre sí que justifiquen el aislamiento adicional de Bulkhead. Si en una futura iteración se agregan más servicios externos de ML o de terceros, el equipo debería reevaluar este punto.
Estos patrones se reutilizan, en su diseño, de la misma regla de resiliencia ya exigida para las fuentes RSS en `docs/architecture.md`, sección 8 — no se introduce una librería o mecanismo distinto, manteniendo consistencia técnica en todo el sistema.
 
---
 
## Alternativas consideradas
 
### Alternativa A — Modelo 100% local (TF-IDF + regresor local, sin servicio externo)
 
Consiste en representar el texto de cada noticia mediante TF-IDF (Term Frequency-Inverse Document Frequency, una técnica clásica de NLP que pondera cada palabra por su frecuencia en el documento e inversamente por su frecuencia en el corpus completo) calculado enteramente en el propio backend, sin llamar a ningún servicio externo, y entrenar sobre esa representación el mismo tipo de regresor local (`scikit-learn`).
 
**Ventajas:** cero dependencia de servicios externos (elimina de raíz la necesidad de los patrones de resiliencia del punto 7), cero riesgo de cuota o costo, funcionamiento 100% determinista y reproducible, no requiere ninguna credencial ni cuenta de terceros.
 
**Desventajas:** TF-IDF es una representación puramente léxica (basada en las palabras exactas usadas) — no captura relaciones semánticas entre sinónimos, contexto o sarcasmo de la misma manera que una representación de embeddings entrenada sobre grandes volúmenes de texto. Esto significa que, en la práctica, un modelo TF-IDF + regresor local tiende a aprender una señal muy similar a la que ya captura el diccionario de términos (ambos dependen en el fondo de qué palabras exactas aparecen), limitando el valor agregado real de esta vía de ML frente a `HU-SENT-007`.
 
**Resultado:** **descartada.** El equipo, tras evaluar el trade-off, priorizó la mayor riqueza semántica de los embeddings frente a la simplicidad y el cero-riesgo de una solución 100% local, aceptando explícitamente introducir la dependencia externa y sus patrones de resiliencia asociados a cambio de un modelo con mayor potencial de generalización real.
 
### Alternativa B — LLM como juez directo (zero-shot, sin entrenamiento)
 
Consiste en enviar el texto de cada noticia directamente a un LLM (mediante prompt) pidiéndole que devuelva un valor de humor, sin entrenar ningún modelo propio — el "modelo" es efectivamente el LLM de terceros usado en modo zero-shot o few-shot.
 
**Ventajas:** implementación más simple en el corto plazo (no requiere pipeline de entrenamiento, ni almacenamiento de modelos versionados, ni conjunto de entrenamiento); potencialmente buena calidad de resultado sin necesidad de datos históricos.
 
**Desventajas:** no involucra ningún entrenamiento ni versionado real por parte del equipo, lo que **entra en conflicto directo con el título y el alcance literal de `HU-SENT-006`** ("Entrenamiento y versionado del modelo de ML") — de adoptarse, la historia debería reescribirse por completo (ya no habría nada que "entrenar" ni "versionar" en el sentido de un artefacto propio, solo una integración de API). Además, implica una llamada a un LLM en cada noticia procesada (si se usa también para el cálculo recurrente vía `HU-SENT-002-v2`), lo cual es más costoso y de mayor latencia por llamada que una llamada de embeddings + inferencia local liviana, especialmente relevante dado que la prioridad explícita del equipo para `HU-SENT-002-v2` es que "el modelo de ML no sea lento".
 
**Resultado:** **descartada.** Se evaluó explícitamente junto con el equipo y se rechazó principalmente por el cambio de alcance que implicaría en el título y la naturaleza de `HU-SENT-006`, y secundariamente por el mayor costo/latencia recurrente frente a la Alternativa elegida.
 
### Alternativa C — Otros proveedores de embeddings (OpenAI, Cohere)
 
Se evaluaron como proveedores alternativos del servicio externo de embeddings:
 
* **OpenAI (`text-embedding-3-*`):** ofrece crédito gratuito inicial para cuentas nuevas, pero ese crédito **expira a los 3 meses**, después de lo cual requiere ingresar un método de pago para continuar usando el servicio.
* **Cohere:** ofrece un tier de prueba (trial), también limitado en el tiempo/volumen, sin ser un free tier permanente equivalente al de Google.
**Resultado:** **descartadas.** Ninguna de las dos ofrece un free tier permanente sin tarjeta de crédito comparable al de Google Gemini Embedding, condición decisiva dado que el proyecto no cuenta con presupuesto y se extiende a lo largo de un semestre académico (más de 3 meses), superando la ventana de crédito gratuito de OpenAI.
 
### Alternativa D — Embeddings auto-hospedados (self-host), p. ej. `sentence-transformers`
 
Consiste en descargar y ejecutar localmente, dentro de la propia infraestructura del equipo (contenedor Docker), un modelo de embeddings open-source (p. ej. de la librería `sentence-transformers`), evitando así cualquier llamada a un servicio externo de terceros.
 
**Ventajas:** elimina la dependencia externa (y por tanto la necesidad de los patrones de resiliencia del punto 7, igual que la Alternativa A), sin las limitaciones semánticas de TF-IDF — un modelo de embeddings pre-entrenado captura relaciones semánticas ricas igual que uno externo tipo Google Gemini Embedding.
 
**Desventajas:** requiere empaquetar el modelo (varios cientos de MB a algunos GB según el modelo elegido) dentro de la imagen Docker o descargarlo en el arranque, con el consiguiente costo de tiempo de build/despliegue y espacio en disco; requiere cómputo local para la inferencia (CPU, potencialmente lento sin GPU) en cada llamada, lo cual entra en tensión directa con la prioridad explícita del equipo de que "el modelo de ML no sea lento"; añade complejidad de infraestructura (gestión de la descarga/versión del modelo local) no trivial para el tiempo disponible en un proyecto de curso.
 
**Resultado:** **alternativa intermedia, no elegida.** Habría evitado por completo la dependencia de un servicio externo de terceros (y, con ello, la necesidad de los patrones de resiliencia del punto 7), pero el equipo optó explícitamente por la vía externa (Google Gemini Embedding), priorizando evitar la complejidad de infraestructura y el riesgo de lentitud de la inferencia local, y aceptando a cambio gestionar la dependencia externa mediante los patrones de resiliencia ya exigidos como regla para las fuentes RSS en `docs/architecture.md`, sección 8.
 
---
 
## Consecuencias
 
### Positivas
 
* `HU-SENT-006` queda completamente desbloqueada arquitectónicamente: los 7 puntos que impedían su implementación quedan resueltos, permitiendo avanzar con el contrato de API (`POST /api/v1/trainings`), el modelo de datos (tabla `modelos_sentimiento`) y, eventualmente, el scaffolding de código correspondiente.
* Se mantiene consistencia técnica con la regla de resiliencia de `docs/architecture.md`, sección 8: los mismos patrones (Timeout, Retry acotado, Circuit Breaker) ya exigidos para las fuentes RSS se reutilizan en su diseño para un segundo servicio externo, en vez de introducir un mecanismo distinto — reduce la superficie de aprendizaje y mantenimiento para el equipo.
* El uso de un free tier permanente sin tarjeta de crédito (Google Gemini Embedding) mantiene el proyecto dentro de la restricción de "sin presupuesto" propia de un curso académico.
* El esquema de versionado (tabla MySQL + archivo `.joblib`) es simple, no introduce herramientas de MLOps especializadas fuera del stack ya definido, y es suficiente para el alcance de un prototipo.
* `HU-SENT-002-v2` gana una justificación más concreta y urgente para su mecanismo de Timeout + fallback a diccionario ya definido: deja de ser una salvaguarda puramente preventiva para convertirse en el mecanismo que protege activamente cada captura frente a la latencia/disponibilidad real de un servicio externo.
### Negativas / riesgos a mitigar
 
* **Dependencia de un tercero fuera del control del equipo:** el sistema queda sujeto a la disponibilidad, latencia y políticas de cuota de Google Gemini Embedding — un cambio en las condiciones del free tier (p. ej. que Google lo reduzca o elimine) afectaría directamente la viabilidad de `HU-SENT-006` sin implementación adicional (habría que migrar de proveedor, revisitando la Alternativa C o D). **Mitigación:** el equipo debe reconfirmar las condiciones de cuota/precio antes de implementar, y el mecanismo de fallback de `HU-SENT-002-v2` garantiza que, si el servicio deja de estar disponible, el sistema sigue funcionando con diccionario.
* **Cuota diaria del free tier (1.500 solicitudes/día) sin validar contra volumen real:** no se ha confirmado si esta cuota es suficiente para el volumen real de noticias que el sistema capturará una vez en producción (ni para el entrenamiento, que podría requerir generar embeddings de un volumen considerable de noticias históricas de una sola vez). Es el mismo tipo de incógnita ya identificada para el umbral mínimo de datos de `HU-SENT-006` (punto 4 de la Decisión) y para la periodicidad del cron de `HU-RSS-007`: no se fija ninguna cifra de mitigación sin datos reales, pero se deja documentado como riesgo a vigilar explícitamente por el equipo durante los Sprints 2-3.
* **Verificación de precios/cuotas con fecha de caducidad:** los datos de pricing/free tier de este ADR fueron obtenidos por búsqueda web el 2026-09-28 y **no deben tratarse como definitivos** — deben reconfirmarse inmediatamente antes de la implementación real en Sprint 4, ya que las condiciones comerciales de APIs externas cambian sin previo aviso.
* **Limitación metodológica del criterio de evaluación (MAE contra diccionario):** como se explica en el punto 6 de la Decisión, el modelo de ML no puede demostrar, con este criterio, una superioridad conceptual sobre el diccionario — cualquier interpretación de los resultados de evaluación en informes o presentaciones del equipo debe mencionar explícitamente esta limitación, para no sobre-representar la calidad del modelo.
* **Manejo de credenciales fuera del alcance de este agente:** la creación de la cuenta de Google y la gestión de la API key de Gemini Embedding es responsabilidad exclusiva del equipo — no se automatiza ni se asiste con esa parte del proceso desde este rol de PO/Arquitecto.
---
 
## Historias de usuario relacionadas
 
* `HU-SENT-006` — Entrenamiento y versionado del modelo de ML *(historia que origina este ADR; todas las decisiones de este documento aplican directamente a su alcance y contrato de API)*.
* `HU-SENT-002-v2` — Cálculo híbrido de humor (diccionario + ML) *(consume el modelo entrenado aquí; su mecanismo de Timeout + fallback a diccionario, ya definido en sesión previa, se ve reforzado y justificado por este ADR)*.
* `HU-SENT-007` — Fallback determinista con diccionario *(fuente de los datos de entrenamiento — noticias ya evaluadas por diccionario — y referencia de evaluación del criterio de MAE)*.
* `HU-SENT-003` — Persistencia del resultado de humor y polarización *(el campo `metodo_calculo` de esta historia distingue si un valor fue calculado por `"ml"` o `"diccionario"`, relevante para separar los datos de entrenamiento — solo noticias evaluadas por diccionario deben usarse como dato de entrenamiento, no las ya evaluadas por un modelo anterior, para no entrenar un modelo sobre las predicciones de otro modelo).*
---
 
## Referencias externas consultadas (verificación de pricing/cuotas, 2026-09-28)
 
Las condiciones de free tier de Google Gemini Embedding, y la comparación con OpenAI y Cohere, fueron verificadas mediante búsqueda web en la fecha de este documento. Dado que el detalle exacto de fuentes no forma parte del contenido técnico del ADR, se deja constancia aquí únicamente de que la verificación fue realizada activamente (no asumida de memoria) y que **debe repetirse antes de la implementación en Sprint 4**, por la naturaleza cambiante de este tipo de información comercial.
 
---
 
## Historial de revisión de este ADR
 
| Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|
| v1.0 | 2026-09-28 | Creación inicial. Resuelve los 7 puntos de arquitectura del modelo de ML que quedaban abiertos en `HU-SENT-006`, con las 4 alternativas evaluadas (modelo 100% local con TF-IDF, LLM como juez directo, otros proveedores de embeddings, embeddings auto-hospedados) y sus trade-offs. Los puntos 4 (umbral mínimo de datos) y 7 (timeout de la llamada a embeddings, dentro de Patrones de resiliencia) quedan como parámetros configurables sin cifra numérica fija. |
| v1.1 | 2026-09-28 | Se fijan **valores propuestos** (no definitivos) para los dos parámetros que quedaban sin cifra en v1.0: umbral mínimo de entrenamiento = 1.000 noticias (punto 4 de la Decisión) y timeout de la llamada a Google Gemini Embedding = 3 segundos (punto 7, Patrones de resiliencia). Ambos valores se derivan de la estimación del equipo de ~50 fuentes RSS activas y de heurísticas generales de ingeniería, no de ningún dato del PDF — quedan marcados explícitamente como propuesta pendiente de ratificación por el equipo, a ajustar con datos reales una vez la integración esté corriendo. Sin cambios en la Decisión de arquitectura, las Alternativas evaluadas ni las Consecuencias. Actualizado en espejo en `HU-SENT-motor-sentimiento.md`. |
| v1.2 (editorial) | 2026-09-29 | Limpieza editorial: se retiran las marcas de sesión ("tercera/cuarta sesión del día") y las etiquetas "PO/Arquitecto" inline dentro del cuerpo del documento, integrando ese contenido como prosa técnica normal. La trazabilidad de cuándo se tomó cada decisión queda exclusivamente en esta tabla de Historial de revisión. Sin cambios de fondo en la arquitectura, la Decisión ni las Consecuencias. |
 
