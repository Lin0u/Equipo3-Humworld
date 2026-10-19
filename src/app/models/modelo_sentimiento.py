"""
Modelo ORM: ModeloSentimiento (tabla modelos_sentimiento).

Origina en: HU-SENT-006 (entrenamiento y versionado del modelo de ML) y
ADR-04, punto 5 (esquema de versionado). Solo guarda metadatos y la ruta del
regresor serializado (.joblib); el archivo vive en disco o en un volumen Docker.

Agregación con Noticia (rombo vacío, diagrama-clases-sentimiento.md): una
noticia calculada con ML referencia la versión usada, pero ambas tienen ciclos
de vida independientes.
"""
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from app.database import Base


class ModeloSentimiento(Base):
    __tablename__ = "modelos_sentimiento"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), nullable=False, unique=True)
    ruta_archivo = Column(String(500), nullable=False)
    # Crítico para detectar incompatibilidad si Google cambia su modelo (ADR-04).
    modelo_embeddings_usado = Column(String(100), nullable=False)
    mae_evaluacion = Column(Float, nullable=False)
    fecha_entrenamiento = Column(DateTime, nullable=False)
    activo = Column(Boolean, nullable=False, default=False, index=True)
