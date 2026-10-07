"""Repositorio de configuración del cron de captura RSS."""

from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.configuracion import Configuracion


class ConfiguracionRepository:
    """Opera sobre la configuración global con transacciones atómicas."""

    def obtener(self, db: Session, clave: str) -> Configuracion | None:
        return db.execute(
            select(Configuracion).where(Configuracion.clave == clave)
        ).scalar_one_or_none()

    def insertar(self, db: Session, configuracion: Configuracion) -> Configuracion:
        db.add(configuracion)
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        db.refresh(configuracion)
        return configuracion

    def actualizar(self, db: Session, valor: int) -> Configuracion:
        if valor <= 0:
            raise ValueError("La periodicidad debe ser un entero positivo.")

        configuracion = self.obtener(db, "periodicidad_cron_minutos")
        if configuracion is None:
            configuracion = Configuracion(
                clave="periodicidad_cron_minutos",
                valor=valor,
            )
            return self.insertar(db, configuracion)

        configuracion.valor = valor
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        db.refresh(configuracion)
        return configuracion
