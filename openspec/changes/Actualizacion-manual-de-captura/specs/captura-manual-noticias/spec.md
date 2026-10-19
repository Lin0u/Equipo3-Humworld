## Purpose

Permitir que el administrador del sistema solicite capturas manuales síncronas de una o varias `FuenteRSS` y reciba un resultado verificable por cada fuente procesada, reutilizando la captura y deduplicación existentes.

## ADDED Requirements

### Requirement: Captura manual individual

El sistema SHALL exponer `POST /api/v1/sources/{id}/captures`. Para una `FuenteRSS` existente y activa, SHALL ejecutar de forma síncrona el mismo procedimiento de captura y deduplicación utilizado por la captura automática y SHALL responder HTTP 201 con el resultado de esa fuente, incluyendo su estado y cantidad de noticias nuevas.

#### Scenario: Captura exitosa de una FuenteRSS activa
- **Dado** que existe una `FuenteRSS` activa con id `X`
- **Cuando** el administrador del sistema envía `POST /api/v1/sources/X/captures`
- **Entonces** el sistema responde HTTP 201 una vez finalizada la captura
- **Y** aplica a `X` el mismo procedimiento de captura y deduplicación del cron
- **Y** la respuesta informa el resultado, estado y cantidad de noticias nuevas de `X`

#### Scenario: Captura manual de una FuenteRSS inactiva
- **Dado** que existe una `FuenteRSS` con id `X` y `activo=false`
- **Cuando** el administrador del sistema envía `POST /api/v1/sources/X/captures`
- **Entonces** el sistema responde HTTP 409
- **Y** indica que la fuente está inactiva
- **Y** no realiza una solicitud HTTP al feed de `X`

#### Scenario: FuenteRSS individual inexistente
- **Dado** que no existe una `FuenteRSS` con id `X`
- **Cuando** el administrador del sistema envía `POST /api/v1/sources/X/captures`
- **Entonces** el sistema responde HTTP 404

### Requirement: Captura manual por lote

El sistema SHALL exponer `POST /api/v1/captures` con un cuerpo que contenga `fuente_ids`, una lista no vacía de identificadores de `FuenteRSS` válidas. SHALL intentar la captura de todos los identificadores recibidos y responder HTTP 201 con un resultado individual por cada id, incluyendo el estado y la cantidad de noticias nuevas o el motivo del fallo. Un fallo de captura de una fuente SHALL NOT impedir el intento de las restantes.

#### Scenario: Captura manual de varias FuenteRSS
- **Dado** que el administrador del sistema dispone de una lista `fuente_ids` con `N` identificadores válidos, donde `N >= 1`
- **Cuando** envía `POST /api/v1/captures`
- **Entonces** el sistema responde HTTP 201 cuando finaliza el procesamiento síncrono
- **Y** intenta capturar el 100% de las `N` fuentes indicadas
- **Y** incluye exactamente un resultado por cada identificador solicitado
- **Y** cada resultado informa el estado y cantidad de noticias nuevas o el motivo del fallo

#### Scenario: Fallo parcial en una captura por lote
- **Dado** que se solicitan `N` `FuenteRSS` válidas y la captura de una falla
- **Cuando** el sistema procesa `POST /api/v1/captures`
- **Entonces** intenta procesar también todas las demás fuentes del lote
- **Y** devuelve un resultado fallido para la fuente que falló
- **Y** devuelve el resultado correspondiente a cada fuente restante sin cancelar el lote

#### Scenario: Lista de identificadores vacía
- **Dado** que el cuerpo de `POST /api/v1/captures` contiene `fuente_ids` vacío o ausente
- **Cuando** el sistema valida la solicitud
- **Entonces** responde HTTP 400
- **Y** no inicia capturas

### Requirement: Reutilización del procesamiento de captura

La captura manual SHALL conservar las reglas de captura, resiliencia y deduplicación establecidas para la captura automática HU-RSS-006. Una noticia ya almacenada SHALL NOT persistirse nuevamente ni contarse como noticia nueva durante una captura manual.

#### Scenario: Ítem ya capturado previamente
- **Dado** que el feed de una `FuenteRSS` contiene un ítem cuyo identificador RSS ya está almacenado
- **Cuando** el administrador del sistema dispara una captura manual que procesa ese feed
- **Entonces** el sistema no crea una segunda `Noticia` para ese identificador
- **Y** no cuenta el ítem duplicado como noticia nueva