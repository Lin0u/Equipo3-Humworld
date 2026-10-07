"""Router API para consultar y actualizar la periodicidad del cron."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.jobs import scheduler as scheduler_module
from app.schemas.common import Error
from app.schemas.configuracion import Configuracion, ConfiguracionActualizar
from app.services.configuracion_service import (
    actualizar_configuracion as actualizar_configuracion_service,
    consultar_configuracion as consultar_configuracion_service,
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
    """Devuelve la periodicidad actual del cron de captura."""
    return {
        "periodicidad_cron_minutos": consultar_configuracion_service(db),
    }


@router.put(
    "",
    response_model=Configuracion,
    responses={400: {"model": Error}, 500: {"model": Error}},
)
def actualizar_configuracion(
    payload: ConfiguracionActualizar,
    db: Session = Depends(get_db),
):
    """Persiste y aplica una nueva periodicidad del cron."""
    try:
        return actualizar_configuracion_service(
            db,
            payload.periodicidad_cron_minutos,
            reprogramar=scheduler_module.reprogramar_periodicidad,
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content={"codigo": "VALOR_INVALIDO", "mensaje": str(exc)},
        )
