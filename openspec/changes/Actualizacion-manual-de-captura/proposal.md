## Why

El administrador del sistema necesita actualizar noticias de una o varias `FuenteRSS` sin esperar al siguiente ciclo del cron. La captura manual debe reutilizar el procesamiento ya definido para la captura automática, mantener la deduplicación y aislar los fallos por fuente.

## What Changes

- Añadir captura manual síncrona de una `FuenteRSS` mediante `POST /api/v1/sources/{id}/captures` y de un lote mediante `POST /api/v1/captures` con `fuente_ids`.
- Responder HTTP 201 con un resultado individual por fuente; para una fuente inactiva, responder HTTP 409.
- Procesar todas las fuentes solicitadas aunque una o varias fallen, e informar el estado, noticias nuevas o motivo del fallo por fuente.
- Reutilizar el procedimiento de captura y deduplicación de HU-RSS-006, sin cambiar el comportamiento del cron.
- Mantener fuera de alcance el procesamiento asíncrono, colas o consulta de estado de trabajos, cambios al scheduler, nuevas reglas de reintento o circuit breaker, autenticación/autorización y análisis de sentimiento.
- No se requieren cambios a `docs/architecture.md` ni a los ADR: los endpoints y el procesamiento síncrono ya están acordados en HU-RSS-008 y el contrato vigente; el diseño aplica la arquitectura por capas existente.

## Capabilities

### New Capabilities

- `captura-manual-noticias`: Disparo síncrono de captura para una o varias `FuenteRSS`, con resultados individuales y aislamiento de errores.

### Modified Capabilities

<!-- No hay especificaciones base en openspec/specs/ que requieran un delta. La captura programada existente permanece sin cambios. -->

## Impact

- API: rutas de captura individual y por lote, documentadas en el contrato OpenAPI vigente.
- Servicios: coordinación de elegibilidad de fuentes y reutilización del servicio de captura de HU-RSS-006.
- Repositorios/Persistencia: consulta de las `FuenteRSS` indicadas y lectura/escritura de noticias y metadatos mediante los repositorios existentes; no se prevén nuevas tablas.
- Pruebas: SQLite aislado y mocks HTTP para feeds; cobertura específica de fuente inactiva y lote parcialmente fallido.
- Sin dependencias nuevas ni cambios a la configuración del cron.