## Why

El módulo de Captura RSS ya permite modelar canales de noticias, pero todavía no ofrece el alta de una `FuenteRSS` asociada a un `CanalNoticias`. Esta capacidad habilita la configuración inicial de fuentes desde las que posteriormente se capturarán noticias, manteniendo la asociación obligatoria con un canal existente y validando los datos antes de persistirlos.

## What Changes

- Añadir el alta de `FuenteRSS` mediante `POST /api/v1/sources`.
- Exigir que el `canal_id` corresponda a un `CanalNoticias` existente.
- Recortar espacios exteriores y validar `url` como URL HTTP o HTTPS válida conforme al contrato API; rechazar entradas inválidas con HTTP 400.
- Validar `categoria_iptc` contra los identificadores canónicos de primer nivel de IPTC Media Topics 1.4, enumerados en la especificación.
- Inicializar `activo` en `true` al crear la fuente.
- Persistir la relación obligatoria `CanalNoticias` -> `FuenteRSS` mediante la FK existente.
- Responder HTTP 404 cuando el canal propietario no exista.
- Mantener autenticación, autorización, captura de noticias y operaciones de consulta, modificación y eliminación fuera de este cambio.
- No modificar `docs/architecture.md` ni los ADR; el cambio usa el modelo de datos, endpoint y separación por capas ya aprobados.

## Capabilities

### New Capabilities

- `alta-fuente-rss-canal`: Alta validada de una `FuenteRSS` asociada a un `CanalNoticias` existente.

### Modified Capabilities

<!-- No existen capacidades base en openspec/specs/ para modificar. -->

## Impact

- API: implementación de `POST /api/v1/sources` y sus respuestas OpenAPI.
- Schemas: validación de `canal_id`, `url` y `categoria_iptc`.
- Servicios: caso de uso de alta y traducción de errores de dominio.
- Repositorios: consulta de existencia de `CanalNoticias` y persistencia de `FuenteRSS`.
- Persistencia: uso de la tabla `fuentes_rss` y sus relaciones; será necesaria una migración Alembic si el esquema desplegado aún no contiene la tabla o sus restricciones.
- Pruebas: unitarias y de integración HTTP con base de datos aislada; no se realizarán llamadas RSS externas en esta historia porque el alta no consume feeds.
- Decisiones cerradas para los artefactos: IPTC Media Topics 1.4, identificadores canónicos como valor persistido, recorte de espacios exteriores, solo esquemas HTTP/HTTPS, sin nueva regla de unicidad de URL en esta HU y formato de errores conforme al contrato OpenAPI.
