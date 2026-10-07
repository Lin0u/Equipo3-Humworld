## Context

Ver [proposal.md](proposal.md) para motivación y alcance; [spec.md](specs/diccionario-terminos-sentimiento/spec.md) fija el comportamiento observable. El contrato OpenAPI de sentimiento ya enumera `/dictionary` y sus esquemas, pero no hay implementación de EPIC-SENT ni una especificación base en `openspec/specs/`. El diccionario es persistencia de dominio independiente de las entidades `CanalNoticias` y `FuenteRSS`.

## Goals / Non-Goals

**Goals:**

- Implementar HU-SENT-001 con las reglas de validación y los códigos HTTP que ya declara el contrato.
- Hacer cumplir en MySQL la unicidad compuesta de palabra e idioma, además de validarla en el caso de uso.
- Mantener los routers sin SQL y los Servicios independientes de FastAPI.
- Cubrir validaciones, errores y round-trip de persistencia con pruebas aisladas.

**Non-Goals:**

- Calcular sentimiento, actualizar noticias, calcular polarización, entrenar/consumir ML o exponer consultas agregadas.
- Cambiar el contrato de paginación de canales/fuentes; `/dictionary` sigue sin paginación según HU-SENT-001 y el contrato existente.
- Autenticación/autorización, importación masiva o carga inicial del diccionario.
- Introducir dependencias, cambios a ADR o nuevas capas.

## Decisions

### Participación de capas

- **API — `src/app/routers/dictionary.py`:** expone listado, detalle, creación, PUT, PATCH y DELETE; valida/path-parsing con FastAPI/Pydantic, delega casos de uso y traduce errores de dominio a HTTP. No ejecuta SQL ni incorpora reglas de negocio.
- **Servicios — `src/app/services/dictionary_service.py`:** implementa crear, listar/buscar, obtener, actualizar completa/parcial y eliminar. Valida palabra/idioma/valor y unicidad como reglas del caso de uso; permanece independiente del framework web.
- **Repositorios — `src/app/repositories/dictionary.py`:** concentra consultas SQLAlchemy para búsqueda parcial, lookup por id y combinación palabra+idioma, además de inserción, actualización y eliminación. Traduce conflictos de unicidad de la base a una excepción de dominio/repositorio consistente.
- **Persistencia — `src/app/models/termino_diccionario.py` y migración Alembic:** tabla para `TerminoDiccionario` con clave primaria y restricción única compuesta por palabra e idioma. MySQL es la persistencia productiva; SQLite en memoria se usa en tests. No se modifica `Noticia`.
- **Schemas — `src/app/schemas/dictionary.py`:** contratos Pydantic v2 para crear, leer, actualizar completa/parcial y validar idioma `es`/`en`, palabra no vacía y valor entero en -10…10.
- **Contrato HTTP — `docs/Contratos/contrato-sentimiento-diccionario.openapi.yaml`:** fuente del contrato del módulo; verificar que su listado simple y los status codes coinciden con los criterios y la spec.

### Unicidad, normalización y búsqueda

Se usa la clave compuesta literal `(palabra, idioma)`: la comparación distingue mayúsculas/minúsculas y se conserva el texto enviado, conforme a la decisión del usuario para este cambio. La capa de servicio detecta duplicados de forma anticipada y la restricción de base de datos garantiza unicidad ante concurrencia; la migración debe usar una comparación binaria/case-sensitive para la clave de palabra aun si la collation por defecto de MySQL es insensible a mayúsculas. No se recortan ni normalizan espacios o acentos. La búsqueda es independiente de la clave: usa coincidencia parcial en palabra no sensible a mayúsculas/minúsculas según contrato.

El PATCH vacío queda rechazado como solicitud inválida (HTTP 400), ya que no representa una modificación. PUT exige los tres campos. Mantener actualización transaccional para que un conflicto de unicidad no deje valores parcialmente cambiados.

### Estrategia de pruebas

- SQLite en memoria con `Base.metadata` para verificar alta, lectura, edición, eliminación, FK no aplicable, unicidad compuesta y persistencia round-trip.
- Pruebas parametrizadas de valor: `-10`, `0`, `10` aceptados; `-11`, `11`, booleanos/no enteros rechazados con 400.
- `TestClient` para status codes, schemas y payloads de cada ruta; fixtures de términos sin datos de producción.
- Pruebas de palabra igual en idiomas distintos, duplicado literal de misma palabra+idioma y diferencia de mayúsculas permitida; cubrir colisiones durante PUT/PATCH.
- Pruebas de búsqueda parcial incluyendo diferencias de mayúsculas/minúsculas y resultado vacío.
- No hay llamadas externas en HU-SENT-001; no se requiere mock HTTP. Ejecutar suite completa con `pytest-cov` y umbral ≥80% conforme al DoD.

### Ficheros afectados

- Crear `src/app/models/termino_diccionario.py` y registrar el modelo en los imports de modelos si el patrón del proyecto lo requiere.
- Crear `src/app/repositories/dictionary.py`, `src/app/services/dictionary_service.py`, `src/app/schemas/dictionary.py` y `src/app/routers/dictionary.py`.
- Registrar el router en `src/app/main.py`.
- Crear migración Alembic para tabla y unicidad compuesta.
- Completar/verificar `docs/Contratos/contrato-sentimiento-diccionario.openapi.yaml` sin añadir endpoints de otras HU-SENT.
- Añadir pruebas focalizadas en `src/tests/test_dictionary.py`.
- Sin cambios previstos en `docs/architecture.md`, ADR-03 o ADR-04.

## Risks / Trade-offs

- **[Riesgo]** Colisiones concurrentes eluden la comprobación previa → **Mitigación:** restricción única en MySQL y traducción de integridad a HTTP 409.
- **[Riesgo]** La collation MySQL predeterminada puede ignorar mayúsculas al comprobar la clave → **Mitigación:** especificar comparación case-sensitive en el índice único y probar `guerra`/`Guerra` en la migración o en CI compatible.
- **[Riesgo]** Contracto, OpenAPI y código se desalinean → **Mitigación:** verificar rutas/schemas/status codes en OpenAPI generado y YAML durante CI.
- **[Trade-off]** El listado devuelve todos los términos sin paginar por coherencia con la HU y contrato actuales; si el volumen crece, la paginación requiere una decisión y versión explícitas posteriores.

## Migration Plan

Aplicar migración Alembic que crea la tabla `terminos_diccionario` y la restricción única `(palabra, idioma)`. Desplegar el backend y luego habilitar el CRUD; no se requiere backfill de términos porque el diccionario parte vacío en esta historia. Rollback: retirar router/capas y revertir la migración solo si la tabla no contiene datos que deban conservarse; no eliminar datos automáticamente.