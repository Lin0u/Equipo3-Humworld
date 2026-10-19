# Historias de Usuario — EPIC-ADMIN (Administración y Configuración)

**Proyecto:** HumWorld — Equipo 3
**Origen:** PDF de especificaciones, §4.2.5 (Purgado de información antigua), §4.3 punto 1 (Panel de administración) y §10.2 (`/config`: GET, PUT; `/news`: DELETE). Títulos y puntos tomados del backlog entregado en P3 (`Anexo-I-Planificacion-entregado-P3.md`, Sprint 4).
**Estado general:** HU-ADMIN-001 (parcial), HU-ADMIN-002 y HU-ADMIN-003 implementadas el 2026-10-19 (rama `feature/cierre-sprint`), pendientes de revisión en el PR y de ratificación del equipo. HU-ADMIN-004 sin iniciar.
**Versión del documento:** v1.0. Ver la Tabla de control de versiones al final del documento.

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

**Estado:** Sin iniciar. No se formaliza en esta versión: depende de que el equipo defina qué vistas incluye (PDF §4.3 punto 1: fuentes RSS, diccionario, parámetros generales y, si se implementa, usuarios). Estimación P3: 2 puntos.

---

## Resumen de trazabilidad

| HU | Tipo | Prioridad | Endpoint(s) | Origen (PDF) |
|---|---|---|---|---|
| HU-ADMIN-001 | Historia de Usuario | Media | `GET`/`PUT /api/v1/config` | §4.2.5, §10.2 |
| HU-ADMIN-002 | Enabler Story | Media | (interno — scheduler) | §4.2.5 |
| HU-ADMIN-003 | Historia de Usuario | Baja | `DELETE /api/v1/news` | §4.2.5, §10.2 |
| HU-ADMIN-004 | Historia de Usuario | — | (frontend) | §4.3 punto 1 |

**Recordatorio:** las estimaciones son las del Planning Poker de P3, un punto de partida sujeto a revisión del equipo (sección 4 de las instrucciones del proyecto).

---

## Tabla de control de versiones

| ID | Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|---|
| HU-ADMIN-001 a 003 | v1.0 | 2026-10-19 | Primera formalización de EPIC-ADMIN a partir de los títulos del backlog de P3 y del PDF §4.2.5, junto con su implementación. Decisiones de la PO: caducidad por defecto de 90 días y fecha de referencia `fecha_registro`. Valor propuesto por el agente PO/Arquitecto: ejecución cada 24 horas. HU-ADMIN-004 queda sin formalizar. |
