## Context

El módulo Captura RSS ya tiene un scheduler APScheduler y un valor de periodicidad en `src/app/core/config.py`. La frecuencia actual se lee desde una variable de entorno y el scheduler ya contiene una función `reprogramar_periodicidad()` pendiente de implementación. No existe todavía un endpoint, schema, modelo, repositorio ni migración para la configuración de `periodicidad_cron_minutos`, ni un contrato OpenAPI para `GET/PUT /api/v1/config`.

La arquitectura aprobada exige mantener API, Servicios, Repositorios y Persistencia separados. Los routers no deben acceder a MySQL ni contener lógica de negocio. La persistencia debe quedar en repositorios y las llamadas a fuentes RSS externas deben seguir las reglas de timeout, retry acotado y Circuit Breaker del ADR-002.

## Goals / Non-Goals

**Goals:**

- Exponer la configuración actual mediante `GET /api/v1/config`.
- Actualizar `periodicidad_cron_minutos` mediante `PUT /api/v1/config` con validación de entero positivo.
- Persistir el valor en MySQL con una operación atómica y mantener el valor previo ante errores o entradas inválidas.
- Reprogramar APScheduler tras una actualización válida.
- Mantener la separación API/Servicios/Repositorios/Persistencia y reutilizar tecnologías aprobadas.
- Incluir pruebas automatizadas con mocks para las dependencias externas y para el scheduler.

**Non-Goals:**

- Modificar otros parámetros del cron o la lógica de captura RSS.
- Crear autenticación, autorización o un gestor de configuración externo.
- Introducir nuevas tecnologías o dependencias.
- Cambiar el contrato de fuentes RSS ni los patrones de resiliencia.

## Decisions

### Capa API

Añadir un router FastAPI para la configuración, con el endpoint `GET /api/v1/config` y `PUT /api/v1/config`. El router validará el cuerpo mediante un schema Pydantic v2 y delegará la lectura y actualización a un servicio. No contendrá SQL, no mantendrá estado del scheduler y no duplicará la validación del valor.

La operación `PUT` responderá `200` con el valor actualizado. La entrada `periodicidad_cron_minutos` se modelará como un entero positivo; `0`, negativos y tipos no enteros se convertirán en `400` mediante el schema y la validación del servicio.

### Capa Servicios

Crear un caso de uso de configuración donde se encapsule:

1. Obtener la configuración existente.
2. Validar que el valor sea un entero positivo.
3. Persistir la nueva configuración en una transacción.
4. Reprogramar el scheduler únicamente después de persistir el cambio.
5. Rolback o mantenimiento del valor previo si la reprogramación falla.

El servicio utilizará un repositorio para la operación de datos y no dependerá de FastAPI ni de SQLAlchemy directamente. El valor debe ser la única fuente de verdad del scheduler; no se debe consultar una variable de entorno en cada ejecución.

### Capa Repositorios y Persistencia

Crear un modelo de configuración con una clave canónica identificadora, por ejemplo `periodicidad_cron_minutos`, y un valor entero. El repositorio deberá:

- Consultar la configuración por clave.
- Insertar el registro si no existe.
- Actualizar el registro existente de forma atómica.
- Ejecutar las operaciones dentro de una transacción SQLAlchemy.
- Devolver el valor anterior cuando una actualización invalidada se rechace, sin escribir el registro.

La migración Alembic debe crear la tabla o columna necesarios si el esquema actual no ya las contiene. La migración deberá conservar un valor inicial aprobado por el equipo. El valor propuesto de 30 minutos del backlog es un punto de partida pendiente de ratificación, pero el diseño no debe fijarlo como una decisión definitiva sin aprobación.

### Scheduler APScheduler

Mantener un único `AsyncIOScheduler` en `src/app/jobs/scheduler.py`. La función `reprogramar_periodicidad(minutos)` deberá detener y volver a registrar el job existente con el nuevo intervalo, sin ejecutar una captura inmediata y manteniendo `max_instances=1` y `coalesce=True`.

La reprogramación se ejecutará solamente tras una actualización persistida correcta. El scheduler debe ser idempotente para poder reiniciarse después de un fallo o una nueva petición de actualización.

### Contrato y documentación

Ampliar `docs/Contratos/contrato-canales-fuentes-rss.openapi.yaml` con:

- `GET /config` con respuesta de configuración.
- `PUT /config` con cuerpo `periodicidad_cron_minutos` y respuestas `200`, `400` y `500` si procede.
- Esquemas de respuesta y solicitud que reutilicen el convenio de `codigo` y `mensaje` para errores.

No se debe alterar el contrato de `/channels`, `/sources` ni `/captures`.

### Pruebas

Las pruebas deben cubrir:

- Consulta de un valor existente.
- Actualización válida y persistencia del nuevo valor.
- Rechazo de `0` y valores negativos.
- Conservación del valor previo tras una actualización inválida.
- Reprogramación del scheduler con el valor actualizado.
- Error de persistencia o de reprogramación sin exponer trazas internas.
- No se ejecutarán llamadas reales a RSS; se usarán mocks para el repositorio, el scheduler y las dependencias HTTP externas cuando se prueben los casos de integración del cron.

## Risks / Trade-offs

- **[Riesgo]** El esquema actual no contiene una tabla de configuración → **Mitigación:** añadir una migración Alembic y cubrir la migración en las pruebas de superficie de persistencia.
- **[Riesgo]** La actualización puede persistir el valor pero fallar la reprogramación → **Mitigación:** definir una operación atómica o una compensación explícita y documentar el comportamiento; no se debe devolver éxito sin que el scheduler reciba el nuevo valor.
- **[Riesgo]** El valor de 30 minutos es solo una estimación → **Mitigación:** conservarlo como valor propuesto y dejar la ratificación de la frecuencia por equipo antes de producción.
- **[Riesgo]** El scheduler puede estar activo durante la reprogramación → **Mitigación:** detener y reinscribir el job con una única operación controlada y mantener `max_instances=1`.

## Migration Plan

1. Verificar la existencia de la configuración y de la tabla de configuración en el modelo y el esquema de MySQL.
2. Añadir la migración Alembic si falta la nueva entidad o columna.
3. Registrar el modelo y el repositorio en la capa de Persistencia.
4. Implementar el router, schema, servicio y reprogramación del scheduler.
5. Verificar la actualización con pruebas automatizadas y la conformidad con el contrato.
6. Ejecutar `pytest` con cobertura mínima del 80% y comprobar la conformidad final con `docs/architecture.md`.

El rollback revertirá la migración y desactivará la nueva endpoint, sin eliminar los registros históricos de noticias capturadas.
