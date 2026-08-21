"""
Modelo ORM: CanalNoticias.

Origina en: HU-RSS-001 (alta de canal de noticias).
Decisión de arquitectura: ADR-002, sección 1 — Modelo de datos y relaciones UML.

Relación de COMPOSICIÓN con FuenteRSS (rombo relleno, entidad "todo"):
una FuenteRSS no tiene sentido de existir sin su CanalNoticias contenedor
(instrucciones del proyecto, sección 8; PDF, sección 4.2.1).
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class CanalNoticias(Base):
    __tablename__ = "canales_noticias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False, unique=True, index=True)
    continente = Column(String(50), nullable=False, index=True)
    pais = Column(String(100), nullable=True)
    descripcion = Column(String(500), nullable=True)

    # Composición: al eliminar el canal, SQLAlchemy propaga el borrado a sus
    # fuentes vía cascade. La política exacta de eliminación (cascada vs.
    # bloqueo si tiene fuentes activas) queda como TODO(equipo) — ver ADR-002,
    # sección "Consecuencias", y HU-RSS-005, nota de diseño.
    fuentes = relationship(
        "FuenteRSS",
        back_populates="canal",
        cascade="all, delete-orphan",  # TODO(equipo): confirmar política de borrado
    )
