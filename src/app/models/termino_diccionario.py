"""Modelo ORM para los términos del diccionario de sentimiento."""

from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.dialects.mysql import VARCHAR

from app.database import Base


class TerminoDiccionario(Base):
    __tablename__ = "terminos_diccionario"
    __table_args__ = (
        UniqueConstraint(
            "palabra",
            "idioma",
            name="uq_termino_diccionario_palabra_idioma",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    palabra = Column(
        String(255).with_variant(VARCHAR(255, collation="utf8mb4_bin"), "mysql"),
        nullable=False,
    )
    idioma = Column(String(2), nullable=False)
    valor = Column(Integer, nullable=False)