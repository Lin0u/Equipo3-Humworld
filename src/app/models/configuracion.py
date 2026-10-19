"""Persistencia de la configuración del cron de captura RSS."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Configuracion(Base):
    """Registro de configuración global para la captura automática."""

    __tablename__ = "configuracion"

    clave: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        nullable=False,
    )
    valor: Mapped[int] = mapped_column(Integer, nullable=False)
