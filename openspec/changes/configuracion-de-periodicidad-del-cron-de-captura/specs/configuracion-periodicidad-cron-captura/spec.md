## Purpose

Permite que el administrador del sistema consulte y modifique la periodicidad del cron de captura para ajustar la frecuencia de actualización de noticias según las necesidades operativas.

## ADDED Requirements

### Requirement: Consultar la periodicidad configurada

El sistema SHALL aceptar `GET /api/v1/config` y responder con HTTP `200` cuando el administrador del sistema solicite la configuración. La respuesta SHALL incluir el valor actual de `periodicidad_cron_minutos`.

#### Scenario: Consulta de la periodicidad configurada

- **Dado** que existe un parámetro de configuración `periodicidad_cron_minutos`
- **Cuando** el administrador del sistema envía `GET /api/v1/config`
- **Entonces** el sistema responde con código HTTP `200`
- **Y** el cuerpo incluye el valor actual de `periodicidad_cron_minutos`

### Requirement: Actualizar la periodicidad del cron

El sistema SHALL aceptar `PUT /api/v1/config` con un cuerpo que incluya `periodicidad_cron_minutos`. Un valor SHALL ser válido cuando sea un entero positivo. Después de una actualización válida, la siguiente ejecución del cron SHALL respetar el nuevo valor.

#### Scenario: Actualización exitosa de la periodicidad

- **Dado** que el administrador del sistema envía `PUT /api/v1/config` con `periodicidad_cron_minutos` igual a un entero positivo
- **Cuando** el sistema procesa la solicitud
- **Entonces** el sistema responde con HTTP `200`
- **Y** la siguiente ejecución del cron respeta el nuevo valor de periodicidad

### Requirement: Rechazar valores inválidos sin modificar el estado

El sistema SHALL rechazar `periodicidad_cron_minutos` cuando sea `0` o un valor negativo y responder con HTTP `400`. La actualización inválida SHALL no modificar el valor previo de configuración.

#### Scenario: Rechazo de valor inválido

- **Dado** que el administrador del sistema envía `PUT /api/v1/config` con `periodicidad_cron_minutos` igual a `0` o a un valor negativo
- **Cuando** el sistema procesa la solicitud
- **Entonces** el sistema responde con HTTP `400`
- **Y** el valor de configuración previo se mantiene sin cambios

### Requirement: Reprogramación y comportamiento operativo

La actualización válida SHALL ser persistida y SHALL reprogramar el scheduler para que el siguiente intervalo se calcule con el nuevo valor. La operación SHALL conservar la configuración anterior si la reprogramación no puede completarse, sin exponer detalles internos al administrador del sistema.

#### Scenario: Reprogramación tras actualizar la periodicidad

- **Dado** que la configuración contiene un valor previo y el scheduler está activo
- **Cuando** el administrador del sistema actualiza la periodicidad con un valor válido
- **Entonces** la configuración persistida cambia y el scheduler queda programado para el siguiente intervalo con el nuevo valor

### Requirement: Alcance y restricciones

Esta capacidad SHALL limitarse a la configuración de la periodicidad del cron. No SHALL modificar otros parámetros, introducir autenticación o autorización, ni añadir una política de reintentos o un mecanismo externo de programación.

#### Scenario: Alcance limitado a la periodicidad

- **Dado** que el administrador del sistema solicita una actualización de periodicidad
- **Cuando** el sistema procesa la solicitud
- **Entonces** solo se modifica `periodicidad_cron_minutos` y no se alteran los demás comportamientos del cron
