## Purpose

Mantiene actualizado el conjunto de `Noticia` mediante ejecuciones periódicas del scheduler interno, consultando las `FuenteRSS` activas con resiliencia y evitando duplicados.

## ADDED Requirements

### Requirement: Ejecución periódica de captura

El sistema SHALL iniciar un scheduler interno con un job de captura cada `30` minutos. El scheduler SHALL esperar el primer intervalo después del arranque de la aplicación y SHALL ejecutar el job sin exponer un endpoint público nuevo. Cada ejecución SHALL considerar todas las `FuenteRSS` con `activo=true`.

#### Scenario: Scheduler iniciado

- **Dado** que la aplicación arranca correctamente
- **Cuando** se completa su ciclo de vida de inicio
- **Entonces** el scheduler queda activo con un intervalo de `30` minutos
- **Y** no realiza una llamada RSS inmediata durante el arranque

#### Scenario: Ejecución sobre fuentes activas

- **Dado** que existen `N` `FuenteRSS` activas, con `N >= 0`
- **Cuando** se dispara una ejecución programada
- **Entonces** el sistema crea un resultado independiente para cada una de las `N` fuentes
- **Y** el fallo de una fuente no impide iniciar el procesamiento de las restantes

### Requirement: Consumo RSS resiliente

Cada consulta externa SHALL usar un timeout explícito con los valores configurados para conexión y lectura, un máximo de `3` reintentos configurados con backoff exponencial acotado y un circuit breaker por `FuenteRSS`. Una fuente con circuit breaker abierto SHALL producir un resultado `fallida_circuito_abierto` sin realizar una llamada HTTP externa. Los fallos de red, timeout o respuestas no válidas SHALL producir `fallida_transitoria`, registrar fuente y motivo, y permitir continuar con las demás fuentes.

#### Scenario: Fuente temporalmente inaccesible

- **Dado** que una `FuenteRSS` activa no responde o responde con error
- **Cuando** el job intenta consultarla
- **Entonces** aplica como máximo `3` reintentos con backoff acotado
- **Y** devuelve un resultado `fallida_transitoria`
- **Y** registra la fuente y el motivo del fallo
- **Y** continúa procesando las demás fuentes

#### Scenario: Circuit breaker abierto

- **Dado** que una `FuenteRSS` activa tiene el circuit breaker en estado abierto
- **Cuando** se ejecuta el job
- **Entonces** devuelve un resultado `fallida_circuito_abierto`
- **Y** no realiza llamadas HTTP a esa fuente
- **Y** continúa procesando el resto de fuentes activas

#### Scenario: Ítem RSS malformado

- **Dado** que un feed válido contiene un ítem que no puede mapearse a una `Noticia`
- **Cuando** el sistema procesa el feed
- **Entonces** omite únicamente ese ítem
- **Y** registra la fuente y el motivo del ítem malformado
- **Y** continúa procesando los demás ítems del feed y las demás fuentes

### Requirement: Persistencia y deduplicación de noticias

Para cada ítem válido, el sistema SHALL usar su identificador RSS como `identificador_item_rss` global. Si no existe previamente, SHALL crear exactamente una `Noticia` con `fecha_registro` igual al timestamp de captura. Si ya existe, SHALL omitir la inserción. La restricción única global existente SHALL mantenerse.

#### Scenario: Alta de noticias nuevas

- **Dado** que una fuente devuelve `M` ítems válidos no registrados
- **Cuando** termina la captura de esa fuente
- **Entonces** se crean exactamente `M` `Noticia`
- **Y** cada una incluye un timestamp de registro
- **Y** el resultado informa `noticias_nuevas=M`

#### Scenario: Noticia duplicada

- **Dado** que una `Noticia` con un identificador RSS ya existe
- **Cuando** una ejecución posterior encuentra el mismo ítem
- **Entonces** no crea otra fila
- **Y** el resultado no cuenta ese ítem como nuevo

#### Scenario: Captura exitosa

- **Dado** que una fuente devuelve un feed válido sin fallos de red
- **Cuando** finaliza su procesamiento
- **Entonces** actualiza `fecha_ultima_captura_exitosa`
- **Y** deja el circuit breaker en estado cerrado

### Requirement: Aislamiento de fallos

El sistema SHALL aislar cada `FuenteRSS` durante una ejecución múltiple. Un error de una fuente no SHALL abortar, cancelar ni impedir los resultados de otras fuentes. Los errores internos SHALL quedar en logs del sistema sin exponerse a consumidores HTTP.

#### Scenario: Fallo aislado

- **Dado** que existen dos fuentes activas y solo la primera falla
- **Cuando** se ejecuta la captura múltiple
- **Entonces** se obtiene un resultado fallido para la primera y se procesa la segunda
- **Y** las noticias válidas de la segunda se persisten

### Requirement: Concurrencia acotada

El sistema SHALL limitar la concurrencia de capturas al valor configurado `captura_concurrencia_maxima` y SHALL impedir que dos ejecuciones del mismo job se solapen de forma ilimitada.

#### Scenario: Límite de concurrencia

- **Dado** que hay más fuentes activas que el límite configurado
- **Cuando** se ejecuta la captura múltiple
- **Entonces** nunca se procesan simultáneamente más fuentes que dicho límite
