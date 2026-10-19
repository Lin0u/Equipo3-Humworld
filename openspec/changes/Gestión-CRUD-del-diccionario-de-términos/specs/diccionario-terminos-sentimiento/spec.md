## Purpose

Permitir que el administrador del sistema mantenga los términos evaluables del diccionario de sentimiento con su palabra, idioma y valor, mediante un contrato CRUD consistente y validado.

## ADDED Requirements

### Requirement: Alta y unicidad de términos

El sistema SHALL permitir crear un `TerminoDiccionario` con palabra no vacía, idioma `es` o `en`, y valor entero entre -10 y +10 inclusive. La combinación literal exacta de palabra e idioma SHALL ser única; la unicidad SHALL distinguir mayúsculas/minúsculas y conservar el valor de palabra recibido. La creación válida SHALL responder HTTP 201 con el término creado; los datos inválidos SHALL responder HTTP 400 y una combinación duplicada SHALL responder HTTP 409.

#### Scenario: Alta exitosa de término
- **Dado** que no existe en el diccionario la combinación palabra `guerra` e idioma `es`
- **Cuando** el administrador del sistema envía `POST /api/v1/dictionary` con palabra `guerra`, idioma `es` y valor `-8`
- **Entonces** el sistema responde HTTP 201
- **Y** devuelve el término con esos datos y su identificador

#### Scenario: Aceptación de valores límite
- **Dado** que el administrador del sistema crea términos con valores `-10`, `0` y `10`
- **Cuando** envía cada solicitud válida a `POST /api/v1/dictionary`
- **Entonces** cada solicitud responde HTTP 201

#### Scenario: Rechazo de valor fuera de rango o no entero
- **Dado** que se envía un término con valor `-11`, `11` o un valor no entero
- **Cuando** el sistema procesa `POST /api/v1/dictionary`
- **Entonces** responde HTTP 400
- **Y** no crea el término

#### Scenario: Rechazo de combinación palabra e idioma duplicada
- **Dado** que ya existe un término con palabra `guerra` e idioma `es`
- **Cuando** el administrador del sistema intenta crear otro término con la misma combinación
- **Entonces** el sistema responde HTTP 409
- **Y** conserva un solo término para esa combinación

#### Scenario: Misma palabra en idiomas distintos
- **Dado** que ya existe el término `guerra` en idioma `es`
- **Cuando** el administrador del sistema crea `guerra` en idioma `en`
- **Entonces** el sistema permite el alta con HTTP 201

#### Scenario: Diferencia de mayúsculas en la clave literal
- **Dado** que existe el término `guerra` en idioma `es`
- **Cuando** el administrador del sistema crea `Guerra` en idioma `es`
- **Entonces** el sistema permite el alta con HTTP 201
- **Y** conserva la capitalización enviada

### Requirement: Consulta y búsqueda del diccionario

El sistema SHALL exponer `GET /api/v1/dictionary` como un array JSON sin paginación. SHALL permitir filtrar por coincidencia parcial de palabra mediante `busqueda`, sin distinguir mayúsculas y minúsculas. La consulta SHALL permitir obtener un `TerminoDiccionario` individual por id y responder HTTP 404 si no existe.

#### Scenario: Listado de términos sin filtro
- **Dado** que hay cero o más términos registrados
- **Cuando** el administrador del sistema envía `GET /api/v1/dictionary`
- **Entonces** el sistema responde HTTP 200
- **Y** devuelve un array con los términos registrados

#### Scenario: Búsqueda parcial por palabra
- **Dado** que existen términos con distintas palabras
- **Cuando** el administrador del sistema envía `GET /api/v1/dictionary?busqueda=guerr`
- **Entonces** el sistema responde HTTP 200
- **Y** incluye únicamente términos cuya palabra contiene `guerr`, sin distinguir mayúsculas y minúsculas

#### Scenario: Consulta de término existente
- **Dado** que existe un término con id `X`
- **Cuando** el administrador del sistema envía `GET /api/v1/dictionary/X`
- **Entonces** el sistema responde HTTP 200 con el término correspondiente

#### Scenario: Consulta de término inexistente
- **Dado** que no existe un término con id `X`
- **Cuando** el administrador del sistema envía `GET /api/v1/dictionary/X`
- **Entonces** el sistema responde HTTP 404

### Requirement: Actualización completa y parcial

El sistema SHALL permitir reemplazar los campos palabra, idioma y valor mediante PUT, y modificar solo los campos presentes mediante PATCH. Ambas operaciones SHALL validar las reglas de palabra, idioma y rango, y SHALL preservar la unicidad compuesta. Una actualización válida SHALL responder HTTP 200 con el término actualizado; id inexistente SHALL responder HTTP 404; datos inválidos SHALL responder HTTP 400; una combinación palabra+idioma perteneciente a otro término SHALL responder HTTP 409.

#### Scenario: Actualización completa
- **Dado** que existe un término con id `X`
- **Cuando** el administrador del sistema envía `PUT /api/v1/dictionary/X` con palabra, idioma y valor válidos
- **Entonces** el sistema reemplaza esos campos y responde HTTP 200 con el término actualizado

#### Scenario: Actualización parcial
- **Dado** que existe un término con id `X`
- **Cuando** el administrador del sistema envía `PATCH /api/v1/dictionary/X` con solo el campo valor válido
- **Entonces** el sistema actualiza el valor, conserva los otros campos y responde HTTP 200

#### Scenario: Rechazo de actualización con valor inválido
- **Dado** que existe un término con id `X`
- **Cuando** se intenta actualizarlo con valor `-11` o `11`
- **Entonces** el sistema responde HTTP 400
- **Y** conserva sin cambios el término anterior

#### Scenario: Rechazo de actualización que duplica otra combinación
- **Dado** que existen dos términos con identificadores distintos y distintas combinaciones palabra+idioma
- **Cuando** la actualización de uno intenta adoptar la combinación del otro
- **Entonces** el sistema responde HTTP 409
- **Y** ambos términos conservan sus datos previos

#### Scenario: Actualización de término inexistente
- **Dado** que no existe un término con id `X`
- **Cuando** el administrador del sistema envía PUT o PATCH a `/api/v1/dictionary/X`
- **Entonces** el sistema responde HTTP 404

### Requirement: Eliminación de términos

El sistema SHALL permitir eliminar un `TerminoDiccionario` existente por id y responder HTTP 204 sin cuerpo al completar la eliminación. Si el id no existe, SHALL responder HTTP 404.

#### Scenario: Eliminación exitosa
- **Dado** que existe un término con id `X`
- **Cuando** el administrador del sistema envía `DELETE /api/v1/dictionary/X`
- **Entonces** el sistema responde HTTP 204
- **Y** el término deja de estar disponible en consultas posteriores

#### Scenario: Eliminación de término inexistente
- **Dado** que no existe un término con id `X`
- **Cuando** el administrador del sistema envía `DELETE /api/v1/dictionary/X`
- **Entonces** el sistema responde HTTP 404