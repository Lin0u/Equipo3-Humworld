## Context

La ruta `POST /channels` y los schemas de canal ya existen, pero la creación real y la comprobación de duplicados están pendientes. La aplicación separa router, schemas, servicios y persistencia; el diseño debe conservar esa separación y el contrato OpenAPI actual. Véase `proposal.md` para la motivación y la delta-spec para el comportamiento requerido.

## Goals / Non-Goals

**Goals:**

- Implementar el flujo de alta a través de la capa de servicio, dejando el router como adaptador HTTP.
- Centralizar la normalización de los campos de texto antes de la validación de negocio y la persistencia.
- Hacer que la comparación de nombres sea case-insensitive de forma consistente entre validación y base de datos.
- Mapear errores de validación y conflicto al schema `Error` (`codigo`, `mensaje`) manteniendo los estados `400` y `409`.

**Non-Goals:**

- No introducir catálogo ni validación cerrada para `continente`.
- No añadir autenticación ni autorización.
- No modificar los endpoints de consulta de canales.

## Decisions

- **Servicio como dueño del caso de uso:** el router delegará la creación y traducirá las excepciones de dominio a respuestas HTTP. Esto evita incorporar reglas de negocio en FastAPI y sigue la separación ya indicada en `channels.py`. Se descarta implementar la lógica directamente en el endpoint.
- **Normalización explícita en la entrada:** los valores `nombre`, `continente`, `pais` y `descripcion` se recortarán antes de validar y guardar; los valores opcionales que resulten vacíos se tratarán según el contrato vigente. Se descarta usar únicamente la validación `min_length`, porque no detecta cadenas compuestas por espacios.
- **Unicidad case-insensitive en persistencia:** el servicio comprobará el nombre normalizado sin distinguir mayúsculas/minúsculas y la migración deberá respaldar esa garantía con una restricción o índice adecuado para el motor de base de datos. Se descarta confiar solo en una consulta previa, porque no protege frente a carreras concurrentes.
- **Errores compatibles con el contrato:** las respuestas `400` y `409` se construirán con el schema `Error` existente y sus campos `codigo` y `mensaje`; no se añadirá un formato paralelo. La conversión concreta de errores de Pydantic/FastAPI se mantendrá alineada con el OpenAPI actual.
- **Migración separada:** la migración Alembic queda pendiente y se registra como tarea explícita. Hasta que se aplique, el cambio no se considera listo para despliegue sobre una base de datos existente.

## Risks / Trade-offs

- **[Riesgo]** Una comparación sensible a la configuración de colación del motor podría permitir duplicados → **Mitigación:** cubrir la unicidad en el modelo/migración y probar nombres con capitalización distinta y solicitudes concurrentes.
- **[Riesgo]** Cambiar cadenas opcionales vacías a `None` puede afectar consumidores → **Mitigación:** confirmar el comportamiento del contrato y cubrirlo con tests antes de persistir; no alterar la forma pública sin necesidad.
- **[Riesgo]** La migración pendiente deja incompleta la garantía en entornos ya desplegados → **Mitigación:** bloquear la salida de despliegue hasta crear y ejecutar la migración, manteniéndola como tarea visible.

## Migration Plan

1. Implementar schemas, servicio, manejo HTTP y tests.
2. Crear y revisar la migración Alembic para la tabla de canales y la unicidad case-insensitive.
3. Ejecutar la migración en un entorno de prueba y validar altas, errores y duplicados.
4. Aplicar la migración antes de desplegar la versión que expone el alta.

El rollback de la aplicación consiste en retirar la versión del endpoint; el rollback de base de datos deberá ejecutarse mediante la migración Alembic inversa, después de evaluar si existen datos creados por la nueva capacidad.