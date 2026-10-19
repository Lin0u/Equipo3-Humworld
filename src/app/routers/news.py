"""
Router: /api/v1/news

Origina en: HU-DASH-002-v2 (listado de noticias más influyentes) y
HU-ADMIN-003 (purgado manual, DELETE).
Contrato: contrato-noticias.openapi.yaml. PDF §10.2: "/news: GET (lista,
detalle, filtros, influyentes), DELETE".
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import FechaPurgadoInvalidaError, NoticiaNotFoundError
from app.schemas.common import Error
from app.schemas.dashboard import Continente
from app.schemas.noticia import (
    NoticiaDetalle,
    NoticiaListado,
    OrdenNoticias,
    ResultadoPurgado,
    SignoHumor,
)
from app.services.noticia_consulta_service import listar_noticias, obtener_noticia
from app.services.purgado_service import purgar_anteriores_a, purgar_por_caducidad

router = APIRouter(prefix="/news", tags=["news"])

# Paginación propuesta por Valentín García (10 por defecto, máximo 50).
TAMANIO_PAGINA_POR_DEFECTO = 10
TAMANIO_PAGINA_MAXIMO = 50


@router.get("", response_model=NoticiaListado, responses={400: {"model": Error}})
def listar(
    orden: OrdenNoticias = Query(
        default=OrdenNoticias.FECHA,
        description="fecha: más recientes primero. influencia: mayor |valor_humor| primero.",
    ),
    signo: SignoHumor = Query(default=SignoHumor.TODAS, description="Filtra por signo del humor."),
    continente: Optional[Continente] = Query(default=None),
    pais: Optional[str] = Query(default=None),
    fecha: Optional[date] = Query(default=None, description="Día de referencia de la noticia."),
    pagina: int = Query(default=1, ge=1),
    tamanio_pagina: int = Query(
        default=TAMANIO_PAGINA_POR_DEFECTO, ge=1, le=TAMANIO_PAGINA_MAXIMO
    ),
    db: Session = Depends(get_db),
):
    """Noticias con humor calculado, paginadas y filtradas."""
    return listar_noticias(db, orden, signo, continente, pais, fecha, pagina, tamanio_pagina)


@router.delete("", response_model=ResultadoPurgado, responses={400: {"model": Error}})
def purgar(
    fecha_anterior_a: Optional[date] = Query(
        default=None,
        description=(
            "Elimina las noticias registradas antes de este día (UTC). "
            "Si se omite, aplica la caducidad configurada en /config."
        ),
    ),
    db: Session = Depends(get_db),
):
    """Purgado manual de noticias antiguas (HU-ADMIN-003)."""
    if fecha_anterior_a is None:
        return purgar_por_caducidad(db)
    try:
        return purgar_anteriores_a(db, fecha_anterior_a)
    except FechaPurgadoInvalidaError:
        cuerpo = Error(
            codigo="FECHA_INVALIDA",
            mensaje="La fecha límite no puede ser posterior a hoy.",
        )
        return JSONResponse(status_code=400, content=cuerpo.model_dump(exclude_none=True))


@router.get("/{noticia_id}", response_model=NoticiaDetalle, responses={404: {"model": Error}})
def detalle(noticia_id: int = Path(ge=1), db: Session = Depends(get_db)):
    try:
        return obtener_noticia(db, noticia_id)
    except NoticiaNotFoundError:
        cuerpo = Error(codigo="NOTICIA_NO_ENCONTRADA", mensaje="La noticia indicada no existe.")
        return JSONResponse(status_code=404, content=cuerpo.model_dump(exclude_none=True))
