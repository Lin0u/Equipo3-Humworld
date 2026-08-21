"""
Scheduler del cron de captura automática.

Origina en: HU-RSS-006 (cron automático), HU-RSS-007 (periodicidad configurable).
Decisión de arquitectura: ADR-002, sección 2 — scheduler interno con
APScheduler (AsyncIOScheduler) en lugar de crontab del sistema operativo,
para permitir cambiar la periodicidad en caliente vía `/api/v1/config` sin
reiniciar el contenedor.

TODO(equipo):
1. Instanciar un AsyncIOScheduler al arrancar la aplicación (ver app/main.py,
   evento "startup").
2. Registrar el job `captura_service.ejecutar_captura_todas_las_activas`
   con la periodicidad leída desde `settings.captura_periodicidad_minutos`
   (o, una vez implementada HU-RSS-007, desde la tabla de configuración).
3. Exponer una función para reprogramar el job cuando `/api/v1/config`
   reciba un PUT con una nueva periodicidad (HU-RSS-007) — actualmente NO
   implementado porque el router/modelo de configuración todavía no existe
   en este scaffold (fuera del contrato OpenAPI ya generado; a definir).
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


def iniciar_scheduler() -> None:
    """Arranca el scheduler. Se invoca desde el evento startup de FastAPI."""
    # TODO(equipo): registrar el job de captura con la periodicidad configurada
    # scheduler.add_job(func=..., trigger="interval", minutes=settings.captura_periodicidad_minutos)
    raise NotImplementedError("Scheduler de captura pendiente de implementación — HU-RSS-006")


def reprogramar_periodicidad(minutos: int) -> None:
    """Reprograma el job de captura con una nueva periodicidad (HU-RSS-007)."""
    raise NotImplementedError("Reprogramación de periodicidad pendiente — HU-RSS-007")
