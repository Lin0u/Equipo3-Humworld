# ADR-002: Arquitectura del módulo de Captura RSS

**Estado:** Aceptado — ratificado por el equipo el 2026-08-19, junto con ADR-001, al confirmar el modelo `CanalNoticias`/`FuenteRSS` en composición (frente a la alternativa simplificada de "canal" como atributo de texto) y proceder con el scaffolding de código de Sprint 1.

---

## Contexto

El módulo de Captura RSS es responsable de (PDF de especificaciones, secciones 4.2.1, 4.2.3 y 4.2.4, págs. 5-6):

1. Gestionar el alta, consulta, modificación y baja de **canales de noticias** (medios) y **fuentes RSS** dentro de cada canal.
2. Ejecutar de forma automática y periódica (cron) el recorrido de todas las fuentes RSS activas, capturando noticias nuevas.
3. Permitir la actualización manual de la captura para una fuente o un conjunto de fuentes.
4. Almacenar el contenido capturado en base de datos junto con fecha y hora de registro.
5. Disponer de una carga inicial de fuentes RSS por continente.

Restricciones y condicionantes reales:

- **No se permite Web Scraping** (PDF, sección 4.2.1): el sistema debe restringirse estrictamente al protocolo RSS/Atom estándar, sin extracción de contenido HTML fuera del feed.
- **Las fuentes RSS son de terceros y de naturaleza inestable**: el PDF (sección 5) lista feeds públicos reales de distintos medios (RTVE, El País, ABC, El Confidencial, etc.) que pueden presentar caídas intermitentes, lentitud, cambios de formato o certificados TLS inválidos — condiciones fuera del control del equipo.
- **MySQL como motor de persistencia** (instrucciones del proyecto, sección 8), lo que determina el diseño relacional de las entidades `CanalNoticias`, `FuenteRSS` y `Noticia`.
- **Relación de composición explícitamente exigida**: las instrucciones del proyecto (sección 8) establecen que debe usarse composición (rombo relleno) para la relación `CanalNoticias` → `FuenteRSS`, dado que una fuente RSS no tiene sentido de existir sin su canal contenedor.
- **Cobertura de pruebas ≥80% con dependencias externas mockeadas** (instrucciones del proyecto, sección 14): ninguna prueba unitaria puede realizar llamadas HTTP reales a los feeds RSS.
- **Plazo académico fijo**, con Sprint 1 dedicado específicamente a "Implementación de captura y almacenamiento de noticias" (PDF, sección 8.1), lo que exige una arquitectura simple de implementar en ese plazo, sin sobre-ingeniería.
- **Stack de backend ya decidido en ADR-001**: Python + FastAPI + SQLAlchemy + `httpx` (async) + `feedparser`.

## Decisión

### 1. Modelo de datos y relaciones UML

Se definen tres entidades principales para este módulo:

```
CanalNoticias (1) ◆──── (0..N) FuenteRSS (1) ──── (0..N) Noticia
                composición                    agregación
```

- **`CanalNoticias`** (medio de comunicación): `id`, `nombre`, `continente`, `pais` (opcional), `descripcion` (opcional).
- **`FuenteRSS`**: `id`, `canal_id` (FK, obligatoria), `url`, `categoria_iptc`, `activo` (booleano), `fecha_ultima_captura_exitosa` (nullable), `estado_circuit_breaker` (ver sección 3).
- **`Noticia`**: `id`, `fuente_rss_id` (FK, obligatoria), `identificador_item_rss` (para deduplicación — típicamente el `<guid>` o, en su defecto, hash del enlace+título), `titulo`, `contenido` o `resumen`, `enlace_original`, `fecha_publicacion` (del propio feed), `fecha_registro` (timestamp de captura por el sistema, exigido explícitamente en sección 4.2.4 del PDF), `idioma_detectado`, `categoria_iptc` (heredada de la fuente o reprocesada por noticia, a definir), `valor_humor` (nullable — poblado por el módulo de Análisis de Sentimiento, fuera de alcance de este ADR).

**Justificación de las relaciones UML:**

- **`CanalNoticias` ◆── `FuenteRSS` (Composición):** una `FuenteRSS` no tiene existencia ni sentido de negocio independiente de su `CanalNoticias`. Si el canal se elimina, sus fuentes deben eliminarse (o el sistema debe impedir la eliminación del canal mientras tenga fuentes asociadas — decisión operativa a confirmar por el equipo, análoga a la nota abierta en HU-RSS-005). Esto es coherente con la instrucción explícita de la sección 8 del proyecto, que usa exactamente este par de entidades como ejemplo de composición.
- **`FuenteRSS` ── `Noticia` (Agregación):** una `Noticia`, una vez capturada, tiene valor informativo y analítico propio (es la base del cálculo de humor histórico). Aunque referencia su fuente de origen, su ciclo de vida es independiente: la eliminación de una fuente **no debería** implicar necesariamente la eliminación en cascada de las noticias ya capturadas desde ella, dado que estas alimentan series históricas de humor que deben mantenerse coherentes para el dashboard (PDF, sección 4.3.2, "mapa del mundo... en el rango de fechas para el que se dispone información"). Este punto queda documentado como decisión abierta a validar con el equipo (ver HU-RSS-005, nota de diseño).

### 2. Mecanismo de captura (cron)

- Se implementa mediante un **scheduler interno a la aplicación** (librería `APScheduler` sobre FastAPI, ejecutando un `BackgroundScheduler`/`AsyncIOScheduler`), en lugar de depender de un cron del sistema operativo del contenedor, para mantener la periodicidad como un parámetro gestionable en caliente vía la API de Configuraciones (`/api/v1/config`, HU-RSS-007) sin requerir reinicio del contenedor ni acceso a crontab del host.
- El job de captura recorre el conjunto de `FuenteRSS` con `activo = verdadero`, lanzando las peticiones HTTP de forma **concurrente y acotada** (usando un semáforo asíncrono para limitar el número de conexiones simultáneas y evitar saturar la red del contenedor o comportarse de forma abusiva contra los servidores de los medios — buena práctica de buen ciudadano de red, aunque el PDF no fija un límite numérico explícito, por lo que el valor concreto del límite de concurrencia **queda como parámetro de configuración a definir por el equipo**, no como cifra fija de este ADR).
- La actualización manual (HU-RSS-008) reutiliza exactamente el mismo procedimiento de captura y deduplicación que el cron automático, parametrizado por una lista de `fuente_rss_id` en lugar de "todas las activas".

### 3. Patrones de resiliencia (sección 13 de las instrucciones del proyecto — propuesta proactiva obligatoria)

Dado que este módulo integra servicios externos inestables (feeds RSS de terceros), se evalúan explícitamente los cuatro patrones indicados por las instrucciones del proyecto:

| Patrón | ¿Aplica a este módulo? | Justificación |
|---|---|---|
| **Timeout explícito** | **Sí — obligatorio en toda llamada.** | Salvaguarda mínima: sin timeout, una fuente RSS que no responde puede bloquear indefinidamente el worker de captura, retrasando la captura del resto de fuentes. Se aplicará un timeout de conexión y de lectura en cada llamada `httpx` a un feed RSS. El valor numérico exacto (p. ej. X segundos de conexión, Y segundos de lectura) **no está especificado en el PDF y debe ser definido y validado por el equipo** durante la implementación, dejándolo como parámetro configurable en lugar de constante hardcodeada. |
| **Retry con backoff exponencial (acotado)** | **Sí, para fallos transitorios.** | Un fallo puntual de red (timeout momentáneo, error 502/503 del servidor del medio) no debería marcar una fuente como caída tras un único intento. Se aplicará un número máximo y acotado de reintentos con backoff exponencial (nunca reintentos infinitos, conforme exige explícitamente la sección 13 del proyecto). El número de reintentos y el factor de backoff son parámetros a definir por el equipo, no cifras contempladas en el PDF. |
| **Circuit Breaker** | **Sí, por fuente RSS.** | Si una fuente falla de forma sistemática y repetida (no un fallo puntual, sino una caída sostenida), seguir reintentándola en cada ejecución del cron desperdicia recursos y aumenta la latencia total del job de captura, que debe procesar potencialmente decenas de fuentes en una misma ejecución. Se propone un circuit breaker **por fuente RSS individual** (estado `estado_circuit_breaker`: `cerrado` / `abierto` / `semi-abierto`), de forma que, tras un número de fallos consecutivos, la fuente se marca temporalmente como "en circuito abierto" y se omite en las siguientes N ejecuciones del cron antes de reintentarla (estado "semi-abierto"), evitando bloquear el resto del job. Esto es coherente con el criterio de aceptación de HU-RSS-006 ("el fallo de esa fuente no impide que el cron continúe procesando el resto de fuentes activas"). |
| **Bulkhead** | **Parcialmente — mitigado mediante el límite de concurrencia del punto 2, no como bulkhead formal separado.** | El proyecto no expone otros servicios externos críticos además de las fuentes RSS en este módulo (no hay, por ejemplo, un pool de base de datos compartido con otro servicio externo de terceros dentro de este mismo módulo). Dado el alcance acotado de un prototipo académico y para evitar sobre-ingeniería en el plazo del curso, se considera que el límite de concurrencia con semáforo (punto 2) ya aísla razonablemente el impacto de fuentes lentas sobre el pool de conexiones disponible, sin requerir un patrón de Bulkhead formal (p. ej. pools de hilos/conexiones completamente separados por fuente). **Si en fases posteriores del proyecto se detecta que una fuente lenta degrada la capacidad de respuesta de la propia API REST** (por ejemplo, porque comparte el mismo event loop sin aislamiento), el equipo debería revisar esta decisión y considerar ejecutar el cron de captura como proceso/worker separado de la API REST — cambio que ameritaría una nueva versión de este ADR. |

**Conclusión de la Decisión respecto a resiliencia:** se adoptan **Timeout explícito + Retry acotado con backoff exponencial + Circuit Breaker por fuente**, implementados en la capa de servicio de captura (no en los controladores REST), de forma reutilizable tanto para el cron automático (HU-RSS-006) como para la captura manual (HU-RSS-008).

### 4. Separación de capas

Conforme a la arquitectura en tres capas exigida por el PDF (sección 6.1):

- **Capa de presentación/API:** routers FastAPI (`/api/v1/channels`, `/api/v1/sources`, `/api/v1/sources/{id}/captures`) — sin lógica de negocio, solo validación de entrada (Pydantic) y delegación a la capa de servicio.
- **Capa de lógica de negocio:** servicio de captura (orquestación del recorrido de fuentes, aplicación de los patrones de resiliencia, deduplicación de noticias por `identificador_item_rss`), independiente del framework web.
- **Capa de datos:** modelos SQLAlchemy + repositorios/DAO para `CanalNoticias`, `FuenteRSS`, `Noticia` sobre MySQL.

## Alternativas consideradas

### Alternativa A: Cron del sistema operativo (crontab) invocando un script independiente

**Ventajas:** desacopla completamente el proceso de captura del proceso de la API REST; falla de forma aislada sin afectar la disponibilidad de la API.

**Desventajas:** la periodicidad configurable en caliente (HU-RSS-007) requeriría reescribir el crontab del contenedor en tiempo de ejecución (operación poco idiomática y con permisos delicados dentro de Docker), o bien un mecanismo adicional de sincronización entre la configuración en base de datos y el crontab del sistema, añadiendo complejidad operativa no justificada para un prototipo de curso.

**Veredicto:** descartada en favor del scheduler interno (`APScheduler`), que permite leer la periodicidad directamente desde la tabla de configuración en cada reprogramación del job, sin tocar el sistema operativo del contenedor.

### Alternativa B: Cola de mensajes (p. ej. Celery + Redis/RabbitMQ) para orquestar la captura

**Ventajas:** mayor escalabilidad horizontal (múltiples workers), mejor aislamiento de fallos entre la API y el procesamiento en segundo plano, patrón de Bulkhead más robusto de forma nativa.

**Desventajas:** introduce infraestructura adicional (broker de mensajes) no contemplada en el stack tecnológico definido por el proyecto (instrucciones del proyecto, sección 8, no menciona colas de mensajes), aumentando la complejidad de despliegue con Docker Compose y el esfuerzo de configuración en un plazo académico acotado, para un volumen de fuentes RSS que, en el contexto de un prototipo de curso, no justifica esta sobre-ingeniería.

**Veredicto:** descartada para el prototipo del curso; queda documentada como posible evolución futura si el proyecto escalara más allá del contexto académico (debería registrarse como nueva versión de este ADR si el equipo decide adoptarla).

### Alternativa C: Sin Circuit Breaker, solo Retry acotado

**Ventajas:** menor complejidad de implementación.

**Desventajas:** con múltiples fuentes RSS y una ejecución periódica del cron, una fuente caída de forma sostenida (no transitoria) seguiría consumiendo el presupuesto completo de reintentos en **cada** ejecución del cron indefinidamente, degradando la latencia total del job de forma recurrente sin necesidad. El Circuit Breaker resuelve específicamente este caso, que el Retry por sí solo no cubre.

**Veredicto:** descartada; se mantiene el Circuit Breaker como parte de la decisión.

### Alternativa D: "Canal" como atributo de texto libre en `FuenteRSS`, en lugar de entidad separada (revisada 2026-08-19)

Contexto de esta alternativa: el documento de planificación efectivamente entregado en la Práctica P3 (`PLANIFICACION-AGIL-HUMWORLD-ENTREGADO-P3.md`) simplifica el módulo fusionando "canal" como un campo dentro de la fuente RSS, sin CRUD propio.

**Ventajas:** una sola alta en vez de dos; menor superficie de endpoints y de pruebas a cubrir para el umbral de cobertura ≥80% en Sprint 1.

**Desventajas:**
- Riesgo de duplicación/inconsistencia del nombre de canal y su continente/país entre distintas fuentes del mismo medio, sin una fuente única de verdad.
- Las consultas agregadas por continente/país (HU-DASH-001, HU-SENT-004, ambas fuera de EPIC-RSS pero consumidoras de este modelo) dependen de que el continente esté normalizado, no repetido como texto libre por fuente.
- El PDF (§4.2.1) describe explícitamente dos altas distintas ("dar de alta canales... y fuentes RSS dentro de cada canal"), no una alta fusionada.
- Pierde el ejemplo de composición UML que las propias instrucciones del proyecto (sección 8) usan como caso de referencia para `CanalNoticias → FuenteRSS`.

**Veredicto:** descartada. El costo adicional de modelar `CanalNoticias` como entidad independiente es bajo (HU-RSS-001 estimada en 1 punto) frente al riesgo de inconsistencia de datos que introduce la alternativa simplificada. Se mantiene el modelo de composición ya definido en la sección 1 de este ADR como diseño vigente para la implementación de Sprint 1, independientemente de la simplificación usada en el documento de planificación de P3 (que se conserva sin modificar como registro de lo efectivamente entregado y calificado).

## Consecuencias

**Positivas:**
- El fallo de una o varias fuentes RSS nunca compromete la disponibilidad de la API REST ni el procesamiento del resto de fuentes, cumpliendo directamente el criterio de aceptación de HU-RSS-006.
- La periodicidad del cron es ajustable en caliente sin reiniciar el contenedor, satisfaciendo HU-RSS-007 sin complejidad operativa adicional.
- La lógica de resiliencia se centraliza en la capa de servicio y es reutilizable entre captura automática (HU-RSS-006) y manual (HU-RSS-008), evitando duplicación.
- El modelo `CanalNoticias`/`FuenteRSS` en composición evita duplicación de continente/país y deja lista la agregación regional que necesitan los dashboards de EPIC-DASH, y sustenta directamente la consulta de canales por continente definida en HU-RSS-010.

**Negativas / riesgos a mitigar:**
- El estado del Circuit Breaker por fuente (`estado_circuit_breaker`) añade un campo mutable adicional a `FuenteRSS` que debe gestionarse con cuidado en escenarios de concurrencia (captura manual disparada mientras el cron automático está en ejecución sobre la misma fuente) — debe evaluarse un mecanismo de bloqueo optimista o un flag `en_captura` para evitar condiciones de carrera. **Este punto de concurrencia no está resuelto en detalle en este ADR y debe abordarse en el diseño detallado del servicio de captura.**
- Todos los valores numéricos de timeout, número de reintentos, factor de backoff y umbral de fallos del Circuit Breaker quedan explícitamente **sin fijar** en este documento (por rigor de grounding frente al PDF) y deben definirse como configuración validada por el equipo antes de la implementación final, evitando hardcodear cifras no acordadas.
- Al aceptar el modelo de composición (Alternativa D descartada), el scaffolding de código expone dos recursos (`/channels` y `/sources`) en vez de uno solo — ligeramente más superficie de API que cubrir con pruebas para el DoD (cobertura ≥80%).
- **Nueva convención de paginación (HU-RSS-010, HU-RSS-003-v2):** al paginar `GET /channels` y `GET /sources`, la forma de la respuesta 200 cambia de un array simple a un objeto con `items`/`pagina`/`tamanio_pagina`/`total`. Este es un cambio de convención de API (no de arquitectura interna) que debe tenerse presente si en el futuro se agregan otros endpoints de listado (p. ej. Noticias, Configuraciones), para mantener la misma forma de respuesta por consistencia.

## Historias de usuario relacionadas

HU-RSS-001, HU-RSS-002, HU-RSS-003 (deprecada, ver HU-RSS-003-v2), HU-RSS-003-v2, HU-RSS-004, HU-RSS-005, HU-RSS-006, HU-RSS-007, HU-RSS-008, HU-RSS-009, HU-RSS-010.

---

## Historial de revisión de este ADR

| Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|
| v1 | 2026-08-14 | Creación inicial del ADR de arquitectura del módulo de Captura RSS, incluyendo evaluación proactiva de patrones de resiliencia (sección 13 de las instrucciones del proyecto). |
| v1.1 | 2026-08-19 | Estado actualizado de "Propuesto" a "Aceptado". Se agrega Alternativa D (canal como atributo simple, según el entregable de P3) evaluada y descartada explícitamente, dejando registrada la razón por la cual se mantiene el modelo de composición frente a la versión simplificada. Sin cambios en las secciones 1-4 de la Decisión. |
| v1.2 | 2026-08-26 | Se agrega HU-RSS-010 (consulta y listado de canales) a la lista de historias relacionadas y a las Consecuencias positivas, tras la formalización de esa historia en `HU-RSS-captura.md` y la corrección de trazabilidad del contrato OpenAPI. Sin cambios en el modelo de datos ni en la Decisión de arquitectura. |
| v1.3 | 2026-08-30 | Se agrega HU-RSS-003-v2 (versión paginada, reemplaza a HU-RSS-003 deprecada) a la lista de historias relacionadas, y se documenta en Consecuencias la nueva convención de paginación adoptada para GET /channels y GET /sources. Sin cambios en el modelo de datos, en los patrones de resiliencia ni en la separación de capas. |
