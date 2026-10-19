"""
Esquemas de la consulta de sentimiento agregado.

Origina en: HU-SENT-004. Coherente con contrato-sentimiento-diccionario.openapi.yaml,
componentes SentimientoAgregado y SentimientoPorFecha.
"""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class SentimientoPorFecha(BaseModel):
    fecha: date
    humor_promedio: Optional[float]
    cantidad_noticias_evaluadas: int


class SentimientoAgregado(BaseModel):
    continente: Optional[str] = None
    pais: Optional[str] = None
    desde: Optional[date] = None
    hasta: Optional[date] = None
    humor_promedio: Optional[float]
    cantidad_noticias_evaluadas: int
    serie_temporal: Optional[List[SentimientoPorFecha]] = None
