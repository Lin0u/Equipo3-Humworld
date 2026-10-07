## 1. Schemas y contrato API

- [x] 1.1 Crear el schema de respuesta paginada de `FuenteRSS` con `items`, `pagina`, `tamanio_pagina` y `total`, y verificar su serialización con un caso de 0 y otro de 23 resultados.
- [x] 1.2 Validar `pagina` y `tamanio_pagina` con defecto 1/10 y máximo 50, y verificar HTTP 400 con `Error` para valores 0 o fuera de rango.
- [x] 1.3 Declarar en el router las respuestas HTTP 200, 400 y 404 y verificar que OpenAPI documenta ambos endpoints y el schema paginado.

## 2. Repositorio y servicio de consulta

- [x] 2.1 Implementar en `app/repositories/` la consulta paginada de `FuenteRSS` con conteo total, orden por `canal_id` y `url`, y verificarla con SQLite.
- [x] 2.2 Implementar los filtros opcionales por `canal_id`, `continente`, `categoria_iptc` y `activo` con semántica `AND`, comparación textual case-insensitive y parámetros vacíos ignorados; verificar filtros individuales y combinados.
- [x] 2.3 Implementar la consulta de detalle por identificador y traducir ausencia a un error de dominio; verificar fuente existente e inexistente.
- [x] 2.4 Implementar el servicio independiente de FastAPI para listado y detalle, verificando que delega al repositorio y no contiene SQL.

## 3. API HTTP

- [x] 3.1 Conectar `GET /api/v1/sources` con el servicio y verificar HTTP 200, respuesta paginada, lista vacía, total filtrado y orden estable.
- [x] 3.2 Conectar `GET /api/v1/sources/{id}` con el servicio y verificar HTTP 200 con todos los campos públicos y HTTP 404 con `Error` cuando no exista.
- [x] 3.3 Verificar que filtros combinados y parámetros textuales vacíos no producen HTTP 500 y que la capacidad no añade autenticación ni modifica endpoints de escritura.

## 4. Pruebas y calidad

- [x] 4.1 Añadir pruebas unitarias de repositorio y servicio usando SQLite aislado para paginación, conteo, orden, filtros, detalle y ausencia.
- [x] 4.2 Añadir pruebas de integración HTTP para filtros por canal, continente, categoría y activo, combinaciones `AND`, paginación inválida, respuesta vacía y contrato OpenAPI.
- [x] 4.3 Ejecutar `pytest` con `pytest-cov` y verificar cobertura total mínima del 80%, sin llamadas RSS reales ni trazas expuestas.
- [x] 4.4 Comprobar conformidad final con `docs/architecture.md`, `openspec/config.yaml` y la separación API/Servicios/Repositorios/Persistencia; confirmar que no se implementaron altas, modificaciones, eliminaciones ni captura RSS.
