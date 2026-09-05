## Why

Las `FuenteRSS` que ya no deben capturarse necesitan retirarse de la configuración operativa sin perder las `Noticia` históricas que dependen de ellas. Una eliminación lógica permite detener su uso futuro, conservar trazabilidad y evitar conflictos con la FK no nula entre `Noticia` y `FuenteRSS`.

## What Changes

- Implementar `DELETE /api/v1/sources/{id}`.
- Aplicar eliminación lógica uniforme: establecer `activo=false` y conservar el registro y sus `Noticia` asociadas.
- Responder HTTP 204 cuando la `FuenteRSS` exista y quede retirada de la operación.
- Ocultar las fuentes eliminadas en el listado y hacer que el detalle responda HTTP 404.
- Responder HTTP 404 cuando el identificador no exista o ya esté eliminado.
- Mantener fuera de alcance el borrado físico, la eliminación en cascada de noticias, la desasociación de noticias, la modificación de fuentes, la captura RSS y la autenticación.
- No modificar `docs/architecture.md` ni los ADR; la política de agregación existente y la FK justifican la eliminación lógica.

## Capabilities

### New Capabilities

- `eliminacion-fuente-rss`: Retirada lógica de una `FuenteRSS` existente mediante DELETE.

### Modified Capabilities

<!-- No existen capacidades base en openspec/specs/ para modificar. -->

## Impact

- API: implementación de `DELETE /api/v1/sources/{id}` y respuestas OpenAPI.
- Servicios: caso de uso de retirada lógica y validación de existencia activa.
- Repositorios: consulta y actualización transaccional de `FuenteRSS`.
- Consultas: el listado y detalle deberán excluir fuentes retiradas para cumplir el comportamiento observable de eliminación.
- Persistencia: actualización del campo existente `activo`; no se añaden tablas ni dependencias.
- Pruebas: SQLite aislado para eliminación, 404, conservación de noticias, ocultación en GET y repetición de DELETE.
