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
- React 19.2.8
- Los routers no acceden a MySQL ni contienen SQL.
- Los servicios no dependen del framework web.
- Toda llamada a una fuente RSS externa aplica Timeout explícito, Retry
  acotado con backoff exponencial y Circuit Breaker por fuente (ADR-002).
  Nunca reintentos infinitos.
- Los listados paginados (GET /channels, GET /sources) devuelven un
  objeto con `items`, `pagina`, `tamanio_pagina` y `total` (tamaño de
  página por defecto 10, máximo 50) — convención acordada por el equipo
  el 2026-08-30. No introducir un formato de paginación distinto sin
  aprobación del equipo.
- No añadir tecnologías sin aprobación humana.

## Terminología
- Las entidades se denominan CanalNoticias y FuenteRSS (no "canal"/
  "fuente" genéricos en el código).
- El actor de las historias administrativas se denomina "administrador
  del sistema".

## Desarrollo con OpenSpec
- No implementar sin especificación revisada.
- Seguir proposal.md, spec.md, design.md y tasks.md.
  - El incremento actual incluye HU-SENT-001, HU-SENT-002-v2 y HU-SENT-003
    además de las historias HU-RSS-* aprobadas; las demás HU-SENT-* quedan
    fuera, salvo campos estrictamente necesarios para estas historias.
- No añadir funcionalidades fuera del alcance aprobado.
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
