"""
Esquemas Pydantic para CanalNoticias.

Origina en: HU-RSS-001.
Coherente 1:1 con `contrato-canales-fuentes-rss.openapi.yaml`,
componentes `CanalNoticias` / `CanalNoticiasCrear`.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CanalNoticiasCrear(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150)
    continente: str = Field(..., min_length=1, max_length=50)
    pais: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)


class CanalNoticias(BaseModel):
    id: int
    nombre: str
    continente: str
    pais: Optional[str] = None
    descripcion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
