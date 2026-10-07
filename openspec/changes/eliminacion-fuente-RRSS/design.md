## Context

`FuenteRSS` tiene un campo `activo` y una relación con `Noticia` cuya FK no permite quedar nula. El modelo documenta `FuenteRSS` -> `Noticia` como agregación, por lo que las noticias históricas deben sobrevivir al ciclo de vida operativo de la fuente. El router DELETE es actualmente un stub. Véanse [proposal.md](proposal.md) y [spec.md](specs/eliminacion-fuente-rss/spec.md) para el contrato acordado.

## Goals / Non-Goals

**Goals:**

- Implementar `DELETE /api/v1/sources/{id}` como eliminación lógica.
- Marcar `activo=false` de forma transaccional y devolver HTTP 204.
- Devolver HTTP 404 para fuentes inexistentes o ya eliminadas.
- Ocultar fuentes eliminadas del listado y detalle sin borrar sus noticias.
- Mantener API, Servicios, Repositorios y Persistencia separados.

**Non-Goals:**

- No borrar físicamente `FuenteRSS`.
- No eliminar en cascada ni desasociar `Noticia`.
- No implementar purgado, archivado histórico adicional, modificación, alta, captura ni autenticación.
- No añadir tablas, dependencias ni cambiar la FK.

## Decisions

### Política de eliminación

Se usará soft delete uniforme mediante `activo=false`, incluso cuando la fuente no tenga noticias. Esta decisión evita dos políticas distintas y mantiene el historial referencial. Se descartan el borrado físico con cascada, por pérdida de datos, y el rechazo 409, porque no satisface la intención de retirar operativamente una fuente.

La consulta de detalle y el listado deberán tratar las fuentes inactivas eliminadas como no encontradas/ocultas. El filtro explícito `activo=false` existente en el listado puede conservar su semántica de auditoría para fuentes inactivas, pero la especificación de esta HU exige que una fuente eliminada no aparezca en la consulta por defecto ni en el detalle.

### API

El router validará `fuente_id`, delegará al servicio y mapeará el error de fuente inexistente o inactiva a HTTP 404 con `Error`. Para éxito devolverá `Response(status_code=204)` sin serializar un cuerpo. Declarará respuestas 204 y 404 en OpenAPI. No contendrá SQL ni manipulación directa del modelo.

### Servicio

El servicio buscará únicamente una `FuenteRSS` activa, lanzará un error de dominio si no existe o ya está inactiva y solicitará al repositorio la actualización de `activo=False`. No dependerá de FastAPI.

### Repositorio y persistencia

El repositorio encapsulará la consulta de fuente activa y el commit de la actualización, con rollback ante errores de SQLAlchemy. No se eliminarán filas de `fuentes_rss` ni `noticias`; la FK y la relación ORM permanecerán intactas. No se requiere migración porque `activo` ya existe.

### Integración con consultas

El repositorio de listado deberá excluir eliminaciones lógicas cuando no se solicite un filtro de estado, y el detalle deberá buscar solo fuentes activas. Si el contrato de consulta actual permite auditar fuentes inactivas mediante `activo=false`, se conservará esa capacidad sin exponer fuentes eliminadas en el detalle, documentando cualquier distinción necesaria en las pruebas.

### Pruebas

Se usarán pruebas unitarias y HTTP con SQLite aislado para DELETE exitoso, 204 sin cuerpo, 404 inexistente, 404 repetido, ocultación en listado/detalle y conservación de `Noticia` asociada. Se verificará el contrato OpenAPI y cobertura mínima del 80%. No hay llamadas a feeds RSS en esta operación, por lo que no se harán llamadas externas.

### Ficheros afectados

- Modificar `src/app/routers/sources.py`.
- Modificar `src/app/services/fuente_service.py`.
- Modificar `src/app/repositories/fuentes.py`.
- Ajustar el repositorio de consulta para ocultar fuentes eliminadas por defecto.
- Añadir pruebas bajo `src/tests/`.
- No modificar modelos ORM, FK ni infraestructura de migraciones.

## Risks / Trade-offs

- **[Riesgo]** Las fuentes inactivas existentes por otras razones pueden confundirse con eliminadas → **Mitigación:** esta HU usa el estado `activo` como indicador operativo y documenta que DELETE solo actúa sobre fuentes activas; cualquier distinción histórica requeriría un campo adicional fuera de alcance.
- **[Riesgo]** Clientes esperan que DELETE libere espacio físico → **Mitigación:** documentar explícitamente la conservación de fuente y noticias; el purgado es otra capacidad.
- **[Riesgo]** El conteo/listado puede cambiar tras la eliminación → **Mitigación:** aplicar el mismo filtro de visibilidad en el conteo y en `items`.

## Migration Plan

No hay migración de base de datos. Desplegar el cambio y ejecutar la suite SQLite/coverage. El rollback de aplicación consiste en retirar DELETE; las filas marcadas inactivas permanecen y pueden reactivarse mediante el procedimiento de modificación definido por la capacidad correspondiente.
