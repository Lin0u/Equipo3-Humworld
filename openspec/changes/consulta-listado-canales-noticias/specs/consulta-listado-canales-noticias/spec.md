## Purpose

Permite consultar y listar los `CanalNoticias` registrados, de forma paginada y ordenada alfabéticamente, con filtrado opcional por continente, así como obtener el detalle de un canal concreto, para conocer los medios configurados y auditar la cobertura por continente.

## ADDED Requirements

### Requirement: Listado paginado de CanalNoticias

El sistema SHALL aceptar `GET /api/v1/channels` y responder HTTP `200` con un objeto que contenga `items`, `pagina`, `tamanio_pagina` y `total`. La página por defecto SHALL ser `1`, el tamaño por defecto SHALL ser `10` y el tamaño máximo SHALL ser `50`. `total` SHALL representar el número total de `CanalNoticias` que cumplen los filtros, mientras `items` SHALL contener como máximo `tamanio_pagina` elementos de la página solicitada. El resultado SHALL ordenarse alfabéticamente en forma ascendente por `nombre`, de manera insensible a mayúsculas/minúsculas.

#### Scenario: Listado sin parámetros con resultados

- **Dado** que existen `N` `CanalNoticias` registrados (`N > 10`)
- **Cuando** el usuario envía `GET /api/v1/channels` sin parámetros de paginación
- **Entonces** el sistema responde con HTTP `200`
- **Y** `items` contiene exactamente `10` elementos
- **Y** `pagina` es igual a `1`
- **Y** `tamanio_pagina` es igual a `10`
- **Y** `total` es igual a `N`

#### Scenario: Orden alfabético ascendente e insensible a mayúsculas/minúsculas

- **Dado** que existen canales con nombres distintos, incluyendo variaciones de capitalización (por ejemplo, `bbc News` y `Al Jazeera`)
- **Cuando** el usuario envía `GET /api/v1/channels`
- **Entonces** los elementos de `items` están ordenados alfabéticamente en forma ascendente por `nombre`, sin que la capitalización altere el orden

#### Scenario: Solicitud de una página específica

- **Dado** que existen `N` `CanalNoticias` registrados (`N > 20`)
- **Cuando** el usuario envía `GET /api/v1/channels?pagina=2`
- **Entonces** el sistema responde con HTTP `200`
- **Y** `items` contiene los elementos correspondientes a la página `2` según `tamanio_pagina`
- **Y** `pagina` es igual a `2`

#### Scenario: tamanio_pagina personalizado dentro del máximo permitido

- **Cuando** el usuario envía `GET /api/v1/channels?tamanio_pagina=50`
- **Entonces** el sistema responde con HTTP `200`
- **Y** `items` contiene como máximo `50` elementos

#### Scenario: Página posterior a la última existente

- **Dado** que existen `N` `CanalNoticias` registrados y la última página con `tamanio_pagina` elementos es la página `P`
- **Cuando** el usuario envía `GET /api/v1/channels?pagina=P+1`
- **Entonces** el sistema responde con HTTP `200`
- **Y** `items` es un array vacío
- **Y** `pagina` es igual a `P+1` y `total` es igual a `N`

#### Scenario: Listado vacío

- **Dado** que no existen `CanalNoticias` registrados
- **Cuando** el usuario envía `GET /api/v1/channels`
- **Entonces** el sistema responde con HTTP `200`
- **Y** `items` es un array vacío
- **Y** `total` es igual a `0`

#### Scenario: Listado con un volumen alto de registros

- **Dado** que existen `500` `CanalNoticias` registrados
- **Cuando** el usuario envía `GET /api/v1/channels` sin parámetros de paginación
- **Entonces** el sistema responde con HTTP `200`
- **Y** el cuerpo mantiene la misma forma que con volúmenes menores: `items` con exactamente `10` elementos, `pagina` igual a `1`, `tamanio_pagina` igual a `10` y `total` igual a `500`
- **Y** el comportamiento de orden, paginación y filtrado no cambia respecto a los escenarios con `N` menor

### Requirement: Validar parámetros de paginación

El sistema SHALL rechazar con HTTP `400` cualquier solicitud cuyo `pagina` sea menor a `1`, cuyo `tamanio_pagina` sea menor a `1` o mayor a `50`, o cuyos valores no sean numéricos. Las respuestas `400` SHALL usar el schema `Error` con los campos `codigo` y `mensaje`, sin depender de un error de validación genérico no conforme al contrato. Cuando una misma solicitud incumpla más de una de estas condiciones a la vez, el sistema SHALL responder con un único HTTP `400` y un único cuerpo conforme al schema `Error`, sin devolver múltiples respuestas ni múltiples objetos de error.

#### Scenario: Rechazo por tamanio_pagina fuera de rango

- **Cuando** el usuario envía `GET /api/v1/channels?tamanio_pagina=51`
- **Entonces** el sistema responde con HTTP `400`
- **Y** el cuerpo contiene `codigo` y `mensaje` conforme al schema `Error`

#### Scenario: Rechazo por pagina o tamanio_pagina en cero o negativos

- **Cuando** el usuario envía `GET /api/v1/channels?pagina=0` o `GET /api/v1/channels?tamanio_pagina=0` o `GET /api/v1/channels?pagina=-1`
- **Entonces** el sistema responde con HTTP `400`
- **Y** el cuerpo contiene `codigo` y `mensaje` conforme al schema `Error`

#### Scenario: Rechazo por valores no numéricos

- **Cuando** el usuario envía `GET /api/v1/channels?pagina=abc` o `GET /api/v1/channels?tamanio_pagina=abc`
- **Entonces** el sistema responde con HTTP `400`
- **Y** el cuerpo contiene `codigo` y `mensaje` conforme al schema `Error`

#### Scenario: Rechazo por múltiples parámetros de paginación inválidos a la vez

- **Cuando** el usuario envía `GET /api/v1/channels?pagina=-1&tamanio_pagina=999`
- **Entonces** el sistema responde con un único HTTP `400`
- **Y** el cuerpo es un único objeto conforme al schema `Error`, con los campos `codigo` y `mensaje`
- **Y** la respuesta no incluye múltiples objetos de error, uno por cada parámetro inválido

### Requirement: Filtrar CanalNoticias por continente

El sistema SHALL aceptar el filtro opcional `continente` combinado con la paginación. La comparación SHALL ser exacta, insensible a mayúsculas/minúsculas e insensible a diacríticos (tildes), y SHALL ignorar los espacios exteriores del parámetro. Un `continente` vacío SHALL tratarse como filtro no proporcionado. `total` SHALL contar únicamente los `CanalNoticias` que cumplen el filtro.

#### Scenario: Filtrado por continente combinado con paginación

- **Dado** que existen `CanalNoticias` en distintos continentes
- **Cuando** el usuario envía `GET /api/v1/channels?continente=America&pagina=1`
- **Entonces** el sistema responde con HTTP `200`
- **Y** el 100% de los elementos de `items` tienen `continente` igual a `America`
- **Y** `total` cuenta únicamente esos canales

#### Scenario: Filtrado insensible a diacríticos

- **Dado** que existe un canal registrado con `continente` igual a `América`
- **Cuando** el usuario envía `GET /api/v1/channels?continente=America`
- **Entonces** el sistema responde con HTTP `200`
- **Y** ese canal está incluido en `items`

#### Scenario: Continente vacío se trata como filtro no aplicado

- **Dado** que existen `CanalNoticias` registrados
- **Cuando** el usuario envía `GET /api/v1/channels?continente=`
- **Entonces** el sistema responde con HTTP `200`
- **Y** el filtro de continente no se aplica
- **Y** la solicitud no produce HTTP `500`

#### Scenario: Continente sin coincidencias

- **Dado** que existen `CanalNoticias` registrados, ninguno con el continente solicitado
- **Cuando** el usuario envía `GET /api/v1/channels?continente=Antartida`
- **Entonces** el sistema responde con HTTP `200`
- **Y** `items` es un array vacío
- **Y** `total` es igual a `0`

### Requirement: Detalle de CanalNoticias

El sistema SHALL aceptar `GET /api/v1/channels/{id}` y devolver HTTP `200` con la representación completa del `CanalNoticias` identificado, incluyendo `id`, `nombre`, `continente`, `pais` y `descripcion`, sin envoltorio de paginación. Si no existe un canal con ese identificador, incluyendo el caso en que `{id}` no sea un valor numérico, el sistema SHALL responder HTTP `404` con el schema `Error` (`codigo`, `mensaje`).

#### Scenario: Consulta de detalle de un canal existente

- **Dado** que existe un `CanalNoticias` con `id=X`
- **Cuando** el usuario envía `GET /api/v1/channels/X`
- **Entonces** el sistema responde con HTTP `200`
- **Y** el cuerpo incluye `id`, `nombre`, `continente`, `pais` y `descripcion` de ese único canal, sin envoltorio de paginación

#### Scenario: Consulta de detalle de un canal inexistente

- **Dado** que no existe ningún `CanalNoticias` con `id=X`
- **Cuando** el usuario envía `GET /api/v1/channels/X`
- **Entonces** el sistema responde con HTTP `404`
- **Y** el cuerpo contiene `codigo` y `mensaje` conforme al schema `Error`

#### Scenario: Consulta de detalle con identificador no numérico

- **Cuando** el usuario envía `GET /api/v1/channels/abc`
- **Entonces** el sistema responde con HTTP `404`
- **Y** el cuerpo contiene `codigo` y `mensaje` conforme al schema `Error`

### Requirement: Alcance de consulta

La capacidad SHALL limitarse a la lectura de `CanalNoticias`. No SHALL modificar datos, no SHALL añadir filtros distintos de `continente`, y no SHALL añadir requisitos de autenticación o autorización. Los errores internos no SHALL exponerse en las respuestas HTTP.

#### Scenario: Consulta sin autenticación añadida

- **Dado** que el usuario solicita un listado o detalle válido
- **Cuando** realiza la petición sin credenciales o permisos nuevos introducidos por esta capacidad
- **Entonces** el sistema procesa la consulta sin rechazarla por autenticación o autorización
