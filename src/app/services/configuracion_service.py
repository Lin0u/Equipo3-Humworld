"""Caso de uso para consultar y actualizar la periodicidad del cron."""

from collections.abc import Callable

from sqlalchemy.orm import Session

from app.repositories.configuracion import ConfiguracionRepository


CONFIGURACION_CLAVE = "periodicidad_cron_minutos"


def consultar_configuracion(
    db: Session,
    repository: ConfiguracionRepository | None = None,
) -> int:
    """Devuelve la periodicidad actual persistida."""
    configuracion_repository = repository or ConfiguracionRepository()
    configuracion = configuracion_repository.obtener(db, CONFIGURACION_CLAVE)
    if configuracion is None:
        raise ValueError("La configuración de periodicidad no existe.")
    return configuracion.valor


def actualizar_configuracion(
    db: Session,
    valor: int,
    repository: ConfiguracionRepository | None = None,
    reprogramar: Callable[[int], None] | None = None,
) -> dict:
    """Valida, persiste y reprograma la periodicidad del cron."""
    if valor <= 0:
        raise ValueError("La periodicidad debe ser un entero positivo.")

    configuracion_repository = repository or ConfiguracionRepository()
    configuracion = configuracion_repository.actualizar(db, valor)
    if reprogramar is not None:
        reprogramar(valor)
    return {"periodicidad_cron_minutos": configuracion.valor}
