"""
Router: /api/v1/dashboards

Origina en: HU-DASH-001-v3 (mapa mundial de humor) y HU-DASH-003-v2 (nube de palabras).
Contrato: contrato-dashboards.openapi.yaml, GET /dashboards/map y /dashboards/word-cloud.
ADR relacionado: ADR-05 (stack de frontend; el frontend no calcula humor).
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import Error
from app.schemas.dashboard import Continente, MapaHumor, NubePalabras
from app.services.dashboard_service import (
    LIMITE_NUBE_MAXIMO,
    LIMITE_NUBE_POR_DEFECTO,
    obtener_mapa,
    obtener_nube,
)

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.get(
    "/map",
    response_model=MapaHumor,
    response_model_by_alias=True,
    responses={400: {"model": Error}},
)
def obtener_mapa_humor(
    fecha: Optional[date] = Query(
        default=None,
        description="Día consultado (AAAA-MM-DD). Si se omite, el último día con datos.",
    ),
    db: Session = Depends(get_db),
):
    """Humor global, de cada uno de los 5 continentes y rango de fechas con datos."""
    return obtener_mapa(db, fecha)


@router.get("/word-cloud", response_model=NubePalabras, responses={400: {"model": Error}})
def obtener_nube_palabras(
    continente: Optional[Continente] = Query(default=None, description="Uno de los 5 continentes."),
    pais: Optional[str] = Query(default=None, description="País del canal de origen."),
    limite: int = Query(
        default=LIMITE_NUBE_POR_DEFECTO,
        ge=1,
        le=LIMITE_NUBE_MAXIMO,
        description="Cantidad máxima de palabras.",
    ),
    db: Session = Depends(get_db),
):
    """Palabras del diccionario ordenadas por la cantidad de noticias que las contienen."""
    return obtener_nube(db, continente, pais, limite)
