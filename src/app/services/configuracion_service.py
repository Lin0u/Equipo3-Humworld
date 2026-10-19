"""Caso de uso para consultar y actualizar la configuración general.

Origina en: HU-RSS-007 (periodicidad del cron) y HU-ADMIN-001 (caducidad de
noticias, PDF §4.2.5).
"""

from collections.abc import Callable

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.configuracion import ConfiguracionRepository


CONFIGURACION_CLAVE = "periodicidad_cron_minutos"
CADUCIDAD_CLAVE = "caducidad_noticias_dias"


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


def consultar_caducidad(
    db: Session,
    repository: ConfiguracionRepository | None = None,
) -> int:
    """Días de caducidad de las noticias (HU-ADMIN-001).

    Si la fila no existe (base sin la migración c3f8a2d6e9b1), usa el valor
    por defecto de settings en vez de fallar.
    """
    configuracion_repository = repository or ConfiguracionRepository()
    configuracion = configuracion_repository.obtener(db, CADUCIDAD_CLAVE)
    if configuracion is None:
        return settings.purgado_caducidad_dias_defecto
    return configuracion.valor


def consultar_configuracion_completa(db: Session) -> dict:
    return {
        "periodicidad_cron_minutos": consultar_configuracion(db),
        "caducidad_noticias_dias": consultar_caducidad(db),
    }


def actualizar_configuracion(
    db: Session,
    valor: int,
    repository: ConfiguracionRepository | None = None,
    reprogramar: Callable[[int], None] | None = None,
    caducidad_dias: int | None = None,
) -> dict:
    """Valida, persiste y aplica la configuración.

    Ambos valores se validan antes de escribir: si uno es inválido no se
    modifica ninguno.
    """
    if valor <= 0:
        raise ValueError("La periodicidad debe ser un entero positivo.")
    if caducidad_dias is not None and caducidad_dias <= 0:
        raise ValueError("La caducidad debe ser un entero positivo de días.")

    configuracion_repository = repository or ConfiguracionRepository()
    if caducidad_dias is not None:
        configuracion_repository.guardar(db, CADUCIDAD_CLAVE, caducidad_dias)
    configuracion = configuracion_repository.actualizar(db, valor)
    if reprogramar is not None:
        reprogramar(valor)
    return {
        "periodicidad_cron_minutos": configuracion.valor,
        "caducidad_noticias_dias": consultar_caducidad(db, configuracion_repository),
    }
