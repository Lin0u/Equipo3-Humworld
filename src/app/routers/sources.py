"""
Router: /api/v1/sources

Origina en: HU-RSS-002 (alta), HU-RSS-003 (consulta/filtrado),
HU-RSS-004 (modificación PUT/PATCH), HU-RSS-005 (eliminación).
ADR relacionado: ADR-002.
Contrato: contrato-canales-fuentes-rss.openapi.yaml, paths /sources, /sources/{id}.

TODO(equipo): sin lógica de negocio implementada — ver TODOs por endpoint.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import (
    CanalNoticiasNotFoundError,
    FuenteRSSNotFoundError,
)
from app.schemas.common import Error
from app.schemas.fuente import (
    FuenteRSS,
    FuenteRSSActualizar,
    FuenteRSSActualizarParcial,
    FuenteRSSCrear,
    FuenteRSSListado,
)
from app.services.fuente_service import (
    actualizar_fuente as actualizar_fuente_service,
    crear_fuente as crear_fuente_service,
    eliminar_fuente as eliminar_fuente_service,
    listar_fuentes as listar_fuentes_service,
    obtener_fuente as obtener_fuente_service,
)

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get(
    "",
    response_model=FuenteRSSListado,
    responses={400: {"model": Error}},
)
def listar_fuentes(
    canal_id: Optional[int] = Query(default=None, description="Filtra por canal propietario."),
    continente: Optional[str] = Query(default=None, description="Filtra por continente del canal."),
    categoria_iptc: Optional[str] = Query(default=None, description="Filtra por categoría IPTC (nivel 1)."),
    activo: Optional[bool] = Query(default=None, description="Filtra por estado activo/inactivo."),
    pagina: int = Query(default=1, ge=1, description="Número de página."),
    tamanio_pagina: int = Query(default=10, ge=1, le=50, description="Elementos por página."),
    db: Session = Depends(get_db),
):
    """Origina en HU-RSS-003 (consulta y filtrado de fuentes RSS)."""
    return listar_fuentes_service(
        db,
        pagina,
        tamanio_pagina,
        canal_id=canal_id,
        continente=continente,
        categoria_iptc=categoria_iptc,
        activo=activo,
    )


@router.post(
    "",
    response_model=FuenteRSS,
    status_code=201,
    responses={400: {"model": Error}, 404: {"model": Error}},
)
def crear_fuente(payload: FuenteRSSCrear, db: Session = Depends(get_db)):
    """
    Origina en HU-RSS-002.

    Criterios de aceptación (ver HU-RSS-002):
    - 201 si el canal existe y los datos son válidos; "activo" se inicializa
      en verdadero.
    - 404 si "canal_id" no corresponde a ningún canal registrado.
    """
    try:
        return crear_fuente_service(db, payload)
    except CanalNoticiasNotFoundError:
        error = Error(
            codigo="CANAL_NOTICIAS_NO_ENCONTRADO",
            mensaje="El canal de noticias indicado no existe.",
        )
        return JSONResponse(
            status_code=404,
            content=error.model_dump(exclude_none=True),
        )


@router.get(
    "/{fuente_id}",
    response_model=FuenteRSS,
    responses={404: {"model": Error}},
)
def obtener_fuente(fuente_id: int, db: Session = Depends(get_db)):
    """Origina en HU-RSS-003 (consulta de detalle)."""
    try:
        return obtener_fuente_service(db, fuente_id)
    except FuenteRSSNotFoundError:
        error = Error(
            codigo="FUENTE_RSS_NO_ENCONTRADA",
            mensaje="La fuente RSS indicada no existe.",
        )
        return JSONResponse(
            status_code=404,
            content=error.model_dump(exclude_none=True),
        )


@router.put(
    "/{fuente_id}",
    response_model=FuenteRSS,
    responses={400: {"model": Error}, 404: {"model": Error}},
)
def actualizar_fuente(fuente_id: int, payload: FuenteRSSActualizar, db: Session = Depends(get_db)):
    """Origina en HU-RSS-004 — actualización completa e idempotente."""
    try:
        return actualizar_fuente_service(db, fuente_id, payload)
    except FuenteRSSNotFoundError:
        error = Error(
            codigo="FUENTE_RSS_NO_ENCONTRADA",
            mensaje="La fuente RSS indicada no existe.",
        )
        return JSONResponse(
            status_code=404,
            content=error.model_dump(exclude_none=True),
        )


@router.patch(
    "/{fuente_id}",
    response_model=FuenteRSS,
    responses={400: {"model": Error}, 404: {"model": Error}},
)
def actualizar_fuente_parcial(
    fuente_id: int, payload: FuenteRSSActualizarParcial, db: Session = Depends(get_db)
):
    """Origina en HU-RSS-004 — actualización parcial (solo campos presentes)."""
    try:
        return actualizar_fuente_service(db, fuente_id, payload)
    except FuenteRSSNotFoundError:
        error = Error(
            codigo="FUENTE_RSS_NO_ENCONTRADA",
            mensaje="La fuente RSS indicada no existe.",
        )
        return JSONResponse(
            status_code=404,
            content=error.model_dump(exclude_none=True),
        )


@router.delete(
    "/{fuente_id}",
    status_code=204,
    responses={404: {"model": Error}},
)
def eliminar_fuente(fuente_id: int, db: Session = Depends(get_db)):
    """
    Origina en HU-RSS-005.

    Nota de diseño abierta (ver HU-RSS-005 y ADR-002, sección Consecuencias):
    política de eliminación en cascada de noticias asociadas vs. desasociación
    (soft delete) — pendiente de decisión del equipo antes de implementar.
    """
    try:
        eliminar_fuente_service(db, fuente_id)
        return Response(status_code=204)
    except FuenteRSSNotFoundError:
        error = Error(
            codigo="FUENTE_RSS_NO_ENCONTRADA",
            mensaje="La fuente RSS indicada no existe.",
        )
        return JSONResponse(
            status_code=404,
            content=error.model_dump(exclude_none=True),
        )
