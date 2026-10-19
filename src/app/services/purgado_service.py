"""
Caso de uso: purgado de noticias antiguas.

Origina en: HU-ADMIN-002 (purgado automático, Enabler Story) y HU-ADMIN-003
(purgado manual). PDF §4.2.5: "Noticias registradas con fecha anterior al
periodo de caducidad se eliminarán de la base de datos. Este será un proceso
automático. También existirá una función de usuario que permita borrar
noticias antiguas."

- La fecha que cuenta es fecha_registro ("noticias registradas"), en UTC.
- Caducidad en días, leída de la tabla configuracion (HU-ADMIN-001).
- Las coincidencias término–noticia se borran con la noticia (HU-SENT-008).
- Sin servicios externos: no requiere patrones de resiliencia.
"""
import logging
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy.orm import Session

from app.exceptions import FechaPurgadoInvalidaError
from app.repositories.noticias import NoticiaRepository
from app.services.configuracion_service import consultar_caducidad

logger = logging.getLogger(__name__)


def _ahora_utc() -> datetime:
    # fecha_registro se guarda como DateTime sin zona, en UTC.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def limite_por_caducidad(dias: int, ahora: datetime | None = None) -> datetime:
    return (ahora or _ahora_utc()) - timedelta(days=dias)


def purgar_por_caducidad(
    db: Session,
    ahora: datetime | None = None,
    repository: NoticiaRepository | None = None,
) -> dict:
    """Elimina las noticias registradas antes de (ahora - caducidad)."""
    limite = limite_por_caducidad(consultar_caducidad(db), ahora)
    eliminadas = (repository or NoticiaRepository()).eliminar_registradas_antes_de(db, limite)
    logger.info("Purgado: %s noticias registradas antes de %s eliminadas", eliminadas, limite)
    return {"noticias_eliminadas": eliminadas, "fecha_limite": limite}


def purgar_anteriores_a(
    db: Session,
    fecha: date,
    hoy: date | None = None,
    repository: NoticiaRepository | None = None,
) -> dict:
    """Purgado manual: elimina las noticias registradas antes del día indicado.

    El día indicado no se borra (límite = 00:00 UTC de esa fecha). Se rechaza
    una fecha posterior a hoy, que borraría noticias recién capturadas.
    """
    if fecha > (hoy or _ahora_utc().date()):
        raise FechaPurgadoInvalidaError(fecha)
    limite = datetime.combine(fecha, time.min)
    eliminadas = (repository or NoticiaRepository()).eliminar_registradas_antes_de(db, limite)
    logger.info("Purgado manual: %s noticias registradas antes de %s eliminadas", eliminadas, limite)
    return {"noticias_eliminadas": eliminadas, "fecha_limite": limite}
