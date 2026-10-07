## Why

El sistema necesita permitir el alta de canales de noticias con datos consistentes y nombres inequívocos. Definir ahora estas reglas evita duplicados por diferencias de mayúsculas/minúsculas y alinea las respuestas de validación con el contrato OpenAPI existente.

## What Changes

- Añadir la capacidad de crear canales de noticias mediante el endpoint correspondiente.
- Recortar espacios iniciales y finales de `nombre`, `continente`, `pais` y `descripcion` antes de validar y persistir.
- Rechazar solicitudes cuyo `nombre` quede vacío tras el recorte.
- Garantizar que `nombre` sea único sin distinguir mayúsculas/minúsculas.
- Mantener `continente` como texto libre, sin catálogo cerrado.
- Responder los datos inválidos con el schema `Error` del contrato, usando `codigo` y `mensaje`, con estado `400`.
- Responder los conflictos de unicidad con el schema `Error`, usando `codigo` y `mensaje`, con estado `409`.
- Mantener autenticación y autorización fuera del alcance.
- Dejar la migración Alembic como tarea pendiente de implementación.

## Capabilities

### New Capabilities

- `alta-canal-noticias`: Alta de canales de noticias, normalización de campos, validación, unicidad del nombre y respuestas de error del contrato.

### Modified Capabilities

<!-- No existen capacidades previas en openspec/specs/. -->

## Impact

- API HTTP de canales y sus schemas OpenAPI.
- Modelos, persistencia y servicio de canales en `src/app/`.
- Tests de validación, alta, duplicados y formato de errores.
- Base de datos: será necesaria una migración Alembic, explícitamente pendiente en `tasks.md`.
- No se añaden dependencias de autenticación o autorización.