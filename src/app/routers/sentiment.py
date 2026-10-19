"""
Router: /api/v1/sentiment

Origina en: HU-SENT-004 (GET: humor global, por continente, por país y timeline).
Contrato: contrato-sentimiento-diccionario.openapi.yaml, path /sentiment.
Pendiente: POST /sentiment (HU-SENT-005).
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import RangoFechasInvalidoError
from app.schemas.common import Error
from app.schemas.sentimiento import SentimientoAgregado
from app.services.consulta_sentimiento_service import consultar_sentimiento

router = APIRouter(prefix="/sentiment", tags=["sentiment"])


@router.get("", response_model=SentimientoAgregado, responses={400: {"model": Error}})
def obtener_sentimiento(
    continente: Optional[str] = Query(default=None, description="Continente del canal de origen."),
    pais: Optional[str] = Query(default=None, description="País del canal de origen."),
    desde: Optional[date] = Query(default=None, description="Fecha inicial (inclusive)."),
    hasta: Optional[date] = Query(default=None, description="Fecha final (inclusive)."),
    db: Session = Depends(get_db),
):
    """Humor agregado; con "desde" y "hasta" incluye la serie temporal día por día."""
    try:
        return consultar_sentimiento(db, continente, pais, desde, hasta)
    except RangoFechasInvalidoError as error:
        cuerpo = Error(codigo="RANGO_FECHAS_INVALIDO", mensaje=str(error))
        return JSONResponse(status_code=400, content=cuerpo.model_dump(exclude_none=True))
