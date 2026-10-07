## Context

Ver [proposal.md](proposal.md) para motivación y alcance, y [spec.md](specs/calculo-hibrido-humor/spec.md) para los requisitos observables. `captura_service.py` ya descarga, parsea, deduplica y persiste `Noticia`; `Noticia` solo posee `valor_humor`, y `scheduler.py` ya administra el cron APScheduler. HU-SENT-001 aporta el diccionario. ADR-03 fija promedio de términos únicos y ADR-04 fija embeddings Gemini + regresor local cuando exista una versión activa.

## Goals / Non-Goals

**Goals:**

- Ejecutar el cálculo de forma síncrona con límite de espera, reutilizando el flujo de captura existente y evitando que un fallo analítico deshaga una noticia ya capturada.
- Usar ML solo si existe modelo activo; conservar el diccionario como método siempre disponible y fallback.
- Reparar mediante APScheduler las noticias pendientes sin crear otra cola ni endpoint.
- Persistir el valor de humor, el método usado y la cantidad evaluada; dejar la versión ML para la integración de HU-SENT-006.
- Aislar las dependencias externas y el modelo mediante mocks para pruebas deterministas.

**Non-Goals:**

- Reimplementar el CRUD del diccionario (HU-SENT-001), implementar entrenamiento/versionado del modelo (HU-SENT-006), ampliar el algoritmo de diccionario definido en HU-SENT-007, polarización, agregaciones o dashboard.
- Añadir un endpoint, cola de mensajes, proveedor o dependencia nueva.
- Hacer asíncrono el cálculo con un sistema de jobs separado.

## Decisions

### Participación de capas

- **API:** no participa; HU-SENT-002-v2 no expone un endpoint propio. Las rutas existentes continúan delegando en Servicios.
- **Servicios — `src/app/services/captura_service.py` y servicio SENT nuevo:** el servicio de captura llama al caso de uso de cálculo después de persistir cada noticia. En este incremento el camino ejecutable es diccionario; el punto de extensión ML, timeout y fallback queda definido para conectarse cuando HU-SENT-006 entregue la interfaz de versión activa. Las excepciones se aíslan para no revertir la captura.
- **Repositorios — repositorio de noticias y diccionario:** encapsulan las consultas por idioma, la lectura de noticias pendientes y la persistencia del resultado. No se añade consulta a un modelo activo ni catálogo ML en este cambio. Toda consulta SQL permanece en `src/app/repositories/`.
- **Persistencia — MySQL/Alembic:** `Noticia.valor_humor` ya existe; añadir únicamente `metodo_calculo` y `cantidad_terminos_evaluados`, imprescindibles para el resultado de esta historia. La versión ML se pospone a HU-SENT-006 cuando exista su contrato de modelo activo. No incluir `polarizacion_terminos` de HU-SENT-003 ni persistencia de entrenamiento.
- **Scheduler — `src/app/jobs/scheduler.py`:** registrar y detener un job de reparación que recorra noticias pendientes. El intervalo será configuración, con 30 minutos como valor propuesto del backlog hasta ratificación del equipo.

### Ejecución, timeout y aislamiento

Se conserva el modo síncrono confirmado por HU-SENT-002-v2: calcular después de persistir la noticia en el mismo flujo. El camino ejecutable en este incremento usa diccionario; el uso de ML se habilitará solo cuando HU-SENT-006 provea la interfaz de versión activa. Se descarta un worker/cola independiente porque no está aprobado y cambiaría la infraestructura. El timeout de 3 segundos es una propuesta configurable (ADR-04), no un valor definitivo; no se fija por código ni se interpreta como ratificado.

El valor de humor debe persistirse en una transacción posterior o separada de la inserción RSS, de modo que un fallo del análisis nunca haga rollback de la noticia ni interrumpa otras capturas. Cuando se conecte ML vía HU-SENT-006, timeout, error de modelo o indisponibilidad de embeddings activan diccionario; el adaptador externo respetará la resiliencia limitada de ADR-04. Esta HU prueba el punto de extensión con mocks, sin integrar ni llamar el proveedor.

### Resultado y persistencia mínima

El diccionario usa el idioma detectado `es`/`en`; si falta o no pertenece a los idiomas soportados, se consultan ambos idiomas. El algoritmo se reutiliza desde HU-SENT-007 (promedio de términos únicos) y no se reimplementa ni persiste polarización. Si no hay coincidencias, `valor_humor=NULL` y cantidad evaluada cero. El mismo NULL es marcador para el barrido de respaldo. No se crea aquí catálogo, versión ni mecanismo de activación del modelo; esos datos se conectan con HU-SENT-006.

### Estrategia de pruebas

- SQLite en memoria para probar la integración captura→cálculo→persistencia, independencia transaccional y barrido de pendientes.
- Mock del adaptador del modelo/embeddings; nunca cargar modelos reales ni llamar a Google en pruebas.
- Probar camino de diccionario ejecutable y ausencia de integración ML; mockear el puerto de modelo para demostrar error/timeout y fallback sin activar dependencias de HU-SENT-006.
- Probar cálculo de diccionario mediante un servicio determinista/mock de HU-SENT-007: coincidencias, cero coincidencias, idioma conocido, idioma nulo/no soportado y método registrado.
- Probar barrido en noticias `valor_humor IS NULL`, fallo aislado por noticia y que se recorre el resto; verificar que el job se registra con intervalo configurable.
- Ejecutar suite completa con `pytest-cov` y cobertura ≥80%; ninguna prueba hace llamadas reales a servicios externos.

### Ficheros afectados

- Modificar `src/app/services/captura_service.py` para invocar el cálculo tras confirmar la captura y aislar fallos.
- Añadir un servicio de sentimiento para diccionario y punto de extensión ML/fallback.
- Modificar `src/app/models/noticia.py` y crear una migración Alembic para `metodo_calculo` y `cantidad_terminos_evaluados` junto al `valor_humor` existente.
- Crear o ampliar repositorios bajo `src/app/repositories/` para consultas de noticias pendientes y diccionario; no incluir consulta del modelo activo en esta HU.
- Modificar `src/app/jobs/scheduler.py` y configuración del sistema para el job periódico y timeout configurable.
- Añadir tests focalizados en `src/tests/` con SQLite y mocks del adaptador ML.
- No modificar contratos HTTP ni añadir routers.

## Risks / Trade-offs

- **[Riesgo]** La inferencia síncrona aumenta la duración del flujo de captura → **Mitigación:** timeout configurable, fallback determinista y error analítico aislado de la persistencia RSS.
- **[Riesgo]** El job puede volver a intentar indefinidamente una noticia con fallo persistente → **Mitigación:** procesar de forma aislada con límites/backoff aplicables al servicio externo y registrar el fallo; la periodicidad no genera reintentos dentro de una ejecución.
- **[Riesgo]** `valor_humor=NULL` significa tanto sin términos evaluables como pendiente → **Mitigación:** conservar semántica existente y no añadir estado adicional sin aprobación; documentar la limitación en la operación del barrido.
- **[Riesgo]** El modelo activo/versionado pertenece a HU-SENT-006 y aún no tiene interfaz implementada → **Mitigación:** este cambio ejecuta diccionario y define un punto de extensión; activar ML requiere integrar HU-SENT-006 y añadir su campo de versión.
- **[Riesgo]** Timeout/periodicidad propuestos podrían no ajustarse a latencias o carga reales → **Mitigación:** mantenerlos configurables y marcados como valores pendientes de ratificación.

## Migration Plan

Aplicar una migración Alembic para los campos mínimos del resultado del cálculo. Desplegar con el cálculo de diccionario disponible aunque no exista modelo activo; el camino ML permanece deshabilitado hasta que el catálogo de modelo activo (fuera de esta HU) lo provea. Al retirar el cambio, conservar las noticias y valores ya calculados; revertir columnas solo si el equipo confirma que no contienen datos que deban mantenerse.