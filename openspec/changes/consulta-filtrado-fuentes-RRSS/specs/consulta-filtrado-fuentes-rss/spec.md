## Purpose

Permite consultar, filtrar y auditar las `FuenteRSS` registradas, así como obtener el detalle de una fuente concreta, mediante respuestas paginadas y compatibles con el contrato de la API.

## ADDED Requirements

### Requirement: Listado paginado de FuenteRSS

El sistema SHALL aceptar `GET /api/v1/sources` y responder HTTP `200` con un objeto que contenga `items`, `pagina`, `tamanio_pagina` y `total`. La página por defecto SHALL ser `1`, el tamaño por defecto SHALL ser `10` y el tamaño máximo SHALL ser `50`. `total` SHALL representar el número total de fuentes que cumplen los filtros, mientras `items` SHALL contener como máximo `tamanio_pagina` elementos de la página solicitada. El resultado SHALL ordenarse por `canal_id` ascendente y después por `url` ascendente.

#### Scenario: Listado sin filtros con resultados

- **Dado** que existen `23` `FuenteRSS` registradas
- **Cuando** el usuario envía `GET /api/v1/sources`
- **Entonces** el sistema responde con HTTP `200`
- **Y** devuelve `pagina=1`, `tamanio_pagina=10` y `total=23`
- **Y** `items` contiene `10` fuentes ordenadas por `canal_id` y `url`

#### Scenario: Listado sin resultados

- **Dado** que no existe ninguna `FuenteRSS` registrada o ningún registro cumple los filtros
- **Cuando** el usuario envía `GET /api/v1/sources`
- **Entonces** el sistema responde con HTTP `200`
- **Y** devuelve `items=[]`, `pagina=1`, `tamanio_pagina=10` y `total=0`

#### Scenario: Página posterior

- **Dado** que existen `23` `FuenteRSS` y se solicita `pagina=3&tamanio_pagina=10`
- **Cuando** el usuario envía `GET /api/v1/sources?pagina=3&tamanio_pagina=10`
- **Entonces** el sistema responde con HTTP `200`
- **Y** devuelve `pagina=3`, `tamanio_pagina=10`, `total=23` y `items` con las `3` fuentes restantes

### Requirement: Filtrar FuenteRSS

El sistema SHALL aceptar los filtros opcionales `canal_id`, `continente`, `categoria_iptc` y `activo`. Cuando se proporcionen varios filtros, SHALL aplicarlos con semántica `AND`. Las comparaciones de `continente` y `categoria_iptc` SHALL ignorar mayúsculas y minúsculas; los espacios exteriores de esos parámetros SHALL ignorarse. Un parámetro textual vacío SHALL tratarse como no proporcionado. El filtro `activo` SHALL aceptar `true` o `false`.

#### Scenario: Filtrado por continente

- **Dado** que existen fuentes asociadas a canales de varios continentes
- **Cuando** el usuario envía `GET /api/v1/sources?continente=America`
- **Entonces** el sistema responde con HTTP `200`
- **Y** todos los elementos de `items` pertenecen a un `CanalNoticias` cuyo continente es `America`, sin distinguir mayúsculas
- **Y** `total` cuenta únicamente esas fuentes

#### Scenario: Filtrado combinado

- **Dado** que existen fuentes de distintas categorías y estados en varios canales
- **Cuando** el usuario envía `GET /api/v1/sources?continente=america&categoria_iptc=07000000&activo=true`
- **Entonces** el sistema responde con HTTP `200`
- **Y** cada elemento cumple simultáneamente los tres filtros

#### Scenario: Parámetros textuales vacíos

- **Dado** que existen fuentes registradas
- **Cuando** el usuario envía `GET /api/v1/sources?continente=&categoria_iptc=`
- **Entonces** el sistema responde con HTTP `200`
- **Y** ambos filtros se consideran no aplicados
- **Y** la solicitud no produce HTTP `500`

#### Scenario: Parámetros de paginación inválidos

- **Dado** que el usuario envía `pagina=0`, un `tamanio_pagina=0` o un `tamanio_pagina=51`
- **Cuando** solicita el listado
- **Entonces** el sistema responde con HTTP `400`
- **Y** el cuerpo contiene `codigo` y `mensaje` conforme al schema `Error`

### Requirement: Detalle de FuenteRSS

El sistema SHALL aceptar `GET /api/v1/sources/{id}` y devolver HTTP `200` con la representación completa de la `FuenteRSS` identificada, incluyendo `id`, `canal_id`, `url`, `categoria_iptc`, `activo`, `fecha_ultima_captura_exitosa` y `estado_circuit_breaker`. Si no existe una fuente con ese identificador, SHALL responder HTTP `404` con el schema `Error` (`codigo`, `mensaje`).

#### Scenario: Consulta de detalle existente

- **Dado** que existe una `FuenteRSS` con `id=42`
- **Cuando** el usuario envía `GET /api/v1/sources/42`
- **Entonces** el sistema responde con HTTP `200`
- **Y** el cuerpo representa únicamente la `FuenteRSS` `42` con todos sus campos públicos

#### Scenario: Consulta de detalle inexistente

- **Dado** que no existe una `FuenteRSS` con `id=999999`
- **Cuando** el usuario envía `GET /api/v1/sources/999999`
- **Entonces** el sistema responde con HTTP `404`
- **Y** el cuerpo contiene `codigo` y `mensaje` conforme al schema `Error`

### Requirement: Alcance de consulta

La capacidad SHALL limitarse a la lectura de `FuenteRSS`. No SHALL modificar datos ni añadir requisitos de autenticación o autorización. Los errores internos no SHALL exponerse en las respuestas HTTP.

#### Scenario: Consulta sin autenticación añadida

- **Dado** que el usuario solicita un listado o detalle válido
- **Cuando** realiza la petición sin credenciales o permisos nuevos introducidos por esta capacidad
- **Entonces** el sistema procesa la consulta sin rechazarla por autenticación o autorización
