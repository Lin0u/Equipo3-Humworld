# Guía de ejecución — Práctica P6 OpenSpec II (Specification-Driven Development) aplicada a HumWorld

**Proyecto:** HumWorld — Equipo 3
**Práctica de referencia:** `P6 - OPENSPEC II` (continuación de P5)
**Historia 1 (ya ejecutada en P5):** HU-RSS-001 — Alta de Canal de Noticias (cambio OpenSpec `alta-canal-noticias`, propuesto en `GUIA-P5-OPENSPEC-HU-RSS-001.md`)
**Historia 2 (nueva, formalizada para esta práctica):** HU-RSS-010 — Consulta y listado de Canales de Noticias
**Fecha/sesión:** 2026-08-30
**Objetivo de este documento:** traducir paso a paso las instrucciones genéricas de P6 (que usa el proyecto de ejemplo "AGENDA" y las historias "HU-01 Registrar persona" / "HU-02 Listar personas") al contexto real de HumWorld, para que el equipo pueda ejecutarla directamente en su repositorio.

> **Importante — qué es y qué no es este documento.** Igual que `GUIA-P5-OPENSPEC-HU-RSS-001.md`, esta práctica requiere trabajo en el entorno local del equipo: crear ficheros en VS Code, ejecutar comandos OpenSpec y conversar con GitHub Copilot Chat dentro del repositorio real de HumWorld. Este documento no reemplaza esos pasos — da el contenido exacto de cada artefacto y el prompt exacto de cada comando, ya adaptados a HumWorld, para no perder tiempo de clase traduciendo "AGENDA/personas" al dominio real.
>
> **Nota de trazabilidad:** HU-RSS-010 fue formalizada en sesión de trabajo el 2026-08-26 a partir de un endpoint (`GET /api/v1/channels`, `GET /api/v1/channels/{id}`) que ya existía en `contrato-canales-fuentes-rss.openapi.yaml` desde el 14-ago pero sin criterios de aceptación propios (estaba atribuido de forma implícita a HU-RSS-001). Ver `HU-RSS-captura.md`, ADR-001 v1.2 y ADR-002 v1.2 para el detalle de esa corrección.

---

## 0. Por qué HU-RSS-001 + HU-RSS-010 son el par correcto para P6

P6 exige una segunda historia que consulte/liste la **misma entidad** que la historia piloto de P5 registró. HU-RSS-001 registra `CanalNoticias`; HU-RSS-010 consulta y lista `CanalNoticias`. Es el mismo patrón que el propio backlog ya usa para Fuentes RSS (HU-RSS-002 alta / HU-RSS-003 consulta), así que no se introduce ningún patrón nuevo — solo se completa, para Canales, el par alta/consulta que ya existía para Fuentes.

---

## 1. Documentar la arquitectura del proyecto (sección 4 del documento original)

Igual que exige P6, la arquitectura debe quedar **almacenada en el repositorio**, no solo en este documento ni en prompts sueltos. Se usan los mismos tres artefactos que indica la práctica.

### 1.1 `docs/architecture.md`

Crear el directorio `docs/` en la raíz del repositorio de HumWorld (si no existe) y, dentro, el fichero `architecture.md`. Contenido a copiar y revisar — es una destilación de lo ya aceptado en **ADR-001** y **ADR-002**, no una decisión nueva:

```markdown
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

## 2. Tecnologías aprobadas (ADR-001, ADR-002)
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

No se añadirán tecnologías sin una decisión explícita y documentada (nuevo
ADR o nueva versión de uno existente).

## 3. Estilo arquitectónico
Arquitectura distribuida/en capas: API, Servicios, Repositorios y
Persistencia (PDF de especificaciones, sección 6.1; ADR-002, sección 4).

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

## 5. Modelo de datos vigente (ADR-002)
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
- GET /api/v1/channels, GET /api/v1/channels/{id} — HU-RSS-010.
- POST /api/v1/sources — HU-RSS-002.
- GET /api/v1/sources, GET /api/v1/sources/{id} — HU-RSS-003.
- PUT/PATCH /api/v1/sources/{id} — HU-RSS-004.
- DELETE /api/v1/sources/{id} — HU-RSS-005.
- GET/PUT /api/v1/config — HU-RSS-007.
- POST /api/v1/sources/{id}/captures, POST /api/v1/captures — HU-RSS-008
  (nombre exacto de recurso pendiente de confirmación por el equipo).

## 7. Organización orientativa
app/main.py, app/api/ (routers), app/models/ (SQLAlchemy),
app/schemas/ (Pydantic), app/services/, app/repositories/ y tests/.
No hay app/static/ ni app/templates/: el frontend de HumWorld es una SPA
separada (PDF, sección 6.2), fuera del alcance de este backend.

## 8. Reglas
- No concentrar toda la aplicación en un fichero.
- No acceder a MySQL desde los routers: toda sentencia de acceso a datos
  va en la capa de Repositorios (SQLAlchemy).
- No colocar lógica de negocio en los routers.
- Cada historia debe incluir pruebas, con dependencias externas (RSS)
  aisladas mediante mocks.
- Todo cambio debe corresponder a una especificación OpenSpec.
- Los cambios arquitectónicos requieren revisión humana y, si alteran una
  decisión ya tomada, una nueva versión del ADR correspondiente.
- Los patrones de resiliencia (Timeout explícito, Retry acotado con
  backoff exponencial, Circuit Breaker por fuente — ADR-002, sección 3)
  son obligatorios en toda llamada a una fuente RSS externa.

## 9. Errores
No exponer trazas internas. Utilizar códigos HTTP coherentes con
contrato-canales-fuentes-rss.openapi.yaml y tratar los errores de
persistencia y de red de forma controlada (nunca reintentos infinitos).

## 10. Fuera de alcance (de esta versión del documento)
Análisis de sentimiento, dashboard/mapa mundial, diccionario de términos,
purgado automático, autenticación y autorización (PDF, sección 3,
Limitaciones).
```

### 1.2 Incorporar la arquitectura al contexto de OpenSpec

Abrir `openspec/config.yaml`. Conservar las opciones ya creadas por `openspec init` (del cambio `alta-canal-noticias` de P5) e integrar, sin duplicar claves, el siguiente contenido:

```yaml
schema: spec-driven
githubCopilot:
  cloudAgent: true
context: |
  Proyecto: HumWorld — Equipo 3.
  Objetivo:
    Sistema que analiza noticias en tiempo real capturadas vía RSS
    para calcular y actualizar el "estado de ánimo" del mundo mediante
    análisis de sentimiento. Este contexto cubre el módulo de Captura
    RSS (Sprint 1 / EPIC-RSS).
  Arquitectura oficial:
    Consultar docs/architecture.md, ADR-001-stack-backend.md y
    ADR-002-arquitectura-captura-rss.md antes de proponer, diseñar o
    implementar cualquier cambio.
  Tecnologías aprobadas:
    - Python 3.11 o superior.
    - FastAPI para la API REST.
    - SQLAlchemy 2.x + Alembic, sobre MySQL.
    - Pydantic v2 para validación y serialización.
    - httpx (async) + feedparser para el consumo de feeds RSS/Atom.
    - APScheduler para el cron interno de captura.
    - pytest + pytest-asyncio + pytest-cov + respx/responses para pruebas.
  Componentes:
    - API FastAPI (routers).
    - Capa de servicios (lógica de negocio y patrones de resiliencia).
    - Capa de repositorios (SQLAlchemy sobre MySQL).
  Organización prevista:
    - app/main.py contiene la aplicación FastAPI y el registro de routers.
    - app/api/ contiene los routers (channels, sources, captures).
    - app/services/ contiene la lógica de negocio.
    - app/repositories/ contiene el acceso a datos (SQLAlchemy).
    - tests/ contiene las pruebas automatizadas.
  Reglas arquitectónicas:
    - Los routers no pueden acceder directamente a MySQL.
    - Las sentencias de acceso a datos deben estar únicamente en
      app/repositories/.
    - app/api/ no debe contener SQL ni lógica de negocio.
    - Todo llamado a una fuente RSS externa debe aplicar Timeout
      explícito, Retry acotado con backoff exponencial y Circuit Breaker
      por fuente (ver ADR-002, sección 3). Nunca reintentos infinitos.
    - No añadir nuevas tecnologías o dependencias sin aprobación humana.
    - Mantener el desarrollo limitado a las historias aprobadas (HU-RSS-*).
    - Cada historia debe incluir pruebas automatizadas con mocks para
      llamadas HTTP externas.
    - Utilizar los términos CanalNoticias y FuenteRSS para las entidades
      gestionadas (no "canal"/"fuente" a secas en el código).
    - El actor de las historias de administración es "administrador del
      sistema".
  Alcance del incremento actual (HU-RSS-001 + HU-RSS-010):
    - Dar de alta canales de noticias.
    - Consultar y listar canales de noticias (con filtro opcional por
      continente).
    - Conservar los datos en MySQL.
  Fuera del alcance:
    - Modificación y eliminación de canales de noticias.
    - Gestión de fuentes RSS (HU-RSS-002 a HU-RSS-005 — incrementos
      posteriores).
    - Cron de captura, configuración de periodicidad y captura manual
      (HU-RSS-006 a HU-RSS-008).
    - Análisis de sentimiento, dashboard, diccionario de términos, purgado.
    - Autenticación y autorización.
rules:
  proposal:
    - Indicar con claridad el objetivo y el alcance del cambio.
    - Identificar expresamente las funcionalidades que quedan fuera.
    - Indicar si el cambio afecta a docs/architecture.md o a algún ADR.
    - No proponer tecnologías que no estén aprobadas en el contexto.
  specs:
    - Escribir los escenarios en formato Given/When/Then (Dado/Cuando/Entonces).
    - Describir comportamientos observables y verificables, con cifras concretas.
    - Mantener los requisitos independientes de los detalles de implementación.
    - Utilizar CanalNoticias/FuenteRSS para las entidades gestionadas.
    - Utilizar "administrador del sistema" para el actor de las historias
      administrativas.
    - Incluir escenarios básicos de funcionamiento correcto y de error.
  design:
    - Leer y respetar docs/architecture.md y los ADR vigentes.
    - Explicar la participación de la capa API, Servicios y Repositorios.
    - Mantener el acceso a datos únicamente en app/repositories/.
    - Identificar los ficheros que deberán crearse o modificarse.
    - No introducir componentes, capas, tecnologías o dependencias
      adicionales.
    - Indicar cómo se probará el cambio (con qué mocks).
    - Justificar cualquier desviación respecto a la arquitectura aprobada.
  tasks:
    - Organizar las tareas por componente o fichero.
    - Dividir la implementación en tareas pequeñas y verificables.
    - Incluir las tareas necesarias para las pruebas automatizadas.
    - Incluir la ejecución final de pytest (con cobertura ≥80%).
    - Incluir una comprobación final de conformidad con docs/architecture.md.
    - No añadir tareas que estén fuera del alcance aprobado.
operations:
  apply:
    guidance:
      - Leer docs/architecture.md y los ADR vigentes antes de modificar código.
      - Leer todos los artefactos OpenSpec del cambio.
      - Implementar únicamente las tareas aprobadas.
      - Mantener la separación entre API, Servicios y Repositorios.
      - Mantener todas las sentencias de acceso a datos en app/repositories/.
      - No incorporar tecnologías ni dependencias nuevas.
      - Ejecutar pytest después de implementar el cambio.
      - No marcar una tarea como completada sin verificarla.
      - Detener la implementación si la especificación contradice la arquitectura.
  archive:
    guidance:
      - Comprobar que la implementación respeta docs/architecture.md.
      - Confirmar que todas las tareas aprobadas están completadas.
      - Confirmar que pytest se ejecuta correctamente con cobertura ≥80%.
      - Comprobar que no se han añadido funcionalidades fuera del alcance.
      - Resumir el resultado de la implementación antes de archivar.
```

**Importante (igual que en el documento original):** si `config.yaml` ya contiene `schema`, `rules`, `operations` o `githubCopilot` desde P5, integrar el contenido; no crear claves duplicadas ni borrar la configuración existente.

### 1.3 Crear instrucciones permanentes para Copilot

Crear `.github/copilot-instructions.md` con el siguiente contenido:

```markdown
# Instrucciones de desarrollo para HumWorld — Módulo Captura RSS

Antes de proponer, diseñar, implementar o revisar:
1. Lee docs/architecture.md.
2. Lee ADR-001-stack-backend.md y ADR-002-arquitectura-captura-rss.md.
3. Lee los artefactos OpenSpec del cambio.
4. Comprueba que la petición no contradice la arquitectura ni los ADR vigentes.
5. Si existe una contradicción, detente e informa antes de modificar código.

## Arquitectura obligatoria
- Python 3.11+, FastAPI, SQLAlchemy 2.x + Alembic sobre MySQL, Pydantic v2.
- httpx async + feedparser para RSS; APScheduler para el cron interno.
- Separar API (routers), Servicios (lógica de negocio) y Repositorios
  (acceso a datos).
- Los routers no acceden a MySQL ni contienen SQL.
- Los servicios no dependen del framework web.
- Toda llamada a una fuente RSS externa aplica Timeout explícito, Retry
  acotado con backoff exponencial y Circuit Breaker por fuente (ADR-002).
  Nunca reintentos infinitos.
- No añadir tecnologías sin aprobación humana.

## Terminología
- Las entidades se denominan CanalNoticias y FuenteRSS (no "canal"/
  "fuente" genéricos en el código).
- El actor de las historias administrativas se denomina "administrador
  del sistema".

## Desarrollo con OpenSpec
- No implementar sin especificación revisada.
- Seguir proposal.md, spec.md, design.md y tasks.md.
- No añadir funcionalidades fuera de alcance (ver HU-RSS-* vigentes).
- No cambiar la especificación sin informar al equipo.
- Marcar tareas solo después de verificarlas.

## Calidad
- Generar pruebas para cada historia (mocks para llamadas HTTP externas)
  y ejecutar pytest.
- Cobertura de pruebas ≥80%, verificada en GitHub Actions.
- Utilizar códigos HTTP coherentes con
  contrato-canales-fuentes-rss.openapi.yaml.
- No exponer trazas internas al usuario.
- SonarQube sin issues críticos.
```

### 1.4 Comprobar que Copilot utiliza las instrucciones

Abrir Copilot Chat en VS Code y enviar:

```
Sin modificar ningún fichero, revisa las instrucciones del repositorio
y docs/architecture.md. Resume:
1. Tecnologías obligatorias.
2. Capas de la aplicación.
3. Dependencias no permitidas.
4. Endpoints vigentes de Sprint 1 (EPIC-RSS).
5. Funcionalidades fuera de alcance.
Indica qué ficheros has utilizado como fuente.
```

Comprobar que la respuesta menciona `docs/architecture.md`, `.github/copilot-instructions.md`, FastAPI, SQLAlchemy/MySQL, separación por capas, `POST /api/v1/channels` y `GET /api/v1/channels`.

---

## 2. Definir HU-RSS-010 — Consulta y listado de Canales de Noticias

### 2.1 Historia (ya formalizada en `HU-RSS-captura.md`)

```
Como administrador o analista de medios, quiero consultar el listado de
canales de noticias registrados, opcionalmente filtrado por continente,
y el detalle de un canal específico, para poder conocer los medios de
comunicación configurados en el sistema y auditar la cobertura de
canales por continente.
```

Criterios ya acordados (ver HU-RSS-captura.md):
- Listado sin filtros: `GET /api/v1/channels` → 200 y N elementos (N≥0).
- Filtro por continente: `GET /api/v1/channels?continente=America` → 100% de los elementos con ese continente.
- Detalle de canal existente: `GET /api/v1/channels/{id}` → 200 con datos completos.
- Detalle de canal inexistente: `GET /api/v1/channels/{id}` → 404.

### 2.2 Decisiones aún abiertas (equivalente a la sección 5.2/5.3 de P6 — a resolver por el equipo, no asumidas aquí)

Al igual que P6 pide analizar ambigüedades con Copilot antes de programar, quedan **al menos** estos puntos sin definir en `HU-RSS-captura.md` (no se han inventado valores):

1. **Orden del listado.** El ejemplo de P6 ordena por apellido y nombre; para canales no se ha definido si se ordena por `nombre`, por `continente` + `nombre`, o si no se garantiza ningún orden. **No especificado — decisión del equipo.**
2. **Paginación.** No está contemplada en los criterios actuales ni exigida por el PDF para este endpoint. Debe confirmarse explícitamente que se excluye para este incremento (igual que ocurre con HU-RSS-003), o definir el mecanismo si el equipo la considera necesaria.
3. **Actualización del listado tras un alta.** HU-RSS-010 es un endpoint puro de backend; si el equipo construye una interfaz de prueba (más allá de Swagger), debe decidir si espera refresco automático o manual.

Prompt sugerido para Copilot Chat (adaptado de la sección 5.2 del documento original) para que el equipo resuelva estos puntos antes de congelarlos:

```
Estamos desarrollando HumWorld mediante SDD y OpenSpec.

Historia: HU-RSS-010 — Consulta y listado de Canales de Noticias.
Como administrador o analista de medios, quiero consultar el listado de
canales de noticias registrados, opcionalmente filtrado por continente,
y el detalle de un canal específico.

Criterios ya acordados:
- GET /api/v1/channels devuelve 200 y N elementos (N≥0).
- GET /api/v1/channels?continente=X devuelve solo canales de ese continente.
- GET /api/v1/channels/{id} devuelve 200 con el detalle, o 404 si no existe.

Quiero utilizar OpenSpec y trabajar siguiendo Specification-Driven
Development.

Analiza la funcionalidad. Identifica: orden del listado, si aplica
paginación, campos exactos a devolver, y casos límite o de error no
cubiertos todavía.

No escribas código ni tomes automáticamente las decisiones. Formula
preguntas para que las resuelva el equipo.
```

---

## 3. Crear el cambio `listar-canales` con OpenSpec

En Copilot Chat, dentro del repositorio de HumWorld:

```
/opsx:propose listar-canales

Antes de generar los artefactos:
1. Lee docs/architecture.md.
2. Aplica el contexto y reglas de openspec/config.yaml.
3. Respeta .github/copilot-instructions.md.
4. Si la historia contradice la arquitectura, informa y no continúes.

Implementar HU-RSS-010 de HumWorld.

Como administrador o analista de medios, quiero consultar el listado de
canales de noticias registrados, opcionalmente filtrado por continente
(GET /api/v1/channels), y el detalle de un canal específico
(GET /api/v1/channels/{id}).

Criterios acordados:
- Sin filtros, devuelve todos los canales existentes (200, N elementos).
- El filtro "continente" devuelve únicamente canales de ese continente.
- El detalle de un canal inexistente devuelve 404.
- [Completar aquí con lo que el equipo decida en la sección 2.2 sobre
  orden del listado y paginación antes de ejecutar este prompt.]

No implementar todavía código. Preparar proposal.md, spec.md, design.md,
tasks.md y estrategia de pruebas. En design.md identifica la
participación de cada capa definida en docs/architecture.md.
```

Resultado esperado:
```
openspec/changes/listar-canales/
├── proposal.md
├── specs/
│   └── listar-canales/
│       └── spec.md
├── design.md
└── tasks.md
```

**Revisar antes de programar** (no saltarse este paso, igual que en GUIA-P5): que `spec.md` cubra los cuatro escenarios ya acordados más los que resuelva el equipo en la sección 2.2; que `design.md` mantenga el acceso a datos en `app/repositories/` y no contradiga el modelo de composición `CanalNoticias → FuenteRSS` (ADR-002); que `tasks.md` no incluya, por error, tareas de HU-RSS-002 a HU-RSS-009.

---

## 4. Implementar HU-RSS-001 — Alta de Canal de Noticias

Abrir la rama `feature/alta-canal-noticias` (o la que use el equipo) y enviar en Copilot Chat:

```
/opsx:apply alta-canal-noticias

Antes de modificar código:
1. Lee docs/architecture.md, ADR-001-stack-backend.md y
   ADR-002-arquitectura-captura-rss.md.
2. Lee .github/copilot-instructions.md.
3. Lee todos los artefactos del cambio alta-canal-noticias.
4. Comprueba que design.md respeta la arquitectura.
5. Si existe una contradicción, detente y comunícala.

Implementa únicamente las tareas aprobadas. Mantén separadas API,
Servicios y Repositorios. Usa SQLAlchemy sobre MySQL. Añade pruebas con
mocks. No añadas funcionalidades no especificadas ni marques una tarea
sin verificarla.

POST /api/v1/channels recibe nombre, continente y opcionalmente pais y
descripcion. Si nombre y continente son válidos y el nombre no está
duplicado, la aplicación crea el canal y devuelve HTTP 201. Si faltan
datos obligatorios, devuelve 400. Si el nombre ya existe, devuelve 409.
```

---

## 5. Implementar HU-RSS-010 — Consulta y listado de Canales de Noticias

```
/opsx:apply listar-canales

1. Lee docs/architecture.md, ADR-001-stack-backend.md y
   ADR-002-arquitectura-captura-rss.md.
2. Lee .github/copilot-instructions.md.
3. Lee todos los artefactos de listar-canales.
4. Comprueba que design.md respeta la arquitectura.
5. Si existe una contradicción, detente y comunícala.

Implementa únicamente las tareas aprobadas. Comprueba: GET
/api/v1/channels, filtro por continente, GET /api/v1/channels/{id},
HTTP 200 con datos completos, HTTP 404 para canal inexistente, y
pruebas para cada escenario.

No implementes modificación ni eliminación de canales, ni gestión de
fuentes RSS: eso corresponde a HU-RSS-002 a HU-RSS-005, fuera de alcance
de este incremento.
```

El equipo revisará manualmente nombres, separación de responsabilidades, duplicación, validaciones, excepciones, consultas, códigos HTTP, dependencias y correspondencia con `spec.md` y `design.md` — igual que exige P6.

---

## 6. Pruebas automatizadas

| ID | Prueba |
|---|---|
| PR-01 | Alta de un canal con datos válidos (`nombre` y `continente`). |
| PR-02 | Rechazar el alta si falta `nombre` o `continente`. |
| PR-03 | Rechazar el alta si `nombre` ya existe (409). |
| PL-01 | Listar varios canales sin filtros. |
| PL-02 | Comprobar los campos devueltos por canal. |
| PL-03 | Filtrar por continente y verificar que el 100% de los resultados coincide. |
| PL-04 | Listar canales cuando no existe ninguno: HTTP 200 y `[]`. |
| PL-05 | Consultar el detalle de un canal existente. |
| PL-06 | Consultar el detalle de un canal inexistente: HTTP 404. |
| PL-07 | Comprobar que un canal recién creado aparece en el listado. |

```
pytest --cov=app --cov-report=term-missing
```

**Criterio:** las pruebas deben contener aserciones relevantes y corresponder a los escenarios de `spec.md`. Ejecutar código sin comprobar el resultado no constituye una prueba suficiente (igual que exige el documento original).

---

## 7. Pruebas manuales

### 7.1 Ejecutar la aplicación
```
uvicorn app.main:app --reload
```

### 7.2 Comprobar Swagger
```
http://127.0.0.1:8000/api/docs
```

### 7.3 Secuencia de validación
- Iniciar la aplicación con la tabla de canales vacía.
- Comprobar que `GET /api/v1/channels` devuelve HTTP 200 y `[]`.
- Registrar un canal (`POST /api/v1/channels`) y verificar que aparece en el listado.
- Registrar un segundo canal en otro continente y comprobar el filtro `?continente=`.
- Consultar el detalle (`GET /api/v1/channels/{id}`) del canal creado.
- Consultar el detalle de un id inexistente y confirmar el 404.
- Reiniciar la aplicación y confirmar que los datos persisten en MySQL.
- Comparar el resultado de Swagger con `contrato-canales-fuentes-rss.openapi.yaml`.

---

## 8. Actualizar GitHub — Pull Request

Igual que indica el documento original: esta actividad queda para una práctica posterior. En esta práctica no se realiza el Pull Request de `alta-canal-noticias` ni de `listar-canales`.

---

## 9. Bibliografía

- Fission AI. OpenSpec: Specification-Driven Development for AI coding assistants. https://github.com/Fission-AI/OpenSpec
- Fission AI. OpenSpec Customization. https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md
- GitHub. Adding repository custom instructions for GitHub Copilot. https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot
- Visual Studio Code. Set up GitHub Copilot in VS Code. https://code.visualstudio.com/docs/setup/copilot
- FastAPI. FastAPI Documentation. https://fastapi.tiangolo.com/
- SQLAlchemy. SQLAlchemy Documentation. https://docs.sqlalchemy.org/
- pytest. pytest Documentation. https://docs.pytest.org/
- GitHub. Building and testing Python. https://docs.github.com/actions/use-cases-and-examples/building-and-testing/building-and-testing-python

---

## 10. Anexo — Errores frecuentes a evitar

- Sobrescribir `openspec/config.yaml` y perder las claves ya creadas por el cambio `alta-canal-noticias` de P5.
- Duplicar claves o usar indentación YAML incorrecta al integrar el nuevo `context`.
- Enviar `/opsx:propose listar-canales` separado de la descripción de la historia.
- Implementar HU-RSS-010 antes de resolver las decisiones abiertas de la sección 2.2 (orden, paginación).
- Documentar los escenarios solo en la Issue de GitHub y dejar `spec.md` incompleto.
- Acceder a MySQL desde los routers o mezclar SQL fuera de `app/repositories/`.
- Confundir `HU-RSS-captura.md` (historia de usuario) con `spec.md` de OpenSpec (especificación) — son artefactos distintos y complementarios.
- Generar pruebas sin aserciones relevantes.
- Aceptar automáticamente artefactos o código generados por IA sin revisión del equipo.
- Reintroducir el endpoint `GET /channels` como si fuera nuevo: ya existía en el contrato desde el 14-ago; este incremento solo lo formaliza con historia y pruebas propias.

---

## Próximo paso sugerido

Una vez el equipo resuelva las decisiones abiertas de la sección 2.2 y ejecute `/opsx:propose listar-canales`, puedo ayudar a: (a) contrastar `spec.md`/`design.md` generados contra ADR-002 y `HU-RSS-captura.md` para detectar inconsistencias, y (b) si el equipo lo pide explícitamente, generar el scaffolding inicial de `GET /api/v1/channels` y `GET /api/v1/channels/{id}` sin lógica de negocio, según la sección 12 de las instrucciones del proyecto.
