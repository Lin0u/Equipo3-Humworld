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
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import CanalNoticiasNotFoundError, ChannelNameConflictError
from app.schemas.canal import CanalNoticias, CanalNoticiasCrear, CanalNoticiasListado
from app.schemas.common import Error
from app.services.canal_service import (
    crear_canal as crear_canal_service,
    listar_canales as listar_canales_service,
    obtener_canal as obtener_canal_service,
)

router = APIRouter(prefix="/channels", tags=["channels"])

_ERROR_CANAL_NO_ENCONTRADO = Error(
    codigo="CANAL_NOTICIAS_NO_ENCONTRADO",
    mensaje="El canal de noticias indicado no existe.",
)


@router.get(
    "",
    response_model=CanalNoticiasListado,
    responses={400: {"model": Error}},
)
def listar_canales(
    continente: Optional[str] = Query(default=None, description="Filtra canales por continente."),
    pagina: int = Query(default=1, ge=1, description="Número de página."),
    tamanio_pagina: int = Query(default=10, ge=1, le=50, description="Elementos por página."),
    db: Session = Depends(get_db),
):
    """Origina en HU-RSS-010 (listado paginado, ordenado por "nombre" y filtrado por continente)."""
    return listar_canales_service(db, pagina, tamanio_pagina, continente=continente)


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


@router.get(
    "/{canal_id}",
    response_model=CanalNoticias,
    responses={404: {"model": Error}},
)
def obtener_canal(canal_id: str, db: Session = Depends(get_db)):
    """
    Origina en HU-RSS-010 (detalle de canal).

    "canal_id" se recibe como texto (no como "int" tipado por FastAPI) para
    que un identificador no numérico responda 404 con el schema "Error",
    en lugar del 422 automático de validación de FastAPI/Pydantic.
    """
    try:
        canal_id_numerico = int(canal_id)
    except ValueError:
        return JSONResponse(
            status_code=404,
            content=_ERROR_CANAL_NO_ENCONTRADO.model_dump(exclude_none=True),
        )

    try:
        return obtener_canal_service(db, canal_id_numerico)
    except CanalNoticiasNotFoundError:
        return JSONResponse(
            status_code=404,
            content=_ERROR_CANAL_NO_ENCONTRADO.model_dump(exclude_none=True),
        )
