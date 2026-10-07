## Purpose

Permite al administrador del sistema actualizar una `FuenteRSS` existente sin eliminarla, mediante reemplazo completo con PUT o modificación parcial con PATCH de sus datos configurables.

## ADDED Requirements

### Requirement: Actualización completa de FuenteRSS

El sistema SHALL aceptar `PUT /api/v1/sources/{id}` con `url`, `categoria_iptc` y `activo` válidos, reemplazar esos tres campos de la `FuenteRSS` indicada y responder HTTP `200` con la representación actualizada. El `canal_id`, `id`, `fecha_ultima_captura_exitosa` y `estado_circuit_breaker` SHALL conservarse sin cambios.

#### Scenario: Actualización completa exitosa

- **Dado** que existe una `FuenteRSS` con `id=42`
- **Cuando** el administrador del sistema envía PUT a `/api/v1/sources/42` con `url`, `categoria_iptc` y `activo` válidos
- **Entonces** el sistema responde con HTTP `200`
- **Y** devuelve los valores enviados para esos tres campos
- **Y** conserva el `canal_id` y los campos de sistema de la fuente

#### Scenario: PUT incompleto o inválido

- **Dado** que existe una `FuenteRSS` con `id=42`
- **Cuando** el administrador del sistema envía un PUT sin uno de los campos obligatorios, con URL no HTTP/HTTPS o con categoría IPTC no reconocida
- **Entonces** el sistema responde con HTTP `400` y un cuerpo `Error` con `codigo` y `mensaje`
- **Y** no modifica la fuente

#### Scenario: Idempotencia de PUT

- **Dado** que existe una `FuenteRSS` con `id=42`
- **Cuando** el administrador del sistema envía dos veces consecutivas el mismo PUT válido
- **Entonces** ambas respuestas son HTTP `200`
- **Y** el estado final de la fuente es idéntico después de ambas ejecuciones

### Requirement: Actualización parcial de FuenteRSS

El sistema SHALL aceptar `PATCH /api/v1/sources/{id}` con uno o más de `url`, `categoria_iptc` y `activo`. SHALL modificar únicamente los campos presentes y válidos, conservar los restantes y mantener `canal_id` inmutable. Un cuerpo vacío o valores explícitamente nulos SHALL producir HTTP `400` sin cambios.

#### Scenario: PATCH de estado activo

- **Dado** que existe una `FuenteRSS` con `id=42` y `activo=true`
- **Cuando** el administrador del sistema envía PATCH a `/api/v1/sources/42` con únicamente `activo=false`
- **Entonces** el sistema responde con HTTP `200`
- **Y** `activo` pasa a `false`
- **Y** URL, categoría, canal y campos de sistema permanecen sin cambios

#### Scenario: PATCH de URL y categoría

- **Dado** que existe una `FuenteRSS` con `id=42`
- **Cuando** el administrador del sistema envía PATCH con una URL HTTP/HTTPS y una categoría IPTC válidas
- **Entonces** el sistema responde con HTTP `200`
- **Y** persiste la URL normalizada y la categoría enviada
- **Y** `activo` permanece sin cambios

#### Scenario: PATCH vacío o con null

- **Dado** que existe una `FuenteRSS` con `id=42`
- **Cuando** el administrador del sistema envía `{}` o un campo modificable con valor `null`
- **Entonces** el sistema responde con HTTP `400` y un cuerpo `Error`
- **Y** la fuente permanece sin cambios

### Requirement: FuenteRSS inexistente y validación común

El sistema SHALL responder HTTP `404` con `Error` cuando el identificador no corresponda a una `FuenteRSS`. Las URL SHALL reutilizar la validación HTTP/HTTPS y normalización de HU-02; `categoria_iptc` SHALL reutilizar los identificadores IPTC Media Topics 1.4. Los errores de entrada SHALL responder HTTP `400` sin trazas internas.

#### Scenario: Actualización de fuente inexistente

- **Dado** que no existe una `FuenteRSS` con `id=999999`
- **Cuando** el administrador del sistema envía PUT o PATCH a `/api/v1/sources/999999`
- **Entonces** el sistema responde con HTTP `404`
- **Y** no se crea ninguna fuente ni se modifica otra

#### Scenario: Normalización antes de persistir

- **Dado** que existe una `FuenteRSS` con `id=42`
- **Cuando** el administrador del sistema envía URL o categoría con espacios exteriores y valores válidos
- **Entonces** el sistema responde con HTTP `200`
- **Y** persiste esos campos sin espacios exteriores

### Requirement: Alcance de modificación

La capacidad SHALL limitarse a modificar `FuenteRSS` existentes. No SHALL permitir cambiar `canal_id`, `id`, `fecha_ultima_captura_exitosa` o `estado_circuit_breaker`, ni SHALL añadir autenticación o autorización.

#### Scenario: Canal propietario inmutable

- **Dado** que existe una `FuenteRSS` asociada al `CanalNoticias` `7`
- **Cuando** se solicita una actualización
- **Entonces** la fuente continúa asociada al `CanalNoticias` `7` después de la operación

#### Scenario: Solicitud de cambio de canal

- **Dado** que existe una `FuenteRSS` asociada al `CanalNoticias` `7`
- **Cuando** el administrador del sistema incluye `canal_id` en un PUT o PATCH para intentar cambiar el propietario
- **Entonces** el sistema responde con HTTP `400` y un cuerpo `Error`
- **Y** la fuente conserva su asociación al `CanalNoticias` `7`
