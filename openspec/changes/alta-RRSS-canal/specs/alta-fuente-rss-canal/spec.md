## Purpose

Permite al administrador del sistema registrar una `FuenteRSS` válida dentro de un `CanalNoticias` existente para preparar la captura posterior de noticias.

## ADDED Requirements

### Requirement: Alta de FuenteRSS en un CanalNoticias

El sistema SHALL aceptar `POST /api/v1/sources` con `canal_id`, `url` y `categoria_iptc` válidos, crear una `FuenteRSS` asociada exactamente al `CanalNoticias` indicado, inicializar `activo` en `true` y responder con HTTP 201 y la representación creada, incluyendo su identificador.

#### Scenario: Alta exitosa de una FuenteRSS

- **Dado** que existe un `CanalNoticias` con el identificador `42`
- **Cuando** el administrador del sistema envía `POST /api/v1/sources` con `canal_id` `42`, una URL válida y una categoría IPTC válida
- **Entonces** el sistema responde con HTTP `201`
- **Y** la respuesta incluye un identificador de `FuenteRSS`, `canal_id` igual a `42` y `activo` igual a `true`
- **Y** la `FuenteRSS` queda asociada únicamente al `CanalNoticias` `42`

#### Scenario: CanalNoticias inexistente

- **Dado** que no existe un `CanalNoticias` con el identificador `999999`
- **Cuando** el administrador del sistema envía `POST /api/v1/sources` con `canal_id` `999999`
- **Entonces** el sistema responde con HTTP `404`
- **Y** no persiste ninguna `FuenteRSS`

### Requirement: Validación de URL

El sistema SHALL recortar los espacios iniciales y finales de `url` antes de validarla y SHALL aceptar únicamente URLs absolutas con esquema `http` o `https` y una autoridad válida. Una URL que no cumpla estas reglas SHALL producir HTTP `400` con el schema `Error`, usando los campos `codigo` y `mensaje`.

#### Scenario: URL con formato inválido

- **Dado** que el campo `url` no es una URL absoluta HTTP/HTTPS válida
- **Cuando** el administrador del sistema envía la solicitud de alta
- **Entonces** el sistema responde con HTTP `400`
- **Y** el cuerpo contiene `codigo` y `mensaje` conforme al schema `Error`
- **Y** no persiste ninguna `FuenteRSS`

#### Scenario: URL con espacios exteriores

- **Dado** que el administrador del sistema envía una URL HTTP/HTTPS válida rodeada de espacios
- **Cuando** el sistema procesa la solicitud
- **Entonces** valida y persiste la URL sin esos espacios
- **Y** la respuesta devuelve la URL normalizada

### Requirement: Validación de categoría IPTC

El sistema SHALL aceptar `categoria_iptc` únicamente como uno de los identificadores canónicos de primer nivel de IPTC Media Topics versión 1.4: `01000000`, `02000000`, `03000000`, `04000000`, `05000000`, `06000000`, `07000000`, `08000000`, `09000000`, `10000000`, `11000000`, `12000000`, `13000000`, `14000000`, `15000000`, `16000000` o `17000000`. El valor SHALL recortarse antes de validarse y persistirse. Cualquier otro valor SHALL producir HTTP `400` con el schema `Error` (`codigo`, `mensaje`).

#### Scenario: Categoría IPTC reconocida

- **Dado** que `categoria_iptc` es `07000000`, identificador de primer nivel de IPTC Media Topics 1.4
- **Cuando** el administrador del sistema solicita el alta con el resto de datos válidos
- **Entonces** el sistema responde con HTTP `201`
- **Y** persiste `categoria_iptc` con el valor canónico `07000000`

#### Scenario: Categoría IPTC no reconocida

- **Dado** que `categoria_iptc` no pertenece a la lista de primer nivel de IPTC Media Topics 1.4
- **Cuando** el administrador del sistema solicita el alta
- **Entonces** el sistema responde con HTTP `400`
- **Y** el cuerpo contiene `codigo` y `mensaje` conforme al schema `Error`
- **Y** no persiste ninguna `FuenteRSS`

### Requirement: Alcance de la capacidad

El alta de `FuenteRSS` SHALL ejecutarse sin exigir autenticación o autorización nuevas. Esta capacidad SHALL limitarse a la creación; no SHALL modificar los contratos de consulta, modificación, eliminación ni captura de noticias. La capacidad no SHALL establecer una regla adicional de unicidad de URL, salvo las restricciones ya existentes en persistencia.

#### Scenario: Solicitud sin autenticación añadida

- **Dado** que la solicitud cumple las validaciones de alta
- **Cuando** se envía sin credenciales o permisos adicionales introducidos por esta HU
- **Entonces** el sistema procesa la solicitud sin rechazarla por autenticación o autorización
