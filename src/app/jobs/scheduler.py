"""Scheduler interno APScheduler para la captura automática de RSS."""

from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import SessionLocal
from app.services.captura_service import ejecutar_captura_todas_las_activas
from app.services.configuracion_service import consultar_configuracion

CAPTURA_JOB_ID = "captura-rss-automatica"
scheduler: AsyncIOScheduler = AsyncIOScheduler()


def _obtener_periodicidad_actual() -> int:
    db = SessionLocal()
    try:
        return consultar_configuracion(db)
    except (SQLAlchemyError, ValueError):
        return settings.captura_periodicidad_minutos
    finally:
        db.close()


async def _ejecutar_captura_automatica() -> None:
    db: Session = SessionLocal()
    try:
        await ejecutar_captura_todas_las_activas(db)
    finally:
        db.close()


def _event_loop_closed() -> bool:
    event_loop = getattr(scheduler, "_eventloop", None)
    return event_loop is not None and event_loop.is_closed()


def iniciar_scheduler() -> None:
    """Registra y arranca el job de captura sin ejecución inmediata."""
    global scheduler
    if scheduler.running and not _event_loop_closed():
        return

    scheduler = AsyncIOScheduler()
    minutos = _obtener_periodicidad_actual()
    scheduler.add_job(
        _ejecutar_captura_automatica,
        id=CAPTURA_JOB_ID,
        trigger="interval",
        minutes=minutos,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=minutos),
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()


def detener_scheduler() -> None:
    """Detiene las tareas del scheduler y libera sus recursos."""
    global scheduler
    if scheduler.running and not _event_loop_closed():
        scheduler.shutdown(wait=True)
    scheduler = AsyncIOScheduler()


def reprogramar_periodicidad(minutos: int) -> None:
    """Reprograma el job de captura con una nueva periodicidad (HU-RSS-007)."""
    if minutos <= 0:
        raise ValueError("La periodicidad debe ser un entero positivo.")

    if scheduler.running and not _event_loop_closed():
        scheduler.modify_job(
            CAPTURA_JOB_ID,
            trigger="interval",
            minutes=minutos,
            next_run_time=datetime.now(timezone.utc) + timedelta(minutes=minutos),
            max_instances=1,
            coalesce=True,
        )
