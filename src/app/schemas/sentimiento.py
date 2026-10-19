"""
Esquemas de la consulta de sentimiento agregado.

Origina en: HU-SENT-004. Coherente con contrato-sentimiento-diccionario.openapi.yaml,
componentes SentimientoAgregado y SentimientoPorFecha.
"""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


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


class AnalisisTextoCrear(BaseModel):
    """HU-SENT-005: cuerpo de POST /sentiment."""

    texto: str = Field(min_length=1)

    @field_validator("texto")
    @classmethod
    def no_vacio(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("El texto no puede estar vacío.")
        return valor


class AnalisisTextoResultado(BaseModel):
    valor_humor: Optional[float]
    cantidad_terminos_evaluados: int
    polarizacion_terminos: Optional[float] = None
