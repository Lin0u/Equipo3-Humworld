# ADR-0004: Estrategia de resiliencia ante fuentes RSS externas inestables

- Estado: Aceptado
- Fecha: 2026-08-19
- Responsables: Equipo 3 (HumWorld)
- Relacionado con: PDF de especificaciones, sección 5; instrucciones del proyecto, sección 13; ADR-0001, ADR-0003; HU-RSS-006, HU-RSS-008

## Problema, elemento de arquitectura sobre el que decidir

Las fuentes RSS son de terceros y pueden presentar caídas intermitentes, lentitud, cambios de formato o certificados TLS inválidos. El módulo de captura debe procesar potencialmente decenas de fuentes en una misma ejecución sin que el fallo o la lentitud de una de ellas bloquee ni degrade el procesamiento del resto.

## Opciones consideradas

### Opción A: Sin mecanismos de resiliencia explícitos
Cada llamada HTTP se ejecuta sin timeout, reintento ni protección adicional.

### Opción B: Retry acotado con backoff exponencial, sin Circuit Breaker
Ante un fallo, se reintenta un número acotado de veces con backoff exponencial, pero sin registrar el historial de fallos de cada fuente.

### Opción C: Timeout explícito + Retry acotado + Circuit Breaker por fuente
Se añade, sobre la Opción B, un estado por fuente RSS que, tras fallos consecutivos, la marca temporalmente como "en circuito abierto" y la omite en las siguientes ejecuciones del cron antes de reintentarla.

## Matriz de decisión

La Opción A deja al sistema expuesto a que una sola fuente sin responder bloquee indefinidamente el worker de captura. La Opción B evita eso, pero con una fuente caída de forma sostenida (no transitoria), cada ejecución del cron volvería a gastar el presupuesto completo de reintentos sobre esa misma fuente, degradando la latencia total del job de forma recurrente. La Opción C resuelve específicamente ese caso al omitir temporalmente las fuentes con fallos sostenidos, a costa de un estado adicional por fuente que debe gestionarse con cuidado si la captura manual y el cron automático corren sobre la misma fuente en simultáneo. Se evaluó además un patrón de Bulkhead formal (aislar recursos por fuente) y se descartó por sobre-ingeniería para el alcance de este prototipo: el límite de concurrencia ya usado en el job de captura (ver ADR-0003) se considera suficiente mitigación.

## Decisión

Se adopta la Opción C: Timeout explícito + Retry acotado con backoff exponencial + Circuit Breaker por fuente RSS, implementados en la capa de servicio de captura y reutilizados tanto por el cron automático como por la captura manual.

## Por qué se elige frente a las demás

Es la única combinación que cubre tanto los fallos transitorios (retry) como los fallos sostenidos de una fuente (circuit breaker), evitando que estos últimos penalicen la latencia del job en cada ejecución del cron, que es justamente el escenario más probable dado que el PDF ya anticipa fuentes inestables de terceros.

## Consecuencias

### Positivas
El fallo de una o varias fuentes nunca compromete la disponibilidad de la API ni el procesamiento del resto de fuentes activas. La lógica es reutilizable entre captura automática y manual.

### Negativas y deuda aceptada
Los valores numéricos de timeout, número de reintentos, factor de backoff y umbral de fallos del Circuit Breaker no están fijados en este ADR y deben definirse como configuración validada por el equipo antes de la implementación final. El estado del Circuit Breaker por fuente es un campo mutable que debe protegerse ante condiciones de carrera entre captura manual y cron concurrentes; este punto de concurrencia queda pendiente de diseño detallado.

## Trazabilidad y sincronización

Servicio de captura (capa de lógica de negocio); campo `estado_circuit_breaker` en `FuenteRSS`; HU-RSS-006, HU-RSS-008.
