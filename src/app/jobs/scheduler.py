"""Scheduler interno APScheduler para la captura automática de RSS."""

import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import SessionLocal
from app.services.captura_service import ejecutar_captura_todas_las_activas
from app.services.configuracion_service import consultar_configuracion
from app.services.purgado_service import purgar_por_caducidad
from app.services.sentimiento_service import procesar_pendientes

logger = logging.getLogger(__name__)

CAPTURA_JOB_ID = "captura-rss-automatica"
BARRIDO_HUMOR_JOB_ID = "barrido-humor-pendiente"  # HU-SENT-002-v2
PURGADO_JOB_ID = "purgado-noticias-caducadas"  # HU-ADMIN-002
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


def _ejecutar_barrido_humor() -> None:
    """Barrido de respaldo de HU-SENT-002-v2: noticias sin humor calculado."""
    db: Session = SessionLocal()
    try:
        procesar_pendientes(db)
    except SQLAlchemyError:
        logger.exception("El barrido de humor no pudo leer las noticias pendientes")
    finally:
        db.close()


def _ejecutar_purgado() -> None:
    """Purgado automático de HU-ADMIN-002 (PDF §4.2.5)."""
    db: Session = SessionLocal()
    try:
        purgar_por_caducidad(db)
    except SQLAlchemyError:
        logger.exception("El purgado automático de noticias falló")
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
    # Primera ejecución 1 minuto después de arrancar, para retomar noticias
    # pendientes (p. ej., capturadas antes de existir el cálculo de humor).
    scheduler.add_job(
        _ejecutar_barrido_humor,
        id=BARRIDO_HUMOR_JOB_ID,
        trigger="interval",
        minutes=settings.sentimiento_barrido_minutos,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=1),
        max_instances=1,
        coalesce=True,
    )
    # HU-ADMIN-002: primera ejecución 5 minutos después de arrancar y luego
    # cada purgado_intervalo_horas (valor propuesto: 24 h).
    scheduler.add_job(
        _ejecutar_purgado,
        id=PURGADO_JOB_ID,
        trigger="interval",
        hours=settings.purgado_intervalo_horas,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=5),
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
