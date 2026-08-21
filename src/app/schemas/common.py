"""
Esquemas comunes. Origina en: contrato-canales-fuentes-rss.openapi.yaml,
componentes `Error`.
"""
from typing import List, Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    codigo: str
    mensaje: str
    detalles: Optional[List[str]] = None
