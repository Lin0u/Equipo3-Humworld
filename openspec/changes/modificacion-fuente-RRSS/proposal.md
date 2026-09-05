## Why

Las `FuenteRSS` ya registradas necesitan poder mantenerse actualizadas sin eliminarse y recrearse, evitando interrupciones innecesarias de configuración. La modificación controlada de URL, categoría IPTC y estado activo permite corregir feeds y activar o desactivar su captura de forma explícita.

## What Changes

- Implementar `PUT /api/v1/sources/{id}` para reemplazar los campos configurables `url`, `categoria_iptc` y `activo`.
- Implementar `PATCH /api/v1/sources/{id}` para modificar parcialmente esos mismos campos.
- Mantener `canal_id` inmutable en esta capacidad.
- Reutilizar la normalización de espacios, validación URL HTTP/HTTPS e IPTC Media Topics 1.4 de HU-02.
- Rechazar con HTTP 400 los datos inválidos, cuerpos PUT incompletos, cuerpos PATCH vacíos y valores nulos no permitidos.
- Responder HTTP 404 cuando no exista la `FuenteRSS` indicada.
- Mantener HTTP 200, idempotencia de PUT y preservación de campos no enviados en PATCH.
- Mantener fuera de alcance el alta, consulta, eliminación, captura RSS y autenticación.
- No modificar `docs/architecture.md` ni los ADR; el cambio implementa endpoints ya previstos.

## Capabilities

### New Capabilities

- `modificacion-fuente-rss`: Actualización completa y parcial de una `FuenteRSS` existente.

### Modified Capabilities

<!-- No existen capacidades base en openspec/specs/ para modificar. -->

## Impact

- API: implementación de `PUT/PATCH /api/v1/sources/{id}` y respuestas OpenAPI.
- Schemas: separación de payload completo y parcial, con validación compartida.
- Servicios: casos de uso de reemplazo e actualización parcial.
- Repositorios: búsqueda y actualización persistente de `FuenteRSS`.
- Persistencia: actualización de columnas existentes; no se añaden tablas ni dependencias.
- Pruebas: SQLite aislado para PUT, PATCH, 404, validación, idempotencia y preservación de campos.
