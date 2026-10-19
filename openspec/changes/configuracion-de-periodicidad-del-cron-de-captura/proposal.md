## Why

El cron de captura necesita una periodicidad modificable por el administrador del sistema para adaptar la frecuencia de actualización de noticias a las necesidades operativas. La implementación actual fija la frecuencia en configuración de entorno y contiene un stub de reprogramación, por lo que no existe un contrato HTTP ni una ruta de persistencia que permita cambiar el valor en caliente.

## What Changes

- Añadir `GET /api/v1/config` para consultar la configuración actual y devolver `periodicidad_cron_minutos`.
- Añadir `PUT /api/v1/config` para actualizar la periodicidad con un entero positivo y conservar el valor previo si la actualización es inválida.
- Persistir la configuración mediante el modelo y repositorio de la capa de Repositorios, usando MySQL y Alembic sin introducir tecnologías nuevas.
- Reprogramar el scheduler APScheduler después de una actualización válida para que la siguiente ejecución use el nuevo valor.
- Mantener la separación entre API, Servicios, Repositorios y Persistencia, y no exponer trazas internas ni añadir autenticación o autorización.
- Ampliar el contrato OpenAPI de `/api/v1/config` con los schemas de consulta y actualización.
- Añadir pruebas automatizadas para lectura, actualización válida, rechazo de valor inválido y conservación del valor previo.

## Capabilities

### New Capabilities

- `configuracion-periodicidad-cron-captura`: consulta y actualización de la periodicidad del cron de captura, con validación, persistencia y reprogramación segura.

### Modified Capabilities

<!-- No existe una capacidad base que deba modificarse en este cambio. -->

## Impact

- API: nuevos endpoints `GET` y `PUT /api/v1/config` y schemas Pydantic v2 para la configuración.
- Servicios: caso de uso de lectura y actualización con validación de entero positivo y coordinación con el scheduler.
- Repositorios: acceso a la configuración persistida y operación atómica de lectura/actualización.
- Persistencia: nuevo modelo y migración Alembic para la configuración, si no existe una tabla equivalente en el esquema actual.
- Scheduler: reprogramación del job de captura sin interrumpir otras ejecuciones y sin crear una nueva dependencia.
- Pruebas: pruebas HTTP con SQLite o el motor de prueba disponible, además de pruebas del servicio y del scheduler con mocks de dependencias.
- Contrato: ampliación de `docs/Contratos/contrato-canales-fuentes-rss.openapi.yaml` y mantenimiento de la estructura existente.

No se modifica `docs/architecture.md` ni los ADR: este cambio implementa una capacidad prevista en el módulo Captura RSS y utiliza las capas y tecnologías ya aprobadas.
