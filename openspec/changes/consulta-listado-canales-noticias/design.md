## Context

El router `/api/v1/channels` ya declara las rutas de listado y detalle, pero ambas son stubs (`NotImplementedError`) y el listado actual no está paginado (`response_model=List[CanalNoticias]`). Esta capacidad reutiliza, para `CanalNoticias`, el mismo patrón de paginación, filtrado y manejo de errores ya implementado y probado para `FuenteRSS` en `consulta-filtrado-fuentes-rss` (véase [proposal.md](proposal.md) y [spec.md](specs/consulta-listado-canales-noticias/spec.md) para el contrato observable).

La aplicación usa MySQL en producción y SQLite aislado para las pruebas. Esta capacidad es de solo lectura y no consume feeds RSS externos ni modifica el modelo `CanalNoticias` existente en `src/app/models/canal.py`.

## Goals / Non-Goals

**Goals:**

- Implementar listado paginado y detalle de `CanalNoticias`.
- Ordenar el listado alfabéticamente por `nombre`, de forma insensible a mayúsculas/minúsculas y consistente entre MySQL y SQLite.
- Filtrar el listado por `continente`, con comparación exacta insensible a mayúsculas/minúsculas y a diacríticos.
- Mantener la separación API, Servicios, Repositorios y Persistencia.
- Exponer en OpenAPI el objeto paginado, los parámetros y los errores 400/404.

**Non-Goals:**

- No implementar alta, modificación ni eliminación de `CanalNoticias` (ya cubiertas o pendientes en otras historias).
- No modificar el modelo de datos ni añadir tablas, columnas, índices o restricciones.
- No añadir filtros distintos de `continente` (por `pais`, por `nombre`, etc.).
- No añadir autenticación, autorización ni llamadas HTTP externas.
- No resolver la referencia a `contrato-canales-fuentes-rss.openapi.yaml` en los comentarios del código existente; queda fuera de alcance de este cambio (ver "Fuera de alcance" en [proposal.md](proposal.md)).

## Decisions

### Capa API

`src/app/routers/channels.py` validará los parámetros de query (`continente`, `pagina`, `tamanio_pagina`) y de path (`canal_id`) mediante FastAPI/Pydantic, tratará `continente` vacío como ausente y delegará el listado y el detalle al servicio. El router mapeará la ausencia de canal a HTTP 404 y los parámetros de paginación inválidos a HTTP 400, ambos con el schema `Error`. No contendrá SQL ni reglas de negocio.

Se declarará un schema de respuesta paginada específico para `CanalNoticias` (`items: list[CanalNoticias]`, `pagina`, `tamanio_pagina`, `total`), análogo a `FuenteRSSListado`, reemplazando el `response_model=List[CanalNoticias]` actual del listado.

Para que `pagina`/`tamanio_pagina` no numéricos o fuera de rango respondan `400` con el schema `Error` (y no el `422` por defecto de FastAPI/Pydantic ni una excepción no controlada), y para que un `{canal_id}` no numérico en el detalle responda `404` en lugar de `422`, el router declarará estos parámetros de forma que capture la validación de tipo/rango junto con la de dominio, y produzca en ambos casos una respuesta conforme al contrato en vez de dejar pasar el error por defecto del framework.

Alternativa descartada: dejar que FastAPI/Pydantic devuelvan su `422` estándar para estos casos, porque contradice el contrato de errores (`codigo`/`mensaje`) ya establecido para el resto de la API.

### Capa Servicios

El servicio en `src/app/services/canal_service.py` recibirá los parámetros ya validados (o normalizados por el router, p. ej. `continente` vacío convertido a `None`) y coordinará el repositorio para el listado paginado y el detalle. Devolverá el resultado de la consulta o un error de dominio (`CanalNoticiasNotFoundError`, ya usado en `sources` para el canal referenciado) cuando el detalle no exista. No dependerá de FastAPI ni contendrá sentencias SQL.

### Capa Repositorios

El repositorio (`src/app/repositories/canales.py`) construirá una consulta SQLAlchemy de lectura sobre `CanalNoticias`:

- **Orden:** ascendente por una expresión insensible a mayúsculas/minúsculas sobre `nombre` (p. ej. `func.lower(CanalNoticias.nombre)`), reutilizando el mismo patrón ya usado en `buscar_por_nombre` para la unicidad del alta. No se requiere clave de desempate adicional porque `nombre` es único ignorando mayúsculas/minúsculas.
- **Filtro por `continente`:** comparación exacta, insensible a mayúsculas/minúsculas y a diacríticos. Dado que ni MySQL ni SQLite garantizan de forma portable una comparación insensible a diacríticos con una única expresión SQL estándar, el repositorio resolverá el filtro combinando normalización (minúsculas y remoción de diacríticos) aplicada de forma simétrica al valor recibido y a los valores de `continente` efectivamente almacenados, de modo que el resultado sea idéntico en ambos motores. El diseño concreto de esa normalización (a nivel de expresión SQL portable vs. resolución de valores candidatos en la capa de aplicación) se define en la tarea de implementación correspondiente, sin apartarse de la regla de mantener el acceso a datos únicamente en `app/repositories/`.
- La consulta ejecutará un conteo total filtrado y, dentro de la misma sesión/transacción de lectura, aplicará offset/límite para obtener `items`, para minimizar la divergencia entre `total` e `items` bajo escrituras concurrentes.

El detalle consultará por identificador y devolverá `None` si no existe. Toda sentencia de acceso a datos permanecerá en `src/app/repositories/`.

### Persistencia

No se requieren cambios de esquema ni migraciones: la capacidad solo lee la tabla `canales_noticias` existente. Las pruebas usarán SQLite en memoria o una base SQLite temporal con los modelos ORM, sin conectarse a MySQL ni a feeds externos.

### Pruebas

Se añadirán pruebas unitarias del servicio/repositorio y pruebas HTTP con `TestClient` y SQLite aislado para:

- listado vacío y listado con paginación por defecto;
- orden alfabético ascendente e insensible a mayúsculas/minúsculas;
- página específica y página posterior a la última existente;
- `tamanio_pagina` personalizado dentro y fuera del máximo permitido;
- paginación inválida (`pagina`/`tamanio_pagina` en cero, negativos o no numéricos) con HTTP 400;
- filtro por continente combinado con paginación, incluyendo coincidencia con y sin diacríticos, continente sin coincidencias y continente vacío sin HTTP 500;
- detalle existente, inexistente y con identificador no numérico, verificando HTTP 200/404;
- esquema OpenAPI y forma de la respuesta paginada.

No se requieren mocks RSS porque ningún flujo de consulta realiza llamadas externas. La suite completa se ejecutará con `pytest` y `pytest-cov`, exigiendo al menos 80% de cobertura.

### Ficheros afectados

- Modificar `src/app/routers/channels.py`.
- Crear o modificar `src/app/services/canal_service.py`.
- Crear o modificar `src/app/repositories/canales.py`.
- Añadir el schema de listado paginado de `CanalNoticias` en `src/app/schemas/canal.py`.
- Añadir pruebas bajo `src/tests/` (ampliando `src/tests/test_channels.py`).
- No modificar `docs/architecture.md`, ADR ni el modelo ORM `CanalNoticias` salvo que una incompatibilidad verificable lo exija.

## Risks / Trade-offs

- **[Riesgo]** El orden y el filtro insensibles a mayúsculas/minúsculas pueden depender de la colación configurada en MySQL → **Mitigación:** usar una expresión SQLAlchemy explícita (p. ej. `func.lower`) en vez de depender de la colación por defecto, y cubrirla con pruebas en SQLite; validar también en CI con el motor objetivo cuando esté disponible.
- **[Riesgo]** La insensibilidad a diacríticos no tiene una expresión SQL única portable entre MySQL y SQLite → **Mitigación:** normalizar de forma simétrica (minúsculas + remoción de diacríticos) el valor de filtro y los valores almacenados dentro del repositorio, evitando depender de funciones o colaciones específicas de un solo motor; cubrir con pruebas explícitas de continentes con y sin tilde.
- **[Riesgo]** El conteo y los resultados pueden divergir bajo escrituras concurrentes → **Mitigación:** ejecutar ambas consultas dentro de la misma sesión/transacción de lectura y documentar que `total` corresponde al momento de la consulta.
- **[Riesgo]** El contrato existente del router usa lista plana (`List[CanalNoticias]`) → **Mitigación:** actualizarlo al objeto paginado exigido por `docs/architecture.md` y `openspec/config.yaml`, cubriendo el cambio en OpenAPI y pruebas.

## Migration Plan

No hay migración de base de datos. El despliegue consiste en publicar la API y ejecutar la suite con la base SQLite de pruebas y, cuando esté disponible, una validación contra MySQL. El rollback consiste en retirar los nuevos métodos de consulta del router, servicio y repositorio; no se requieren cambios de datos.
