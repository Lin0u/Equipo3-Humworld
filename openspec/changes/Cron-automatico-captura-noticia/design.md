## Context

El scheduler y `captura_service.py` son stubs. La arquitectura exige APScheduler interno, `httpx` asíncrono + `feedparser`, timeout explícito, retry acotado, circuit breaker por fuente y acceso SQLAlchemy únicamente en repositorios. El modelo `Noticia` ya contiene `identificador_item_rss` con unicidad global, `fecha_registro` y FK hacia `FuenteRSS`. Véanse [proposal.md](proposal.md) y [spec.md](specs/cron-automatico-captura-noticia/spec.md) para el contrato.

## Goals / Non-Goals

**Goals:**

- Activar el scheduler en el lifespan sin captura inmediata.
- Implementar captura individual, múltiple y de todas las fuentes activas.
- Persistir noticias nuevas, deduplicar globalmente y registrar timestamp.
- Aplicar timeout, retries, backoff, circuit breaker y concurrencia limitada.
- Aislar fallos por fuente y registrar motivos sin exponer trazas HTTP.
- Mantener API, Servicios, Repositorios y Persistencia separadas.

**Non-Goals:**

- No crear endpoint público de captura automática.
- No implementar captura manual HU-RSS-008.
- No implementar configuración dinámica HU-RSS-007 ni cambiar periodicidad en caliente.
- No analizar sentimiento, modificar noticias existentes ni purgar históricos.
- No introducir dependencias nuevas.

## Decisions

### Scheduler y ciclo de vida

`app/jobs/scheduler.py` mantendrá un `AsyncIOScheduler` y registrará un job de intervalo de 30 minutos con `max_instances=1` y una política de coalescencia para evitar acumulación de ejecuciones. `app/main.py` lo iniciará y detendrá en el lifespan. Se descarta iniciar una captura inmediata porque el arranque no debe provocar llamadas externas inesperadas.

La función de reprogramación queda fuera de esta HU y seguirá pendiente de HU-RSS-007.

### Servicio de captura

`captura_service.py` será independiente de FastAPI. `ejecutar_captura_todas_las_activas` obtendrá ids activas desde un repositorio y delegará en captura múltiple. `ejecutar_captura_multiple` usará un semáforo asíncrono con el límite configurado y aislará excepciones por fuente. `ejecutar_captura` gestionará estado del circuito, descarga, parseo, deduplicación y resultado.

Alternativa descartada: colocar el cron y las reglas RSS en el router, porque violaría la separación arquitectónica y dificultaría probar fallos aislados.

### Cliente RSS y resiliencia

Cada fuente se descargará con `httpx.AsyncClient` y timeout explícito compuesto por conexión y lectura. Los fallos reintentables tendrán como máximo 3 reintentos y backoff exponencial acotado; no habrá reintentos infinitos. El estado del circuit breaker residirá en `FuenteRSS.estado_circuit_breaker`. Una fuente abierta se reportará sin HTTP externo; una respuesta no válida o timeout se registra como fallo transitorio.

No se usará una llamada externa real en pruebas: `respx` mockeará respuestas correctas, lentas, erróneas y cuerpos malformados.

### Parseo y mapeo

`feedparser` convertirá el feed a ítems. El identificador se tomará del identificador RSS disponible (`guid`/`id`) y se aplicará la unicidad global ya existente. Los campos se mapearán a `Noticia` sin inventar datos: título, resumen/contenido, enlace, fecha de publicación, idioma y categoría cuando estén presentes. Un ítem que no tenga datos mínimos válidos se omite y se registra.

### Repositorio y transacción

Se añadirá un repositorio para consultar `FuenteRSS` activas, buscar `Noticia` por `identificador_item_rss`, insertar noticias y actualizar fecha/estado de la fuente. Las operaciones de persistencia harán commit/rollback controlado. La deduplicación se protegerá además con la restricción única de la base de datos; una carrera de inserción duplicada se trata como duplicado, no como fallo de toda la captura.

### Logging y resultados

Se usará logging estándar con `fuente_id` y motivo estructurado en cada fallo o ítem malformado. El servicio devolverá `ResultadoCaptura` con `EXITOSA`, `FALLIDA_TRANSITORIA` o `FALLIDA_CIRCUITO_ABIERTO` y el número de noticias nuevas. No se propagarán trazas internas mediante HTTP.

### Ficheros afectados

- Modificar `src/app/jobs/scheduler.py`.
- Modificar `src/app/main.py` para iniciar/detener scheduler.
- Modificar `src/app/services/captura_service.py`.
- Crear o modificar repositorios de fuentes/noticias bajo `src/app/repositories/`.
- Reutilizar `src/app/models/fuente.py`, `noticia.py` y `schemas/captura.py` salvo ajustes imprescindibles.
- Añadir pruebas bajo `src/tests/` con SQLite y `respx`.
- No modificar contratos HTTP existentes ni añadir endpoints.

## Risks / Trade-offs

- **[Riesgo]** Feeds heterogéneos no contienen todos los campos → **Mitigación:** validar mínimos, omitir solo ítems inválidos y registrar motivo.
- **[Riesgo]** Dos ejecuciones concurrentes intentan insertar el mismo ítem → **Mitigación:** `max_instances=1`, deduplicación previa y restricción única global.
- **[Riesgo]** Un circuito abierto retrasa recuperación → **Mitigación:** reportar estado explícito y dejar la transición de recuperación bajo la política del circuit breaker de ADR-002.
- **[Riesgo]** Una transacción parcial puede mezclar noticias persistidas y fallos posteriores → **Mitigación:** definir commit por fuente o lote pequeño y actualizar resultado de forma independiente; cubrirlo con pruebas de aislamiento.

## Migration Plan

Revisar si el esquema actual ya contiene las tablas y columnas necesarias. Si están presentes, no se requiere migración. Si falta infraestructura Alembic o alguna restricción existente, registrar una migración separada antes del despliegue. El rollback de aplicación consiste en detener el scheduler y retirar el job; las noticias ya capturadas no se eliminan automáticamente.
