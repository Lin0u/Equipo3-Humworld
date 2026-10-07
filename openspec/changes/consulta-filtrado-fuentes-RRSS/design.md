## Context

El router `/api/v1/sources` ya declara los parámetros de filtrado, pero sus endpoints de listado y detalle son stubs. `FuenteRSS` mantiene una FK obligatoria hacia `CanalNoticias`, por lo que el filtro por continente requiere consultar la entidad propietaria. La arquitectura exige respuestas paginadas para los listados y concentra el acceso SQLAlchemy en repositorios. Véase [proposal.md](proposal.md) para el motivo y [spec.md](specs/consulta-filtrado-fuentes-rss/spec.md) para el contrato observable.

La aplicación usa MySQL en producción y SQLite aislado para las pruebas. Esta capacidad es de solo lectura y no consume feeds RSS externos.

## Goals / Non-Goals

**Goals:**

- Implementar listado paginado y detalle de `FuenteRSS`.
- Mantener filtros combinables por canal, continente, categoría y activo.
- Devolver resultados deterministas ordenados por `canal_id` y `url`.
- Mantener la separación API, Servicios, Repositorios y Persistencia.
- Exponer en OpenAPI el objeto paginado, los parámetros y errores 400/404.

**Non-Goals:**

- No implementar alta, modificación, eliminación ni captura RSS.
- No modificar el modelo de datos ni añadir tablas, índices o restricciones.
- No añadir autenticación, autorización ni llamadas HTTP externas.
- No cambiar el contrato de paginación de `GET /channels`.

## Decisions

### Capa API

`src/app/routers/sources.py` validará los parámetros de ruta y query mediante FastAPI/Pydantic, tratará cadenas vacías como ausentes y delegará el listado y detalle al servicio. El router mapeará errores de dominio a HTTP 404 y errores de parámetros a HTTP 400 con el schema `Error`. No contendrá SQL, joins ni reglas de negocio.

Se declarará un schema de respuesta paginada específico para `FuenteRSS`, con `items: list[FuenteRSS]`, `pagina`, `tamanio_pagina` y `total`. Se mantendrán intactos los endpoints de escritura y los stubs de otras historias.

Alternativa descartada: devolver una lista plana, porque contradice la convención obligatoria de `docs/architecture.md` y `openspec/config.yaml`.

### Capa Servicios

El servicio recibirá los parámetros ya validados y coordinará el repositorio. Aplicará únicamente transformaciones de entrada no propias de SQL, como convertir cadenas vacías a `None`, y devolverá resultados de consulta o un error de dominio cuando el detalle no exista. No dependerá de FastAPI ni contendrá sentencias SQL.

### Capa Repositorios

El repositorio construirá una consulta SQLAlchemy de lectura sobre `FuenteRSS`, con unión a `CanalNoticias` solo cuando sea necesario para filtrar por continente. Los filtros presentes se combinarán con `AND`; continente y categoría usarán comparación case-insensitive. La consulta aplicará orden estable por `FuenteRSS.canal_id` y `FuenteRSS.url`, ejecutará un conteo total filtrado y después aplicará offset/limit.

El detalle consultará por identificador y devolverá `None` si no existe. Toda sentencia de acceso a datos permanecerá en `src/app/repositories/`.

### Persistencia

No se requieren cambios de esquema ni migraciones: la capacidad solo lee las tablas existentes. Las pruebas usarán SQLite en memoria o una base SQLite temporal con los modelos ORM, sin conectarse a MySQL ni a feeds externos.

### Pruebas

Se añadirán pruebas unitarias del servicio/repositorio y pruebas HTTP con `TestClient` y SQLite aislado para:

- listado vacío y listado con paginación;
- orden por `canal_id` y `url`;
- filtros individuales y combinados con `AND`;
- filtro `activo=false`;
- parámetros textuales vacíos sin HTTP 500;
- paginación inválida con HTTP 400;
- detalle existente e inexistente con HTTP 200/404;
- esquema OpenAPI y forma de la respuesta paginada.

No se requieren mocks RSS porque ningún flujo de consulta realiza llamadas externas. La suite completa se ejecutará con `pytest` y `pytest-cov`, exigiendo al menos 80% de cobertura.

### Ficheros afectados

- Modificar `src/app/routers/sources.py`.
- Crear o modificar `src/app/services/fuentes_service.py`.
- Crear o modificar `src/app/repositories/fuentes.py`.
- Añadir schemas de paginación y error si no existen equivalentes reutilizables.
- Añadir pruebas bajo `src/tests/`.
- No modificar `docs/architecture.md`, ADR ni modelos ORM salvo que una incompatibilidad verificable lo exija.

## Risks / Trade-offs

- **[Riesgo]** El conteo y los resultados pueden divergir bajo escrituras concurrentes → **Mitigación:** ejecutar ambas consultas dentro de la misma sesión/transacción de lectura y documentar que `total` corresponde al momento de la consulta.
- **[Riesgo]** La comparación case-insensitive puede depender de la colación de MySQL → **Mitigación:** usar una expresión SQLAlchemy explícita compatible con el motor soportado y cubrirla con pruebas SQLite; validar también en CI con el motor objetivo cuando esté disponible.
- **[Riesgo]** Consultas con joins pueden duplicar filas si se amplían relaciones futuras → **Mitigación:** unir solo `CanalNoticias` y contar `FuenteRSS.id` de forma estable.
- **[Riesgo]** El contrato existente del router usa lista plana → **Mitigación:** actualizarlo al objeto paginado exigido por arquitectura y cubrir el cambio en OpenAPI y pruebas.

## Migration Plan

No hay migración de base de datos. El despliegue consiste en publicar la API y ejecutar la suite con la base SQLite de pruebas y, cuando esté disponible, una validación contra MySQL. El rollback consiste en retirar los nuevos métodos de consulta del router, servicio y repositorio; no se requieren cambios de datos.
