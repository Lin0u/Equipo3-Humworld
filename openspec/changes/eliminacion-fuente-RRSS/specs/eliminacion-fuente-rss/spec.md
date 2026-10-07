## Purpose

Permite al administrador del sistema retirar una `FuenteRSS` de la captura futura sin destruir las `Noticia` históricas ni romper la relación referencial con la fuente original.

## ADDED Requirements

### Requirement: Eliminación lógica de FuenteRSS

El sistema SHALL aceptar `DELETE /api/v1/sources/{id}` para una `FuenteRSS` activa, establecer su estado `activo` en `false` y responder HTTP `204` sin cuerpo. La `FuenteRSS` y sus `Noticia` asociadas SHALL permanecer almacenadas.

#### Scenario: Eliminación exitosa

- **Dado** que existe una `FuenteRSS` activa con `id=42`
- **Cuando** el administrador del sistema envía `DELETE /api/v1/sources/42`
- **Entonces** el sistema responde con HTTP `204` y cuerpo vacío
- **Y** la fuente queda marcada como `activo=false`
- **Y** sus `Noticia` asociadas permanecen almacenadas

#### Scenario: Fuente ya eliminada

- **Dado** que existe una `FuenteRSS` con `id=42` y `activo=false`
- **Cuando** el administrador del sistema envía `DELETE /api/v1/sources/42`
- **Entonces** el sistema responde con HTTP `404`
- **Y** no modifica sus datos ni sus `Noticia` asociadas

### Requirement: FuenteRSS inexistente

El sistema SHALL responder HTTP `404` cuando el identificador no corresponda a una `FuenteRSS` activa o almacenada. El cuerpo de error SHALL usar el schema `Error` con `codigo` y `mensaje`.

#### Scenario: Eliminación de fuente inexistente

- **Dado** que no existe ninguna `FuenteRSS` con `id=999999`
- **Cuando** el administrador del sistema envía `DELETE /api/v1/sources/999999`
- **Entonces** el sistema responde con HTTP `404`
- **Y** el cuerpo contiene `codigo` y `mensaje`

### Requirement: Ocultar fuentes eliminadas

Las `FuenteRSS` con `activo=false` por eliminación SHALL quedar ocultas en el listado por defecto y SHALL responder HTTP `404` en el detalle. La eliminación no SHALL borrar ni desasociar `Noticia`.

#### Scenario: Consulta posterior a la eliminación

- **Dado** que una `FuenteRSS` con `id=42` fue eliminada lógicamente
- **Cuando** el usuario solicita `GET /api/v1/sources/42`
- **Entonces** el sistema responde con HTTP `404`
- **Y** cuando solicita `GET /api/v1/sources`, la fuente `42` no aparece en `items`

#### Scenario: Conservación de noticias históricas

- **Dado** que la `FuenteRSS` `42` tiene una o más `Noticia` asociadas
- **Cuando** se elimina lógicamente la fuente
- **Entonces** las `Noticia` conservan su `fuente_rss_id=42` y sus datos
- **Y** ninguna `Noticia` se elimina ni se desasocia

### Requirement: Alcance de eliminación

La capacidad SHALL usar eliminación lógica uniforme, sin borrado físico, cascada de `Noticia` ni desasociación. No SHALL añadir autenticación o autorización ni modificar otros endpoints de escritura.

#### Scenario: Sin requisitos de autenticación añadidos

- **Dado** que existe una `FuenteRSS` activa
- **Cuando** el administrador del sistema solicita su eliminación sin credenciales nuevas
- **Entonces** el sistema procesa la operación sin exigir autenticación o autorización introducida por esta HU
