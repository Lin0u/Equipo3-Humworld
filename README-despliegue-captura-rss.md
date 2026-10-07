# HumWorld — Módulo Captura RSS (esqueleto, Sprint 1)

Scaffolding del módulo de Captura RSS (EPIC-RSS), generado a partir de:
- **HU-RSS-001 a HU-RSS-009** (`HU-RSS-captura.md`)
- **ADR-001** — Elección del stack tecnológico de backend (Aceptado)
- **ADR-002** — Arquitectura del módulo de Captura RSS (Aceptado)
- **Contrato OpenAPI** — `contrato-canales-fuentes-rss.openapi.yaml`

**Importante:** este es un esqueleto (scaffolding), conforme a la sección 12
de las instrucciones del proyecto. Los endpoints de negocio (`/api/v1/channels`,
`/api/v1/sources`, `/api/v1/captures`, etc.) lanzan `NotImplementedError`
intencionalmente — el equipo debe implementar la lógica real apoyándose en
GitHub Copilot, revisando cada implementación antes de mergear. Lo que sí
funciona de inmediato: arranque del servidor, health check y documentación
Swagger/OpenAPI autogenerada.

---

## Opción A — Con Docker (recomendada)

```bash
docker compose up --build
```

Levanta dos servicios:
- `db`: MySQL 8.0 (credenciales de ejemplo en `docker-compose.yml` —
  **reemplazar antes de usar en cualquier entorno compartido**).
- `api`: la aplicación FastAPI, expuesta en `http://localhost:8000`.

Verificar:

```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok"}
```

Documentación interactiva (Swagger UI): `http://localhost:8000/api/docs`.

```bash
docker compose down       # detener
docker compose down -v    # detener y borrar datos de MySQL
```

## Opción B — Sin Docker (Python local)

```bash
cd src
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # y ajustar DATABASE_URL si corresponde

uvicorn app.main:app --reload --port 8000
```

`/api/v1/health` y `/api/docs` funcionan sin base de datos real (SQLAlchemy
no abre conexión hasta la primera consulta). Los endpoints de negocio fallan
hoy de todas formas por el `NotImplementedError` intencional.

## Ejecutar las pruebas

```bash
cd src
python -m venv venv
venv\Scripts\activate        # Windows (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt

pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

Las pruebas usan **SQLite en memoria** (con `dependency_overrides` de la sesión
de base de datos), por lo que **no requieren MySQL ni Docker** para ejecutarse.
Las llamadas a servicios externos (feeds RSS) se aíslan con mocks (`respx`),
nunca con llamadas reales — conforme a la sección 14 de las instrucciones del
proyecto.

### Estado de la Definition of Done de testing — Sprint 1 (EPIC-RSS)

La suite automatizada cubre las historias entregadas en Sprint 1:

- **HU-RSS-001** — Alta de canal de noticias.
- **HU-RSS-002** — Alta de fuente RSS dentro de un canal.
- **HU-RSS-003-v2** — Consulta y filtrado paginado de fuentes RSS (reemplaza a
  la HU-RSS-003 deprecada).
- **HU-RSS-004** — Modificación de fuente RSS (PUT/PATCH).
- **HU-RSS-005** — Eliminación de fuente RSS (borrado lógico).
- **HU-RSS-010** — Consulta y listado paginado de canales de noticias.

Cada prueba lleva un comentario de trazabilidad (`# HU-RSS-00X — Escenario: …`)
que la vincula con el escenario Gherkin correspondiente de
`docs/Backlog/HU-RSS-captura.md`.

Resultado de la última ejecución local: **78 pruebas en verde, cobertura del
módulo 95.90%** (umbral de la DoD: ≥80%, alcanzado).

### Alcance de la medición de cobertura (`.coveragerc`)

El archivo `src/.coveragerc` excluye de la medición el scaffolding intencional
de historias todavía no implementadas (HU-RSS-006/007/008/009), que lanzan
`NotImplementedError` a propósito (sección 12 de las instrucciones del
proyecto):

- `app/routers/captures.py`
- `app/services/captura_service.py`
- `app/jobs/scheduler.py`

De este modo, el umbral del 80% se calcula solo sobre el código realmente
entregado en Sprint 1 (canales y fuentes RSS con sus capas de router, servicio,
repositorio, esquemas y modelos), sin penalizar código que aún no corresponde
probar. Cuando se implementen HU-RSS-006 a 009, esos archivos deben retirarse
del `omit` y cubrirse con sus propias pruebas.

`pytest-cov` lee `.coveragerc` automáticamente al ejecutarse desde `src/`, tanto
en local como en el pipeline de CI.

### Recomendación al equipo — alineación del pipeline de CI

El pipeline (`.github/workflows/ci.yml`) exige cobertura ≥80%
(`--cov-fail-under=80`) y bloquea build/deploy si tests o SonarQube fallan
(`needs: [test, sonarqube]`). Como QA **no modifica el pipeline**, se deja como
recomendación para el responsable de CI/DevOps:

1. Verificar que el paso de `pytest` del CI se ejecuta desde `src/` (ya es el
   caso), de forma que recoja automáticamente `src/.coveragerc`. Con eso,
   `--cov-fail-under=80` pasa a medirse sobre el módulo entregado y el job de
   `test` deja de fallar de forma intencional para las historias de Sprint 1.
2. Considerar retirar el comentario "fallará intencionalmente…" del `ci.yml`
   una vez confirmado el punto anterior, ya que las HU-RSS-001 a 005 y 010
   cuentan con lógica y pruebas reales.
3. Mantener el `omit` actualizado a medida que se implementen las historias de
   captura (HU-RSS-006 a 009).

## Estructura

```
src/
  app/
    core/config.py       # Settings (env vars) — ver TODOs de periodicidad/timeouts
    database.py           # SQLAlchemy engine/session (MySQL)
    models/                # CanalNoticias, FuenteRSS, Noticia (ORM)
    schemas/                # Pydantic — coherentes 1:1 con el contrato OpenAPI
    routers/                # channels, sources, captures, health
    services/captura_service.py  # lógica de captura (stub) — HU-RSS-006/008
    jobs/scheduler.py       # cron (APScheduler, stub) — HU-RSS-006/007
    main.py
  scripts/seed.py           # carga inicial por continente (stub) — HU-RSS-009
  tests/test_health.py      # health check del scaffold
  tests/test_channels.py    # HU-RSS-001 (alta) + HU-RSS-010 (listado/detalle)
  tests/test_sources.py     # HU-RSS-002/003-v2/004/005 (alta, consulta, PUT/PATCH, delete)
  .coveragerc               # excluye el scaffolding de HU-RSS-006/007/008/009 de la cobertura
  pytest.ini                # config de pytest (loop scope de asyncio, testpaths)
  requirements.txt
Dockerfile
docker-compose.yml
.github/workflows/ci.yml
```

## Siguiente paso para el equipo

1. Completar los `TODO(equipo)` en `app/routers/*.py` y
   `app/services/captura_service.py`, apoyándose en GitHub Copilot (sección
   12 de las instrucciones del proyecto).
2. Configurar Alembic (`alembic init`) para generar la migración inicial de
   `canales_noticias`, `fuentes_rss` y `noticias`.
3. Escribir pruebas unitarias con mocks (`respx`, ya en `requirements.txt`)
   para las llamadas HTTP a feeds RSS — nunca pruebas con llamadas reales.
4. Definir y confirmar (pendientes explícitos en HU-RSS-005, HU-RSS-008,
   HU-RSS-009 y en ADR-002): política de borrado en cascada de noticias,
   nombre exacto del recurso de captura, valores por defecto de timeout/
   retry/circuit breaker, y listado definitivo de fuentes semilla.
5. **Fuera de este scaffold:** HU-RSS-007 (config de periodicidad) requiere
   un router/modelo `/api/v1/config` que todavía no existe en el contrato
   OpenAPI actual — falta generarlo antes de implementar esa historia.
