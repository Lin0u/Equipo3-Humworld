"""
Router: /api/v1/channels

Origina en: HU-RSS-001 (alta de canal de noticias).
ADR relacionado: ADR-002 (arquitectura de captura RSS, sección 1 y 4).
Contrato: contrato-canales-fuentes-rss.openapi.yaml, paths /channels, /channels/{id}.

TODO(equipo): este router solo define firma, rutas y validación básica de
entrada (Pydantic). La lógica de negocio (persistencia real, verificación de
nombre duplicado -> 409, etc.) debe implementarse en `app/services/` — no
directamente aquí, para mantener la separación de capas de ADR-002, sección 4.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import ChannelNameConflictError
from app.schemas.canal import CanalNoticias, CanalNoticiasCrear
from app.schemas.common import Error
from app.services.canal_service import crear_canal as crear_canal_service

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("", response_model=List[CanalNoticias])
def listar_canales(
    continente: Optional[str] = Query(default=None, description="Filtra canales por continente."),
    db: Session = Depends(get_db),
):
    """Origina en HU-RSS-001 (consulta implícita, soporte de sección 4.2.1 del PDF)."""
    # TODO(equipo): implementar consulta real vía app/services/canal_service.py
    raise NotImplementedError("HU-RSS-001: listado de canales pendiente de implementación")


@router.post("", response_model=CanalNoticias, status_code=201)
def crear_canal(payload: CanalNoticiasCrear, db: Session = Depends(get_db)):
    """
    Origina en HU-RSS-001.

    Criterios de aceptación (Gherkin, ver HU-RSS-001):
    - 201 si "nombre" y "continente" son válidos y no vacíos.
    - 409 si ya existe un canal con el mismo "nombre" sin distinguir
      mayúsculas/minúsculas.
    """
    try:
      return crear_canal_service(db, payload)
    except ChannelNameConflictError:
      error = Error(
        codigo="NOMBRE_CANAL_DUPLICADO",
        mensaje="Ya existe un canal con ese nombre.",
      )
      return JSONResponse(
        status_code=409,
        content=error.model_dump(exclude_none=True),
      )


@router.get("/{canal_id}", response_model=CanalNoticias)
def obtener_canal(canal_id: int, db: Session = Depends(get_db)):
    """Origina en HU-RSS-001 (soporte de consulta de detalle)."""
    # TODO(equipo): implementar consulta real; 404 si no existe
    raise NotImplementedError("HU-RSS-001: detalle de canal pendiente de implementación")
