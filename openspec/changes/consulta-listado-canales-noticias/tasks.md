## 1. Schemas y contrato API

- [x] 1.1 Crear el schema de respuesta paginada de `CanalNoticias` con `items`, `pagina`, `tamanio_pagina` y `total`, y verificar su serialización con un caso de 0 y otro de N resultados.
- [x] 1.2 Validar `pagina` y `tamanio_pagina` con defecto 1/10 y máximo 50, y verificar HTTP 400 con `Error` para valores en cero, negativos, fuera de rango o no numéricos.
- [x] 1.3 Declarar en el router las respuestas HTTP 200, 400 y 404 y verificar que OpenAPI documenta ambos endpoints y el schema paginado.

## 2. Repositorio y servicio de consulta

- [x] 2.1 Implementar en `app/repositories/canales.py` la consulta paginada de `CanalNoticias` con conteo total y orden alfabético ascendente por `nombre` insensible a mayúsculas/minúsculas (reutilizando el patrón `func.lower` ya usado para la unicidad del alta); verificarla con SQLite.
- [x] 2.2 Implementar el filtro opcional por `continente` con comparación exacta, insensible a mayúsculas/minúsculas y a diacríticos, y con el parámetro vacío ignorado; verificar coincidencias con y sin tilde, y ausencia de coincidencias.
- [x] 2.3 Implementar la consulta de detalle por identificador (incluyendo identificadores no numéricos) y traducir la ausencia a un error de dominio; verificar canal existente e inexistente.
- [x] 2.4 Implementar en `app/services/canal_service.py` el listado y el detalle independientes de FastAPI, verificando que delegan al repositorio y no contienen SQL.

## 3. API HTTP

- [x] 3.1 Conectar `GET /api/v1/channels` con el servicio y verificar HTTP 200, respuesta paginada, orden alfabético, listado vacío, página posterior a la última existente y total filtrado.
- [x] 3.2 Conectar `GET /api/v1/channels/{id}` con el servicio y verificar HTTP 200 con `id`, `nombre`, `continente`, `pais` y `descripcion`, y HTTP 404 con `Error` cuando no exista o el identificador no sea numérico.
- [x] 3.3 Verificar que el filtro de continente combinado con paginación, y los parámetros de continente vacíos, no producen HTTP 500 y que la capacidad no añade autenticación ni modifica los endpoints de escritura existentes.

## 4. Pruebas y calidad

- [x] 4.1 Añadir pruebas unitarias de repositorio y servicio usando SQLite aislado para paginación, conteo, orden alfabético, filtro por continente (con y sin diacríticos), detalle y ausencia.
- [x] 4.2 Añadir pruebas de integración HTTP para listado por defecto, orden alfabético, página específica, tamaño personalizado, límites de paginación inválidos, página posterior a la última existente, filtro por continente y contrato OpenAPI.
- [x] 4.3 Añadir una prueba de integración HTTP para `GET /api/v1/channels?pagina=-1&tamanio_pagina=999`, verificando que la respuesta es un único HTTP 400 con un único cuerpo `Error` (`codigo`, `mensaje`) genérico, sin usar el campo `detalles` ni devolver múltiples objetos de error.
- [x] 4.4 Añadir una prueba con un fixture de aproximadamente 500 `CanalNoticias` verificando que `GET /api/v1/channels` conserva la forma esperada (`items` con 10 elementos, `pagina=1`, `tamanio_pagina=10`, `total=500`) sin cambios de comportamiento respecto a volúmenes menores.
- [x] 4.5 Ejecutar `pytest` con `pytest-cov` y verificar cobertura total mínima del 80%, sin llamadas RSS reales ni trazas internas expuestas en las respuestas.
- [x] 4.6 Comprobar conformidad final con `docs/architecture.md`, `openspec/config.yaml` y la separación API/Servicios/Repositorios/Persistencia; confirmar que no se implementaron alta, modificación, eliminación de `CanalNoticias` ni filtros distintos de `continente`.
