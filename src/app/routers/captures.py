"""Router para la captura manual de una o varias `FuenteRSS` (HU-RSS-008)."""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import FuenteRSSInactiveError, FuenteRSSNotFoundError
from app.schemas.common import Error
from app.schemas.captura import ResultadoCaptura, SolicitudCapturaMultiple
from app.services.captura_service import (
    ejecutar_captura_manual_fuente,
    ejecutar_captura_manual_multiple,
)

router = APIRouter(tags=["captures"])


@router.post(
    "/sources/{fuente_id}/captures",
    response_model=ResultadoCaptura,
    status_code=201,
    responses={
        404: {"model": Error, "description": "La FuenteRSS indicada no existe."},
        409: {"model": Error, "description": "La FuenteRSS indicada está inactiva."},
    },
)
async def disparar_captura_fuente(fuente_id: int, db: Session = Depends(get_db)):
    """Ejecuta síncronamente una captura manual de una FuenteRSS activa."""
    try:
        return await ejecutar_captura_manual_fuente(fuente_id, db)
    except FuenteRSSNotFoundError:
        error = Error(
            codigo="FUENTE_RSS_NO_ENCONTRADA",
            mensaje="La fuente RSS indicada no existe.",
        )
        return JSONResponse(status_code=404, content=error.model_dump())
    except FuenteRSSInactiveError:
        error = Error(
            codigo="FUENTE_RSS_INACTIVA",
            mensaje="La fuente RSS indicada está inactiva.",
        )
        return JSONResponse(status_code=409, content=error.model_dump())


@router.post("/captures", response_model=list[ResultadoCaptura], status_code=201)
async def disparar_captura_multiple(
    payload: SolicitudCapturaMultiple, db: Session = Depends(get_db)
):
    """Ejecuta síncronamente el lote, aislando el resultado por FuenteRSS."""
    return await ejecutar_captura_manual_multiple(payload.fuente_ids, db)
