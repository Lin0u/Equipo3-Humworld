## 1. Modelo y persistencia

- [x] 1.1 Crear el modelo `TerminoDiccionario` con palabra, idioma, valor y clave primaria; verificar creación de tabla y round-trip con SQLite.
- [x] 1.2 Crear migración Alembic para tabla del diccionario y unicidad compuesta literal `(palabra, idioma)` case-sensitive; verificar generación/aplicación offline de la migración y la diferencia permitida entre `guerra` y `Guerra` en MySQL o test compatible.
- [x] 1.3 Registrar el modelo en la metadata/mecanismo de carga ORM del proyecto; verificar que Alembic detecta el modelo y que no cambian las tablas RSS existentes.

## 2. Repositorio y servicio

- [x] 2.1 Implementar consultas de Repositorio por id, clave palabra+idioma y búsqueda parcial; verificar filtros, resultado vacío y ausencia de SQL fuera de `app/repositories/`.
- [x] 2.2 Implementar Servicios CRUD con validación de palabra, idioma `es`/`en`, entero -10…10 y unicidad literal; verificar límites -10/0/10 aceptados y -11/11/no entero rechazados.
- [x] 2.3 Traducir conflictos de unicidad tanto en alta como en PUT/PATCH a error de dominio sin dejar cambios parciales; verificar HTTP/domain conflict con SQLite y rollback.

## 3. Schemas, API y contrato

- [x] 3.1 Crear schemas Pydantic para lectura, creación, actualización completa y parcial; verificar campos requeridos, idioma y escala.
- [x] 3.2 Implementar `src/app/routers/dictionary.py` y registrar el router en `src/app/main.py`; verificar los seis endpoints con `TestClient` y que el router no consulta la base directamente.
- [x] 3.3 Alinear `docs/Contratos/contrato-sentimiento-diccionario.openapi.yaml` con rutas, parámetros, esquemas y códigos HTTP de la spec; verificar YAML válido y OpenAPI runtime consistente.
- [x] 3.4 Verificar códigos HTTP: 201 alta, 200 listado/detalle/PUT/PATCH, 204 DELETE, 400 validación, 404 id inexistente y 409 duplicado compuesto.

## 4. Pruebas y calidad

- [x] 4.1 Añadir pruebas con SQLite para CRUD completo, unicidad compuesta, idiomas distintos, diferencia literal de mayúsculas, colisiones de actualización, límites numéricos, búsqueda parcial y round-trip.
- [x] 4.2 Añadir pruebas API para listado array sin paginación, detalle existente/inexistente, body inválido, PATCH vacío y respuesta 204 sin cuerpo.
- [x] 4.3 Ejecutar `pytest` y `pytest-cov`; verificar suite completa y cobertura mínima del 80% sin dependencias externas.
- [x] 4.4 Revisar conformidad con `docs/architecture.md`, `openspec/config.yaml` y `.github/copilot-instructions.md`; verificar separación API/Servicios/Repositorios/Persistencia y que solo se implementó HU-SENT-001.