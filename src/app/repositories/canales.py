import unicodedata

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import UniqueConstraintViolation
from app.models.canal import CanalNoticias


def _normalizar(texto: str) -> str:
    """Minúsculas y sin diacríticos, para comparar 'America' con 'América'."""
    descompuesto = unicodedata.normalize("NFKD", texto)
    sin_diacriticos = "".join(c for c in descompuesto if not unicodedata.combining(c))
    return sin_diacriticos.lower()


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

    def listar(
        self,
        db: Session,
        pagina: int,
        tamanio_pagina: int,
        continente: str | None = None,
    ) -> tuple[list[CanalNoticias], int]:
        consulta = select(CanalNoticias)
        conteo = select(func.count(CanalNoticias.id)).select_from(CanalNoticias)

        if continente is not None:
            continente_normalizado = _normalizar(continente)
            valores_registrados = db.execute(
                select(CanalNoticias.continente).distinct()
            ).scalars().all()
            coincidencias = [
                valor
                for valor in valores_registrados
                if _normalizar(valor) == continente_normalizado
            ]
            if not coincidencias:
                return [], 0
            consulta = consulta.where(CanalNoticias.continente.in_(coincidencias))
            conteo = conteo.where(CanalNoticias.continente.in_(coincidencias))

        total = db.execute(conteo).scalar_one()
        canales = db.execute(
            consulta.order_by(func.lower(CanalNoticias.nombre))
            .offset((pagina - 1) * tamanio_pagina)
            .limit(tamanio_pagina)
        ).scalars().all()
        return list(canales), total

    def buscar_por_id(self, db: Session, canal_id: int) -> CanalNoticias | None:
        return db.execute(
            select(CanalNoticias).where(CanalNoticias.id == canal_id)
        ).scalar_one_or_none()