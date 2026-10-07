## Purpose

Calcular y persistir el valor de humor de cada noticia capturada usando el diccionario como camino efectivo mientras HU-SENT-006 no provea una interfaz de modelo activo, y conservar el fallback para habilitar ML cuando dicha integración esté disponible.

## ADDED Requirements

### Requirement: Cálculo híbrido síncrono tras captura

Tras persistir una `Noticia` capturada, el sistema SHALL calcular su humor sincrónicamente antes de completar el flujo de captura. El cálculo de humor SHALL estar aislado para que un fallo interno del análisis no revierta ni impida guardar la noticia RSS capturada. Mientras HU-SENT-006 no provea una fuente de versiones ML activas, SHALL usar el método determinista del diccionario. Cuando esa integración futura provea una versión activa, el sistema SHALL intentar usarla dentro del timeout configurable.

#### Scenario: Cálculo con modelo ML activo tras integración de HU-SENT-006
- **Dado** que la integración de HU-SENT-006 provee una versión activa y disponible del modelo ML
- **Cuando** se captura y persiste una noticia nueva
- **Entonces** el sistema intenta calcular el valor de humor con el modelo ML de forma síncrona
- **Y** si termina dentro del timeout configurado, persiste `metodo_calculo=ml`, el valor calculado y el identificador de versión utilizado

#### Scenario: Cálculo sin integración ML disponible
- **Dado** que HU-SENT-006 aún no provee una fuente de versiones activas
- **Cuando** se captura y persiste una noticia nueva
- **Entonces** el sistema calcula su valor mediante el diccionario
- **Y** persiste `metodo_calculo=diccionario`
- **Y** el resultado no depende de un modelo entrenado

### Requirement: Fallback determinista por fallo o timeout

Cuando la integración ML de HU-SENT-006 esté disponible, un error de inferencia, indisponibilidad del servicio de embeddings o expiración del timeout SHALL activar el cálculo determinista por diccionario para esa `Noticia`. La llamada externa de embeddings SHALL aplicar timeout explícito y reintentos acotados con backoff conforme a ADR-04; nunca SHALL reintentar indefinidamente. El sistema SHALL registrar el incidente y SHALL persistir el resultado del fallback con `metodo_calculo=diccionario`, sin versión ML.

#### Scenario: Fallo explícito del modelo tras integración de HU-SENT-006
- **Dado** que la integración de HU-SENT-006 provee un modelo ML activo cuya inferencia falla
- **Cuando** el sistema calcula el humor de una noticia
- **Entonces** registra el fallo sin exponer trazas al usuario
- **Y** calcula y persiste el resultado mediante el diccionario
- **Y** marca `metodo_calculo=diccionario`

#### Scenario: Timeout del modelo o servicio de embeddings tras integración de HU-SENT-006
- **Dado** que el camino ML disponible no completa dentro del timeout configurado
- **Cuando** el sistema calcula el humor de una noticia
- **Entonces** no espera más allá del timeout configurado
- **Y** usa el método determinista de diccionario
- **Y** registra que se activó el fallback y persiste `metodo_calculo=diccionario`

### Requirement: Semántica y persistencia del fallback de diccionario

El cálculo por diccionario SHALL usar el promedio simple de los valores de términos únicos distintos que coincidan con el texto, según ADR-03/HU-SENT-007. Si no hay coincidencias, SHALL persistir `valor_humor=NULL`, `cantidad_terminos_evaluados=0` y `metodo_calculo=diccionario`. Cuando la noticia tenga `idioma_detectado=es` o `en`, SHALL limitar coincidencias a ese idioma. Si el idioma es nulo o no soportado, SHALL buscar coincidencias en ambos idiomas soportados. Esta HU solo requiere persistir humor, método de cálculo y, cuando HU-SENT-006 provea la integración, versión ML utilizada; no incluye polarización.

#### Scenario: Fallback con términos coincidentes
- **Dado** que el diccionario contiene `guerra=-8` y `victoria=6`, y el idioma de la noticia es `es`
- **Y** el texto de la noticia contiene ambos términos únicos
- **Cuando** se ejecuta el fallback determinista
- **Entonces** persiste `valor_humor=-1.0`, `cantidad_terminos_evaluados=2` y `metodo_calculo=diccionario`

#### Scenario: Término repetido en el texto
- **Dado** que el diccionario contiene `crisis=-6` en el idioma evaluado
- **Y** la noticia contiene `crisis` tres veces
- **Cuando** se ejecuta el fallback determinista
- **Entonces** el término se cuenta una sola vez
- **Y** persiste `valor_humor=-6.0` y `cantidad_terminos_evaluados=1`

#### Scenario: Idioma de noticia desconocido
- **Dado** que `idioma_detectado` es nulo o no es `es` ni `en`
- **Y** existen términos coincidentes en uno o ambos idiomas soportados
- **Cuando** se ejecuta el fallback determinista
- **Entonces** busca coincidencias en los diccionarios de español e inglés
- **Y** cuenta cada término de diccionario distinto por su combinación palabra+idioma

#### Scenario: Ningún término coincidente
- **Dado** que el texto no coincide con ningún término evaluable
- **Cuando** se ejecuta el fallback determinista
- **Entonces** persiste `valor_humor=NULL`, `cantidad_terminos_evaluados=0` y `metodo_calculo=diccionario`

### Requirement: Barrido periódico de respaldo

El sistema SHALL disponer de un job APScheduler configurable que vuelva a intentar calcular noticias cuyo procesamiento de sentimiento quedó pendiente (`valor_humor IS NULL` por interrupción o fallo no recuperado). El job SHALL reutilizar el mismo selector ML/diccionario, timeout y fallback del flujo de captura, procesar las noticias sin impedir el trabajo RSS y evitar reintentos infinitos. La periodicidad propuesta por el backlog es 30 minutos y queda configurable y pendiente de validación del equipo.

#### Scenario: Barrido repara cálculo interrumpido
- **Dado** que una noticia quedó con `valor_humor=NULL` porque el cálculo se interrumpió antes de finalizar
- **Cuando** se ejecuta el job periódico de respaldo
- **Entonces** el sistema vuelve a calcularla con ML si está disponible o diccionario en caso contrario
- **Y** persiste el método utilizado y el resultado correspondiente

#### Scenario: Barrido no bloquea la captura RSS
- **Dado** que una noticia pendiente falla durante un intento de cálculo del job
- **Cuando** el job procesa el conjunto de noticias pendientes
- **Entonces** registra el fallo de esa noticia
- **Y** continúa con las demás noticias pendientes y ejecuciones de captura RSS