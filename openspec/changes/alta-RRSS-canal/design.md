## Context

El modelo `FuenteRSS` ya existe con `canal_id` como FK obligatoria a `canales_noticias`, los campos `url`, `categoria_iptc` y `activo`, y la relación ORM con `CanalNoticias`. El router de `/api/v1/sources` contiene actualmente un stub para `POST`; la implementación debe seguir la arquitectura por capas descrita en `docs/architecture.md`. Véase [proposal.md](proposal.md) para la motivación y [spec.md](specs/alta-fuente-rss-canal/spec.md) para el contrato observable.

Los ADR referenciados por la documentación no están presentes en el árbol actual; no se propone modificar decisiones arquitectónicas y el diseño se limita a las reglas verificables de `docs/architecture.md` y `openspec/config.yaml`.

## Goals / Non-Goals

**Goals:**

- Implementar únicamente el caso de uso de alta de `FuenteRSS`.
- Validar URL HTTP/HTTPS y categoría IPTC Media Topics 1.4 antes de persistir.
- Verificar la existencia del `CanalNoticias` y traducir su ausencia a HTTP 404.
- Inicializar `activo` en `true` y devolver HTTP 201 con la representación creada.
- Mantener la API, los servicios, los repositorios y la persistencia separados.
- Actualizar el contrato OpenAPI generado por FastAPI mediante schemas y respuestas declaradas.

**Non-Goals:**

- No implementar listados, detalle, PUT/PATCH, DELETE ni captura de noticias.
- No añadir autenticación, autorización, consumo RSS, reintentos ni circuit breaker en el alta.
- No añadir una regla nueva de unicidad para URL en esta HU.
- No modificar `docs/architecture.md` ni los ADR.

## Decisions

### API y schemas

`src/app/routers/sources.py` conservará únicamente la responsabilidad de recibir la petición, inyectar la sesión, delegar al servicio y mapear errores de dominio a HTTP. `FuenteRSSCrear` se ampliará para recortar `url` y `categoria_iptc` antes de validarlos. La validación de URL usará el tipo Pydantic existente, restringido a URL absoluta HTTP/HTTPS; la categoría se validará contra una constante inmutable con los 17 identificadores de primer nivel de IPTC Media Topics 1.4.

La respuesta de validación usará el schema `Error` existente con `codigo` y `mensaje`, sin exponer trazas ni detalles internos. El error de canal inexistente se mapeará a HTTP 404 con el mismo contrato de error. La documentación OpenAPI declarará las respuestas 201, 400 y 404 del endpoint.

Alternativa descartada: validar la categoría únicamente por longitud o texto libre, porque permitiría valores que no pertenecen al estándar acordado. Alternativa descartada: colocar consultas de existencia en el router, porque rompería la separación arquitectónica.

### Servicio

Se añadirá un servicio independiente del framework web que orqueste el alta: recibe una sesión y un payload validado, solicita al repositorio la búsqueda del `CanalNoticias`, lanza un error de dominio si no existe, construye la `FuenteRSS` con `activo=True` y solicita su persistencia. El servicio no contendrá sentencias SQL ni tipos FastAPI.

### Repositorios y persistencia

Se añadirá un repositorio para encapsular la consulta de `CanalNoticias` y la inserción de `FuenteRSS`. El repositorio gestionará `commit`, `refresh` y rollback controlado ante errores de persistencia, sin filtrar detalles internos a la API.

La relación se respaldará con la FK existente `fuentes_rss.canal_id -> canales_noticias.id`. Se revisará la migración Alembic: si la tabla o la FK no existen en el esquema gestionado, se creará la migración necesaria. No se añadirá una restricción de unicidad de URL porque no forma parte de HU-02.

### Pruebas

Se añadirán pruebas unitarias del schema y servicio, y pruebas HTTP con `TestClient` y una base de datos aislada. Se cubrirán alta válida, `activo=True`, asociación al canal, canal inexistente, URL inválida, categoría IPTC inválida y normalización. No se harán llamadas a fuentes RSS externas en esta historia; por tanto, no se requiere mock de HTTP externo para el caso de uso, aunque la suite conservará la regla general de aislar cualquier llamada externa.

La suite se ejecutará con `pytest` y `pytest-cov`, verificando una cobertura mínima del 80%. También se comprobará que el OpenAPI generado incluye el endpoint y las respuestas previstas.

### Ficheros afectados

- Modificar `src/app/schemas/fuente.py`.
- Modificar `src/app/routers/sources.py`.
- Crear o modificar `src/app/services/fuente_service.py`.
- Crear o modificar `src/app/repositories/fuentes.py` y el inicializador del paquete.
- Reutilizar `src/app/models/fuente.py` y `src/app/models/canal.py`, modificándolos solo si la migración o la relación requieren un ajuste imprescindible.
- Añadir la migración Alembic correspondiente si el esquema actual no está versionado.
- Añadir pruebas bajo `src/tests/` para schema, servicio, API y persistencia.

## Risks / Trade-offs

- **[Riesgo]** El catálogo IPTC puede cambiar en versiones posteriores → **Mitigación:** fijar explícitamente IPTC Media Topics 1.4 y aislar la lista en un único punto del schema o dominio.
- **[Riesgo]** La validación Pydantic y la base de datos pueden aceptar formas distintas de URL → **Mitigación:** normalizar antes de validar, usar el mismo valor normalizado al persistir y cubrirlo con pruebas HTTP.
- **[Riesgo]** Una FK no aplicada en un entorno existente permitiría inconsistencias → **Mitigación:** revisar y ejecutar la migración Alembic antes del despliegue.
- **[Riesgo]** Cambios futuros de consulta/modificación podrían reutilizar el mismo schema → **Mitigación:** mantener el schema de creación separado de los schemas de actualización ya definidos.

## Migration Plan

1. Revisar el estado de Alembic y comparar el modelo `FuenteRSS` con el esquema desplegable.
2. Crear y revisar la migración de la tabla/FK solo si falta en el historial.
3. Ejecutar la migración en un entorno de prueba y validar alta y rollback.
4. Desplegar la API después de aplicar la migración.
5. Para rollback, retirar el endpoint y revertir la migración únicamente si no existen datos que deban conservarse; evaluar primero las `FuenteRSS` creadas.
