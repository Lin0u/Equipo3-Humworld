"""
Router: /api/v1/sources/{id}/captures y /api/v1/captures

Origina en: HU-RSS-008 (actualización manual de captura, una o varias fuentes).
ADR relacionado: ADR-002, sección 2 (mecanismo de captura) y sección 3
(patrones de resiliencia: Timeout, Retry acotado, Circuit Breaker).
Contrato: contrato-canales-fuentes-rss.openapi.yaml, paths /sources/{id}/captures, /captures.

TODO(equipo): delega en app/services/captura_service.py (compartido con el
cron automático de HU-RSS-006, ver ADR-002 sección 2 — "la actualización
manual reutiliza exactamente el mismo procedimiento que el cron").
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.captura import ResultadoCaptura, SolicitudCapturaMultiple

router = APIRouter(tags=["captures"])


@router.post("/sources/{fuente_id}/captures", response_model=ResultadoCaptura, status_code=201)
def disparar_captura_fuente(fuente_id: int, db: Session = Depends(get_db)):
    """
    Origina en HU-RSS-008 — captura manual de una única fuente.

    Criterios de aceptación (ver HU-RSS-008):
    - 201/202 según procesamiento síncrono/asíncrono (a definir por el equipo).
    - 404 si la fuente no existe.
    - 409 si la fuente está inactiva ("activo"=falso).
    """
    # TODO(equipo): delegar en captura_service.ejecutar_captura(fuente_id)
    raise NotImplementedError("HU-RSS-008: captura manual (fuente única) pendiente de implementación")


@router.post("/captures", response_model=list[ResultadoCaptura], status_code=201)
def disparar_captura_multiple(payload: SolicitudCapturaMultiple, db: Session = Depends(get_db)):
    """
    Origina en HU-RSS-008 — captura manual de un conjunto de fuentes.

    Criterio de aceptación: el fallo de una fuente del conjunto no impide el
    procesamiento del resto (ver ADR-002, sección 3 — Circuit Breaker por fuente).
    """
    # TODO(equipo): delegar en captura_service.ejecutar_captura_multiple(fuente_ids)
    raise NotImplementedError("HU-RSS-008: captura manual (conjunto) pendiente de implementación")
