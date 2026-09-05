from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import UniqueConstraintViolation
from app.models.canal import CanalNoticias


class CanalNoticiasRepository:
    def buscar_por_nombre(self, db: Session, nombre: str) -> CanalNoticias | None:
        consulta = select(CanalNoticias).where(
            func.lower(CanalNoticias.nombre) == nombre.lower()
        )
        return db.execute(consulta).scalar_one_or_none()

    def crear(self, db: Session, canal: CanalNoticias) -> CanalNoticias:
        db.add(canal)
        try:
            db.commit()
        except IntegrityError as error:
            db.rollback()
            raise UniqueConstraintViolation from error
        db.refresh(canal)
        return canal