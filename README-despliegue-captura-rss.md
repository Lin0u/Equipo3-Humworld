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
pytest --cov=app --cov-report=term-missing
```

Actualmente solo existe la prueba del health check. El pipeline de CI
(`.github/workflows/ci.yml`) ya está preparado para exigir cobertura ≥80%
(`--cov-fail-under=80`) y bloquear build/deploy si tests o SonarQube fallan
(`needs: [test, sonarqube]`) — fallará intencionalmente hasta que el equipo
implemente la lógica real y sus pruebas.

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
  tests/test_health.py
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
