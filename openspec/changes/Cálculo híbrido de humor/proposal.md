## Why

Las noticias capturadas necesitan un valor de humor para quedar utilizables por el análisis de sentimiento. HU-SENT-002-v2 define que el sistema use ML cuando haya una versión activa y recurra al diccionario de HU-SENT-001 cuando el modelo falte, falle o exceda el timeout.

## What Changes

- Añadir un servicio interno que calcule el humor de cada `Noticia` nueva de forma síncrona durante el flujo de captura, con límite de timeout al camino ML y fallback al diccionario.
- Aplicar el método determinista de HU-SENT-007 como camino efectivo mientras HU-SENT-006 no provea el contrato de modelo activo; mantener definida la selección ML, timeout/fallback y persistencia de versión para habilitar la integración posterior sin implementar el catálogo ni entrenamiento.
- Añadir un barrido de respaldo con APScheduler para volver a procesar noticias con `valor_humor IS NULL`; la periodicidad propuesta de 30 minutos queda configurable y pendiente de validación del equipo.
- Persistir únicamente los campos de `Noticia` imprescindibles para HU-SENT-002-v2: idioma detectado cuando esté disponible, método de cálculo y versión del modelo cuando se use ML. No incluir la polarización de HU-SENT-003 ni implementar el catálogo/entrenamiento de HU-SENT-006.
- Mantener el alcance del incremento en HU-SENT-001 y HU-SENT-002-v2 junto con las HU-RSS ya aprobadas; las demás HU-SENT quedan fuera.
- No exponer endpoints nuevos ni introducir colas, proveedores o dependencias adicionales a las ya aprobadas en ADR-04. No se requieren cambios arquitectónicos ni de ADR.

## Capabilities

### New Capabilities

- `calculo-hibrido-humor`: Cálculo síncrono del valor de humor de noticias usando una versión ML activa cuando esté disponible y fallback determinista por diccionario, con reparación periódica de resultados pendientes.

### Modified Capabilities

<!-- No hay especificaciones base en openspec/specs/ para modificar. La persistencia de campos de Noticia se limita a lo imprescindible para esta capacidad. -->

## Impact

- Servicios: orquestación de selección de método, timeout/fallback y servicio de cálculo del diccionario.
- Integración RSS: invocación síncrona tras persistir una noticia capturada, manteniendo el fallo del sentimiento aislado de la captura.
- Persistencia/Repositorios: consulta de diccionario/modelo activo/noticias pendientes y almacenamiento de valor, método y versión; migración limitada a campos requeridos.
- Scheduler: job APScheduler de reparación con intervalo configurable (propuesta actual 30 minutos, pendiente de validación).
- Pruebas: servicios externos/ML mockeados; SQLite para persistencia; sin llamadas reales a Gemini ni carga de modelo ML en unit tests.
- API/OpenAPI: sin endpoint nuevo; el recurso `/dictionary` pertenece a HU-SENT-001.