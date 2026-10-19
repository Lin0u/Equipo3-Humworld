# Equipo3-Humworld

Proyecto final HumWorld — IA aplicada a Ingeniería de Software (UNAB, Equipo 3).

HumWorld captura noticias desde feeds RSS, calcula su "humor" (análisis de sentimiento) y lo muestra en dashboards: mapa mundial, evolución temporal, nube de palabras y listado de noticias.

| Módulo | Qué hace | Historias |
|---|---|---|
| Captura RSS | Canales y fuentes RSS, cron de captura, captura manual, carga inicial | HU-RSS-001 a 010 |
| Motor de sentimiento | Diccionario, cálculo híbrido (diccionario + ML), polarización, `GET`/`POST /sentiment`, entrenamiento del modelo | HU-SENT-001 a 008 |
| Dashboards | Mapa, gráfico de evolución, nube de palabras, noticias (frontend React) | HU-DASH-001 a 003 |
| Administración | Parámetros generales (`/config`), purgado automático y manual | HU-ADMIN-001 a 003 |

Documentación: historias en `docs/Backlog`, decisiones en `docs/Adr` (ADR-001 a ADR-005), contratos OpenAPI en `docs/Contratos`, diagramas en `docs/UML`.

## Levantar el sistema

```bash
docker compose up -d --build                                  # MySQL + API (aplica las migraciones al arrancar)
docker compose exec api python -m scripts.seed                # 11 canales y 20 fuentes RSS (HU-RSS-009-v2)
docker compose exec api python -m scripts.seed_diccionario    # diccionario inicial: AFINN en + traducción es
```

- API y Swagger: http://localhost:8000/api/docs
- El cron captura cada 30 minutos; el barrido de humor corre 1 minuto después de arrancar y luego cada 30 minutos; el purgado, 5 minutos después de arrancar y luego cada 24 horas.

Frontend (en otra terminal):

```bash
cd frontend
npm ci
npm run dev        # http://localhost:5173
```

## Pruebas

```bash
# Backend (SQLite en memoria; sin MySQL, Docker ni red)
cd src
pip install -r requirements.txt
pytest --cov=app --cov-fail-under=80

# Frontend (Vitest + Testing Library; la API se simula)
cd frontend
npm run lint
npm run coverage   # falla si la cobertura baja de 80 %
```

El pipeline de GitHub Actions (`.github/workflows/ci.yml`) corre ambos en cada PR a `master`, `main` o `develop`; el análisis de SonarQube y el build de Docker solo corren si las pruebas pasan.

## Modelo de ML (opcional)

Sin configuración, todo el humor se calcula por diccionario. Para activar el modelo de ADR-004:

1. Crear una clave de la Gemini API (cuenta del equipo) y dejarla en un archivo `.env` junto a `docker-compose.yml`: `GEMINI_API_KEY=...`. Ese archivo no se sube al repositorio.
2. `docker compose up -d` para recargar la variable.
3. Con al menos 1.000 noticias evaluadas por diccionario: `POST /api/v1/trainings`. Desde ese momento el cálculo de humor usa el modelo activo y vuelve al diccionario si Gemini falla o no responde.

## Administración

- `GET`/`PUT /api/v1/config`: periodicidad del cron (minutos) y caducidad de las noticias (días, 90 por defecto).
- `DELETE /api/v1/news?fecha_anterior_a=AAAA-MM-DD`: borra las noticias registradas antes de esa fecha. Sin parámetro, aplica la caducidad configurada. Es irreversible.
