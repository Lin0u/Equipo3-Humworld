## Why

El sistema ya permite dar de alta `CanalNoticias` (HU-RSS-001), pero no ofrece una consulta operativa para conocer los medios configurados ni auditar la cobertura por continente. Esta capacidad implementa el listado paginado y el detalle de `CanalNoticias`, siguiendo el mismo contrato de paginación y las mismas decisiones de diseño ya validadas para `GET /api/v1/sources` (HU-RSS-003), de modo que ambos listados del módulo de captura RSS se comporten de manera consistente.

## What Changes

- Implementar `GET /api/v1/channels` con paginación mediante `items`, `pagina`, `tamanio_pagina` y `total`, reemplazando el stub actual (`response_model=List[CanalNoticias]`, sin paginar y sin implementación) por un nuevo schema de respuesta paginado específico para `CanalNoticias`.
- Ordenar `items` alfabéticamente en forma ascendente por `nombre`, de manera case-insensitive y mediante una expresión SQL explícita (p. ej. `LOWER(nombre)`) para que el orden sea idéntico en MySQL (producción) y SQLite (pruebas). No se requiere clave de desempate adicional porque `nombre` ya es único sin distinguir mayúsculas/minúsculas (HU-RSS-001).
- Usar `pagina=1` y `tamanio_pagina=10` por defecto, con un máximo de `50` elementos por página (igual que en `/sources`).
- Permitir el filtro opcional `continente`, con comparación exacta, insensible a mayúsculas/minúsculas y a diacríticos (tildes), y con recorte (`trim`) de espacios; por ejemplo, `?continente=America` debe coincidir con un canal registrado como `América`. Se aplicará la misma estrategia (expresión SQL explícita o normalización en la capa de aplicación) usada para el orden case-insensitive de `nombre`, de modo que el comportamiento sea idéntico en MySQL y SQLite. Un `continente` vacío (`?continente=`) se trata como filtro no aplicado. Si ningún canal coincide, el sistema responde `200` con `items=[]` y `total=0`.
- Rechazar con `HTTP 400` (schema `Error`, campos `codigo`/`mensaje`) los parámetros de paginación inválidos: `pagina=0`, `pagina` negativa, `tamanio_pagina=0`, `tamanio_pagina` fuera de rango (`>50`), y valores no numéricos en `pagina` o `tamanio_pagina` (en lugar del `422` automático de FastAPI/Pydantic).
- Si se solicita una página posterior a la última existente, responder `HTTP 200` con `items=[]` (sin error), manteniendo `pagina` y `tamanio_pagina` con los valores solicitados y `total` con el conteo real.
- Implementar `GET /api/v1/channels/{id}` devolviendo la representación completa de un único `CanalNoticias` (`id`, `nombre`, `continente`, `pais`, `descripcion`), sin envoltorio de paginación y sin datos derivados (p. ej. no se incluye el conteo de `FuenteRSS` asociadas).
- Responder `HTTP 404` con el schema `Error` (`codigo`, `mensaje`) cuando no exista un canal con el `id` solicitado, incluyendo el caso en que `id` no sea numérico (en lugar del `422` automático de FastAPI/Pydantic).
- Ejecutar el conteo total y la obtención de `items` dentro de la misma transacción/sesión de lectura, para minimizar la divergencia entre `total` e `items` bajo escrituras concurrentes (misma mitigación documentada como riesgo conocido en el diseño de `/sources`).
- No agregar filtros adicionales (por `pais`, por `nombre`, etc.) en esta historia.
- Mantener autenticación y autorización fuera de alcance, igual que en el resto de las capacidades de lectura del módulo.

## Fuera de alcance

- El código existente referencia un archivo `contrato-canales-fuentes-rss.openapi.yaml` (ver comentarios en `src/app/routers/channels.py` y `src/app/models/canal.py`) que no está presente en este repositorio. Su resolución (ubicación, vigencia o reemplazo por los specs de OpenSpec) queda fuera del alcance de esta propuesta y no bloquea su aprobación ni implementación.

## Capabilities

### New Capabilities

- `consulta-listado-canales-noticias`: Consulta paginada, filtrado por continente y detalle de `CanalNoticias`.

### Modified Capabilities

<!-- `alta-canal-noticias` no incluye requisitos de consulta/listado; esta propuesta no modifica sus requisitos existentes. -->

## Impact

- API: implementación de `GET /api/v1/channels` y `GET /api/v1/channels/{id}` (actualmente stubs con `NotImplementedError`) y su schema de respuesta paginada.
- Servicios: caso de uso de listado paginado con filtro por continente y de obtención de detalle, en `src/app/services/canal_service.py`.
- Repositorios: consultas SQLAlchemy de `CanalNoticias` en `src/app/repositories/canales.py`, con orden case-insensitive por `nombre`, filtro por `continente`, conteo total y paginación.
- Schemas: nuevo schema de listado paginado para `CanalNoticias` (análogo a `FuenteRSSListado`) en `src/app/schemas/canal.py`; reutilización del schema `Error` existente.
- Persistencia: solo lectura sobre la tabla `canales_noticias` existente; no se añaden tablas, columnas ni migraciones.
- Pruebas: integración HTTP con SQLite aislado cubriendo listado por defecto, orden alfabético, paginación (página específica, tamaño personalizado, límites inválidos, página fuera de rango), filtro por continente (con y sin coincidencias, vacío), listado vacío, detalle existente/inexistente (incluyendo `id` no numérico) y forma del schema de respuesta.
- No se modifican `docs/architecture.md` ni los ADR: el cambio implementa un endpoint ya previsto en la arquitectura (`openspec/config.yaml` ya declara el contrato de paginación de `GET /channels`).
- No se realizan llamadas HTTP a feeds RSS ni cambios de alcance en autenticación/autorización.
