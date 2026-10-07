## 1. Schemas y validación

- [x] 1.1 Ajustar `FuenteRSSActualizar` para exigir únicamente `url`, `categoria_iptc` y `activo`, rechazar campos extra como `canal_id` y verificar PUT incompleto o con canal_id mediante HTTP 400.
- [x] 1.2 Ajustar `FuenteRSSActualizarParcial` para aceptar solo campos modificables, rechazar cuerpos vacíos y valores null, y verificar esos errores con HTTP 400.
- [x] 1.3 Reutilizar en ambos payloads la normalización URL HTTP/HTTPS y el catálogo IPTC Media Topics 1.4 de HU-02, verificando espacios exteriores y categorías inválidas.

## 2. Repositorio y servicio

- [x] 2.1 Implementar la búsqueda y actualización de `FuenteRSS` en `app/repositories/`, con commit, refresh y rollback controlado; verificar persistencia con SQLite.
- [x] 2.2 Implementar el caso de uso PUT en `app/services/`, reemplazando solo URL, categoría y activo, y verificar idempotencia y preservación de canal/campos de sistema.
- [x] 2.3 Implementar el caso de uso PATCH aplicando solo campos presentes, incluido `activo=false`, y verificar que los demás valores permanecen sin cambios.
- [x] 2.4 Traducir fuente inexistente a error de dominio y verificar que PUT/PATCH responden 404 sin crear ni modificar registros.

## 3. API HTTP

- [x] 3.1 Conectar `PUT /api/v1/sources/{id}` con el servicio y declarar respuestas 200, 400 y 404 en OpenAPI; verificar actualización completa e idempotencia.
- [x] 3.2 Conectar `PATCH /api/v1/sources/{id}` con el servicio y declarar respuestas 200, 400 y 404 en OpenAPI; verificar actualización parcial y preservación de campos.
- [x] 3.3 Verificar que router, servicio y repositorio permanecen separados, que no se modifican endpoints fuera de HU-04 y que no se añade autenticación/autorización.

## 4. Pruebas y calidad

- [x] 4.1 Añadir pruebas unitarias de schema, servicio y repositorio con SQLite aislado para PUT completo, PATCH parcial, activo=false, idempotencia, 404 y preservación de campos.
- [x] 4.2 Añadir pruebas HTTP para datos inválidos, cuerpos vacíos/null, canal_id inmutable, normalización, respuestas 200/400/404 y contrato OpenAPI.
- [x] 4.3 Ejecutar `pytest` con `pytest-cov` y verificar cobertura total mínima del 80%, sin llamadas RSS reales ni trazas expuestas.
- [x] 4.4 Comprobar conformidad final con `docs/architecture.md`, `openspec/config.yaml` y la separación API/Servicios/Repositorios/Persistencia; confirmar que no se implementaron funcionalidades fuera de modificación de FuenteRSS.
