# Historias de Usuario — Módulo Captura RSS
 
**Proyecto:** HumWorld — Equipo 3
**Módulo:** Captura RSS (gestión de canales/fuentes, cron de captura, actualización manual)
**Fuente:** `0 PROYECTO_FINAL_HUMWORLD 260714.pdf`, secciones 4.2.1 (Orígenes de Información, pág. 5), 4.2.3 (Captura de Información, pág. 5), 4.2.4 (Procesado de la información, pág. 6) y 10.2 (Endpoints mínimos obligatorios, pág. 13).
**Versión del documento:** v1.10. Fija un valor propuesto para la periodicidad por defecto del cron de captura (HU-RSS-007) y retira los bloques de comentario en formato cita que narraban el proceso de decisión, integrando su contenido como texto normal del documento. Ver la Tabla de control de versiones para el historial completo.
**Estado general:** Propuesto (pendiente de revisión crítica y Planning Poker por el equipo, según Práctica P3, Paso 2 y Paso 4)
 
**Nota de alcance (grounding):** la tabla de endpoints mínimos obligatorios (sección 10.2) solo lista `/sources` (Fuentes RSS) como categoría de endpoint explícita. La gestión de **canales** (medios de comunicación) está exigida funcionalmente en la sección 4.2.1 ("El sistema permitirá dar de alta canales (medios) y fuentes RSS dentro de cada canal"), pero no aparece como categoría separada en la tabla de mínimos. Dado que la tabla se define como "mínimos obligatorios" (piso, no techo) y la funcionalidad de canales está explícitamente descrita en el cuerpo del documento, se incluye un recurso `/channels` adicional — interpretación confirmada por el equipo al formalizar **HU-RSS-010** (ver más abajo), que documenta con criterios Gherkin propios el listado de canales (`GET /api/v1/channels`, `GET /api/v1/channels/{id}`).
 
El equipo decidió además paginar tanto el listado de Canales (HU-RSS-010) como el de Fuentes RSS (HU-RSS-003 → **HU-RSS-003-v2**), para mantener una convención de API consistente y porque el número de fuentes RSS puede crecer considerablemente (el equipo estima un mínimo de 20 fuentes). El listado de Fuentes RSS se ordena por `canal_id` (agrupando las fuentes de un mismo canal) y, dentro de cada canal, alfabéticamente por `url` — ver el detalle completo de la convención de paginación en HU-RSS-010 y HU-RSS-003-v2.
 
**Nota de alcance (algoritmo de humor):** el valor de "humor" que se persiste junto a cada noticia (sección 4.2.4) es calculado por el módulo de Análisis de Sentimiento (fuera de alcance de este documento). Las historias de este módulo únicamente contemplan la captura, almacenamiento y gestión de metadatos de fuentes y noticias — no el cálculo del valor de humor en sí.
 
---
 
## Tabla de control de versiones
 
| ID | Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|---|
| HU-RSS-001 a HU-RSS-009 | v1 | 2026-08-14 | Creación inicial del backlog del módulo Captura RSS |
| HU-RSS-010 | v1 | 2026-08-26 | Nueva historia: formaliza con criterios Gherkin propios el listado de canales de noticias (`GET /api/v1/channels`, `GET /api/v1/channels/{id}`), endpoint que ya existía en el contrato OpenAPI pero estaba atribuido de forma implícita a HU-RSS-001 (sin criterios de aceptación propios). Decisión tomada en sesión de trabajo tras revisar la práctica P6-OpenSpec-II, que exige una segunda historia de consulta sobre la misma entidad de la historia piloto (HU-RSS-001). No modifica HU-RSS-001, que conserva su alcance original (alta de canal). Se corrige en consecuencia la trazabilidad de `contrato-canales-fuentes-rss.openapi.yaml`. |
| HU-RSS-010 | v1 (completada) | 2026-08-30 | Se completan los criterios que quedaban abiertos desde su creación (no se trata de una historia ya publicada/ratificada, por lo que no aplica el proceso de deprecación de la sección 3): orden del listado (alfabético ascendente por "nombre") y paginación (parámetros `pagina`/`tamanio_pagina`, valores por defecto 10 y máximo 50, respuesta en formato objeto con `items` + metadatos). |
| HU-RSS-003 | v1 → **Deprecada** | 2026-08-30 | Se deprecа en favor de **HU-RSS-003-v2**, que agrega paginación al listado de Fuentes RSS por consistencia con HU-RSS-010 y porque el volumen esperado de fuentes (mínimo 20, según estimación del equipo) lo justifica. El endpoint (`GET /api/v1/sources`) no cambia de ruta, pero sí cambia la forma de la respuesta (de array simple a objeto paginado) y se agregan parámetros de query. Se corrige en consecuencia `contrato-canales-fuentes-rss.openapi.yaml`. |
| HU-RSS-003-v2 | v1 | 2026-08-30 | Creación de la versión paginada de la consulta de Fuentes RSS. Motivo: consistencia de convención de API con HU-RSS-010 y volumen esperado de datos. Queda abierta la definición del criterio de orden del listado (Fuentes no tiene un campo "nombre" como Canales — **pendiente de decisión del equipo**). |
| HU-RSS-003-v2 | v1 (completada) | 2026-08-30 | Se define el criterio de orden que quedaba pendiente: ordenar por `canal_id` ascendente (agrupando las fuentes de un mismo canal/medio) y, dentro de un mismo canal, alfabéticamente por `url`. |
| HU-RSS-010 | v1 (editorial) | 2026-08-31 | Se acorta la nota de grounding de la historia (quedaba redundante con esta misma tabla, fila 2026-08-26) a una referencia breve. No cambia alcance, criterios ni prioridad/estimación. |
| HU-RSS-001, HU-RSS-002, HU-RSS-003-v2, HU-RSS-004, HU-RSS-005, HU-RSS-010 | v1 (evidencia DoD) | 2026-09-06 | Se documenta evidencia de verificación del pipeline CI/CD en GitHub Actions (workflow `CI`, run #16, commit `7a5c18b`, rama `main`, verde) para los criterios de DoD "cobertura ≥80% verificada en GitHub Actions" y "build y despliegue exitosos (`needs: [test, sonarqube]`)", sección 14. Ver sección "Evidencia de verificación de DoD" más abajo. No modifica alcance, criterios de aceptación ni prioridad/estimación de ninguna historia — no aplica el proceso de deprecación de la sección 3. |
| HU-RSS-008 | v1 (completada) | 2026-09-10 | Se completan los criterios que quedaban abiertos desde su creación (no se trata de una historia ya publicada/ratificada, por lo que no aplica el proceso de deprecación de la sección 3): (1) se confirman **dos** endpoints del recurso `captures` — `POST /api/v1/sources/{id}/captures` (una fuente puntual) y `POST /api/v1/captures` con body `{"fuente_ids": [...]}` (lote) —, y (2) se define el procesamiento como **síncrono** (HTTP 201), descartando para el alcance de este curso la alternativa asíncrona (202), por la infraestructura adicional que implicaría (cola de tareas, tabla de estado de trabajos, endpoint de consulta de estado) sin un sistema de colas aprobado en ADR-001/ADR-002. Se actualiza en consecuencia `contrato-canales-fuentes-rss.openapi.yaml` (v1.4.0). |
| HU-RSS-009 | v1 (completada parcial) | 2026-09-10 | Se cambia el actor de "equipo de desarrollo" a "administrador del sistema" (no se trata de una historia ya publicada/ratificada, por lo que no aplica el proceso de deprecación de la sección 3): la historia deja de ser Enabler Story y pasa a ser Historia de Usuario clásica, disparada manualmente vía el nuevo endpoint `POST /api/v1/seeds` (propuesta, aún no incorporada al contrato OpenSpec) en vez de un script/migración. Quedan **todavía pendientes** de decisión del equipo: continentes contemplados, listado real de fuentes RSS por continente y campo exacto de clave de idempotencia. |
| HU-RSS-009 | v1 (completada) | 2026-09-28 | Se confirman 2 de los 3 puntos pendientes desde la sesión 2026-09-10: (1) **continentes contemplados** = los 5 continentes habitados (América, Europa, Asia, África, Oceanía) — decisión del equipo, sin especificación en el PDF; (2) **clave de idempotencia** confirmada tal como estaba propuesta (`nombre` para Canales, `url` para Fuentes). **Sigue pendiente:** el listado real de fuentes RSS por continente (URLs verificadas) — no es una decisión de alcance sino datos concretos que el equipo debe investigar y verificar, por lo que el agente PO/Arquitecto no los propone para evitar el riesgo de inventar fuentes inexistentes o desactualizadas. Se actualiza en consecuencia `contrato-canales-fuentes-rss.openapi.yaml` (v1.6.0). |
| HU-RSS-007 | v1 (valor propuesto) | 2026-09-28 (cuarta sesión del día) | Se fija un **valor propuesto** (no definitivo) para el parámetro `periodicidad_cron_minutos`, que quedaba abierto desde la creación de la historia por no estar fijado en el PDF: **30 minutos**, a partir de heurísticas generales de agregadores RSS (no de un dato del proyecto) y de la estimación del equipo de ~50 fuentes activas. Queda marcado explícitamente como propuesta del PO/Arquitecto pendiente de ratificación por el equipo. Se actualiza en espejo la nota de grounding de periodicidad en HU-RSS-006. |
| Todas | v1 (editorial) | 2026-09-29 | Limpieza editorial: se retiran los bloques de comentario en formato cita ("— CONFIRMADO/A (decisión del equipo, sesión...)", "Nota de grounding (decisión del equipo, sesión...)", "Actualización (sesión...)") y se integra su contenido como texto normal del documento, sin narrar el proceso de decisión turno a turno. No cambia ninguna decisión, valor propuesto, criterio de aceptación ni alcance — solo la forma en que se presenta. El historial de sesiones/fechas queda concentrado en esta tabla. |
 
---
 
## Evidencia de verificación de DoD — Pipeline CI/CD (Sprint 1)
 
**Aplica a:** HU-RSS-001, HU-RSS-002, HU-RSS-003-v2, HU-RSS-004, HU-RSS-005 y HU-RSS-010 — las 6 historias de este módulo con lógica de negocio y pruebas implementadas a la fecha de esta nota (HU-RSS-006 a 009 siguen siendo scaffolding, sección 12, y quedan explícitamente excluidas de la medición de cobertura vía `src/.coveragerc`).
 
**Ejecución verificada:** GitHub Actions, workflow `CI`, run **#16** ("fix ci.yml"), commit `7a5c18b`, rama `main`, pusheado el 2026-09-06 — **resultado: verde** (los tres jobs `test` → `sonarqube` → `build-and-deploy`, encadenados por `needs`, completaron exitosamente; por diseño de GitHub Actions, un job con `needs` no corre si el/los job(s) del que depende no terminaron en éxito, así que el verde de `build-and-deploy` confirma transitivamente el de `sonarqube` y `test`).
 
Qué queda confirmado con esta ejecución, y qué no:
 
-  **Cobertura ≥80% verificada en el pipeline** (sección 14, DoD): el job `test` ejecuta `pytest --cov=app --cov-report=xml --cov-report=term-missing --cov-fail-under=80` desde `src/`, por lo que recoge automáticamente `src/.coveragerc` (excluye del cálculo el scaffolding aún no implementado de `app/routers/captures.py`, `app/services/captura_service.py` y `app/jobs/scheduler.py`, HU-RSS-006/007/008/009) y `src/pytest.ini`. El job no falló, luego la cobertura real de las 6 historias listadas arriba es ≥80% **en CI**, no solo en ejecución local.
-  **Build y despliegue del job Docker exitoso, dependiente de `needs: [test, sonarqube]`**: el job `build-and-deploy` completó — solo ocurre si `test` y `sonarqube` también completaron exitosamente.
-  **Verificación parcial — "Análisis de SonarQube ejecutado sin issues críticos ni deuda técnica no justificada":** el verde del job `sonarqube` confirma que el scanner se autenticó correctamente (secret `SONAR_TOKEN` cargado y funcional, confirmado en Settings > Secrets and variables > Actions del repositorio) y que el análisis se subió sin error técnico. **No confirma por sí solo la ausencia de issues críticos**: este `ci.yml` no incluye un paso de Quality Gate (p. ej. `sonarqube-quality-gate-action`) que bloquee el job ante hallazgos de severidad alta — el job puede terminar en verde aun si SonarCloud reportó issues. Para cerrar por completo este punto de la DoD, alguien del equipo debe revisar el resultado del análisis directamente en el dashboard de SonarCloud/SonarQube del proyecto.
**Historial de ejecuciones relevante (contexto, no requiere acción):** los runs #1 a #4 del workflow (anteriores al 23 de agosto de 2026) fallaron por falta de `sonar-project.properties` y por una versión desactualizada de la action de SonarQube — ambos problemas ya resueltos (commits `8233b61` y `51fa76c` respectivamente). Todos los runs desde el #5 en adelante están en verde.
 
---
 
## HU-RSS-001 — Alta de Canal de Noticias
 
**Tipo:** Historia de Usuario
**Como** administrador del sistema,
**quiero** dar de alta un canal de noticias (medio de comunicación),
**para** poder agrupar bajo él las fuentes RSS que se van a capturar.
 
**Prioridad:** Alta
**Estimación relativa:** S *(punto de partida orientativo; debe validarse con Planning Poker real del equipo — no es un valor definitivo)*
**Depende de contrato de API:** Sí — `POST /api/v1/channels`
 
### Criterios de aceptación (Gherkin)
 
```gherkin
Escenario: Alta exitosa de un canal de noticias
  Dado que el administrador envía una solicitud POST a /api/v1/channels
  Y el cuerpo incluye "nombre" y "continente" válidos y no vacíos
  Cuando el sistema procesa la solicitud
  Entonces el sistema responde con código HTTP 201
  Y se crea exactamente 1 registro de canal en la base de datos
  Y la respuesta incluye el identificador único generado para el canal
 
Escenario: Rechazo por datos obligatorios faltantes
  Dado que el administrador envía una solicitud POST a /api/v1/channels
  Y el campo "nombre" está vacío o ausente
  Cuando el sistema procesa la solicitud
  Entonces el sistema responde con código HTTP 400
  Y no se crea ningún registro en la base de datos
 
Escenario: Rechazo por nombre de canal duplicado
  Dado que ya existe un canal registrado con el mismo "nombre"
  Cuando el administrador intenta crear otro canal con el mismo "nombre"
  Entonces el sistema responde con código HTTP 409
```
 
### Definition of Done
- Código implementado y revisado por al menos 1 miembro distinto del equipo.
- Pruebas unitarias del endpoint escritas y pasando, sin llamadas reales a servicios externos.
- Cobertura de pruebas del módulo ≥ 80%, verificada en el pipeline de GitHub Actions. ** Verificado — ver "Evidencia de verificación de DoD" (run #16, commit `7a5c18b`).**
- Análisis de SonarQube ejecutado sin issues críticos ni deuda técnica no justificada. ** Ejecución confirmada; pendiente revisión del dashboard de SonarCloud para el punto "sin issues críticos" — ver "Evidencia de verificación de DoD".**
- Endpoint documentado en Swagger/OpenAPI (`/api/docs`).
- Build y despliegue exitosos en el job de Docker (dependiente de `needs: [test, sonarqube]`). ** Verificado — ver "Evidencia de verificación de DoD".**
---
 
## HU-RSS-002 — Alta de Fuente RSS dentro de un Canal
 
**Tipo:** Historia de Usuario
**Como** administrador del sistema,
**quiero** dar de alta una fuente RSS asociada a un canal existente, indicando su URL y categoría IPTC Media Topics,
**para** que el sistema pueda capturar noticias desde ella.
 
**Prioridad:** Alta
**Estimación relativa:** M *(punto de partida orientativo, sujeto a Planning Poker)*
**Depende de contrato de API:** Sí — `POST /api/v1/sources`
 
### Criterios de aceptación (Gherkin)
 
```gherkin
Escenario: Alta exitosa de una fuente RSS
  Dado que existe un canal con id válido
  Y el administrador envía POST a /api/v1/sources con "canal_id", "url" y "categoria_iptc" válidos
  Cuando el sistema procesa la solicitud
  Entonces el sistema responde con código HTTP 201
  Y la fuente queda asociada exactamente al canal indicado (relación de composición CanalNoticias → FuenteRSS)
  Y el campo "activo" de la fuente se inicializa en verdadero
 
Escenario: Rechazo por canal inexistente
  Dado que "canal_id" no corresponde a ningún canal registrado
  Cuando el administrador envía POST a /api/v1/sources
  Entonces el sistema responde con código HTTP 404
 
Escenario: Rechazo por URL con formato inválido
  Dado que el campo "url" no cumple el formato de URL válido (RFC 3986)
  Cuando el administrador envía POST a /api/v1/sources
  Entonces el sistema responde con código HTTP 400
 
Escenario: Rechazo por categoría IPTC no reconocida
  Dado que "categoria_iptc" no pertenece al primer nivel del estándar IPTC Media Topics
  Cuando el administrador envía POST a /api/v1/sources
  Entonces el sistema responde con código HTTP 400
```
 
### Definition of Done
(Idéntico al bloque general de la sección 14 de las instrucciones del proyecto — código revisado, pruebas con mocks, cobertura ≥80%, SonarQube sin críticos, Swagger actualizado, build/deploy con `needs: [test, sonarqube]`.) **✅ Cobertura y build/deploy verificados en pipeline;  "SonarQube sin críticos" pendiente de revisión de dashboard — ver "Evidencia de verificación de DoD".**
 
---
 
## HU-RSS-003 — Consulta y filtrado de Fuentes RSS
 
**Estado:** **Deprecada** — reemplazada por **HU-RSS-003-v2** (ver más abajo), que agrega paginación. Se conserva este bloque íntegro como registro histórico, conforme a la sección 3 de las instrucciones del proyecto (gestión de cambios en historias existentes).
 
**Tipo:** Historia de Usuario
**Como** administrador o analista de medios,
**quiero** consultar el listado de fuentes RSS registradas, con filtros por canal, continente, categoría y estado activo/inactivo,
**para** poder auditar y gestionar el conjunto de fuentes configuradas.
 
**Prioridad:** Alta
**Estimación relativa:** S *(orientativo, sujeto a Planning Poker)*
**Depende de contrato de API:** Sí — `GET /api/v1/sources` y `GET /api/v1/sources/{id}`
 
### Criterios de aceptación (Gherkin)
 
```gherkin
Escenario: Listado exitoso sin filtros
  Dado que existen N fuentes RSS registradas (N ≥ 0)
  Cuando el usuario envía GET a /api/v1/sources
  Entonces el sistema responde con código HTTP 200
  Y el cuerpo de la respuesta contiene exactamente N elementos
 
Escenario: Filtrado por continente
  Dado que existen fuentes RSS en distintos continentes
  Cuando el usuario envía GET a /api/v1/sources?continente=America
  Entonces el sistema responde con código HTTP 200
  Y el 100% de los elementos devueltos pertenecen a un canal cuyo continente es "America"
 
Escenario: Consulta de detalle de una fuente existente
  Dado que existe una fuente RSS con id=X
  Cuando el usuario envía GET a /api/v1/sources/X
  Entonces el sistema responde con código HTTP 200
  Y el cuerpo incluye los datos completos de esa única fuente
 
Escenario: Consulta de detalle de una fuente inexistente
  Dado que no existe ninguna fuente RSS con id=X
  Cuando el usuario envía GET a /api/v1/sources/X
  Entonces el sistema responde con código HTTP 404
```
 
### Definition of Done
(Bloque general DoD, sección 14 — incluye adicionalmente: validación de que los filtros combinados no producen errores 500 con parámetros vacíos.)
 
---
 
## HU-RSS-003-v2 — Consulta y filtrado de Fuentes RSS (con paginación)
 
**Tipo:** Historia de Usuario
**Como** administrador o analista de medios,
**quiero** consultar el listado paginado y ordenado de fuentes RSS registradas, con filtros por canal, continente, categoría y estado activo/inactivo,
**para** poder auditar y gestionar el conjunto de fuentes configuradas sin recibir todo el listado de una sola vez cuando el volumen de fuentes crezca.
 
**Prioridad:** Alta
**Estimación relativa:** S *(orientativo, sujeto a Planning Poker; el cambio respecto a HU-RSS-003 es principalmente de forma de respuesta y de orden, no de lógica de filtrado)*
**Depende de contrato de API:** Sí — `GET /api/v1/sources` y `GET /api/v1/sources/{id}`
 
**Nota de grounding (motivo del cambio):** el equipo decidió paginar este listado por dos razones: (1) mantener la misma convención de API que HU-RSS-010 (Canales), y (2) el volumen esperado de fuentes RSS es significativamente mayor que el de canales — el equipo estima un mínimo de 20 fuentes registradas — lo que hace más necesaria la paginación aquí que en Canales. Reemplaza a HU-RSS-003, que queda Deprecada.
 
**Criterio de orden:** a diferencia de Canales (que se ordena alfabéticamente por "nombre"), `FuenteRSS` no tiene un campo de nombre propio. El equipo decidió ordenar el listado por `canal_id` en forma ascendente (agrupando las fuentes de un mismo canal/medio) y, dentro de un mismo canal, alfabéticamente por `url`.
 
### Criterios de aceptación (Gherkin)
 
```gherkin
Escenario: Listado paginado por defecto
  Dado que existen N fuentes RSS registradas (N > 10)
  Cuando el usuario envía GET a /api/v1/sources sin parámetros de paginación
  Entonces el sistema responde con código HTTP 200
  Y el cuerpo incluye un campo "items" con exactamente 10 elementos
  Y el campo "pagina" es igual a 1
  Y el campo "tamanio_pagina" es igual a 10
  Y el campo "total" es igual a N
 
Escenario: Orden del listado por canal y url
  Dado que existen fuentes RSS de distintos canales y con distintas URLs
  Cuando el usuario envía GET a /api/v1/sources
  Entonces los elementos de "items" están ordenados en forma ascendente por "canal_id"
  Y, dentro de un mismo "canal_id", ordenados alfabéticamente por "url"
 
Escenario: Solicitud de una página específica
  Dado que existen N fuentes RSS registradas (N > 20)
  Cuando el usuario envía GET a /api/v1/sources?pagina=2
  Entonces el sistema responde con código HTTP 200
  Y el campo "items" contiene los elementos correspondientes a la página 2 según `tamanio_pagina`
  Y el campo "pagina" es igual a 2
 
Escenario: tamanio_pagina personalizado dentro del máximo permitido
  Cuando el usuario envía GET a /api/v1/sources?tamanio_pagina=50
  Entonces el sistema responde con código HTTP 200
  Y el campo "items" contiene como máximo 50 elementos
 
Escenario: Rechazo por tamanio_pagina fuera de rango
  Cuando el usuario envía GET a /api/v1/sources?tamanio_pagina=51
  Entonces el sistema responde con código HTTP 400
 
Escenario: Filtrado por continente combinado con paginación
  Dado que existen fuentes RSS en distintos continentes
  Cuando el usuario envía GET a /api/v1/sources?continente=America&pagina=1
  Entonces el sistema responde con código HTTP 200
  Y el 100% de los elementos de "items" pertenecen a un canal cuyo continente es "America"
 
Escenario: Listado vacío
  Dado que no existen fuentes RSS registradas
  Cuando el usuario envía GET a /api/v1/sources
  Entonces el sistema responde con código HTTP 200
  Y el campo "items" es un array vacío
  Y el campo "total" es igual a 0
 
Escenario: Consulta de detalle de una fuente existente
  Dado que existe una fuente RSS con id=X
  Cuando el usuario envía GET a /api/v1/sources/X
  Entonces el sistema responde con código HTTP 200
  Y el cuerpo incluye los datos completos de esa única fuente (sin paginación: el detalle de un único recurso no aplica el envoltorio de paginación)
 
Escenario: Consulta de detalle de una fuente inexistente
  Dado que no existe ninguna fuente RSS con id=X
  Cuando el usuario envía GET a /api/v1/sources/X
  Entonces el sistema responde con código HTTP 404
```
 
### Definition of Done
(Bloque general DoD, sección 14 — incluye adicionalmente: validación de que los filtros combinados con paginación no producen errores 500 con parámetros vacíos, y prueba específica del orden por `canal_id`+`url` y del límite de `tamanio_pagina`.) ** Cobertura y build/deploy verificados en pipeline (incluye la prueba `test_listar_fuentes_filtra_por_canal_id` y el round-trip POST→GET de HU-RSS-002/003-v2);  "SonarQube sin críticos" pendiente de revisión de dashboard — ver "Evidencia de verificación de DoD".**
 
---
 
## HU-RSS-004 — Modificación de Fuente RSS
 
**Tipo:** Historia de Usuario
**Como** administrador del sistema,
**quiero** modificar los datos de una fuente RSS existente (URL, categoría, estado activo/inactivo),
**para** mantener actualizada la configuración de captura sin necesidad de eliminar y recrear la fuente.
 
**Prioridad:** Media
**Estimación relativa:** S *(orientativo, sujeto a Planning Poker)*
**Depende de contrato de API:** Sí — `PUT /api/v1/sources/{id}` y `PATCH /api/v1/sources/{id}`
 
### Criterios de aceptación (Gherkin)
 
```gherkin
Escenario: Actualización completa exitosa (PUT)
  Dado que existe una fuente RSS con id=X
  Cuando el administrador envía PUT a /api/v1/sources/X con todos los campos obligatorios válidos
  Entonces el sistema responde con código HTTP 200
  Y los campos de la fuente quedan reemplazados por los valores enviados
 
Escenario: Actualización parcial exitosa (PATCH)
  Dado que existe una fuente RSS con id=X
  Cuando el administrador envía PATCH a /api/v1/sources/X con únicamente el campo "activo"=falso
  Entonces el sistema responde con código HTTP 200
  Y únicamente el campo "activo" cambia de valor, el resto de campos permanece sin modificar
 
Escenario: Actualización de fuente inexistente
  Dado que no existe ninguna fuente RSS con id=X
  Cuando el administrador envía PUT o PATCH a /api/v1/sources/X
  Entonces el sistema responde con código HTTP 404
 
Escenario: Idempotencia de PUT
  Dado que existe una fuente RSS con id=X
  Cuando el administrador envía dos veces consecutivas la misma solicitud PUT a /api/v1/sources/X
  Entonces el estado final de la fuente es idéntico tras ambas ejecuciones
```
 
### Definition of Done
(Bloque general DoD, sección 14.) **Cobertura y build/deploy verificados en pipeline;  "SonarQube sin críticos" pendiente de revisión de dashboard — ver "Evidencia de verificación de DoD".**
 
---
 
## HU-RSS-005 — Eliminación de Fuente RSS
 
**Tipo:** Historia de Usuario
**Como** administrador del sistema,
**quiero** eliminar una fuente RSS que ya no debe capturarse,
**para** evitar que el cron siga consultándola innecesariamente.
 
**Prioridad:** Media
**Estimación relativa:** S *(orientativo, sujeto a Planning Poker)*
**Depende de contrato de API:** Sí — `DELETE /api/v1/sources/{id}`
 
### Criterios de aceptación (Gherkin)
 
```gherkin
Escenario: Eliminación exitosa
  Dado que existe una fuente RSS con id=X
  Cuando el administrador envía DELETE a /api/v1/sources/X
  Entonces el sistema responde con código HTTP 204
  Y una consulta posterior GET a /api/v1/sources/X responde con código HTTP 404
 
Escenario: Eliminación de fuente inexistente
  Dado que no existe ninguna fuente RSS con id=X
  Cuando el administrador envía DELETE a /api/v1/sources/X
  Entonces el sistema responde con código HTTP 404
```
 
**Nota de diseño (a validar por el equipo):** dado que las noticias almacenadas referencian su fuente RSS de origen (sección 4.2.4), debe definirse si la eliminación de una fuente implica eliminación en cascada de sus noticias asociadas o desasociación (soft delete). **No especificado en el PDF — requiere decisión del equipo**, documentada en un ADR posterior si aplica.
 
### Definition of Done
(Bloque general DoD, sección 14.) **Cobertura y build/deploy verificados en pipeline (el código implementado usa soft delete — `activo=false` — conforme al `design.md` de OpenSpec del equipo); ⚠️ "SonarQube sin críticos" pendiente de revisión de dashboard — ver "Evidencia de verificación de DoD".**
 
---
 
## HU-RSS-006 — Cron automático de captura de noticias
 
**Tipo:** Historia Técnica / Enabler Story *(el actor es el propio sistema, según sección 4, Historias de Usuario, de las instrucciones del proyecto)*
**Como** sistema HumWorld,
**quiero** recorrer automáticamente, de forma periódica, todas las fuentes RSS activas y almacenar las noticias nuevas encontradas,
**para** mantener actualizado el conjunto de datos usado en el cálculo del humor mundial.
 
**Prioridad:** Alta
**Estimación relativa:** L *(orientativo, sujeto a Planning Poker — historia con mayor incertidumbre técnica por la integración con feeds externos)*
**Depende de contrato de API:** No expone endpoint propio de invocación automática (se ejecuta por scheduler interno); consume el modelo de datos definido por HU-RSS-001 y HU-RSS-002.
 
### Criterios de aceptación (Gherkin)
 
```gherkin
Escenario: Ejecución del cron sobre fuentes activas
  Dado que existen fuentes RSS con "activo"=verdadero
  Cuando se dispara la ejecución programada del cron
  Entonces el sistema intenta consultar el 100% de las fuentes con "activo"=verdadero
  Y para cada noticia nueva (no existente previamente por identificador único de entrada del feed) se crea exactamente 1 registro en la tabla de noticias
  Y cada registro de noticia creado incluye fecha y hora de registro (timestamp de captura)
 
Escenario: Fuente RSS temporalmente inaccesible
  Dado que una fuente RSS activa no responde o responde con error
  Cuando el cron intenta consultarla
  Entonces el fallo de esa fuente no impide que el cron continúe procesando el resto de fuentes activas
  Y el incidente queda registrado en el log del sistema con la fuente afectada y el motivo del fallo
 
Escenario: Noticia duplicada
  Dado que una noticia ya fue capturada previamente desde una fuente (mismo identificador único del ítem RSS)
  Cuando el cron vuelve a encontrar esa misma noticia en una ejecución posterior
  Entonces el sistema no crea un registro duplicado
```
 
**Nota (grounding — resiliencia):** esta historia se apoya en los patrones de resiliencia (Circuit Breaker, Timeout explícito, Retry con backoff exponencial acotado) que se documentan formalmente en **ADR-002**, conforme a la sección 13 de las instrucciones del proyecto.
 
**Nota (grounding — periodicidad):** el PDF (sección 4.2.3) establece que "la periodicidad de ejecución del cron será un parámetro que el usuario puede cambiar", pero no fija un valor por defecto. El valor por defecto de periodicidad queda como parámetro configurable, con un **valor propuesto de 30 minutos** (ver HU-RSS-007, nota de valor propuesto), pendiente de ratificación formal por el equipo.
 
### Definition of Done
- Además del bloque general DoD (sección 14):
- Pruebas unitarias que simulan (mock) fuentes RSS caídas, lentas y con contenido malformado, sin llamadas reales a servicios externos.
- Prueba de integración que verifica que un fallo aislado de una fuente no interrumpe el procesamiento del resto (ver Escenario 2).
---
 
## HU-RSS-007 — Configuración de periodicidad del cron de captura
 
**Tipo:** Historia de Usuario
**Como** administrador del sistema,
**quiero** modificar el parámetro de periodicidad con el que se ejecuta el cron de captura,
**para** ajustar la frecuencia de actualización de noticias según las necesidades operativas.
 
**Prioridad:** Media
**Estimación relativa:** S *(orientativo, sujeto a Planning Poker)*
**Depende de contrato de API:** Sí — `GET /api/v1/config` y `PUT /api/v1/config` (endpoint de Configuraciones, sección 10.2 del PDF)
 
**Valor propuesto para "periodicidad_cron_minutos" (pendiente de validación del equipo): 30 minutos.** El PDF (§4.2.3) exige que el valor sea configurable pero no fija un default. Justificación: es un intervalo habitual para agregadores de noticias RSS — suficientemente frecuente para dar una sensación real de "tiempo real" en la demo/evaluación del curso, sin golpear las ~50 fuentes estimadas cada muy pocos minutos (riesgo de rate-limiting) ni sobrecargar el pipeline durante desarrollo/CI. No es una cifra tomada del PDF — es un punto de partida a validar por el equipo, con el mismo tratamiento que una estimación de Planning Poker.
 
### Criterios de aceptación (Gherkin)
 
```gherkin
Escenario: Consulta de la periodicidad configurada
  Dado que existe un parámetro de configuración "periodicidad_cron_minutos"
  Cuando el administrador envía GET a /api/v1/config
  Entonces el sistema responde con código HTTP 200
  Y el cuerpo incluye el valor actual de "periodicidad_cron_minutos"
 
Escenario: Actualización exitosa de la periodicidad
  Dado que el administrador envía PUT a /api/v1/config con "periodicidad_cron_minutos"=un entero positivo
  Cuando el sistema procesa la solicitud
  Entonces el sistema responde con código HTTP 200
  Y la siguiente ejecución del cron respeta el nuevo valor de periodicidad
 
Escenario: Rechazo de valor inválido
  Dado que el administrador envía PUT a /api/v1/config con "periodicidad_cron_minutos"=0 o un valor negativo
  Cuando el sistema procesa la solicitud
  Entonces el sistema responde con código HTTP 400
  Y el valor de configuración previo se mantiene sin cambios
```
 
### Definition of Done
(Bloque general DoD, sección 14.)
 
---
 
## HU-RSS-008 — Actualización manual de captura (una o varias fuentes)
 
**Tipo:** Historia de Usuario
**Como** administrador del sistema,
**quiero** forzar manualmente la captura de noticias para una fuente RSS específica o para un conjunto de fuentes,
**para** obtener noticias actualizadas sin esperar a la siguiente ejecución programada del cron.
 
**Prioridad:** Media
**Estimación relativa:** M *(orientativo, sujeto a Planning Poker)*
**Depende de contrato de API:** Sí — dos endpoints:
- `POST /api/v1/sources/{id}/captures` — captura de una fuente puntual.
- `POST /api/v1/captures` con body `{"fuente_ids": [...]}` — captura de un lote de fuentes.
Ambos respetan la convención de sustantivos en plural sin verbos en la URL (sección 6 de las instrucciones del proyecto). El endpoint individual puede implementarse internamente reutilizando el mismo servicio que el de lote (invocándolo con una lista de un único id), para no duplicar lógica — decisión de diseño de la capa de Servicios, no cambia el contrato expuesto.
 
**Nota de grounding (procesamiento síncrono):** ambos endpoints son **síncronos**: el sistema espera a que la captura termine (aplicando los patrones de resiliencia de ADR-002 — Timeout explícito, Retry acotado con backoff exponencial, Circuit Breaker — que acotan el tiempo máximo de espera por fuente) y devuelve el resultado en la misma respuesta HTTP. Se descarta, para el alcance de este curso, el procesamiento asíncrono (202 + endpoint de consulta de estado), por la complejidad de infraestructura adicional que implicaría (cola de tareas, tabla de estado de trabajos, endpoint nuevo) sin un sistema de colas aprobado en ADR-001/ADR-002. Si el volumen de uso creciera significativamente, esta decisión podría revisarse en un ADR posterior — está fuera del alcance actual.
 
### Criterios de aceptación (Gherkin)
 
```gherkin
Escenario: Captura manual exitosa de una única fuente
  Dado que existe una fuente RSS activa con id=X
  Cuando el administrador envía POST a /api/v1/sources/X/captures
  Entonces el sistema responde con código HTTP 201
  Y se ejecuta sobre la fuente X el mismo procedimiento de captura y deduplicación que utiliza el cron automático (HU-RSS-006)
  Y el cuerpo de la respuesta incluye el resultado de la captura para la fuente X (estado y cantidad de noticias nuevas)
 
Escenario: Captura manual de un conjunto de fuentes
  Dado que el administrador envía POST a /api/v1/captures con un campo "fuente_ids" con una lista de N ids de fuentes RSS válidas
  Cuando el sistema procesa la solicitud
  Entonces el sistema responde con código HTTP 201
  Y el sistema intenta capturar el 100% de las fuentes indicadas en la lista
  Y el fallo de una fuente del conjunto no impide el procesamiento del resto
  Y el cuerpo de la respuesta incluye un resultado individual por cada fuente del lote (estado y cantidad de noticias nuevas, o motivo de fallo)
 
Escenario: Captura manual sobre fuente inactiva
  Dado que la fuente RSS con id=X tiene "activo"=falso
  Cuando el administrador envía POST a /api/v1/sources/X/captures
  Entonces el sistema responde con código HTTP 409, indicando que la fuente está inactiva
```
 
### Definition of Done
(Bloque general DoD, sección 14 — más pruebas unitarias con mocks para el escenario de fuente inactiva y de conjunto parcialmente fallido.)
 
---
 
## HU-RSS-009 — Carga inicial de fuentes RSS por continente (seed)
 
**Tipo:** Historia de Usuario *(el actor es el administrador del sistema, no el propio sistema, por lo que no se clasifica como Enabler Story — ver Tabla de control de versiones para el historial de este cambio)*
**Como** administrador del sistema,
**quiero** disparar manualmente la carga inicial de canales y fuentes RSS de ejemplo agrupados por continente,
**para** disponer de datos de partida sin tener que darlos de alta uno por uno, cumpliendo el requisito de "carga inicial de fuentes RSS por continente".
 
**Prioridad:** Alta
**Estimación relativa:** S *(orientativo, sujeto a Planning Poker)*
**Depende de contrato de API:** Sí — `POST /api/v1/seeds` *(recurso ya incorporado al contrato OpenSpec — ver `contrato-canales-fuentes-rss.openapi.yaml` v1.6.0). Internamente reutiliza el mismo servicio de creación que `POST /api/v1/channels` y `POST /api/v1/sources` (HU-RSS-001/002), para no duplicar validaciones.*
 
**Nota de grounding (mecanismo de carga):** al pasar el actor a "administrador del sistema", la carga se dispara **vía API** (no vía script/migración directa a la base de datos), reutilizando el servicio de alta ya existente de Canales y Fuentes — así se prueba de paso que HU-RSS-001/002 funcionan correctamente, sin duplicar lógica de validación en dos lugares.
 
### Criterios de aceptación (Gherkin)
 
```gherkin
Escenario: Carga inicial exitosa en base de datos vacía
  Dado que la base de datos no contiene canales ni fuentes RSS
  Cuando el administrador envía POST a /api/v1/seeds
  Entonces el sistema responde con código HTTP 201
  Y se crea al menos 1 canal y 1 fuente RSS por cada uno de los 5 continentes contemplados (América, Europa, Asia, África, Oceanía)
  Y cada fuente creada queda asociada a un canal válido
  Y el cuerpo de la respuesta incluye la cantidad de canales y de fuentes creados
 
Escenario: Ejecución repetida de la carga inicial
  Dado que la base de datos ya contiene los canales y fuentes cargados inicialmente
  Cuando el administrador envía POST a /api/v1/seeds nuevamente
  Entonces el sistema responde con código HTTP 201
  Y no se crean registros duplicados
  Y el cuerpo de la respuesta indica 0 canales y 0 fuentes nuevos creados
```
 
**Nota de grounding (alcance de datos):** el PDF (sección 4.2.1) exige la existencia de una "carga inicial de fuentes RSS por continente" pero **no especifica el listado exacto ni el número mínimo de fuentes por continente**; la sección 5 (Fuentes de Información, pág. 9) ofrece únicamente ejemplos de medios españoles a modo ilustrativo. De los 3 puntos que quedaban pendientes de esta historia, el equipo cerró 2:
 
1. **Continentes contemplados:** los 5 continentes habitados (América, Europa, Asia, África, Oceanía). El seed debe crear al menos 1 canal y 1 fuente por cada uno de estos 5.
2. **Clave de idempotencia:** `nombre` para Canales, `url` para Fuentes — por consistencia con el criterio de duplicado ya usado en HU-RSS-001 (código 409).
3. **Listado real de fuentes RSS por continente (URLs verificadas) — SIGUE PENDIENTE.** A diferencia de los dos puntos anteriores, esto no es una decisión de alcance sino datos concretos (URLs de feeds reales que funcionen) que el equipo debe investigar y verificar antes de escribir el seed — el agente PO/Arquitecto no propone URLs de feeds RSS reales aquí, para evitar el riesgo de inventar fuentes que no existan o hayan cambiado de dirección.
**Referencia útil:** el equipo estimó un mínimo de 20 fuentes RSS en total como volumen esperado — repartido entre los 5 continentes ya confirmados, son un mínimo orientativo de 4 fuentes por continente (esta cifra puede orientar, no sustituir, el diseño final del seed).
 
### Definition of Done
(Bloque general DoD, sección 14 — adaptado: no aplica "validado visualmente" (sin UI); sí aplica prueba de idempotencia del endpoint, ver Escenario 2.)
 
---
 
## HU-RSS-010 — Consulta y listado de Canales de Noticias
 
**Tipo:** Historia de Usuario
**Como** administrador o analista de medios,
**quiero** consultar el listado paginado de canales de noticias registrados, ordenado alfabéticamente y opcionalmente filtrado por continente, y el detalle de un canal específico,
**para** poder conocer los medios de comunicación configurados en el sistema y auditar la cobertura de canales por continente.
 
**Prioridad:** Alta *(misma prioridad que HU-RSS-001, de la que depende funcionalmente al consultar la misma entidad `CanalNoticias`)*
**Estimación relativa:** S *(punto de partida orientativo; debe validarse con Planning Poker real del equipo — no es un valor definitivo)*
**Depende de contrato de API:** Sí — `GET /api/v1/channels` y `GET /api/v1/channels/{id}`
 
**Nota de grounding:** origen y trazabilidad de esta historia en la tabla de control de versiones. Convención de paginación: parámetros de query `pagina` (entero, mínimo 1, por defecto 1) y `tamanio_pagina` (entero, por defecto 10, máximo 50). La respuesta de `GET /api/v1/channels` es un objeto con `items` (el array de canales de la página actual), `pagina`, `tamanio_pagina` y `total`. Esta misma convención se aplica también a Fuentes RSS (ver HU-RSS-003-v2), para mantener consistencia de API.
 
### Criterios de aceptación (Gherkin)
 
```gherkin
Escenario: Listado paginado por defecto
  Dado que existen N canales de noticias registrados (N > 10)
  Cuando el usuario envía GET a /api/v1/channels sin parámetros de paginación
  Entonces el sistema responde con código HTTP 200
  Y el cuerpo incluye un campo "items" con exactamente 10 elementos
  Y el campo "pagina" es igual a 1
  Y el campo "tamanio_pagina" es igual a 10
  Y el campo "total" es igual a N
 
Escenario: Orden alfabético del listado
  Dado que existen canales con nombres distintos
  Cuando el usuario envía GET a /api/v1/channels
  Entonces los elementos de "items" están ordenados alfabéticamente en forma ascendente por el campo "nombre"
 
Escenario: Solicitud de una página específica
  Dado que existen N canales de noticias registrados (N > 20)
  Cuando el usuario envía GET a /api/v1/channels?pagina=2
  Entonces el sistema responde con código HTTP 200
  Y el campo "items" contiene los elementos correspondientes a la página 2 según `tamanio_pagina`
  Y el campo "pagina" es igual a 2
 
Escenario: tamanio_pagina personalizado dentro del máximo permitido
  Cuando el usuario envía GET a /api/v1/channels?tamanio_pagina=50
  Entonces el sistema responde con código HTTP 200
  Y el campo "items" contiene como máximo 50 elementos
 
Escenario: Rechazo por tamanio_pagina fuera de rango
  Cuando el usuario envía GET a /api/v1/channels?tamanio_pagina=51
  Entonces el sistema responde con código HTTP 400
 
Escenario: Filtrado por continente combinado con paginación
  Dado que existen canales de noticias en distintos continentes
  Cuando el usuario envía GET a /api/v1/channels?continente=America&pagina=1
  Entonces el sistema responde con código HTTP 200
  Y el 100% de los elementos de "items" tienen "continente"="America"
 
Escenario: Listado vacío
  Dado que no existen canales de noticias registrados
  Cuando el usuario envía GET a /api/v1/channels
  Entonces el sistema responde con código HTTP 200
  Y el campo "items" es un array vacío
  Y el campo "total" es igual a 0
 
Escenario: Consulta de detalle de un canal existente
  Dado que existe un canal de noticias con id=X
  Cuando el usuario envía GET a /api/v1/channels/X
  Entonces el sistema responde con código HTTP 200
  Y el cuerpo incluye los datos completos de ese único canal (nombre, continente, pais, descripcion; sin envoltorio de paginación)
 
Escenario: Consulta de detalle de un canal inexistente
  Dado que no existe ningún canal de noticias con id=X
  Cuando el usuario envía GET a /api/v1/channels/X
  Entonces el sistema responde con código HTTP 404
```
 
### Definition of Done
(Bloque general DoD, sección 14 — incluye adicionalmente: validación de que el filtro por continente combinado con paginación y con parámetro vacío o ausente no produce error 500, y prueba específica del límite de `tamanio_pagina`.) ** Cobertura y build/deploy verificados en pipeline (incluye el round-trip POST→GET de HU-RSS-001/010);  "SonarQube sin críticos" pendiente de revisión de dashboard — ver "Evidencia de verificación de DoD".**
 
---
 
## Resumen de trazabilidad
 
| HU | Tipo | Prioridad | Endpoint(s) asociado(s) | Origen (PDF) |
|---|---|---|---|---|
| HU-RSS-001 | Historia de Usuario | Alta | `POST /api/v1/channels` | 4.2.1 |
| HU-RSS-002 | Historia de Usuario | Alta | `POST /api/v1/sources` | 4.2.1 |
| HU-RSS-003 | **Deprecada** (ver HU-RSS-003-v2) | Alta | `GET /api/v1/sources`, `GET /api/v1/sources/{id}` | 10.2 |
| HU-RSS-003-v2 | Historia de Usuario | Alta | `GET /api/v1/sources` (paginado, orden por `canal_id`+`url`), `GET /api/v1/sources/{id}` | 10.2 |
| HU-RSS-004 | Historia de Usuario | Media | `PUT`/`PATCH /api/v1/sources/{id}` | 10.2 |
| HU-RSS-005 | Historia de Usuario | Media | `DELETE /api/v1/sources/{id}` | 10.2 |
| HU-RSS-006 | Enabler Story | Alta | (interno — scheduler) | 4.2.3, 4.2.4 |
| HU-RSS-007 | Historia de Usuario | Media | `GET`/`PUT /api/v1/config` | 4.2.3, 10.2 |
| HU-RSS-008 | Historia de Usuario | Media | `POST /api/v1/sources/{id}/captures` (individual, síncrono), `POST /api/v1/captures` (lote, síncrono) | 4.2.3 |
| HU-RSS-009 | Historia de Usuario | Alta | `POST /api/v1/seeds` (confirmado; continentes y clave de idempotencia definidos, listado real de fuentes aún pendiente) | 4.2.1 |
| HU-RSS-010 | Historia de Usuario | Alta | `GET /api/v1/channels` (paginado, orden alfabético por `nombre`), `GET /api/v1/channels/{id}` | 4.2.1 |
 
**Recordatorio:** todas las estimaciones (S/M/L) son un punto de partida orientativo generado por el agente Product Owner/Arquitecto, sujetas a validación mediante Planning Poker real por el equipo (sección 4 de las instrucciones del proyecto).
 
