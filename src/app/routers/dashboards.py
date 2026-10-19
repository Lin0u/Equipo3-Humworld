"""
Router: /api/v1/dashboards

Origina en: HU-DASH-001-v3 (mapa mundial de humor).
Contrato: contrato-dashboards.openapi.yaml, GET /dashboards/map.
ADR relacionado: ADR-05 (stack de frontend; el frontend no calcula humor).
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import Error
from app.schemas.dashboard import MapaHumor
from app.services.dashboard_service import obtener_mapa

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
