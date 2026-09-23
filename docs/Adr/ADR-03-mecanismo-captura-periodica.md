# ADR-0003: Mecanismo de captura periódica de fuentes RSS

- Estado: Aceptado
- Fecha: 2026-08-19
- Responsables: Equipo 3 (HumWorld)
- Relacionado con: PDF de especificaciones, sección 4.2.3; ADR-0001; HU-RSS-006, HU-RSS-007, HU-RSS-008

## Problema, elemento de arquitectura sobre el que decidir

El sistema debe recorrer periódicamente todas las fuentes RSS activas y capturar noticias nuevas, y esa periodicidad debe poder configurarse en caliente vía la API de Configuraciones (HU-RSS-007), sin reiniciar el contenedor. Debe definirse qué mecanismo dispara y ejecuta esa captura periódica.

## Opciones consideradas

### Opción A: Scheduler interno a la aplicación (APScheduler sobre FastAPI)
El propio proceso de la API programa y ejecuta el job de captura, leyendo la periodicidad desde la tabla de configuración.

### Opción B: Cron del sistema operativo del contenedor
Un script independiente, invocado por crontab, separado del proceso de la API.

### Opción C: Cola de mensajes (Celery + Redis/RabbitMQ)
Orquestación de la captura mediante workers separados y un broker de mensajes.

## Matriz de decisión

La Opción B desacopla completamente la captura de la API y aísla sus fallos, pero hacer la periodicidad configurable en caliente exigiría reescribir el crontab del contenedor en tiempo de ejecución o sincronizarlo con la configuración en base de datos, complejidad operativa no justificada para un prototipo de curso. La Opción C ofrece mejor escalabilidad y aislamiento de fallos, pero introduce infraestructura (broker de mensajes) no contemplada en el stack del proyecto, con un esfuerzo de configuración que no se justifica para el volumen de fuentes de este prototipo académico.

## Decisión

Se adopta la Opción A: un scheduler interno a la aplicación (APScheduler).

## Por qué se elige frente a las demás

Es la única opción que permite leer la periodicidad directamente desde la tabla de configuración en cada reprogramación del job, sin tocar el sistema operativo del contenedor ni sumar infraestructura adicional fuera del stack ya definido en ADR-0001, dentro del plazo acotado del curso.

## Consecuencias

### Positivas
Periodicidad ajustable en caliente sin reiniciar el contenedor, satisfaciendo HU-RSS-007 sin complejidad operativa adicional. La captura manual (HU-RSS-008) reutiliza el mismo procedimiento.

### Negativas y deuda aceptada
El job de captura comparte el mismo proceso y event loop que la API REST: una fuente lenta podría degradar la capacidad de respuesta de la propia API si no se limita la concurrencia (ver ADR-0004). Si en fases posteriores esto se detecta como problema, debería evaluarse ejecutar la captura como proceso separado, lo que ameritaría revisar este ADR.

## Trazabilidad y sincronización

Servicio de captura (capa de lógica de negocio); endpoint `/api/v1/config`; HU-RSS-006, HU-RSS-007, HU-RSS-008.
