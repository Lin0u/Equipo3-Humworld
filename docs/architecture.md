# Arquitectura de la aplicación HumWorld (v1 — Sprint 1, módulo Captura RSS)

## 1. Objetivo
HumWorld es un sistema que analiza noticias en tiempo real capturadas vía
RSS para calcular y actualizar el "estado de ánimo" del mundo mediante
análisis de sentimiento. Esta arquitectura documenta las restricciones
obligatorias vigentes para Sprint 1 (módulo de Captura RSS: gestión de
canales y fuentes, cron de captura). Módulos posteriores (Análisis de
Sentimiento, Dashboard/Mapa Mundial, Diccionario de Términos, Purgado) se
incorporarán a este documento en versiones sucesivas, conforme se definan
sus propios ADR.

## 2. Tecnologías aprobadas (ADR-01, ADR-02)
- Python 3.11 o superior.
- FastAPI para la API REST.
- SQLAlchemy 2.x (modo declarativo) + Alembic para migraciones, sobre MySQL.
- Pydantic v2 para validación y serialización.
- httpx (async) + feedparser para el consumo de feeds RSS/Atom.
- APScheduler para el scheduler interno del cron de captura.
- pytest + pytest-asyncio + pytest-cov + respx/responses para pruebas
  (mocks obligatorios para llamadas RSS, nunca llamadas reales).
- OpenAPI/Swagger generado automáticamente por FastAPI (/api/docs, /api/redoc).
- Docker (imagen python:3.11-slim + uvicorn) para contenerización.
- GitHub Actions para CI/CD, con SonarQube y needs: [test, sonarqube].

> Nota: la SPA de frontend (React 19.2.8 o superior) queda **fuera del
> alcance de este backend** (ver secciones 1 y 10); se lista aquí solo como
> referencia de la tecnología prevista para el cliente, no como dependencia
> del módulo de Captura RSS.

## 3. Estilo arquitectónico
Arquitectura distribuida/en capas: API, Servicios, Repositorios y
Persistencia (PDF de especificaciones, sección 6.1; ADR-02).

## 4. Responsabilidades de cada capa
- Capa API (routers FastAPI): expone los endpoints, valida entrada con
  Pydantic y delega a Servicios. No contiene sentencias SQL ni lógica de
  negocio.
- Capa Servicios: implementa los casos de uso (alta/consulta de canales y
  fuentes, orquestación de captura, deduplicación, patrones de
  resiliencia). Independiente del framework web.
- Capa Repositorios: encapsula el acceso a datos vía SQLAlchemy para
  CanalNoticias, FuenteRSS y Noticia.
- Capa Persistencia: MySQL, con migraciones gestionadas por Alembic.

## 5. Modelo de datos vigente (ADR-02)
- CanalNoticias: id, nombre, continente, pais (opcional), descripcion
  (opcional).
- FuenteRSS: id, canal_id (FK), url, categoria_iptc, activo,
  fecha_ultima_captura_exitosa (nullable), estado_circuit_breaker.
- Noticia: id, fuente_rss_id (FK), identificador_item_rss, titulo,
  contenido/resumen, enlace_original, fecha_publicacion, fecha_registro,
  idioma_detectado, categoria_iptc, valor_humor (nullable, fuera de
  alcance de EPIC-RSS).
Relaciones UML: CanalNoticias ◆── FuenteRSS (composición);
FuenteRSS ── Noticia (agregación).

## 6. API vigente (Sprint 1 — EPIC-RSS)
- POST /api/v1/channels — HU-RSS-001.
- GET /api/v1/channels (paginado, orden alfabético por "nombre"),
  GET /api/v1/channels/{id} — HU-RSS-010.
- POST /api/v1/sources — HU-RSS-002.
- GET /api/v1/sources (paginado, orden por "canal_id" y luego "url"),
  GET /api/v1/sources/{id} — HU-RSS-003-v2 (reemplaza a HU-RSS-003,
  deprecada).
- PUT/PATCH /api/v1/sources/{id} — HU-RSS-004.
- DELETE /api/v1/sources/{id} — HU-RSS-005.
- GET/PUT /api/v1/config — HU-RSS-007.
- POST /api/v1/sources/{id}/captures, POST /api/v1/captures — HU-RSS-008
  (nombre exacto de recurso pendiente de confirmación por el equipo).

Los listados paginados (/channels, /sources) devuelven un objeto con
`items`, `pagina`, `tamanio_pagina` y `total` (convención de paginación
acordada por el equipo el 2026-08-30) — ver
`contrato-canales-fuentes-rss.openapi.yaml` para el detalle exacto.

## 7. Organización orientativa
Estructura confirmada en el repositorio (revisión de sesión 2026-08-30):
`src/app/main.py`, `src/app/core/` (configuración, ADR-01),
`src/app/routers/` (capa API: channels, sources, captures, health),
`src/app/models/` (SQLAlchemy), `src/app/schemas/` (Pydantic),
`src/app/jobs/` (scheduler APScheduler del cron de captura),
`src/app/services/`, `src/app/database.py` (motor/sesión SQLAlchemy —
ver ADR-01) y `tests/`.

La capa de Repositorios (`src/app/repositories/`) ya está implementada
tras el Sprint 1: `repositories/canales.py` y `repositories/fuentes.py`
concentran todo el acceso a datos de `CanalNoticias` y `FuenteRSS`
(HU-RSS-001 a 005 y HU-RSS-010). Se mantiene la regla de que ninguna
sentencia de acceso a datos vaya en `services/` ni en `routers/`.

No hay app/static/ ni app/templates/: el frontend de HumWorld es una SPA
separada (PDF, sección 6.2), fuera del alcance de este backend.

## 8. Reglas
- No concentrar toda la aplicación en un fichero.
- No acceder a MySQL desde los routers: toda sentencia de acceso a datos
  va en la capa de Repositorios (SQLAlchemy).
- No colocar lógica de negocio en los routers.
- Cada historia debe incluir pruebas, con dependencias externas (RSS)
  aisladas mediante mocks. La estrategia de pruebas, el alcance de cobertura
  y la matriz de trazabilidad HU-RSS ↔ escenario ↔ prueba del Sprint 1 se
  documentan en `docs/Testing/plan-de-pruebas-sprint-1.md`.
- Todo cambio debe corresponder a una especificación OpenSpec.
- Los cambios arquitectónicos requieren revisión humana y, si alteran una
  decisión ya tomada, una nueva versión del ADR correspondiente.
- Los patrones de resiliencia (Timeout explícito, Retry acotado con
  backoff exponencial, Circuit Breaker por fuente — exigidos por la
  sección 13 de las instrucciones del proyecto) son obligatorios en toda
  llamada a una fuente RSS externa. Esta regla es la fuente de verdad de
  dicho requisito para todo el sistema (RSS y, por extensión, servicios
  externos de EPIC-SENT).

## 9. Errores
No exponer trazas internas. Utilizar códigos HTTP coherentes con
contrato-canales-fuentes-rss.openapi.yaml y tratar los errores de
persistencia y de red de forma controlada (nunca reintentos infinitos).

## 10. Fuera de alcance (de esta versión del documento)
Análisis de sentimiento, dashboard/mapa mundial, diccionario de términos,
purgado automático, autenticación y autorización (PDF, sección 3,
Limitaciones).