## 1. Repositorio y servicio

- [x] 1.1 Implementar en `app/repositories/` la búsqueda de `FuenteRSS` activa y su actualización transaccional a `activo=false`, con rollback controlado; verificarlo con SQLite.
- [x] 1.2 Implementar el caso de uso de eliminación lógica en `app/services/`, traduciendo fuente inexistente o ya inactiva a error de dominio; verificar que nunca borra `FuenteRSS` ni `Noticia`.

## 2. API HTTP

- [x] 2.1 Conectar `DELETE /api/v1/sources/{id}` con el servicio y declarar respuestas 204 y 404 en OpenAPI; verificar 204 sin cuerpo para una fuente activa.
- [x] 2.2 Mapear fuente inexistente o ya eliminada a HTTP 404 con schema `Error`, verificando que no se modifican registros.
- [x] 2.3 Verificar que el router no contiene SQL ni lógica de persistencia, que no se añade autenticación y que no se modifican otros endpoints de escritura.

## 3. Consultas y persistencia

- [x] 3.1 Ajustar el listado y detalle de `FuenteRSS` para ocultar fuentes eliminadas por defecto y devolver 404 en detalle; verificar coherencia entre `total` e `items`.
- [x] 3.2 Verificar que las `Noticia` asociadas conservan su FK y todos sus datos después del DELETE, sin cascada ni desasociación.
- [x] 3.3 Confirmar que no se requieren migraciones porque se reutiliza el campo `activo` existente y que no se añade borrado físico.

## 4. Pruebas y calidad

- [x] 4.1 Añadir pruebas unitarias de repositorio y servicio con SQLite aislado para eliminación activa, fuente inexistente, fuente ya eliminada y conservación de noticias.
- [x] 4.2 Añadir pruebas HTTP para 204, cuerpo vacío, 404, consulta posterior, ocultación en listado y contrato OpenAPI.
- [x] 4.3 Ejecutar `pytest` con `pytest-cov` y verificar cobertura total mínima del 80%, sin llamadas RSS reales ni trazas expuestas.
- [x] 4.4 Comprobar conformidad final con `docs/architecture.md`, `openspec/config.yaml` y la separación API/Servicios/Repositorios/Persistencia; confirmar que no se implementaron funcionalidades fuera de eliminación lógica de FuenteRSS.
