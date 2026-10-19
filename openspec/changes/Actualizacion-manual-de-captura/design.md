## Context

Ver [proposal.md](proposal.md) para la motivación y [spec.md](specs/captura-manual-noticias/spec.md) para el contrato observable. El router `captures.py` y el esquema `captura.py` ya existen como scaffolding; el servicio de captura automática HU-RSS-006 proporciona captura individual, por lote y deduplicación. La implementación debe completar HU-08 sin duplicar esa lógica ni trasladar acceso a datos a routers o servicios.

## Goals / Non-Goals

**Goals:**

- Implementar las dos operaciones síncronas y mapear los estados del dominio a las respuestas HTTP fijadas por HU-RSS-008 y el contrato OpenAPI.
- Diferenciar `FuenteRSS` inexistente de inactiva antes de iniciar una solicitud externa.
- Mantener un resultado para cada id válido del lote y aislar los errores de captura.
- Entregar pruebas reproducibles sin conexiones RSS reales ni dependencia de MySQL.

**Non-Goals:**

- Rediseñar el proceso común de captura, el cron, la resiliencia RSS o el modelo de noticias.
- Cambiar el contrato funcional vigente, añadir colas, tareas en segundo plano, nuevos estados persistidos o tablas.
- Añadir autenticación/autorización, tecnologías o dependencias.

## Decisions

### Participación de capas

- **API — `src/app/routers/captures.py`:** conserva las rutas existentes, valida el identificador/body mediante FastAPI y Pydantic, delega en Servicios y transforma errores de dominio a HTTP. No contiene SQL ni decide cómo capturar.
- **Servicios — `src/app/services/captura_service.py`:** expone el caso de uso manual individual y el de lote. Verifica precondiciones de existencia/actividad con el repositorio, invoca el mismo procedimiento de captura que utiliza HU-RSS-006 y convierte fallos por fuente en resultados individuales. La operación individual comparte el mismo flujo que la captura por lote de un id, salvo la traducción HTTP específica requerida.
- **Repositorios — `src/app/repositories/fuentes.py` y `src/app/repositories/noticias.py`:** encapsulan la consulta que permite distinguir una `FuenteRSS` inexistente de una inactiva, y las operaciones ya necesarias para noticias/deduplicación. Si las funciones existentes bastan, se reutilizan; cualquier consulta SQL adicional queda exclusivamente en estos repositorios.
- **Persistencia — MySQL en producción y SQLite aislado en pruebas:** reutiliza `fuentes_rss`, `noticias` y la unicidad de `identificador_item_rss`. No requiere migración ni tabla de trabajos. Las transacciones y escritura de noticias siguen bajo repositorios y el flujo HU-RSS-006.

### Contrato y ejecución

Se conserva el contrato actual: `POST /sources/{id}/captures` y `POST /captures` con `fuente_ids`; ambos esperan a terminar y responden 201. La ruta individual responde 404 si no existe la `FuenteRSS` y 409 si existe pero está inactiva. Se descarta 202 porque exigiría infraestructura de trabajos asíncronos no aprobada. En el lote, cada captura produce su propio resultado; los errores de una captura no abortan las demás. No se altera el formato OpenAPI salvo corregir descripciones obsoletas que contradicen las decisiones ya aprobadas.

### Estrategia de pruebas

- Usar SQLite en memoria con las tablas ORM y `TestClient` para las rutas; sobreescribir `get_db` con la sesión de prueba.
- Mockear el transporte HTTP RSS con `respx`; no realizar llamadas de red reales. Mockear el servicio común cuando la prueba sea de orquestación/API, y usar el parser/capturador con respuestas RSS mockeadas cuando la prueba verifique deduplicación e integración.
- Verificar HTTP 201 y resultado de una captura activa; HTTP 404 para inexistente; HTTP 409 para inactiva y cero solicitudes HTTP externas en esa condición.
- Verificar lote no vacío con una fuente fallida y otra exitosa: se intenta el total de IDs, la respuesta contiene un resultado por fuente y persiste las noticias válidas de la exitosa.
- Verificar rechazo 400 de `fuente_ids` vacío/ausente, reutilización de deduplicación y forma del OpenAPI.

### Ficheros afectados

- Modificar `src/app/routers/captures.py` para sustituir los stubs y documentar el mapeo HTTP.
- Modificar `src/app/services/captura_service.py` para la precondición inactiva/inexistente y orquestación manual con aislamiento.
- Modificar `src/app/repositories/fuentes.py` solo si hace falta una operación de lectura para distinguir estado de la fuente.
- Modificar `docs/Contratos/contrato-canales-fuentes-rss.openapi.yaml` únicamente para retirar texto pendiente/alternativo ya resuelto y mantenerlo consistente con HU-RSS-008.
- Añadir pruebas en `src/tests/test_captura_manual.py` o ampliar las pruebas de captura existentes, según la organización final del módulo.

## Risks / Trade-offs

- **[Riesgo]** Confundir fuente inexistente e inactiva produce códigos incompatibles → **Mitigación:** resolver ambos estados explícitamente mediante el repositorio antes de llamar al capturador; probar 404 y 409 por separado.
- **[Riesgo]** Una excepción escapa del procesamiento por lote → **Mitigación:** aislar el error por id y comprobar que los resultados incluyen cada fuente solicitada.
- **[Riesgo]** Reimplementar captura manual diverge del cron → **Mitigación:** delegar al servicio/procedimiento común de HU-RSS-006 y probar deduplicación compartida.
- **[Trade-off]** El procesamiento síncrono mantiene una respuesta simple y evita infraestructura nueva, pero la duración de la solicitud depende de los límites de resiliencia de las fuentes RSS.

## Migration Plan

No se requiere migración de base de datos: se reutilizan las tablas y restricciones actuales. Desplegar la aplicación con el router funcional y el contrato sincronizado; el rollback consiste en volver a la versión anterior del servicio, sin cambios de datos estructurales que revertir.