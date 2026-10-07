"""
Esquemas Pydantic para CanalNoticias.

Origina en: HU-RSS-001.
Coherente 1:1 con `contrato-canales-fuentes-rss.openapi.yaml`,
componentes `CanalNoticias` / `CanalNoticiasCrear`.
"""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CanalNoticiasCrear(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150)
    continente: str = Field(..., min_length=1, max_length=50)
    pais: Optional[str] = Field(default=None, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)

    @field_validator("nombre", "continente", "pais", "descripcion", mode="before")
    @classmethod
    def recortar_texto(cls, valor):
        if isinstance(valor, str):
            return valor.strip()
        return valor


class CanalNoticias(BaseModel):
    id: int
    nombre: str
    continente: str
    pais: Optional[str] = None
    descripcion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CanalNoticiasListado(BaseModel):
    items: List[CanalNoticias]
    pagina: int
    tamanio_pagina: int
    total: int
