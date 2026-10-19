"""
Esquemas de lectura de noticias.

Origina en: HU-DASH-002-v2. Coherente con contrato-noticias.openapi.yaml,
componentes NoticiaResumen, NoticiaDetalle y NoticiaListado.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class OrdenNoticias(str, Enum):
    FECHA = "fecha"
    INFLUENCIA = "influencia"


class SignoHumor(str, Enum):
    TODAS = "todas"
    POSITIVAS = "positivas"
    NEGATIVAS = "negativas"


class NoticiaResumen(BaseModel):
    id: int
    titulo: str
    enlace_original: str
    canal: str
    continente: str
    pais: Optional[str] = None
    categoria_iptc: Optional[str] = None
    fecha_publicacion: Optional[datetime] = None
    fecha_registro: datetime
    valor_humor: Optional[float] = None
    metodo_calculo: Optional[str] = None


class NoticiaDetalle(NoticiaResumen):
    contenido: Optional[str] = None
    cantidad_terminos_evaluados: Optional[int] = None


class NoticiaListado(BaseModel):
    items: List[NoticiaResumen]
    pagina: int
    tamanio_pagina: int
    total: int
