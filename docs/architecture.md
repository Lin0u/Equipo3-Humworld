# Arquitectura de la aplicación HumWorld

## 1. Objetivo

HumWorld es un sistema que analiza noticias en tiempo real, capturadas vía
RSS, para calcular y actualizar el "estado de ánimo" (humor) del mundo mediante
análisis de sentimiento, y lo presenta en dashboards (mapa mundial, evolución
temporal, nube de palabras y listado de noticias). Este documento describe la
arquitectura del sistema completo, tal como está implementado en el
repositorio, cubriendo sus cuatro épicas: Captura RSS (EPIC-RSS), Motor de
Análisis de Sentimiento (EPIC-SENT), Dashboards y Visualización (EPIC-DASH) y
Administración (EPIC-ADMIN).

Fuentes: PDF de especificaciones del proyecto (§4, §6, §10), decisiones de
arquitectura (`docs/Adr/ADR-001` a `ADR-005`) y el código del repositorio
(`src/`, `frontend/`, `alembic/`).

## 2. Tecnologías (ADR-001 a ADR-005)

**Backend (ADR-001, ADR-002):**
- Python 3.11+.
- FastAPI para la API REST; OpenAPI/Swagger autogenerado (`/api/docs`, `/api/redoc`).
- SQLAlchemy 2.x (declarativo) + Alembic para migraciones, sobre MySQL.
- Pydantic v2 para validación y serialización.
- httpx (async) + feedparser para el consumo de feeds RSS/Atom.
- APScheduler para los jobs internos (captura, barrido de humor, purgado).
- pytest + pytest-asyncio + pytest-cov + respx/responses para pruebas (mocks
  obligatorios para servicios externos, nunca llamadas reales).

**Motor de sentimiento (ADR-003, ADR-004):**
- spaCy para lematización y detección de idioma (es/en) en el método de diccionario.
- scikit-learn (regresor sobre embeddings) para el camino de ML, con embeddings
  de Google Gemini Embedding como servicio externo. El camino de ML es opcional:
  sin clave de API, el humor se calcula 100% por diccionario.

**Frontend (ADR-005):**
- React 19 con Vite; Leaflet (mapa) y Chart.js (gráfico de evolución); CSS plano
  y `fetch` nativo. SPA separada que consume la API; no accede a MySQL.
- Vitest + Testing Library para las pruebas del frontend.

**Infraestructura:**
- Docker (imagen `python:3.11-slim` + uvicorn) y `docker-compose` (API + MySQL).
- GitHub Actions para CI/CD, con SonarQube y jobs encadenados por `needs`.

## 3. Estilo arquitectónico

Arquitectura distribuida en capas (§6.1 de la especificación; ADR-002): una SPA
de presentación (frontend React) que consume una API REST, y un backend
organizado en capas API → Servicios → Repositorios → Persistencia.

```
Frontend (React SPA)  ──HTTP/JSON──>  API REST (FastAPI, /api/v1)
                                           │
                                   Routers (capa API)
                                           │
                                   Servicios (lógica de negocio)
                                           │
                                   Repositorios (acceso a datos)
                                           │
                                   Persistencia (MySQL + Alembic)
```

Jobs internos (APScheduler) corren dentro del proceso del backend para la
captura automática, el barrido de humor y el purgado.

## 4. Responsabilidades de cada capa

- **Presentación (frontend):** vistas de mapa de humor, evolución temporal, nube
  de palabras y listado de noticias. No calcula humor ni influencia: solo
  consume datos ya agregados por el backend (ADR-005).
- **API (routers FastAPI):** expone los endpoints, valida la entrada con Pydantic
  y delega a Servicios. No contiene SQL ni lógica de negocio.
- **Servicios:** implementan los casos de uso (gestión de canales/fuentes,
  captura, cálculo de humor, agregaciones, purgado, entrenamiento del modelo).
  Independientes del framework web.
- **Repositorios:** encapsulan el acceso a datos vía SQLAlchemy.
- **Persistencia:** MySQL, con migraciones gestionadas por Alembic.

## 5. Modelo de datos

Entidades implementadas (`src/app/models/`), con sus migraciones en
`alembic/versions/`:

- **CanalNoticias** (EPIC-RSS): id, nombre, continente, pais (opcional),
  descripcion (opcional).
- **FuenteRSS** (EPIC-RSS): id, canal_id (FK), url, categoria_iptc, activo,
  fecha_ultima_captura_exitosa, estado_circuit_breaker.
- **Noticia** (EPIC-RSS + EPIC-SENT): id, fuente_rss_id (FK),
  identificador_item_rss (dedup), titulo, contenido, enlace_original,
  fecha_publicacion, fecha_registro, idioma_detectado, categoria_iptc y los
  campos de humor poblados por EPIC-SENT: valor_humor, metodo_calculo
  ("diccionario" | "ml" | NULL), cantidad_terminos_evaluados,
  polarizacion_terminos, modelo_sentimiento_id (FK, nullable).
- **TerminoDiccionario** (EPIC-SENT): id, palabra, idioma (es/en), valor (-10 a +10).
- **CoincidenciaTermino** (EPIC-SENT, tabla `noticia_termino`, HU-SENT-008):
  composición con Noticia (clave compuesta noticia_id + termino_id).
- **ModeloSentimiento** (EPIC-SENT, HU-SENT-006): id, version, ruta_archivo,
  modelo_embeddings_usado, mae_evaluacion, fecha_entrenamiento, activo.
- **Configuracion** (EPIC-ADMIN): parámetros clave-valor (periodicidad del cron,
  caducidad de noticias).

Relaciones UML: CanalNoticias ◆── FuenteRSS (composición); FuenteRSS ── Noticia
(agregación); Noticia ◆── CoincidenciaTermino (composición);
TerminoDiccionario ──< CoincidenciaTermino (referencia); ModeloSentimiento ──o
Noticia (agregación). Detalle del modelo de datos completo en
`docs/UML/diagrama-clases.md`.

## 6. API (bajo `/api/v1`)

Todos los routers se montan bajo `/api/v1` en `src/app/main.py`. Detalle de
cada contrato en `docs/Contratos/`.

- **Canales y fuentes (EPIC-RSS):** `POST/GET /channels`, `GET /channels/{id}`;
  `POST/GET /sources`, `GET/PUT/PATCH/DELETE /sources/{id}`;
  `POST /sources/{id}/captures`, `POST /captures`. (`contrato-canales-fuentes-rss.openapi.yaml`.)
- **Configuración (EPIC-RSS/EPIC-ADMIN):** `GET/PUT /config`. (Mismo contrato.)
- **Diccionario y sentimiento (EPIC-SENT):** `GET/POST /dictionary`,
  `GET/PUT/PATCH/DELETE /dictionary/{id}`; `GET /sentiment` (global, continente,
  país, timeline), `POST /sentiment` (análisis de texto); `POST /trainings`
  (entrenamiento del modelo de ML). (`contrato-sentimiento-diccionario.openapi.yaml`.)
- **Dashboards (EPIC-DASH):** `GET /dashboards/map`, `GET /dashboards/word-cloud`.
  (`contrato-dashboards.openapi.yaml`.)
- **Noticias (EPIC-DASH/EPIC-ADMIN):** `GET /news`, `GET /news/{id}`,
  `DELETE /news` (purgado manual). (`contrato-noticias.openapi.yaml`.)
- **Operativo:** `GET /health` — estado del sistema; informa además si los
  modelos de spaCy (lematización) están cargados.

Los listados paginados (`/channels`, `/sources`, `/news`) devuelven un objeto con
`items`, `pagina`, `tamanio_pagina` y `total`.

## 7. Jobs internos (APScheduler)

Registrados en `src/app/jobs/scheduler.py`, iniciados en el `lifespan` de la app:

- **Captura automática** (HU-RSS-006): recorre las fuentes activas según la
  periodicidad configurable (por defecto cada 30 minutos).
- **Barrido de humor** (HU-SENT-002-v3): procesa noticias con
  `metodo_calculo = NULL`; primera ejecución 1 minuto tras arrancar, luego cada
  30 minutos.
- **Purgado de noticias caducadas** (HU-ADMIN-002): primera ejecución 5 minutos
  tras arrancar, luego cada 24 horas.

## 8. Organización del código

```
src/app/
  main.py            # FastAPI app, CORS, montaje de routers, lifespan (spaCy + scheduler)
  core/config.py     # Settings (variables de entorno)
  database.py        # motor/sesión SQLAlchemy
  routers/           # capa API: channels, sources, captures, configuracion,
                     #           dictionary, sentiment, dashboards, news, trainings, health
  services/          # lógica de negocio (captura, sentimiento, dashboards, purgado, ML, seeds...)
  repositories/      # acceso a datos (canales, fuentes, noticias, dictionary, sentimiento...)
  models/            # entidades SQLAlchemy
  schemas/           # modelos Pydantic
  jobs/scheduler.py  # jobs APScheduler
  scripts/           # cargas iniciales (seed de fuentes y de diccionario)
  tests/             # pruebas (SQLite en memoria; mocks para servicios externos)
alembic/             # migraciones
frontend/src/        # SPA React (api/, componentes/, pantallas/, utilidades/, datos/)
```

Reglas de capas: los routers no acceden a MySQL ni contienen SQL; los servicios
no dependen del framework web; toda sentencia de acceso a datos va en los
repositorios.

## 9. Resiliencia

Toda llamada a un servicio externo aplica patrones de resiliencia (§13 de las
instrucciones del proyecto; ADR-002 y ADR-004):

- **Captura RSS:** Timeout explícito, Retry acotado con backoff exponencial y
  Circuit Breaker por fuente. El fallo de una fuente no interrumpe el resto de
  la captura; nunca reintentos infinitos.
- **Cálculo con ML:** Timeout sobre la llamada a Google Gemini Embedding y
  fallback automático al método de diccionario si el servicio falla o no
  responde. El purgado y las agregaciones operan solo sobre MySQL, sin servicios
  externos.

## 10. Manejo de errores

No se exponen trazas internas. Se usan códigos HTTP coherentes con los contratos
OpenAPI (§10.3: 200/201/204/400/404/500) y un cuerpo de error uniforme
(`{codigo, mensaje}`). Los errores de persistencia y de red se tratan de forma
controlada.

## 11. Despliegue

`docker-compose.yml` levanta MySQL y la API; las migraciones de Alembic se
aplican al arrancar y MySQL tiene healthcheck para que la API no arranque antes
de tiempo. El camino de ML se activa con la variable `GEMINI_API_KEY` (opcional);
sin ella, el humor se calcula solo por diccionario. El frontend se construye y
sirve por separado. Pasos detallados en `README.md`.

## 12. Fuera de alcance

Autenticación y autorización (§3 de la especificación, Limitaciones, punto 3:
no se contempla autenticación). Las funcionalidades opcionales de §4.5 (alertas
por correo, expansión automática del diccionario por LLM) no están implementadas.

---

## Historial de versiones

| Versión | Fecha | Motivo del cambio |
|---|---|---|
| v1 | 2026-09-02 | Creación. Arquitectura del Sprint 1 (módulo de Captura RSS, EPIC-RSS): capas, stack, modelo de datos de canales/fuentes/noticias, API de EPIC-RSS, reglas y patrones de resiliencia. Declaraba fuera de alcance los módulos aún no implementados (sentimiento, dashboards, diccionario, purgado). |
| v2 | 2026-10-29 | Actualización a la arquitectura del sistema completo (rol Documentación): se extiende a las cuatro épicas (RSS, SENT, DASH, ADMIN) y al frontend, reflejando el código implementado. Se añaden el modelo de datos extendido (TerminoDiccionario, CoincidenciaTermino, ModeloSentimiento, Configuracion, campos de humor en Noticia), el inventario de endpoints real, los jobs internos (captura, barrido de humor, purgado), la resiliencia del camino de ML y el despliegue con Docker. Se corrige la sección "Fuera de alcance" (solo autenticación y opcionales de §4.5). |
