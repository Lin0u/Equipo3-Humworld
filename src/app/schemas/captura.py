"""
Esquemas Pydantic para el disparo de capturas manuales.

Origina en: HU-RSS-008.
Coherente 1:1 con `contrato-canales-fuentes-rss.openapi.yaml`, componente
`ResultadoCaptura`.
"""
import enum
from typing import List, Optional

from pydantic import BaseModel, Field


class EstadoResultadoCaptura(str, enum.Enum):
    EXITOSA = "exitosa"
    FALLIDA_TRANSITORIA = "fallida_transitoria"
    FALLIDA_CIRCUITO_ABIERTO = "fallida_circuito_abierto"


class ResultadoCaptura(BaseModel):
    fuente_id: int
    estado: EstadoResultadoCaptura
    noticias_nuevas: int
    mensaje: Optional[str] = None


class SolicitudCapturaMultiple(BaseModel):
    fuente_ids: List[int] = Field(..., min_length=1)
