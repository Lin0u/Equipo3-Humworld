## 1. Repositorios y persistencia

- [x] 1.1 Crear repositorios para listar `FuenteRSS` activas, consultar `Noticia` por `identificador_item_rss`, insertar noticias y actualizar fecha/estado de captura; verificar operaciones con SQLite.
- [x] 1.2 Verificar que la unicidad global de `Noticia.identificador_item_rss` se mantiene y que un intento duplicado no crea una segunda fila.
- [ ] 1.3 Verificar el commit/rollback por fuente y que un fallo de persistencia no aborta el procesamiento de otras fuentes.

## 2. Servicio de captura RSS

- [x] 2.1 Implementar captura individual con `httpx` asíncrono, timeout explícito y parseo `feedparser`; verificar feed válido con mock `respx`.
- [ ] 2.2 Implementar retry acotado de máximo 3 reintentos con backoff exponencial y registrar fuente/motivo en fallos de red, timeout o respuesta inválida; verificar con mocks de fuente caída y lenta.
- [x] 2.3 Implementar circuit breaker por `FuenteRSS`, omitiendo la llamada HTTP cuando esté abierto y devolviendo `fallida_circuito_abierto`; verificar transitioned/resultado con SQLite.
- [x] 2.4 Implementar mapeo de ítems RSS, timestamp `fecha_registro`, deduplicación y omisión de ítems malformados; verificar noticias nuevas, duplicadas y contenido inválido.
- [ ] 2.5 Implementar captura múltiple con semáforo limitado por `captura_concurrencia_maxima` y aislamiento de excepciones por fuente; verificar que un fallo no detiene fuentes restantes.
- [x] 2.6 Implementar `ejecutar_captura_todas_las_activas` y verificar que recorre todas las fuentes activas y no procesa fuentes inactivas.

## 3. Scheduler y ciclo de vida

- [ ] 3.1 Registrar el job APScheduler con intervalo de 30 minutos, `max_instances=1` y sin ejecución inmediata; verificar configuración del job sin llamadas RSS durante el arranque.
- [x] 3.2 Iniciar y detener el scheduler desde el lifespan de FastAPI, verificando que el ciclo de vida no deja tareas activas.
- [x] 3.3 Verificar que la reprogramación dinámica queda fuera de esta HU y no se modifica el router/config de HU-RSS-007.

## 4. Pruebas y calidad

- [ ] 4.1 Añadir pruebas unitarias con SQLite y `respx` para éxito, duplicados, feed lento, error HTTP, respuesta malformada, timeout, circuito abierto e ítem malformado.
- [ ] 4.2 Añadir prueba de integración del job con varias fuentes donde una falla y las demás persisten noticias correctamente.
- [x] 4.3 Verificar actualización de `fecha_ultima_captura_exitiva`, estados del circuit breaker, timestamp de noticias y resultados `exitosa`/`fallida_transitoria`/`fallida_circuito_abierto`.
- [x] 4.4 Ejecutar `pytest` con `pytest-cov` y verificar cobertura total mínima del 80%, sin llamadas RSS reales ni trazas expuestas.
- [x] 4.5 Comprobar conformidad final con `docs/architecture.md`, `openspec/config.yaml` y la separación API/Servicios/Repositorios/Persistencia; confirmar que no se añadieron endpoints ni funcionalidades fuera del cron automático.
