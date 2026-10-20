"""
Esquemas del módulo Dashboards.

Origina en: HU-DASH-001-v3. Coherente con contrato-dashboards.openapi.yaml,
componentes Continente, HumorAgregado, HumorContinente y MapaHumor.
"""
from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Continente(str, Enum):
    """Los 5 continentes de HU-RSS-009-v2, con tilde (decisión del 2026-10-18)."""

    AMERICA = "América"
    EUROPA = "Europa"
    ASIA = "Asia"
    AFRICA = "África"
    OCEANIA = "Oceanía"


class HumorAgregado(BaseModel):
    humor_promedio: Optional[float] = Field(
        default=None,
        description="Promedio de valor_humor (escala -10 a +10). Null si no hay noticias evaluadas."
    )
    cantidad_noticias_evaluadas: int


class HumorContinente(HumorAgregado):
    continente: Continente


class MapaHumor(BaseModel):
    fecha: Optional[date] = None
    fecha_minima_con_datos: Optional[date] = None
    fecha_maxima_con_datos: Optional[date] = None
    global_: HumorAgregado = Field(alias="global", serialization_alias="global")
    continentes: List[HumorContinente] = Field(min_length=5, max_length=5)

    model_config = {"populate_by_name": True}


class PalabraInfluyente(BaseModel):
    """Origina en HU-DASH-003-v2: un TerminoDiccionario más su peso."""

    termino_id: int
    palabra: str
    idioma: str
    valor: int = Field(ge=-10, le=10)
    peso: int = Field(ge=1, description="Cantidad de noticias del filtro que contienen el término.")


class NubePalabras(BaseModel):
    continente: Optional[Continente] = None
    pais: Optional[str] = None
    items: List[PalabraInfluyente]
