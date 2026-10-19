"""Router API /config: periodicidad del cron (HU-RSS-007) y caducidad de noticias (HU-ADMIN-001)."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.jobs import scheduler as scheduler_module
from app.schemas.common import Error
from app.schemas.configuracion import Configuracion, ConfiguracionActualizar
from app.services.configuracion_service import (
    actualizar_configuracion as actualizar_configuracion_service,
    consultar_configuracion_completa,
)

router = APIRouter(prefix="/config", tags=["config"])


@router.get(
    "",
    response_model=Configuracion,
    responses={400: {"model": Error}, 500: {"model": Error}},
)
def consultar_configuracion(
    db: Session = Depends(get_db),
):
    """Devuelve la periodicidad del cron y la caducidad de las noticias."""
    return consultar_configuracion_completa(db)


@router.put(
    "",
    response_model=Configuracion,
    responses={400: {"model": Error}, 500: {"model": Error}},
)
def actualizar_configuracion(
    payload: ConfiguracionActualizar,
    db: Session = Depends(get_db),
):
    """Persiste y aplica la periodicidad del cron y, si viene, la caducidad."""
    try:
        return actualizar_configuracion_service(
            db,
            payload.periodicidad_cron_minutos,
            reprogramar=scheduler_module.reprogramar_periodicidad,
            caducidad_dias=payload.caducidad_noticias_dias,
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content={"codigo": "VALOR_INVALIDO", "mensaje": str(exc)},
        )
