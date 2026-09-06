# Historias de Usuario — Módulo Captura RSS

**Proyecto:** HumWorld — Equipo 3
**Módulo:** Captura RSS (gestión de canales/fuentes, cron de captura, actualización manual)
**Fuente:** `0 PROYECTO_FINAL_HUMWORLD 260714.pdf`, secciones 4.2.1 (Orígenes de Información, pág. 5), 4.2.3 (Captura de Información, pág. 5), 4.2.4 (Procesado de la información, pág. 6) y 10.2 (Endpoints mínimos obligatorios, pág. 13).
**Versión del documento:** v1.4 — Sesión 2026-08-31 (nota de grounding de HU-RSS-010 acortada por redundancia con la tabla de control de versiones)
**Estado general:** Propuesto (pendiente de revisión crítica y Planning Poker por el equipo, según Práctica P3, Paso 2 y Paso 4)

> **Nota de alcance (grounding):** La tabla de endpoints mínimos obligatorios (sección 10.2) solo lista `/sources` (Fuentes RSS) como categoría de endpoint explícita. La gestión de **canales** (medios de comunicación) está exigida funcionalmente en la sección 4.2.1 ("El sistema permitirá dar de alta canales (medios) y fuentes RSS dentro de cada canal"), pero no aparece como categoría separada en la tabla de mínimos. Dado que la tabla se define como "mínimos obligatorios" (piso, no techo) y la funcionalidad de canales está explícitamente descrita en el cuerpo del documento, se incluye aquí un recurso `/channels` adicional. **Esta interpretación debe ser confirmada por el equipo** antes de congelar el contrato de API definitivo.
>
> **Actualización 2026-08-26:** el equipo confirmó esta interpretación al decidir formalizar **HU-RSS-010** (ver más abajo), que documenta con criterios Gherkin propios el listado de canales (`GET /api/v1/channels`, `GET /api/v1/channels/{id}`) que ya estaba expuesto en el contrato OpenAPI pero atribuido de forma implícita a HU-RSS-001.
>
> **Actualización 2026-08-30:** el equipo decidió paginar tanto el listado de Canales (HU-RSS-010) como el de Fuentes RSS (HU-RSS-003 → **HU-RSS-003-v2**), para mantener una convención de API consistente y porque el número de fuentes RSS puede crecer considerablemente (el equipo estima un mínimo de 20 fuentes). Ver el detalle de la convención de paginación en HU-RSS-010 y HU-RSS-003-v2.
>
> **Actualización 2026-08-30 (cont.):** el equipo definió el criterio de orden que quedaba pendiente en HU-RSS-003-v2: el listado de Fuentes RSS se ordena por `canal_id` (agrupando las fuentes de un mismo canal) y, dentro de cada canal, alfabéticamente por `url`.
>
> **Nota de alcance (algoritmo de humor):** El valor de "humor" que se persiste junto a cada noticia (sección 4.2.4) es calculado por el módulo de Análisis de Sentimiento (fuera de alcance de este documento). Las historias de este módulo únicamente contemplan la captura, almacenamiento y gestión de metadatos de fuentes y noticias — no el cálculo del valor de humor en sí.

---

## Tabla de control de versiones

| ID | Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|---|
| HU-RSS-001 a HU-RSS-009 | v1 | 2026-08-14 | Creación inicial del backlog del módulo Captura RSS |
| HU-RSS-010 | v1 | 2026-08-26 | Nueva historia: formaliza con criterios Gherkin propios el listado de canales de noticias (`GET /api/v1/channels`, `GET /api/v1/channels/{id}`), endpoint que ya existía en el contrato OpenAPI pero estaba atribuido de forma implícita a HU-RSS-001. Decisión tomada en sesión de trabajo tras revisar la práctica P6-OpenSpec-II, que exige una segunda historia de consulta sobre la misma entidad de la historia piloto (HU-RSS-001). No modifica HU-RSS-001, que conserva su alcance original (alta de canal). Se corrige en consecuencia la trazabilidad de `contrato-canales-fuentes-rss.openapi.yaml`. |
| HU-RSS-010 | v1 (completada) | 2026-08-30 | Se completan los criterios que quedaban abiertos desde su creación (no se trata de una historia ya publicada/ratificada, por lo que no aplica el proceso de deprecación de la sección 3): orden del listado (alfabético ascendente por "nombre") y paginación (parámetros `pagina`/`tamanio_pagina`, valores por defecto 10 y máximo 50, respuesta en formato objeto con `items` + metadatos). |
| HU-RSS-003 | v1 → **Deprecada** | 2026-08-30 | Se deprecа en favor de **HU-RSS-003-v2**, que agrega paginación al listado de Fuentes RSS por consistencia con HU-RSS-010 y porque el volumen esperado de fuentes (mínimo 20, según estimación del equipo) lo justifica. El endpoint (`GET /api/v1/sources`) no cambia de ruta, pero sí cambia la forma de la respuesta (de array simple a objeto paginado) y se agregan parámetros de query. Se corrige en consecuencia `contrato-canales-fuentes-rss.openapi.yaml`. |
| HU-RSS-003-v2 | v1 | 2026-08-30 | Creación de la versión paginada de la consulta de Fuentes RSS. Motivo: consistencia de convención de API con HU-RSS-010 y volumen esperado de datos. Queda abierta la definición del criterio de orden del listado (Fuentes no tiene un campo "nombre" como Canales — **pendiente de decisión del equipo**). |
| HU-RSS-003-v2 | v1 (completada) | 2026-08-30 | Se define el criterio de orden que quedaba pendiente: ordenar por `canal_id` ascendente (agrupando las fuentes de un mismo canal/medio) y, dentro de un mismo canal, alfabéticamente por `url`. |
| HU-RSS-010 | v1 (editorial) | 2026-08-31 | Se acorta la nota de grounding de la historia (quedaba redundante con esta misma tabla, fila 2026-08-26) a una referencia breve. No cambia alcance, criterios ni prioridad/estimación. |

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
- Cobertura de pruebas del módulo ≥ 80%, verificada en el pipeline de GitHub Actions.
- Análisis de SonarQube ejecutado sin issues críticos ni deuda técnica no justificada.
- Endpoint documentado en Swagger/OpenAPI (`/api/docs`).
- Build y despliegue exitosos en el job de Docker (dependiente de `needs: [test, sonarqube]`).

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
(Idéntico al bloque general de la sección 14 de las instrucciones del proyecto — código revisado, pruebas con mocks, cobertura ≥80%, SonarQube sin críticos, Swagger actualizado, build/deploy con `needs: [test, sonarqube]`.)

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

> **Nota de grounding (motivo del cambio):** el equipo decidió (sesión 2026-08-30) paginar este listado por dos razones: (1) mantener la misma convención de API que HU-RSS-010 (Canales), y (2) el volumen esperado de fuentes RSS es significativamente mayor que el de canales — el equipo estima un mínimo de 20 fuentes registradas — lo que hace más necesaria la paginación aquí que en Canales. Reemplaza a HU-RSS-003, que queda Deprecada.
>
> **Criterio de orden (decidido por el equipo, sesión 2026-08-30):** a diferencia de Canales (que se ordena alfabéticamente por "nombre"), `FuenteRSS` no tiene un campo de nombre propio. El equipo decidió ordenar el listado por `canal_id` en forma ascendente (agrupando las fuentes de un mismo canal/medio) y, dentro de un mismo canal, alfabéticamente por `url`.

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
(Bloque general DoD, sección 14 — incluye adicionalmente: validación de que los filtros combinados con paginación no producen errores 500 con parámetros vacíos, y prueba específica del orden por `canal_id`+`url` y del límite de `tamanio_pagina`.)

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
(Bloque general DoD, sección 14.)

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
(Bloque general DoD, sección 14.)

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

**Nota (grounding — periodicidad):** el PDF (sección 4.2.3) establece que "la periodicidad de ejecución del cron será un parámetro que el usuario puede cambiar", pero no fija un valor por defecto. El valor por defecto de periodicidad **no está especificado y debe ser definido por el equipo** (ver HU-RSS-007).

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
**Depende de contrato de API:** Sí — endpoint dedicado a disparar una captura (a definir como recurso, p. ej. `POST /api/v1/sources/{id}/captures` o `POST /api/v1/captures` con lista de ids en el cuerpo — **nombre exacto de recurso pendiente de confirmación por el equipo** para respetar la convención de sustantivos en plural sin verbos en la URL).

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Captura manual exitosa de una única fuente
  Dado que existe una fuente RSS activa con id=X
  Cuando el administrador dispara una captura manual para la fuente X
  Entonces el sistema responde con código HTTP 201 o 202 (según se procese de forma síncrona o asíncrona — a definir por el equipo)
  Y se ejecuta sobre la fuente X el mismo procedimiento de captura y deduplicación que utiliza el cron automático (HU-RSS-006)

Escenario: Captura manual de un conjunto de fuentes
  Dado que el administrador indica una lista de N ids de fuentes RSS válidas
  Cuando dispara la captura manual del conjunto
  Entonces el sistema intenta capturar el 100% de las fuentes indicadas en la lista
  Y el fallo de una fuente del conjunto no impide el procesamiento del resto

Escenario: Captura manual sobre fuente inactiva
  Dado que la fuente RSS con id=X tiene "activo"=falso
  Cuando el administrador dispara una captura manual para la fuente X
  Entonces el sistema responde con código HTTP 409, indicando que la fuente está inactiva
```

### Definition of Done
(Bloque general DoD, sección 14 — más pruebas unitarias con mocks para el escenario de fuente inactiva y de conjunto parcialmente fallido.)

---

## HU-RSS-009 — Carga inicial de fuentes RSS por continente (seed)

**Tipo:** Historia Técnica / Enabler Story *(proceso de inicialización del sistema, no una interacción directa de un usuario final en tiempo de ejecución)*
**Como** equipo de desarrollo,
**quiero** disponer de un procedimiento de carga inicial (seed) que registre canales y fuentes RSS de ejemplo agrupados por continente,
**para** cumplir con el requisito de "carga inicial de fuentes RSS por continente" y disponer de datos de partida para desarrollo y pruebas.

**Prioridad:** Alta
**Estimación relativa:** S *(orientativo, sujeto a Planning Poker)*
**Depende de contrato de API:** No expone endpoint propio; utiliza internamente `POST /api/v1/channels` y `POST /api/v1/sources` (o inserción directa vía script/migración, a decidir por el equipo).

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Ejecución del script de carga inicial en base de datos vacía
  Dado que la base de datos no contiene canales ni fuentes RSS
  Cuando se ejecuta el procedimiento de carga inicial
  Entonces se crea al menos 1 canal y 1 fuente RSS por cada continente contemplado
  Y cada fuente creada queda asociada a un canal válido

Escenario: Ejecución repetida del script de carga inicial
  Dado que la base de datos ya contiene los canales y fuentes cargados inicialmente
  Cuando se vuelve a ejecutar el procedimiento de carga inicial
  Entonces no se crean registros duplicados
```

**Nota de grounding:** el PDF (sección 4.2.1) exige la existencia de una "carga inicial de fuentes RSS por continente" pero **no especifica el listado exacto ni el número mínimo de fuentes por continente**; la sección 5 (Fuentes de Información, pág. 9) ofrece únicamente ejemplos de medios españoles a modo ilustrativo. El listado definitivo de fuentes semilla **debe ser definido por el equipo**, cuidando la cobertura de continentes exigida. **Referencia útil:** en la sesión 2026-08-30 el equipo estimó un mínimo de 20 fuentes RSS en total como volumen esperado — esta cifra puede orientar (no sustituir) el diseño del seed.

### Definition of Done
(Bloque general DoD, sección 14 — adaptado: no aplica cobertura de pruebas de UI; sí aplica prueba de idempotencia del script, ver Escenario 2.)

---

## HU-RSS-010 — Consulta y listado de Canales de Noticias

**Tipo:** Historia de Usuario
**Como** administrador o analista de medios,
**quiero** consultar el listado paginado de canales de noticias registrados, ordenado alfabéticamente y opcionalmente filtrado por continente, y el detalle de un canal específico,
**para** poder conocer los medios de comunicación configurados en el sistema y auditar la cobertura de canales por continente.

**Prioridad:** Alta *(misma prioridad que HU-RSS-001, de la que depende funcionalmente al consultar la misma entidad `CanalNoticias`)*
**Estimación relativa:** S *(punto de partida orientativo; debe validarse con Planning Poker real del equipo — no es un valor definitivo)*
**Depende de contrato de API:** Sí — `GET /api/v1/channels` y `GET /api/v1/channels/{id}`

> **Nota de grounding:** origen y trazabilidad de esta historia en la tabla de control de versiones (fila 2026-08-26). Convención de paginación (decidida por el equipo, sesión 2026-08-30): parámetros de query `pagina` (entero, mínimo 1, por defecto 1) y `tamanio_pagina` (entero, por defecto 10, máximo 50). La respuesta de `GET /api/v1/channels` es un objeto con `items` (el array de canales de la página actual), `pagina`, `tamanio_pagina` y `total`. Esta misma convención se aplica también a Fuentes RSS (ver HU-RSS-003-v2), para mantener consistencia de API.

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
(Bloque general DoD, sección 14 — incluye adicionalmente: validación de que el filtro por continente combinado con paginación y con parámetro vacío o ausente no produce error 500, y prueba específica del límite de `tamanio_pagina`.)

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
| HU-RSS-008 | Historia de Usuario | Media | `POST /api/v1/sources/{id}/captures` (a confirmar) | 4.2.3 |
| HU-RSS-009 | Enabler Story | Alta | (interno — script de seed) | 4.2.1 |
| HU-RSS-010 | Historia de Usuario | Alta | `GET /api/v1/channels` (paginado, orden alfabético por `nombre`), `GET /api/v1/channels/{id}` | 4.2.1 |

**Recordatorio:** todas las estimaciones (S/M/L) son un punto de partida orientativo generado por el agente Product Owner/Arquitecto, sujetas a validación mediante Planning Poker real por el equipo (sección 4 de las instrucciones del proyecto).
