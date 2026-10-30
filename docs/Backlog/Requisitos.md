# Lista Formal de Requisitos — HumWorld

**Proyecto:** HumWorld — Equipo 3
**Fuente:** PDF de especificaciones del proyecto final (`0 PROYECTO_FINAL_HUMWORLD`). Las referencias de sección (§) apuntan a ese documento.
**Propósito:** entregable exigido por §4.7 punto 2 ("Lista de requisitos. Épicas / Historias de usuario derivadas") y por §8.1 ("Lista formal de requisitos").
**Estado:** reconstruido a partir de la especificación, el backlog vigente (`docs/Backlog/`), los contratos OpenAPI (`docs/Contratos/`), los routers implementados (`src/app/routers/`) y la suite de pruebas (`src/tests/`, `frontend/src/`). Documenta el estado real del sistema a la fecha de esta versión.

**Notas de alcance (rol Documentación):**
- Este documento recopila y relaciona requisitos; no modifica código, contratos ni decisiones de equipo.
- Las decisiones de diseño ya materializadas en código, migraciones y pruebas se documentan como implementadas. Los pasos de proceso ágil sin evidencia en el repositorio (ratificación formal en reunión, Planning Poker definitivo, revisión del dashboard de SonarQube) se marcan como pendientes del equipo donde correspondan.
- Las historias de usuario deprecadas no se listan como requisitos activos; se usa siempre la versión vigente (p. ej. HU-RSS-003-v2, no HU-RSS-003).

---

## 1. Requisitos Funcionales

Cada requisito funcional (RF) deriva de una función descrita en el PDF (§4.1 a §4.3) o de la tabla de endpoints mínimos obligatorios (§10.2). La columna "Historia(s)" indica la HU vigente que lo cubre.

| ID | Requisito funcional | Origen (PDF) | Historia(s) |
|---|---|---|---|
| RF-01 | Alta de canales de noticias (medios de comunicación). | §4.2.1 | HU-RSS-001 |
| RF-02 | Alta de fuentes RSS dentro de un canal, con categoría IPTC Media Topics (primer nivel). | §4.2.1, §3 punto 3 | HU-RSS-002 |
| RF-03 | Consulta y listado paginado/filtrado de fuentes RSS, y detalle de una fuente. | §4.2.1, §10.2 | HU-RSS-003-v2 |
| RF-04 | Modificación de una fuente RSS (completa y parcial). | §10.2 | HU-RSS-004 |
| RF-05 | Eliminación de una fuente RSS. | §10.2 | HU-RSS-005 |
| RF-06 | Captura automática periódica de noticias desde las fuentes RSS activas (cron). | §4.2.3, §4.2.4 | HU-RSS-006 |
| RF-07 | Configuración, modificable por el usuario, de la periodicidad del cron de captura. | §4.2.3 | HU-RSS-007 |
| RF-08 | Actualización manual de la captura para una o varias fuentes RSS. | §4.2.3 | HU-RSS-008 |
| RF-09 | Carga inicial de fuentes RSS por continente. | §4.2.1 | HU-RSS-009-v2 |
| RF-10 | Consulta y listado paginado/filtrado de canales, y detalle de un canal. | §4.2.1 | HU-RSS-010 |
| RF-11 | Diccionario de términos evaluables con su valor; mantenible por CRUD vía API REST. | §4.2.2, §10.2 | HU-SENT-001 |
| RF-12 | Carga inicial del diccionario de términos. | §4.2.2 | HU-SENT-001 (dataset: `Dataset-diccionario-inicial.md`) |
| RF-13 | Cálculo del valor de "humor" (análisis de sentimiento) de cada noticia capturada. | §4.2.4, §10.4 | HU-SENT-002-v3 |
| RF-14 | Persistencia del valor de humor junto a cada noticia. | §4.2.4 | HU-SENT-003 |
| RF-15 | Consulta del humor agregado: global, por continente, por país y evolución temporal (timeline). | §4.3.2, §10.2 | HU-SENT-004 |
| RF-16 | Análisis de sentimiento de un texto arbitrario que devuelve su valor de humor. | §10.2 | HU-SENT-005 |
| RF-17 | Entrenamiento y versionado de un modelo de ML para el cálculo de humor. | §2 Objetivo específico 2 | HU-SENT-006 |
| RF-18 | Detección de términos del diccionario presentes en cada noticia (base de la nube de palabras). | §4.3.1 | HU-SENT-008 |
| RF-19 | Dashboard de humor: mapa mundial con el humor por continente, con selector de fecha dentro del rango con información. | §4.3, §4.3.2 | HU-DASH-001-v3 |
| RF-20 | Listado de las noticias que más han influido en el cálculo del humor, con detalle y filtros. | §4.3, §4.3.2, §10.2 | HU-DASH-002-v2 |
| RF-21 | Nube de palabras influyentes, con filtro por continente y por país. | §4.3, §4.3.1, §10.2 | HU-DASH-003-v2 |
| RF-22 | Configuración de parámetros generales del sistema (periodicidad del cron y caducidad de noticias). | §4.2.5, §10.2 | HU-ADMIN-001 |
| RF-23 | Purgado automático de noticias anteriores al periodo de caducidad. | §4.2.5 | HU-ADMIN-002 |
| RF-24 | Purgado manual de noticias antiguas bajo demanda. | §4.2.5, §10.2 | HU-ADMIN-003 |
| RF-25 | Panel de administración unificado (fuentes, diccionario, parámetros). | §4.3 punto 1 | HU-ADMIN-004 |
| RF-26 | Documentación interactiva de la API REST con Swagger/OpenAPI (`/api/docs`). | §10.1 | (transversal, FastAPI) |

**Notas:**
- RF-25 (HU-ADMIN-004) está declarada **sin iniciar** en el backlog (`HU-ADMIN-administracion.md`): no se ha implementado un panel unificado. Las vistas de gestión existentes (fuentes, diccionario, parámetros) se operan hoy vía la API REST y las vistas del frontend. Se deja como requisito pendiente del equipo.
- RF-12 (carga inicial del diccionario) se implementó como script interno (`python -m scripts.seed_diccionario`), de forma análoga a RF-09 (carga inicial de fuentes, `python -m scripts.seed`). El dataset está en `docs/Backlog/Dataset-diccionario-inicial.md`, propuesto y pendiente de aprobación del equipo.

---

## 2. Requisitos No Funcionales

Derivados de §4.4, §4.6, §7 y §10.3.

| ID | Requisito no funcional | Origen (PDF) | Cómo se cumple hoy |
|---|---|---|---|
| RNF-01 | Idiomas soportados para el análisis: inglés y español. | §4.4, §3 punto 2 | Diccionario con campo `idioma` (es/en); detección de idioma por noticia (HU-SENT-007-v3, `lematizacion.py`). |
| RNF-02 | Categorización de noticias por IPTC Media Topics (primer nivel). | §3 punto 3 | Validación de `categoria_iptc` en el alta de fuentes (HU-RSS-002). |
| RNF-03 | Fuentes RSS exclusivamente (sin web scraping). | §3 punto 1, §4.2.1 | Captura vía feedparser/httpx sobre feeds RSS (EPIC-RSS). |
| RNF-04 | Seguridad y privacidad: fuentes públicas, sin datos sensibles; proteger correos si se implementan alertas. | §4.6.1 | No se manejan datos sensibles; sin autenticación (§3 punto 3); alertas por correo no implementadas (opcional, §4.5). |
| RNF-05 | Mantenibilidad: estándares de calidad de código, recomendado SonarQube. | §4.6.2 | Job `sonarqube` en `.github/workflows/ci.yml`; `sonar-project.properties` en la raíz. **Pendiente del equipo:** revisar el dashboard de SonarQube para confirmar ausencia de issues críticos (el pipeline no incluye Quality Gate bloqueante). |
| RNF-06 | Arquitectura modular en capas (datos, lógica, presentación). | §4.6.2, §6.1 | API (`routers/`), Servicios (`services/`), Repositorios (`repositories/`), Persistencia (MySQL/Alembic); frontend React separado. |
| RNF-07 | Todo el código versionado en GitHub. | §4.6.2 | Repositorio GitHub `Lin0u/Equipo3-Humworld`. |
| RNF-08 | CI/CD: pipeline que ejecute pruebas, análisis de calidad y build de imagen Docker. | §4.6.3 | `.github/workflows/ci.yml`: jobs `test`, `test-frontend`, `sonarqube`, `build-and-deploy`. |
| RNF-09 | Dependencias entre jobs (`needs`) para que build/despliegue solo ocurra si tests y calidad pasan. | §4.6.3 (instrucciones de equipo) | `build-and-deploy` con `needs: [test, test-frontend, sonarqube]`. |
| RNF-10 | Cobertura mínima de pruebas del 80%. | §7 | Backend: `pytest --cov-fail-under=80` en CI. Frontend: umbral 80% (líneas/sentencias/funciones/ramas) en `vite.config.js`. |
| RNF-11 | Pruebas unitarias por módulo, con dependencias externas simuladas (mocks). | §7, DoD | Suite en `src/tests/` (RSS, respx; ML con Gemini mockeado) y `frontend/src/` (API simulada). |
| RNF-12 | Pruebas de integración (API ↔ BD, Frontend ↔ API). | §7 | Pruebas de endpoint con `TestClient` sobre SQLite en memoria; pruebas del cliente del frontend con `fetch` simulado. **Pendiente del equipo:** pruebas de integración extremo a extremo Frontend ↔ API real. |
| RNF-13 | Pruebas de aceptación (escenarios de usuario) y de carga. | §7 | Escenarios Gherkin en cada HU cubiertos por pruebas automatizadas. **Pendiente del equipo:** pruebas de carga con múltiples fuentes RSS (no implementadas). |
| RNF-14 | Contenerización con Docker. | §4.6.3, §6.2 | `Dockerfile` y `docker-compose.yml` (API + MySQL). |
| RNF-15 | Convenciones de API: base `/api/v1`, JSON, códigos HTTP estándar (200/201/204/400/404/500). | §10.3 | Todos los routers bajo `/api/v1`; respuestas JSON; códigos declarados en los contratos OpenAPI. |
| RNF-16 | Resiliencia ante servicios externos inestables (feeds RSS). | §13 instrucciones de equipo (grounding en `docs/architecture.md` §8) | Timeout, Retry con backoff acotado y Circuit Breaker por fuente en la captura; fallback a diccionario en el cálculo con ML. |

---

## 3. Matriz de Trazabilidad

Trazabilidad **requisito → historia → endpoint/mecanismo → prueba**. El endpoint se lista con su prefijo real (`/api/v1`, montado en `src/app/main.py`). La columna "Prueba" referencia archivos de `src/tests/` (backend) o `frontend/src/` (frontend).

| RF | Historia | Endpoint / mecanismo | Contrato OpenAPI | Prueba |
|---|---|---|---|---|
| RF-01 | HU-RSS-001 | `POST /api/v1/channels` | canales-fuentes-rss v1.8.0 | `test_channels.py` |
| RF-03 | HU-RSS-003-v2 | `GET /api/v1/sources`, `GET /api/v1/sources/{id}` | canales-fuentes-rss | `test_sources.py` |
| RF-02 | HU-RSS-002 | `POST /api/v1/sources` | canales-fuentes-rss | `test_sources.py` |
| RF-04 | HU-RSS-004 | `PUT /api/v1/sources/{id}`, `PATCH /api/v1/sources/{id}` | canales-fuentes-rss | `test_sources.py` |
| RF-05 | HU-RSS-005 | `DELETE /api/v1/sources/{id}` (soft delete) | canales-fuentes-rss | `test_sources.py` |
| RF-06 | HU-RSS-006 | Cron interno (APScheduler) | — (sin endpoint) | `test_captura_automatica.py` |
| RF-07 | HU-RSS-007 | `GET /api/v1/config`, `PUT /api/v1/config` | canales-fuentes-rss | `test_configuracion_periodicidad.py` |
| RF-08 | HU-RSS-008 | `POST /api/v1/sources/{id}/captures`, `POST /api/v1/captures` | canales-fuentes-rss | `test_captura_manual.py` |
| RF-09 | HU-RSS-009-v2 | Script `python -m scripts.seed` | — (sin endpoint) | `test_seed.py` |
| RF-10 | HU-RSS-010 | `GET /api/v1/channels`, `GET /api/v1/channels/{id}` | canales-fuentes-rss | `test_channels.py` |
| RF-11 | HU-SENT-001 | `GET/POST /api/v1/dictionary`, `GET/PUT/PATCH/DELETE /api/v1/dictionary/{id}` | sentimiento-diccionario v1.1.0 | `test_dictionary.py` |
| RF-12 | HU-SENT-001 | Script `python -m scripts.seed_diccionario` | — (sin endpoint) | `test_seed_diccionario.py` |
| RF-13 | HU-SENT-002-v3 | Servicio interno (post-captura + barrido) | — (sin endpoint) | `test_sentimiento.py`, `test_modelo_ml.py` |
| RF-14 | HU-SENT-003 | Modelo `Noticia` (`valor_humor`, `polarizacion_terminos`) | — (sin endpoint) | `test_polarizacion_y_analisis.py` |
| RF-15 | HU-SENT-004 | `GET /api/v1/sentiment` | sentimiento-diccionario | `test_sentiment.py` |
| RF-16 | HU-SENT-005 | `POST /api/v1/sentiment` | sentimiento-diccionario | `test_polarizacion_y_analisis.py` |
| RF-17 | HU-SENT-006 | `POST /api/v1/trainings` | sentimiento-diccionario | `test_modelo_ml.py` |
| RF-18 | HU-SENT-008 | Tabla `noticia_termino` (consumida por word-cloud) | — (sin endpoint propio) | `test_nube_palabras.py`, `test_lematizacion.py` |
| RF-19 | HU-DASH-001-v3 | `GET /api/v1/dashboards/map` (+ `GET /api/v1/sentiment` para la serie temporal) | dashboards v1.1.0 | `test_dashboards.py`; frontend: `App.test.jsx` |
| RF-20 | HU-DASH-002-v2 | `GET /api/v1/news`, `GET /api/v1/news/{id}` | noticias v1.1.0 | `test_news.py`; frontend: `pantallas/ListadoNoticias.test.jsx` |
| RF-21 | HU-DASH-003-v2 | `GET /api/v1/dashboards/word-cloud` | dashboards | `test_nube_palabras.py`; frontend: `pantallas/NubePalabras.test.jsx`, `componentes/SelectorPais.test.jsx` |
| RF-22 | HU-ADMIN-001 | `GET /api/v1/config`, `PUT /api/v1/config` | canales-fuentes-rss | `test_purgado.py` |
| RF-23 | HU-ADMIN-002 | Job interno de purgado (APScheduler) | — (sin endpoint) | `test_purgado.py` |
| RF-24 | HU-ADMIN-003 | `DELETE /api/v1/news?fecha_anterior_a=YYYY-MM-DD` | noticias | `test_purgado.py` |
| RF-25 | HU-ADMIN-004 | (panel unificado, frontend) | — | — (sin iniciar) |
| RF-26 | — (transversal) | `/api/docs` (Swagger autogenerado) | — | `test_sources.py` (verifica el esquema OpenAPI del alta) |

**Endpoint implementado no cubierto por un requisito del PDF:** `GET /api/v1/health` (`health.py`) es un health check técnico; informa además si los modelos de spaCy (lematización) están cargados. No proviene de un RF del PDF; se documenta como endpoint operativo del sistema.

### Huecos de trazabilidad detectados

1. **RF-25 (HU-ADMIN-004, panel de administración unificado):** sin implementar. Pendiente del equipo.
2. **RNF-13 (pruebas de carga, §7):** no existen pruebas de carga con múltiples fuentes RSS. Pendiente del equipo.
3. **RNF-12 (integración Frontend ↔ API real, §7):** las pruebas del frontend simulan la API; no hay una prueba de integración extremo a extremo contra el backend real. Pendiente del equipo.
4. **RNF-05 (SonarQube sin issues críticos, §4.6.2):** el pipeline ejecuta el análisis pero no incluye un Quality Gate bloqueante; la ausencia de issues críticos debe confirmarse en el dashboard de SonarQube. Pendiente del equipo.

---

## Tabla de control de versiones

| Versión | Fecha | Motivo del cambio |
|---|---|---|
| v1.0 | 2026-10-29 | Creación. Lista formal de requisitos funcionales (RF-01 a RF-26) y no funcionales (RNF-01 a RNF-16) derivada del PDF de especificaciones del proyecto, con matriz de trazabilidad requisito → historia → endpoint → prueba y registro de huecos. Entregable de §4.7 punto 2 y §8.1. |
