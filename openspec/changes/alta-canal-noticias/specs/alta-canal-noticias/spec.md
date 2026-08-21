## Purpose

Permite registrar canales de noticias de forma consistente, evitando nombres duplicados y exponiendo errores compatibles con el contrato OpenAPI actual.

## ADDED Requirements

### Requirement: Crear un canal de noticias
El sistema SHALL aceptar la creación de un canal mediante `POST /channels` y SHALL devolver el canal creado con estado `201` cuando los datos sean válidos y el nombre no esté registrado.

#### Scenario: Alta válida con campos opcionales
- **WHEN** se envía un `nombre` no vacío, un `continente` no vacío y valores válidos opcionales para `pais` y `descripcion`
- **THEN** el sistema crea el canal y responde con estado `201` y su representación, incluyendo su identificador

#### Scenario: Continente como texto libre
- **WHEN** se envía un `continente` que no pertenece a un catálogo predefinido
- **THEN** el sistema acepta el valor siempre que cumpla las restricciones de texto del contrato

### Requirement: Normalizar y validar los datos de entrada
El sistema SHALL recortar los espacios iniciales y finales de `nombre`, `continente`, `pais` y `descripcion` antes de validarlos y persistirlos. El sistema SHALL rechazar con estado `400` cualquier solicitud cuyo `nombre` resulte vacío después del recorte y cualquier otro dato que incumpla el contrato. Las respuestas `400` SHALL usar el schema `Error` con los campos `codigo` y `mensaje`.

#### Scenario: Nombre compuesto solo por espacios
- **WHEN** se envía un `nombre` compuesto únicamente por espacios
- **THEN** el sistema rechaza la solicitud con estado `400` y un cuerpo conforme al schema `Error`, con `codigo` y `mensaje`

#### Scenario: Espacios recortados antes de persistir
- **WHEN** se envían espacios al inicio o al final de cualquiera de los campos de texto
- **THEN** el sistema valida los valores recortados y, si son válidos, persiste y devuelve esos valores sin dichos espacios

#### Scenario: Campo obligatorio inválido tras normalización
- **WHEN** `nombre` o `continente` queda vacío después de recortar espacios
- **THEN** el sistema rechaza la solicitud con estado `400` y un cuerpo conforme al schema `Error`

### Requirement: Mantener nombres únicos sin distinguir mayúsculas/minúsculas
El sistema SHALL impedir la creación de dos canales cuyos nombres sean iguales ignorando mayúsculas y minúsculas, después de aplicar el recorte definido. Los conflictos SHALL responder con estado `409` y un cuerpo conforme al schema `Error`, con los campos `codigo` y `mensaje`.

#### Scenario: Nombre duplicado con distinta capitalización
- **WHEN** ya existe un canal con nombre `Noticias Globales` y se solicita crear otro con nombre `noticias globales`
- **THEN** el sistema rechaza la solicitud con estado `409` y un cuerpo conforme al schema `Error`

#### Scenario: Nombre duplicado por espacios exteriores
- **WHEN** ya existe un canal con nombre `Noticias Globales` y se solicita crear otro con nombre `  Noticias Globales  `
- **THEN** el sistema recorta el valor, detecta el conflicto y responde con estado `409` y un cuerpo conforme al schema `Error`

### Requirement: No exigir autenticación para esta capacidad
El alta de canales SHALL quedar fuera del alcance de autenticación y autorización de este cambio.

#### Scenario: Solicitud sin requisitos de autenticación añadidos
- **WHEN** se envía una solicitud que cumple el contrato funcional de alta
- **THEN** la evaluación de autenticación o autorización no añade un requisito nuevo como parte de esta capacidad