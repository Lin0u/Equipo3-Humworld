"""
Router: /api/v1/sources

Origina en: HU-RSS-002 (alta), HU-RSS-003 (consulta/filtrado),
HU-RSS-004 (modificación PUT/PATCH), HU-RSS-005 (eliminación).
ADR relacionado: ADR-002.
Contrato: contrato-canales-fuentes-rss.openapi.yaml, paths /sources, /sources/{id}.

TODO(equipo): sin lógica de negocio implementada — ver TODOs por endpoint.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.fuente import (
    FuenteRSS,
    FuenteRSSActualizar,
    FuenteRSSActualizarParcial,
    FuenteRSSCrear,
)

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=List[FuenteRSS])
def listar_fuentes(
    canal_id: Optional[int] = Query(default=None, description="Filtra por canal propietario."),
    continente: Optional[str] = Query(default=None, description="Filtra por continente del canal."),
    categoria_iptc: Optional[str] = Query(default=None, description="Filtra por categoría IPTC (nivel 1)."),
    activo: Optional[bool] = Query(default=None, description="Filtra por estado activo/inactivo."),
    db: Session = Depends(get_db),
):
    """Origina en HU-RSS-003 (consulta y filtrado de fuentes RSS)."""
    # TODO(equipo): implementar consulta real con filtros combinables
    raise NotImplementedError("HU-RSS-003: listado de fuentes pendiente de implementación")


@router.post("", response_model=FuenteRSS, status_code=201)
def crear_fuente(payload: FuenteRSSCrear, db: Session = Depends(get_db)):
    """
    Origina en HU-RSS-002.

    Criterios de aceptación (ver HU-RSS-002):
    - 201 si el canal existe y los datos son válidos; "activo" se inicializa
      en verdadero.
    - 404 si "canal_id" no corresponde a ningún canal registrado.
    """
    # TODO(equipo): verificar existencia de canal_id (404 si no existe) + persistir
    raise NotImplementedError("HU-RSS-002: alta de fuente pendiente de implementación")


@router.get("/{fuente_id}", response_model=FuenteRSS)
def obtener_fuente(fuente_id: int, db: Session = Depends(get_db)):
    """Origina en HU-RSS-003 (consulta de detalle)."""
    # TODO(equipo): implementar consulta real; 404 si no existe
    raise NotImplementedError("HU-RSS-003: detalle de fuente pendiente de implementación")


@router.put("/{fuente_id}", response_model=FuenteRSS)
def actualizar_fuente(fuente_id: int, payload: FuenteRSSActualizar, db: Session = Depends(get_db)):
    """Origina en HU-RSS-004 — actualización completa e idempotente."""
    # TODO(equipo): implementar reemplazo completo; 404 si no existe
    raise NotImplementedError("HU-RSS-004: actualización (PUT) pendiente de implementación")


@router.patch("/{fuente_id}", response_model=FuenteRSS)
def actualizar_fuente_parcial(
    fuente_id: int, payload: FuenteRSSActualizarParcial, db: Session = Depends(get_db)
):
    """Origina en HU-RSS-004 — actualización parcial (solo campos presentes)."""
    # TODO(equipo): aplicar solo los campos no-None del payload; 404 si no existe
    raise NotImplementedError("HU-RSS-004: actualización (PATCH) pendiente de implementación")


@router.delete("/{fuente_id}", status_code=204)
def eliminar_fuente(fuente_id: int, db: Session = Depends(get_db)):
    """
    Origina en HU-RSS-005.

    Nota de diseño abierta (ver HU-RSS-005 y ADR-002, sección Consecuencias):
    política de eliminación en cascada de noticias asociadas vs. desasociación
    (soft delete) — pendiente de decisión del equipo antes de implementar.
    """
    # TODO(equipo): implementar eliminación real; 404 si no existe
    raise NotImplementedError("HU-RSS-005: eliminación pendiente de implementación")
