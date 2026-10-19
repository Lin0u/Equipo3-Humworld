## Why

El proyecto necesita datos iniciales de `CanalNoticias` y `FuenteRSS` para desarrollo y pruebas, cubriendo los cinco continentes acordados. Un seed interno e idempotente permitirá inicializar la persistencia sin crear registros duplicados al repetir su ejecución.

## What Changes

- Completar el procedimiento interno de carga inicial que hoy existe como plantilla vacía en `src/scripts/seed.py`.
- Cubrir América, Europa, Asia, África y Oceanía, con al menos un `CanalNoticias` y una `FuenteRSS` asociada por continente.
- Reutilizar los casos de uso de Servicios y el acceso a datos de Repositorios; persistir en MySQL mediante SQLAlchemy y sin una migración de esquema.
- Hacer idempotente la carga usando `nombre` de `CanalNoticias` y `url` de `FuenteRSS` como claves de existencia.
- No exponer endpoint API ni añadir dependencias. Las URLs de feeds reales quedan pendientes de aprobación del equipo; no se inventan como parte de este cambio. Hay un dataset propuesto de 20 fuentes verificadas el 2026-10-18 en `docs/Backlog/Dataset-fuentes-RSS-seed-HU-RSS-009.md`, pendiente de aprobación.
- **Alineado con el backlog:** el equipo adoptó este enfoque el 2026-10-18. HU-RSS-009 quedó Deprecada en favor de HU-RSS-009-v2 (Historia Técnica/Enabler Story, carga mediante script interno), y `POST /api/v1/seeds` quedó retirado en `contrato-canales-fuentes-rss.openapi.yaml` v1.7.0.
- No requiere modificar `docs/architecture.md` ni los ADR: el mecanismo reutiliza las capas existentes y no introduce decisiones tecnológicas o arquitectónicas nuevas.

## Capabilities

### New Capabilities

- `carga-inicial-fuentes-por-continente`: Inicialización idempotente de `CanalNoticias` y `FuenteRSS` con cobertura de los cinco continentes.

### Modified Capabilities

<!-- No hay especificaciones base en openspec/specs/ para modificar. -->

## Impact

- Script: completar `src/scripts/seed.py` como punto de entrada interno.
- Servicios y repositorios: reutilizar o ampliar de forma mínima los casos de uso/repositories de `CanalNoticias` y `FuenteRSS` para creación idempotente.
- Persistencia: reutilizar tablas y restricciones existentes; no hay cambios de esquema.
- Pruebas: ejecución repetida sobre SQLite aislado, verificación de relaciones e idempotencia; URLs externas no se consultan durante el seed ni las pruebas.
- API/OpenAPI: sin cambios. `POST /api/v1/seeds` no forma parte del contrato vigente (v1.7.0).