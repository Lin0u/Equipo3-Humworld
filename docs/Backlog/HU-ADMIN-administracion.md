# Historias de Usuario — EPIC-ADMIN (Administración y Configuración)

**Proyecto:** HumWorld — Equipo 3
**Origen:** PDF de especificaciones, §4.2.5 (Purgado de información antigua), §4.3 punto 1 (Panel de administración) y §10.2 (`/config`: GET, PUT; `/news`: DELETE). Títulos y puntos tomados del backlog entregado en P3 (`Anexo-I-Planificacion-entregado-P3.md`, Sprint 4).
**Estado general:** HU-ADMIN-001 (parcial), HU-ADMIN-002 y HU-ADMIN-003 implementadas el 2026-10-19 (rama `feature/cierre-sprint`), pendientes de revisión en el PR y de ratificación del equipo. HU-ADMIN-004 formalizada el 2026-10-20, pendiente de implementación.
**Versión del documento:** v1.2. Ver la Tabla de control de versiones al final del documento.

> **Nota de grounding (valores propuestos):** el PDF exige que la caducidad sea "un parámetro modificable por el usuario", pero no fija su valor. Los valores de este documento — caducidad por defecto de **90 días** y ejecución del purgado automático **cada 24 horas** — son propuestos (decisión de la PO del 2026-10-19), no tomados del PDF, y quedan pendientes de ratificación del equipo con el mismo tratamiento que una estimación de Planning Poker. Justificación de los 90 días: cubren con holgura la ventana de 30 días del gráfico de evolución (HU-DASH-001-v3) y conservan historial suficiente para el umbral de entrenamiento del modelo de ML (1.000 noticias, ADR-004).

---

## HU-ADMIN-001 — Configuración de parámetros generales del sistema

**Tipo:** Historia de Usuario
**Como** administrador del sistema,
**quiero** consultar y modificar los parámetros generales del sistema,
**para** ajustar su comportamiento operativo sin tocar el código ni reiniciar la aplicación.

**Prioridad:** Media
**Estimación (Planning Poker P3):** 2 puntos *(punto de partida del P3, sujeto a revisión del equipo)*
**Depende de contrato de API:** Sí — `GET /api/v1/config` y `PUT /api/v1/config` (`contrato-canales-fuentes-rss.openapi.yaml` v1.8.0).
**Alcance implementado:** los dos parámetros que el PDF exige configurables: `periodicidad_cron_minutos` (§4.2.3, ya cubierto por HU-RSS-007) y `caducidad_noticias_dias` (§4.2.5, nuevo). Cualquier otro parámetro queda fuera de alcance hasta que el equipo lo defina.

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Consulta de la configuración general
  Dado que la periodicidad es 45 minutos y la caducidad es 60 días
  Cuando el administrador envía GET a /api/v1/config
  Entonces el sistema responde con código HTTP 200
  Y el cuerpo es {"periodicidad_cron_minutos": 45, "caducidad_noticias_dias": 60}

Escenario: Caducidad no persistida
  Dado que la tabla de configuración no contiene la caducidad
  Cuando el administrador envía GET a /api/v1/config
  Entonces el cuerpo incluye "caducidad_noticias_dias": 90

Escenario: Actualización de la caducidad
  Dado que la caducidad es 90 días
  Cuando el administrador envía PUT a /api/v1/config con periodicidad 30 y caducidad 15
  Entonces el sistema responde con código HTTP 200
  Y la siguiente ejecución del purgado usa 15 días

Escenario: PUT sin caducidad
  Dado que la caducidad es 90 días
  Cuando el administrador envía PUT a /api/v1/config solo con "periodicidad_cron_minutos": 60
  Entonces el sistema responde con código HTTP 200
  Y la caducidad sigue siendo 90 días

Escenario: Caducidad inválida
  Dado que la periodicidad es 30 minutos y la caducidad es 90 días
  Cuando el administrador envía PUT con periodicidad 45 y caducidad 0 o negativa
  Entonces el sistema responde con código HTTP 400
  Y ninguno de los dos valores cambia
```

### Definition of Done
(Bloque general DoD, sección 14.) Adicionalmente:
- Migración `c3f8a2d6e9b1` que inserta la caducidad inicial (90 días), con downgrade que la retira.
- Pruebas de compatibilidad: las pruebas existentes de HU-RSS-007 siguen pasando.

---

## HU-ADMIN-002 — Purgado automático de noticias antiguas

**Tipo:** Historia Técnica / Enabler Story *(el actor es el propio sistema)*
**Como** sistema HumWorld,
**quiero** eliminar periódicamente las noticias registradas antes del periodo de caducidad,
**para** que la base de datos no crezca sin límite y los dashboards trabajen solo con información vigente.

**Prioridad:** Media
**Estimación (Planning Poker P3):** 2 puntos *(punto de partida del P3, sujeto a revisión del equipo)*
**Depende de contrato de API:** No expone endpoint propio (job interno del scheduler). Lee la caducidad de `GET/PUT /api/v1/config` (HU-ADMIN-001).
**Fecha que cuenta:** `fecha_registro` (timestamp de captura, UTC), porque el PDF habla de "noticias **registradas** con fecha anterior al periodo de caducidad". No se usa `fecha_publicacion`, que puede faltar en el feed.
**Resiliencia:** el purgado opera solo sobre MySQL, sin servicios externos, por lo que no requiere Circuit Breaker, Bulkhead ni Retry (mismo criterio que ADR-003, sección 4). Un fallo de base de datos se registra en el log y el job vuelve a intentarlo en la siguiente ejecución, sin reintentos inmediatos.

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Purgado de noticias caducadas
  Dado que la caducidad es 90 días
  Y existen noticias registradas hace 91, 89 y 0 días
  Cuando se ejecuta el purgado automático
  Entonces se elimina exactamente 1 noticia, la registrada hace 91 días
  Y las otras 2 se conservan

Escenario: Límite exacto
  Dado que la caducidad es 10 días
  Y existe una noticia registrada hace exactamente 10 días
  Cuando se ejecuta el purgado automático
  Entonces la noticia se conserva

Escenario: Coincidencias de las noticias eliminadas
  Dado una noticia caducada y otra vigente, ambas con el término "guerra"
  Cuando se ejecuta el purgado automático
  Entonces solo queda la coincidencia de la noticia vigente (HU-SENT-008)
  Y el término del diccionario no se elimina

Escenario: Periodicidad del job
  Cuando arranca la aplicación
  Entonces el scheduler registra el job "purgado-noticias-caducadas"
  Y su primera ejecución ocurre 5 minutos después del arranque y luego cada 24 horas

Escenario: Sin noticias caducadas
  Dado que ninguna noticia supera la caducidad
  Cuando se ejecuta el purgado automático
  Entonces se eliminan 0 noticias y no se produce ningún error
```

### Definition of Done
(Bloque general DoD, sección 14.) Adicionalmente:
- Pruebas deterministas con un "ahora" fijo inyectado, sin depender del reloj real ni del scheduler real.
- El borrado de noticias y de sus coincidencias ocurre en una sola transacción.

---

## HU-ADMIN-003 — Purgado manual de noticias antiguas

**Tipo:** Historia de Usuario
**Como** administrador del sistema,
**quiero** eliminar bajo demanda las noticias anteriores a una fecha,
**para** liberar espacio o limpiar datos de prueba sin esperar al purgado automático.

**Prioridad:** Baja
**Estimación (Planning Poker P3):** 1 punto *(punto de partida del P3, sujeto a revisión del equipo)*
**Depende de contrato de API:** Sí — `DELETE /api/v1/news?fecha_anterior_a=YYYY-MM-DD` (`contrato-noticias.openapi.yaml` v1.1.0). Se modela como DELETE sobre la colección `/news`, el método que el PDF (§10.2) asigna a `/news`, sin verbos en la URL.
**Respuesta 200 con resumen en vez de 204:** el 204 del PDF (§10.3) aplica a la eliminación de un recurso individual; en un borrado masivo el administrador necesita saber cuántas noticias se eliminaron.

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Purgado manual por fecha
  Dado una noticia registrada el 2026-09-30 23:59 UTC y otra el 2026-10-01 00:00 UTC
  Cuando el administrador envía DELETE a /api/v1/news?fecha_anterior_a=2026-10-01
  Entonces el sistema responde con código HTTP 200
  Y el cuerpo informa "noticias_eliminadas": 1
  Y la noticia del 2026-10-01 se conserva

Escenario: Purgado manual con la caducidad configurada
  Dado que la caducidad es 1 día y existe una noticia registrada en 2020
  Cuando el administrador envía DELETE a /api/v1/news sin parámetros
  Entonces el sistema responde con código HTTP 200 y elimina esa noticia

Escenario: Fecha futura
  Cuando el administrador envía DELETE a /api/v1/news?fecha_anterior_a con una fecha posterior a hoy
  Entonces el sistema responde con código HTTP 400 y codigo "FECHA_INVALIDA"
  Y no se elimina ninguna noticia

Escenario: Fecha mal formada
  Cuando el administrador envía DELETE a /api/v1/news?fecha_anterior_a=ayer
  Entonces el sistema responde con código HTTP 400

Escenario: Idempotencia
  Dado que ya se ejecutó un purgado con fecha_anterior_a=2026-10-01
  Cuando se repite la misma solicitud
  Entonces el sistema responde 200 con "noticias_eliminadas": 0
```

### Definition of Done
(Bloque general DoD, sección 14.) Adicionalmente:
- Endpoint documentado en Swagger con la advertencia de que la operación es irreversible.

---

## HU-ADMIN-004 — Panel de administración unificado

**Tipo:** Historia de Usuario
**Como** administrador del sistema,
**quiero** una sección de administración en la interfaz web desde donde gestionar las fuentes RSS, el diccionario y los parámetros generales, y ejecutar la captura y el purgado manuales,
**para** operar HumWorld sin usar Swagger ni llamar a la API a mano.

**Prioridad:** Alta *(es la única vista obligatoria del PDF que falta: §4.3, vista 1)*
**Estimación (Planning Poker P3):** 2 puntos. *Con el detalle de abajo el alcance es mayor que el estimado en P3; el equipo debe re-estimarla. Es un punto de partida, no un valor definitivo.*
**Responsable propuesto:** Valentín García (frontend).
**Depende de contrato de API:** Sí. No requiere endpoints nuevos: consume los ya implementados.

| Pestaña | Endpoints | Contrato |
|---|---|---|
| Fuentes RSS | `GET`/`POST /channels`, `GET`/`POST /sources`, `PUT`/`PATCH`/`DELETE /sources/{id}`, `POST /sources/{id}/captures`, `POST /captures` | `contrato-canales-fuentes-rss.openapi.yaml` v1.8.0 |
| Diccionario | `GET`/`POST /dictionary` (paginado, HU-SENT-001-v2), `PUT`/`PATCH`/`DELETE /dictionary/{id}` | `contrato-sentimiento-diccionario.openapi.yaml` v1.2.0 |
| Parámetros | `GET`/`PUT /config` | `contrato-canales-fuentes-rss.openapi.yaml` v1.8.0 |
| Purgado | `DELETE /news` | `contrato-noticias.openapi.yaml` v1.1.0 |
| Modelo ML *(opcional)* | `POST /trainings` | `contrato-sentimiento-diccionario.openapi.yaml` v1.1.0 |

**Origen (PDF):** §4.3, vista 1 ("Panel de administración: gestión de fuentes RSS, diccionario, parámetros generales"); §4.1, punto 4 ("gestión de fuentes, diccionarios y parámetros de caducidad mediante una interfaz de usuario y una API REST"); §4.2.2 (CRUD del diccionario "con endpoints API REST e interface de usuario"); §4.2.3 (actualización manual de uno o varios RSS); §4.2.5 (función de usuario para borrar noticias antiguas).

**Fuera de alcance:**
- Gestión de usuarios: el PDF la condiciona a que exista autenticación, que no se implementa (§3, limitación 3).
- Editar o eliminar canales: ninguna historia de EPIC-RSS lo define y la API no lo expone (solo alta y consulta, HU-RSS-001 y HU-RSS-010).

**Decisiones de diseño propuestas (a ratificar):**
1. **Navegación:** una cuarta opción "Administración" en el menú actual, con pestañas internas. Mismo patrón que las otras vistas (`useState`, sin librería de rutas; ADR-005).
2. **Listados grandes:** `GET /dictionary` está paginado desde HU-SENT-001-v2 (contrato v1.2.0). La vista pide páginas de 25 (`tamanio_pagina=25`) y usa `busqueda` para filtrar.
3. **Fuentes:** "Eliminar" es una baja lógica (la API deja `activo = false`, HU-RSS-005). La vista lo nombra "Desactivar" para no confundir al usuario.
4. **Acciones irreversibles** (purgado, eliminar término): piden confirmación explícita antes de llamar a la API.
5. **Errores:** se muestra el `mensaje` que devuelve la API (por ejemplo, el 409 de término duplicado), no un texto genérico.

### Criterios de aceptación (Gherkin)

```gherkin
# --- Fuentes RSS (HU-RSS-001 a 010) ---
Escenario: Listado de fuentes con su estado
  Dado que existen 20 fuentes RSS
  Cuando el administrador abre la pestaña "Fuentes RSS"
  Entonces ve una tabla paginada de 10 fuentes por página con: canal, URL, categoría IPTC, activa (sí/no), fecha de la última captura exitosa y estado del circuit breaker
  Y puede filtrar por canal, continente, categoría IPTC y activa

Escenario: Alta de una fuente
  Dado un canal existente
  Cuando el administrador completa URL y categoría IPTC (lista de las 17 categorías de primer nivel) y guarda
  Entonces la API responde 201 y la fuente aparece en el listado sin recargar la página

Escenario: URL inválida o duplicada
  Cuando el administrador guarda una fuente con una URL mal formada o ya registrada
  Entonces la vista muestra el mensaje de error que devuelve la API (400 o 409)
  Y el formulario conserva los datos escritos

Escenario: Desactivar y reactivar una fuente
  Dado una fuente activa
  Cuando el administrador la desactiva
  Entonces se envía PATCH con activo = false y la fila la muestra como inactiva
  Y puede reactivarla con PATCH activo = true

Escenario: Alta de un canal
  Cuando el administrador crea un canal con nombre, continente (lista de 5) y país opcional
  Entonces la API responde 201 y el canal queda disponible al dar de alta fuentes

Escenario: Captura manual de una fuente
  Dado una fuente activa
  Cuando el administrador presiona "Capturar ahora" en esa fila
  Entonces se envía POST /sources/{id}/captures
  Y la vista muestra el resultado: estado y cantidad de noticias nuevas

Escenario: Captura manual de varias fuentes
  Dado que el administrador selecciona 3 fuentes
  Cuando presiona "Capturar seleccionadas"
  Entonces se envía POST /captures con los 3 ids
  Y la vista muestra un resultado por fuente, aunque alguna falle

Escenario: Captura de una fuente inactiva
  Cuando el administrador intenta capturar una fuente inactiva
  Entonces la vista muestra el mensaje del 409 de la API

# --- Diccionario (HU-SENT-001) ---
Escenario: Búsqueda en el diccionario
  Cuando el administrador escribe "guerra" en el buscador
  Entonces se consulta GET /dictionary?busqueda=guerra&tamanio_pagina=25
  Y ve los términos que coinciden, con palabra, idioma y valor, en páginas de 25 con el total encontrado

Escenario: Alta de un término
  Cuando el administrador crea un término con palabra, idioma (es/en) y valor entre -10 y +10
  Entonces la API responde 201 y el término aparece en el listado
  Y la vista avisa que el humor de las noticias se recalculará en el próximo barrido (HU-SENT-002-v3)

Escenario: Valor fuera de rango
  Cuando el administrador ingresa un valor de 11 o de -11
  Entonces el formulario no permite guardar y explica el rango válido

Escenario: Término duplicado
  Cuando el administrador crea un término con una palabra e idioma ya existentes
  Entonces la vista muestra el mensaje del 409 de la API

Escenario: Edición y eliminación de un término
  Dado un término existente
  Cuando el administrador cambia su valor y guarda
  Entonces se envía PATCH y el listado muestra el valor nuevo
  Y al eliminarlo, la vista pide confirmación antes de enviar DELETE

# --- Parámetros generales (HU-RSS-007, HU-ADMIN-001) ---
Escenario: Consulta y cambio de parámetros
  Cuando el administrador abre la pestaña "Parámetros"
  Entonces ve la periodicidad del cron (minutos) y la caducidad de las noticias (días)
  Y al guardar valores enteros mayores o iguales a 1 se envía PUT /config y se muestran los valores guardados

Escenario: Parámetro inválido
  Cuando el administrador ingresa 0 o un valor negativo
  Entonces el formulario no permite guardar
  Y los valores vigentes no cambian

# --- Purgado manual (HU-ADMIN-003) ---
Escenario: Purgado por fecha con confirmación
  Cuando el administrador elige una fecha no posterior a hoy y presiona "Purgar"
  Entonces la vista pide confirmación indicando que la operación es irreversible
  Y al confirmar se envía DELETE /news?fecha_anterior_a=<fecha>
  Y se muestra la cantidad de noticias eliminadas

Escenario: Purgado con la caducidad configurada
  Cuando el administrador presiona "Purgar según caducidad" y confirma
  Entonces se envía DELETE /news sin parámetros y se muestra la cantidad eliminada

Escenario: Cancelación del purgado
  Cuando el administrador cancela la confirmación
  Entonces no se envía ninguna solicitud

# --- Modelo de ML (HU-SENT-006, opcional) ---
Escenario: Entrenamiento manual
  Cuando el administrador presiona "Entrenar modelo"
  Entonces se envía POST /trainings
  Y la vista muestra la versión creada y su MAE (201), o el mensaje de la API (409 datos insuficientes, 502 servicio caído, 503 sin clave)

# --- Comunes ---
Escenario: API no disponible
  Dado que la API no responde
  Cuando el administrador abre cualquier pestaña
  Entonces la vista muestra un mensaje de error en vez de quedar en blanco
```

### Definition of Done
(Bloque general DoD, sección 14.) Adicionalmente:
- Pruebas con Vitest y Testing Library para cada escenario, con la API simulada (mock de `api/cliente.js`); cobertura del frontend ≥ 80 % en el pipeline.
- Ninguna acción irreversible sin confirmación (prueba que verifica que cancelar no llama a la API).
- Validación visual en al menos una resolución de escritorio y una de celular, con capturas en el PR.
- Lint sin errores.
- Revisión de al menos un miembro del equipo antes del merge.

---

## Resumen de trazabilidad

| HU | Tipo | Prioridad | Endpoint(s) | Origen (PDF) |
|---|---|---|---|---|
| HU-ADMIN-001 | Historia de Usuario | Media | `GET`/`PUT /api/v1/config` | §4.2.5, §10.2 |
| HU-ADMIN-002 | Enabler Story | Media | (interno — scheduler) | §4.2.5 |
| HU-ADMIN-003 | Historia de Usuario | Baja | `DELETE /api/v1/news` | §4.2.5, §10.2 |
| HU-ADMIN-004 | Historia de Usuario | Alta | (frontend) consume `/channels`, `/sources`, `/captures`, `/dictionary`, `/config`, `/news`, `/trainings` | §4.1, §4.2.2, §4.2.3, §4.2.5, §4.3 vista 1 |

**Recordatorio:** las estimaciones son las del Planning Poker de P3, un punto de partida sujeto a revisión del equipo (sección 4 de las instrucciones del proyecto).

---

## Tabla de control de versiones

| ID | Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|---|
| HU-ADMIN-001 a 003 | v1.0 | 2026-10-19 | Primera formalización de EPIC-ADMIN a partir de los títulos del backlog de P3 y del PDF §4.2.5, junto con su implementación. Decisiones de la PO: caducidad por defecto de 90 días y fecha de referencia `fecha_registro`. Valor propuesto por el agente PO/Arquitecto: ejecución cada 24 horas. HU-ADMIN-004 queda sin formalizar. |
| HU-ADMIN-004 | v1.1 | 2026-10-20 | Formalización de HU-ADMIN-004: pestañas, endpoints que consume, 20 escenarios Gherkin, DoD, alcance excluido (usuarios, edición de canales) y 5 decisiones de diseño propuestas. Sube a prioridad Alta por ser la única vista obligatoria del PDF pendiente; se pide re-estimar. |
| HU-ADMIN-004 | v1.2 | 2026-10-20 | Decisión de la PO: el diccionario se pagina en el backend (HU-SENT-001-v2), no en el navegador. Se ajustan la decisión de diseño 2, el escenario de búsqueda y la tabla de endpoints. |
