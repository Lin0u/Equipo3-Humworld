## Why

HumWorld necesita mantener actualizado el conjunto de noticias sin depender de una invocación manual. Un cron interno debe recorrer periódicamente las `FuenteRSS` activas, aplicar resiliencia ante fallos externos y almacenar solo noticias nuevas, preservando la continuidad del procesamiento cuando una fuente falla.

## What Changes

- Activar el scheduler interno APScheduler durante el ciclo de vida de la aplicación.
- Ejecutar la captura automática cada 30 minutos, esperando el primer intervalo tras el arranque.
- Recorrer todas las `FuenteRSS` activas en cada ejecución lógica.
- Consultar feeds RSS/Atom mediante `httpx` asíncrono y `feedparser`.
- Aplicar timeout explícito, reintentos acotados con backoff exponencial, circuit breaker por fuente y concurrencia limitada según la configuración existente.
- Omitir la llamada HTTP cuando el circuit breaker esté abierto, registrando el resultado de esa fuente y continuando con las demás.
- Deduplicar globalmente por `identificador_item_rss`, manteniendo la restricción única existente de `Noticia`.
- Registrar timestamp de captura en cada noticia nueva.
- Omitir ítems RSS malformados y continuar procesando el resto, dejando constancia en logs.
- Aislar los fallos por fuente y registrar fuente y motivo sin exponer trazas al consumidor HTTP.
- Mantener fuera de alcance la captura manual, la configuración dinámica de periodicidad de HU-RSS-007, el análisis de sentimiento y nuevos endpoints públicos.
- No modificar `docs/architecture.md` ni los ADR; el cambio implementa patrones ya aprobados.

## Capabilities

### New Capabilities

- `cron-automatico-captura-noticia`: Captura periódica resiliente y deduplicada de noticias desde `FuenteRSS` activas.

### Modified Capabilities

<!-- No existen capacidades base en openspec/specs/ para modificar. -->

## Impact

- Scheduler: activación del job APScheduler desde el lifespan de FastAPI.
- Servicios: implementación de captura individual, múltiple y de todas las fuentes activas.
- Repositorios: lectura de fuentes activas, deduplicación de `Noticia`, inserción y actualización de estado de captura.
- Persistencia: uso de las tablas existentes `fuentes_rss` y `noticias`; no se añade una tecnología nueva.
- Configuración: se usan los valores actuales de timeout, reintentos, concurrencia y circuit breaker; HU-RSS-007 seguirá siendo responsable de modificarlos dinámicamente.
- Pruebas: mocks de HTTP externo para feeds lentos, caídos, malformados, con duplicados y con éxito; pruebas aisladas de SQLite.
