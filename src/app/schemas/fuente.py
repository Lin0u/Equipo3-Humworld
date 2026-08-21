"""
Esquemas Pydantic para FuenteRSS.

Origina en: HU-RSS-002 (alta), HU-RSS-003 (consulta/filtrado), HU-RSS-004
(actualización PUT/PATCH), HU-RSS-005 (eliminación).
Coherente 1:1 con `contrato-canales-fuentes-rss.openapi.yaml`.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.fuente import EstadoCircuitBreaker


class FuenteRSSCrear(BaseModel):
    canal_id: int
    url: HttpUrl
    categoria_iptc: str = Field(..., min_length=1, max_length=100)


class FuenteRSSActualizar(BaseModel):
    """PUT — actualización completa/idempotente (HU-RSS-004)."""

    canal_id: int
    url: HttpUrl
    categoria_iptc: str = Field(..., min_length=1, max_length=100)
    activo: bool


class FuenteRSSActualizarParcial(BaseModel):
    """PATCH — todos los campos opcionales; se aplican solo los presentes (HU-RSS-004)."""

    canal_id: Optional[int] = None
    url: Optional[HttpUrl] = None
    categoria_iptc: Optional[str] = Field(default=None, min_length=1, max_length=100)
    activo: Optional[bool] = None


class FuenteRSS(BaseModel):
    id: int
    canal_id: int
    url: HttpUrl
    categoria_iptc: str
    activo: bool
    fecha_ultima_captura_exitosa: Optional[datetime] = None
    estado_circuit_breaker: EstadoCircuitBreaker

    model_config = ConfigDict(from_attributes=True)
