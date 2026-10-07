## Why

El sistema ya permite registrar `FuenteRSS`, pero no ofrece una consulta operativa para auditar las fuentes configuradas ni localizar una fuente concreta. Esta capacidad permite consultar y filtrar el inventario por canal, continente, categoría IPTC y estado activo, manteniendo el contrato de paginación vigente.

## What Changes

- Implementar `GET /api/v1/sources` con paginación mediante `items`, `pagina`, `tamanio_pagina` y `total`.
- Usar `pagina=1`, `tamanio_pagina=10` y un máximo de 50 elementos por página.
- Permitir filtros combinables por `canal_id`, `continente`, `categoria_iptc` y `activo`.
- Aplicar los filtros presentes con semántica `AND` y comparaciones de texto case-insensitive.
- Ordenar el listado por `canal_id` y después por `url`, conforme a la arquitectura vigente.
- Implementar `GET /api/v1/sources/{id}` para devolver una única `FuenteRSS` existente.
- Responder HTTP 404 con `Error` cuando no exista la `FuenteRSS` solicitada.
- Tratar parámetros de texto vacíos como filtros no aplicados y rechazar parámetros de paginación inválidos con HTTP 400.
- Mantener fuera de alcance el alta, modificación, eliminación, captura RSS y autenticación.
- No modificar `docs/architecture.md` ni los ADR; el cambio implementa endpoints ya previstos en la arquitectura.

## Capabilities

### New Capabilities

- `consulta-filtrado-fuentes-rss`: Consulta paginada, filtrado y detalle de `FuenteRSS`.

### Modified Capabilities

<!-- No existen capacidades base en openspec/specs/ para modificar. -->

## Impact

- API: implementación de `GET /api/v1/sources` y `GET /api/v1/sources/{id}` y actualización de sus schemas OpenAPI.
- Servicios: caso de uso de consulta paginada, combinación de filtros y detalle.
- Repositorios: consultas SQLAlchemy de `FuenteRSS` con unión a `CanalNoticias`, orden, conteo y paginación.
- Schemas: respuesta paginada y errores `Error`.
- Persistencia: lectura sobre las tablas existentes; no se añaden tablas ni dependencias.
- Pruebas: integración HTTP con SQLite aislado, filtros individuales y combinados, paginación, lista vacía, detalle existente/inexistente y parámetros vacíos.
- No se realizan llamadas HTTP a feeds RSS en esta capacidad.
