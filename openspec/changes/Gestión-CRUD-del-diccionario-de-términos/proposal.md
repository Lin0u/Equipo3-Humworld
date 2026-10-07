## Why

El método determinista de sentimiento necesita un vocabulario editable de términos con idioma y valor numérico. HU-SENT-001 habilita al administrador del sistema a mantener ese diccionario mediante operaciones CRUD y a buscar palabras sin modificar el resto del flujo de sentimiento.

## What Changes

- Incorporar el recurso `TerminoDiccionario` con altas, consulta/listado, modificación completa y parcial, y eliminación mediante las seis rutas `/api/v1/dictionary` del contrato de sentimiento.
- Validar idiomas `es` y `en`, valor entero entre -10 y +10 inclusive y unicidad compuesta por palabra e idioma.
- Aplicar los códigos HTTP ya definidos en el contrato: 201 al crear, 200 en consultas/actualizaciones, 204 al eliminar, 400 ante validación, 404 si el id no existe y 409 ante duplicado compuesto.
- Buscar por coincidencia parcial de palabra; conservar el listado como array sin paginación, dado que HU-SENT-001 no define paginación.
- Completar el contrato OpenAPI de `docs/Contratos/contrato-sentimiento-diccionario.openapi.yaml` si es necesario para alinearlo con los criterios y eliminar notas ya resueltas solo cuando exista aprobación.
- Mantener fuera de alcance el cálculo de humor, polarización, ML, análisis de texto, agregaciones, seeds y cualquier otra HU-SENT.
- El alcance del incremento incluye HU-RSS-001/HU-RSS-010 y HU-SENT-001. No se requieren cambios de arquitectura ni de ADR; se reutiliza FastAPI, Pydantic, SQLAlchemy/Alembic, MySQL y las capas ya aprobadas.

## Capabilities

### New Capabilities

- `diccionario-terminos-sentimiento`: Gestión CRUD y búsqueda del diccionario con validación de idioma, escala y unicidad palabra+idioma.

### Modified Capabilities

<!-- No existen especificaciones base en openspec/specs/ para modificar. -->

## Impact

- API: nuevo router para `/api/v1/dictionary` y sus operaciones de detalle.
- Servicios: casos de uso independientes del framework para crear, consultar, listar, actualizar y eliminar `TerminoDiccionario`.
- Repositorios/Persistencia: modelo SQLAlchemy, repositorio y migración Alembic para la tabla del diccionario y la restricción única compuesta.
- Contrato: OpenAPI del módulo de sentimiento, tag `dictionary`.
- Pruebas: SQLite aislado para persistencia y `TestClient` para respuestas HTTP; fixtures deterministas, sin llamadas externas.
- No se añaden dependencias ni se alteran las rutas de captura RSS.