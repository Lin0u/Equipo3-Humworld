"""
Esquemas Pydantic para FuenteRSS.

Origina en: HU-RSS-002 (alta), HU-RSS-003 (consulta/filtrado), HU-RSS-004
(actualización PUT/PATCH), HU-RSS-005 (eliminación).
Coherente 1:1 con `contrato-canales-fuentes-rss.openapi.yaml`.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

from app.models.fuente import EstadoCircuitBreaker


IPTC_MEDIA_TOPICS_NIVEL_1 = frozenset(
    {
        "01000000",
        "02000000",
        "03000000",
        "04000000",
        "05000000",
        "06000000",
        "07000000",
        "08000000",
        "09000000",
        "10000000",
        "11000000",
        "12000000",
        "13000000",
        "14000000",
        "15000000",
        "16000000",
        "17000000",
    }
)


class FuenteRSSCrear(BaseModel):
    canal_id: int
    url: HttpUrl
    categoria_iptc: str = Field(..., min_length=1, max_length=100)

    @field_validator("url", "categoria_iptc", mode="before")
    @classmethod
    def recortar_texto(cls, valor):
        if isinstance(valor, str):
            return valor.strip()
        return valor

    @field_validator("categoria_iptc")
    @classmethod
    def validar_categoria_iptc(cls, valor: str) -> str:
        if valor not in IPTC_MEDIA_TOPICS_NIVEL_1:
            raise ValueError("categoria_iptc no pertenece a IPTC Media Topics 1.4")
        return valor


class FuenteRSSActualizar(BaseModel):
    """PUT — actualización completa/idempotente (HU-RSS-004)."""

    url: HttpUrl
    categoria_iptc: str = Field(..., min_length=1, max_length=100)
    activo: bool

    model_config = ConfigDict(extra="forbid")

    @field_validator("url", "categoria_iptc", mode="before")
    @classmethod
    def recortar_texto(cls, valor):
        if isinstance(valor, str):
            return valor.strip()
        return valor

    @field_validator("categoria_iptc")
    @classmethod
    def validar_categoria_iptc(cls, valor: str) -> str:
        if valor not in IPTC_MEDIA_TOPICS_NIVEL_1:
            raise ValueError("categoria_iptc no pertenece a IPTC Media Topics 1.4")
        return valor


class FuenteRSSActualizarParcial(BaseModel):
    """PATCH — todos los campos opcionales; se aplican solo los presentes (HU-RSS-004)."""

    url: Optional[HttpUrl] = None
    categoria_iptc: Optional[str] = Field(default=None, min_length=1, max_length=100)
    activo: Optional[bool] = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("url", "categoria_iptc", mode="before")
    @classmethod
    def recortar_texto(cls, valor):
        if isinstance(valor, str):
            return valor.strip()
        return valor

    @field_validator("categoria_iptc")
    @classmethod
    def validar_categoria_iptc(cls, valor: str) -> str:
        if valor not in IPTC_MEDIA_TOPICS_NIVEL_1:
            raise ValueError("categoria_iptc no pertenece a IPTC Media Topics 1.4")
        return valor

    @model_validator(mode="after")
    def validar_campos_presentes(self):
        if not self.model_fields_set:
            raise ValueError("PATCH debe incluir al menos un campo modificable")
        if any(getattr(self, campo) is None for campo in self.model_fields_set):
            raise ValueError("Los campos de PATCH no pueden ser nulos")
        return self


class FuenteRSS(BaseModel):
    id: int
    canal_id: int
    url: HttpUrl
    categoria_iptc: str
    activo: bool
    fecha_ultima_captura_exitosa: Optional[datetime] = None
    estado_circuit_breaker: EstadoCircuitBreaker

    model_config = ConfigDict(from_attributes=True)


class FuenteRSSListado(BaseModel):
    items: List[FuenteRSS]
    pagina: int
    tamanio_pagina: int
    total: int
