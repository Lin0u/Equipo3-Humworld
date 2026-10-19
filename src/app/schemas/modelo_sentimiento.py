"""Esquema de lectura de una versión del modelo de ML.

Origina en: HU-SENT-006. Coherente con contrato-sentimiento-diccionario.openapi.yaml,
componente ModeloSentimiento (ruta_archivo no se expone).
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ModeloSentimientoLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version: str
    modelo_embeddings_usado: str
    mae_evaluacion: float
    fecha_entrenamiento: datetime
    activo: bool
