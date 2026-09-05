## 1. Schemas y catálogo IPTC

- [x] 1.1 Actualizar `FuenteRSSCrear` para recortar `url` y `categoria_iptc` antes de validar y verificar con pruebas que los valores persistidos no conservan espacios exteriores.
- [x] 1.2 Fijar en un único punto los 17 identificadores de primer nivel de IPTC Media Topics 1.4 y verificar que una categoría reconocida se acepta y una no reconocida se rechaza.
- [x] 1.3 Verificar que `url` acepta únicamente URLs absolutas HTTP/HTTPS válidas y rechaza formatos inválidos con errores de validación convertibles a HTTP 400.

## 2. Repositorio y servicio

- [x] 2.1 Crear el repositorio de `FuenteRSS` y la consulta de `CanalNoticias`, manteniendo todas las sentencias SQLAlchemy en `app/repositories/`, y verificar existencia y ausencia de canal con pruebas unitarias.
- [x] 2.2 Implementar el servicio de alta de `FuenteRSS`, asociarlo al `CanalNoticias` encontrado e inicializar `activo=True`; verificar la persistencia y la asociación mediante una prueba con base de datos aislada.
- [x] 2.3 Traducir la ausencia de `CanalNoticias` a un error de dominio 404 y verificar que no se inserta ninguna `FuenteRSS`.

## 3. API HTTP

- [x] 3.1 Conectar `POST /api/v1/sources` con el servicio y declarar las respuestas del contrato OpenAPI; verificar que una alta válida responde HTTP 201 con identificador, `canal_id` y `activo=true`.
- [x] 3.2 Mapear errores de URL y categoría a HTTP 400 con el schema `Error` (`codigo`, `mensaje`), y el canal inexistente a HTTP 404; verificar los cuerpos sin trazas internas.
- [x] 3.3 Verificar que el alta no añade autenticación/autorización ni altera los endpoints de consulta, modificación, eliminación o captura existentes.

## 4. Persistencia y migración

- [ ] 4.1 Revisar el historial Alembic frente a `CanalNoticias` y `FuenteRSS`; crear o ajustar únicamente la migración necesaria para la tabla `fuentes_rss` y la FK obligatoria al canal, verificando `upgrade` y `downgrade` en un entorno de prueba.

> Bloqueada: el scaffold no contiene `alembic.ini`, `env.py` ni historial de revisiones. Crear una migración ejecutable requiere inicializar esa infraestructura y definir también la migración base de las tablas existentes, lo que excede la HU-02 actual.
- [x] 4.2 Verificar que `activo` se almacena como verdadero por defecto y que no se añade una restricción de unicidad de URL no especificada por HU-02.

## 5. Pruebas y calidad

- [x] 5.1 Añadir pruebas unitarias de schema, servicio y repositorio para alta válida, normalización, IPTC 1.4, URL inválida y canal inexistente; no realizar llamadas RSS reales.
- [x] 5.2 Añadir pruebas de integración HTTP con base de datos aislada para HTTP 201, 400 y 404, asociación exacta al `CanalNoticias` y `activo=true`; verificar también el esquema OpenAPI generado.
- [x] 5.3 Ejecutar `pytest` con `pytest-cov` y verificar cobertura total mínima del 80%, sin fallos ni trazas expuestas.
- [x] 5.4 Comprobar conformidad final con `docs/architecture.md`, `openspec/config.yaml` y la separación API/Servicios/Repositorios/Persistencia; confirmar que no se implementaron funcionalidades fuera de HU-02.
