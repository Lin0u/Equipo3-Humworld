"""
Modelo ORM: Noticia.

Origina en: HU-RSS-006 (cron de captura) y HU-RSS-008 (captura manual).
Decisión de arquitectura: ADR-002, sección 1.

Relación de AGREGACIÓN con FuenteRSS (rombo vacío): una Noticia, una vez
capturada, mantiene valor analítico propio y su eliminación no debería
depender necesariamente del ciclo de vida de la fuente (ver ADR-002,
sección "Consecuencias" — punto abierto a validar por el equipo).

Nota de alcance: el campo `valor_humor` es poblado por el módulo de Análisis
de Sentimiento (EPIC-SENT, fuera de alcance de este scaffold de Sprint 1).
"""
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Noticia(Base):
    __tablename__ = "noticias"

    id = Column(Integer, primary_key=True, index=True)
    fuente_rss_id = Column(Integer, ForeignKey("fuentes_rss.id"), nullable=False, index=True)

    # Identificador único del ítem RSS (guid o hash de enlace+título), usado
    # para deduplicación — ver ADR-002 y HU-RSS-006, escenario "Noticia duplicada".
    identificador_item_rss = Column(String(255), nullable=False, unique=True, index=True)

    titulo = Column(String(500), nullable=False)
    contenido = Column(Text, nullable=True)
    enlace_original = Column(String(500), nullable=False)
    fecha_publicacion = Column(DateTime, nullable=True)  # fecha del propio feed
    fecha_registro = Column(DateTime, nullable=False)  # timestamp de captura (PDF §4.2.4)
    idioma_detectado = Column(String(10), nullable=True)
    categoria_iptc = Column(String(100), nullable=True)

    # Fuera de alcance de Sprint 1 / EPIC-RSS — poblado por EPIC-SENT.
    valor_humor = Column(Float, nullable=True)

    fuente = relationship("FuenteRSS", back_populates="noticias")
