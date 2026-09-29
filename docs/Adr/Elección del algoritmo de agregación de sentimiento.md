# ADR-003: Elección del algoritmo de agregación de sentimiento
 
**Estado:** Propuesto — pendiente de revisión y ratificación del equipo, análogo al proceso seguido con ADR-002.
 
---
 
## Contexto
 
El módulo de Análisis de Sentimiento (EPIC-SENT) es responsable de calcular el "humor" de cada noticia capturada por EPIC-RSS y de agregarlo a nivel global, continental y por país (PDF de especificaciones, secciones 4.2.2, 4.2.4 y 10.4, y Objetivos específicos, punto 2).
 
Restricciones y condicionantes reales:
 
- **El PDF no impone un algoritmo único.** Los Objetivos específicos (punto 2) piden "diseñar e implementar un algoritmo de análisis de sentimiento (basado en diccionario, LLM u otro método justificado)". La sección 10.4 ofrece explícitamente un "posible algoritmo" a modo de referencia, no de obligación: palabras con valor de -10 a +10, sumando los valores de las palabras evaluables encontradas en la noticia — y cierra con "Esta es solo una posible solución. Cada equipo puede determinar otra manera de hacer análisis de sentimiento."
- **Escala ya fijada:** -10 (mal humor) a +10 (muy buen humor) por palabra, tomada literalmente del PDF §10.4 y confirmada como vigente en la sección 11 de las instrucciones del proyecto.
- **Algoritmo base ya definido por las instrucciones del proyecto (sección 11), con una diferencia deliberada respecto al PDF:** el PDF sugiere *sumar* los valores de las palabras evaluables; las instrucciones del proyecto fijan en cambio un **promedio simple** (`sentimiento = Σ(términos) / n`) como algoritmo base. Este ADR sigue la instrucción del proyecto (más específica y más reciente que el PDF general del curso) porque sumar sin normalizar sesgaría el valor por la cantidad de términos evaluables de cada noticia — un artículo largo con muchos términos leves acumularía una suma mayor que uno corto con pocos términos intensos, aunque el segundo sea "más expresivo" por palabra. El promedio evita ese sesgo de longitud sin renunciar a la simplicidad exigida por el plazo académico.
- **Limitación conocida y ya documentada (instrucciones del proyecto, sección 11):** el promedio simple diluye la intensidad emocional real de una noticia — un término +9 y uno -10 en la misma noticia dan un resultado casi neutro, ocultando que la noticia es en realidad polarizada/controversial. Las instrucciones del proyecto exigen explícitamente documentar esta limitación en este ADR (lo cual se hace en la sección de Decisión, punto 2) y evaluar como alternativas la suma ponderada por frecuencia de aparición, el valor absoluto máximo, y la desviación estándar de los términos.
- **El backlog ya oficializado por el equipo (hoja Backlog del Excel entregado en P3) separa el algoritmo en dos caminos:** un camino determinista de diccionario, siempre disponible (HU-SENT-007, "Fallback determinista con diccionario"), y un camino híbrido que usa además un modelo de ML cuando esté disponible (HU-SENT-002-v2). **Este ADR decide únicamente el algoritmo del camino de diccionario** — es la parte completamente grounded en el PDF y en la sección 11 del proyecto. El diseño del modelo de ML (HU-SENT-006) queda fuera de alcance de este documento; su arquitectura completa fue decidida por separado y está documentada en `ADR-004-arquitectura-modelo-ml-sentimiento.md`.
- **MySQL como motor de persistencia** (instrucciones del proyecto, sección 8): el resultado del algoritmo (valor de humor y polarización) se persiste como campos de la entidad `Noticia` ya modelada en `diagrama-clases.md` (EPIC-RSS), no en una tabla separada.
- **Cobertura de pruebas ≥80% con dependencias externas mockeadas** (instrucciones del proyecto, sección 14): a diferencia de EPIC-RSS, el algoritmo de diccionario aquí decidido es puramente computacional sobre datos ya persistidos — no depende de ningún servicio externo, por lo que sus pruebas unitarias pueden ser 100% deterministas sin necesidad de mocks de red.
- **Plazo académico fijo**, con Sprint 2 dedicado a "Desarrollo del algoritmo de análisis de sentimiento y diccionario" (PDF, sección 8.1), lo que exige un algoritmo simple de implementar y de verificar en ese plazo.
## Decisión
 
### 1. Fórmula del valor de humor (camino de diccionario)
 
Se adopta el **promedio simple** de los valores de los términos del diccionario que coinciden con el texto de la noticia, tal como fija la sección 11 de las instrucciones del proyecto:
 
```
valor_humor = Σ(valor_termino_i) / n
```
 
donde `n` es la cantidad de términos evaluables encontrados en el texto de la noticia (contando el idioma detectado de la noticia contra el idioma de cada término del diccionario, HU-SENT-001).
 
- Si `n = 0` (ningún término del diccionario aparece en el texto), `valor_humor` se persiste como **NULL**, nunca como 0 — para distinguir "sin datos suficientes para evaluar" de "evaluado y el resultado fue neutro" en las consultas agregadas (HU-SENT-004).
- **Divisor "n":** `n` cuenta **términos únicos distintos** del diccionario que aparecen en el texto, no cada aparición individual. Justificación: contar apariciones repetidas dejaría que una noticia que menciona muchas veces la misma palabra (algo común por estilo de redacción periodística, no necesariamente porque el evento sea más intenso) pesara desproporcionadamente en el promedio, distorsionando el resultado por frecuencia de mención en vez de por contenido real evaluado. Esta decisión queda formalizada con su propio escenario Gherkin en `HU-SENT-007` (ver "Término que aparece más de una vez en el mismo texto"); este ADR fija el mismo criterio a nivel algorítmico para mantener ambos documentos consistentes.
### 2. Indicador complementario de polarización
 
Además del promedio, se calcula la **desviación estándar** (poblacional) de los valores de los mismos términos coincidentes, y se persiste como un campo adicional (propuesta de nombre: `polarizacion_terminos`) junto al `valor_humor` (ver `HU-SENT-003`):
 
```
polarizacion_terminos = desviación_estándar([valor_termino_1, ..., valor_termino_n])
```
 
Esta decisión responde directamente a la limitación conocida documentada en el Contexto: una noticia con términos +9 y -10 da un promedio casi neutro (-0.5) que oculta su carácter polarizado, pero su desviación estándar (~9.5) sí lo revela. El promedio simple **se mantiene como el valor principal** reportado en dashboards y agregados (por su simplicidad y por ser el que exige la sección 11 del proyecto como algoritmo base); la desviación estándar se añade como señal complementaria, sin sustituirlo, resolviendo la limitación sin abandonar la simplicidad exigida para el prototipo del curso.
 
**Pendiente de decisión del equipo:** si además se expone un indicador categórico derivado ("noticia polarizada": sí/no) a partir de un umbral sobre `polarizacion_terminos`. Este ADR **no fija un valor de corte numérico** para ese umbral por no estar especificado en ningún documento fuente — fijarlo sin respaldo violaría la regla de "Cero Alucinaciones" de las instrucciones del proyecto (sección 7). Si el equipo lo requiere, debe decidirlo explícitamente y documentarlo como una nueva versión de este ADR.
 
### 3. Alcance excluido de esta decisión
 
Este ADR decide exclusivamente el algoritmo del camino de diccionario (HU-SENT-007), que actúa además como *fallback* del camino híbrido (HU-SENT-002-v2). El diseño del modelo de ML (tipo de modelo, features, mecanismo de entrenamiento y versionado — HU-SENT-006) queda **explícitamente fuera de alcance** de este documento; esa arquitectura fue decidida en sesión de trabajo dedicada y está completamente documentada en `ADR-004-arquitectura-modelo-ml-sentimiento.md`.
 
### 4. Patrones de resiliencia (sección 13 de las instrucciones del proyecto)
 
El algoritmo de diccionario decidido en este ADR **no integra ningún servicio externo inestable**: opera exclusivamente sobre datos ya persistidos en MySQL (el texto de la noticia y el diccionario de términos, ambos locales a la aplicación). Por lo tanto, **no aplican** los patrones de Circuit Breaker, Timeout explícito, Retry con backoff ni Bulkhead para esta parte de la decisión — a diferencia de `ADR-002`, que sí integra fuentes RSS de terceros.
 
**Excepción ya resuelta:** el camino de ML (HU-SENT-006, fuera de alcance de este ADR) **sí terminó consumiendo un servicio externo real** — la API de Google Gemini Embedding, para la generación de vectores de embeddings. Esta decisión, junto con la evaluación completa de los cuatro patrones de resiliencia de la sección 13 aplicados a ese servicio externo (Timeout explícito y Retry acotado con backoff aplican; Circuit Breaker aplica con matiz, especialmente relevante en `HU-SENT-002-v2` por su alta frecuencia de llamadas; Bulkhead se evalúa y se descarta por ahora), quedó documentada en detalle en `ADR-004-arquitectura-modelo-ml-sentimiento.md`, sección "Patrones de resiliencia" — ya no es una incógnita futura, sino una decisión tomada y grounded en ese documento.
 
## Alternativas consideradas
 
### Alternativa A: Suma ponderada por frecuencia de aparición
 
**Ventajas:** da más peso a los términos que aparecen muchas veces en el texto, capturando la intensidad temática dominante del artículo (una noticia que menciona "guerra" cinco veces pesaría más ese término que una que lo menciona una sola vez).
 
**Desventajas:** sin normalizar por la longitud total del texto o por la cantidad total de términos evaluables, un artículo largo acumula naturalmente más apariciones (de cualquier signo) que uno corto, reintroduciendo el mismo sesgo de longitud que motivó descartar la suma simple del PDF en favor del promedio. Además, "frecuencia de aparición" pesa igual una repetición mecánica de una misma palabra (título y cuerpo repiten "guerra" varias veces) que menciones genuinamente distintas de varios términos, lo que puede sobre-representar una única palabra repetida frente a una noticia con vocabulario más diverso pero cada término mencionado una sola vez.
 
**Veredicto:** descartada como método principal. El promedio simple (Decisión, punto 1) ya resuelve el problema de longitud de forma más simple y explicable, sin necesidad de un esquema de ponderación adicional no especificado en ningún documento fuente. Coherente además con la decisión ya confirmada de que `n` cuenta términos únicos, no apariciones repetidas.
 
### Alternativa B: Valor absoluto máximo (intensidad emocional dominante)
 
**Ventajas:** identifica de un vistazo el término más extremo presente en la noticia (por ejemplo, el término con mayor valor absoluto, sea +10 o -10), útil para detectar rápidamente contenido potencialmente muy positivo o muy negativo sin que el promedio lo diluya.
 
**Desventajas:** ignora por completo el resto del contenido de la noticia. Una noticia con un único término extremo (+10) rodeada de varios términos neutros o levemente opuestos se reportaría con el mismo "humor máximo" que una noticia mayoritariamente positiva en todo su contenido — no resume el tono general del artículo, solo su pico puntual, lo cual puede ser engañoso si se reporta como "el humor" representativo de la noticia completa en los dashboards de EPIC-DASH.
 
**Veredicto:** descartada como valor principal de humor. Se deja anotada como una posible métrica secundaria de interés futuro (por ejemplo, para identificar "la palabra más influyente de la noticia", coherente con el requisito de HU-DASH-002/003 de listar noticias y palabras influyentes) — no se implementa en el prototipo del curso por no estar solicitada explícitamente en ninguna historia actual, para no ampliar el alcance sin que el equipo lo pida.
 
### Alternativa C: Desviación estándar como valor principal de humor (en vez de complementario)
 
**Ventajas:** expone directamente la polarización de la noticia, que es precisamente la limitación que el promedio simple no resuelve por sí solo.
 
**Desventajas:** la desviación estándar no tiene signo — no distingue una noticia "muy positiva y consistente" (términos +8, +9, +8 → desviación estándar baja) de una noticia "muy negativa y consistente" (términos -8, -9, -8 → desviación estándar igualmente baja), pese a representar estados de ánimo opuestos. No puede reemplazar al promedio como valor de "humor" reportado, porque por sí sola no dice si ese humor es positivo o negativo.
 
**Veredicto:** descartada como valor principal, pero adoptada como el **indicador complementario de polarización** de la Decisión (punto 2) — de las cuatro alternativas evaluadas, es la que mejor captura específicamente el matiz de polarización que el promedio simple pierde, sin necesidad de sustituirlo.
 
### Alternativa D: Suma simple sin promediar y sin indicador complementario (tal como lo sugiere literalmente el PDF §10.4)
 
**Ventajas:** mínima complejidad de implementación; es exactamente el "posible algoritmo" que describe el PDF, sin ningún ajuste adicional.
 
**Desventajas:** es precisamente el algoritmo cuya limitación queda documentada en la sección 11 de las instrucciones del proyecto — diluye la intensidad emocional real de las noticias polarizadas/controversiales, sin ningún mecanismo para detectarlo ni reportarlo. Además, al sumar en vez de promediar, el valor resultante queda sesgado por la cantidad de términos evaluables de cada noticia, dificultando comparar noticias de distinta extensión en los agregados de HU-SENT-004 y en los dashboards de EPIC-DASH (una noticia larga con muchos términos levemente positivos podría superar en "suma" a una noticia corta con pocos términos muy positivos, invirtiendo la intuición de cuál noticia es realmente "más feliz").
 
**Veredicto:** descartada tal cual la describe el PDF. Se adopta en su lugar la variante corregida (promedio, no suma) con el indicador complementario de polarización descrito en la Decisión — el propio PDF autoriza expresamente esta desviación ("Cada equipo puede determinar otra manera de hacer análisis de sentimiento"), y las instrucciones del proyecto (sección 11) ya fijan el promedio como algoritmo base para este curso.
 
## Consecuencias
 
**Positivas:**
- Resuelve explícitamente la limitación documentada en la sección 11 de las instrucciones del proyecto, sin abandonar la simplicidad de implementación exigida por el plazo académico (Sprint 2, dos semanas).
- El campo de polarización habilita directamente futuros requisitos de EPIC-DASH (por ejemplo, destacar noticias controversiales en el listado de noticias influyentes) sin necesidad de un nuevo ADR cuando esos requisitos se aborden.
- El algoritmo es 100% determinista y computable sin dependencias externas, lo que permite pruebas unitarias completamente verificables con valores numéricos exactos (ver `HU-SENT-007`, escenario Gherkin con el ejemplo -8/+6 → -1.0/7.0), sin necesidad de mocks de red ni de modelo de ML.
- Al no integrar servicios externos, esta parte del sistema no está sujeta a los mismos riesgos de disponibilidad que EPIC-RSS (fuentes RSS caídas, lentas, etc. — ver `ADR-002`), simplificando su operación.
- El divisor `n` queda alineado, en este mismo documento y en `HU-SENT-007`, como "términos únicos distintos" — evitando cualquier inconsistencia entre el ADR y la historia que lo implementa.
**Negativas / riesgos a mitigar:**
- Requiere extender el modelo `Noticia` (`diagrama-clases.md`, EPIC-RSS) con el nuevo campo de polarización — no se modifica ese diagrama en esta sesión (se generaron solo historias y este ADR, no código ni diagramas), queda pendiente para cuando el equipo aborde la implementación de Sprint 2.
- Quedan explícitamente sin fijar en este documento, por no estar especificados en ningún documento fuente: (a) el nombre y tipo de dato exacto del campo de polarización en la base de datos, y (b) si se expone un umbral categórico de "noticia polarizada" y, de ser así, su valor de corte. Fijar cualquiera de estos sin respaldo violaría la regla de "Cero Alucinaciones" de la sección 7 del proyecto — deben decidirse explícitamente por el equipo. *(El divisor `n`, antes pendiente en este mismo listado, ya quedó confirmado — ver Decisión, punto 1.)*
- La ruta de ML (`HU-SENT-002-v2`, `HU-SENT-006`) queda completamente fuera del alcance algorítmico de este ADR. Su arquitectura completa (tipo de modelo, features, proveedor externo, mecanismo de entrenamiento y versionado, criterio de evaluación y patrones de resiliencia) fue decidida en sesión de trabajo dedicada y está documentada en `ADR-004-arquitectura-modelo-ml-sentimiento.md`, incluyendo sus propios riesgos y limitaciones (dependencia de un proveedor externo con free tier no garantizado a futuro, limitación metodológica del criterio de evaluación MAE contra diccionario).
- El camino de ML sí involucra ahora un servicio externo de terceros (Google Gemini Embedding, vía `ADR-004`) — los patrones de resiliencia de la sección 13 del proyecto (Circuit Breaker, Timeout explícito, Retry con backoff acotado) **ya fueron evaluados y decididos** para ese caso en `ADR-004`, análogos a los definidos en `ADR-002` para las fuentes RSS. Este ADR-003 no los repite por no aplicar a su propio alcance (el camino de diccionario), pero deja la referencia cruzada explícita para evitar que el equipo busque esa decisión en el documento equivocado.
## Historias de usuario relacionadas
 
HU-SENT-001, HU-SENT-002-v2, HU-SENT-003, HU-SENT-004, HU-SENT-005, HU-SENT-006 *(solo en la parte de fallback a diccionario; su propia arquitectura de ML está documentada en `ADR-004-arquitectura-modelo-ml-sentimiento.md`, fuera del alcance de este ADR)*, HU-SENT-007.
 
---
 
## Historial de revisión de este ADR
 
| Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|
| v1.0 | 2026-09-28 | Creación inicial. Decide el algoritmo del camino de diccionario (promedio simple + desviación estándar como indicador de polarización complementario), evaluando explícitamente las cuatro alternativas exigidas por la sección 11 de las instrucciones del proyecto (suma ponderada por frecuencia, valor absoluto máximo, desviación estándar como valor principal, y suma simple sin promediar tal como sugiere el PDF). Deja explícitamente fuera de alcance el diseño del modelo de ML (HU-SENT-006). |
| v1.1 | 2026-09-28 | Se actualizan las referencias cruzadas ahora que `HU-SENT-006` quedó completamente resuelta en `ADR-004-arquitectura-modelo-ml-sentimiento.md`: la sección 4 ("Patrones de resiliencia") y los dos puntos correspondientes de "Consecuencias negativas" dejan de describir la arquitectura de ML como una incógnita futura y pasan a referenciar la decisión ya tomada. Se confirma además, en la Decisión punto 1, que el divisor `n` del promedio cuenta términos únicos distintos (decisión ya reflejada en `HU-SENT-007` v1.1), eliminando ese punto de la lista de pendientes en Consecuencias. No cambia ninguna fórmula ni alternativa evaluada — solo referencias cruzadas y el cierre de un punto pendiente ya resuelto en otro documento. |
| v1.2 (editorial) | 2026-09-29 | Limpieza editorial: se retiran las etiquetas "CONFIRMADO (decisión del equipo, sesión...)" y las marcas de fecha inline dentro del cuerpo del documento, integrando ese contenido como prosa técnica normal. La trazabilidad de cuándo se tomó cada decisión queda exclusivamente en esta tabla de Historial de revisión. Sin cambios de fondo en el algoritmo, las alternativas evaluadas ni las Consecuencias. |
