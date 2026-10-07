from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.canal import CanalNoticias
from app.models.fuente import EstadoCircuitBreaker, FuenteRSS


class FuenteRSSRepository:
    def buscar_canal(self, db: Session, canal_id: int) -> CanalNoticias | None:
        return db.execute(
            select(CanalNoticias).where(CanalNoticias.id == canal_id)
        ).scalar_one_or_none()

    def crear(self, db: Session, fuente: FuenteRSS) -> FuenteRSS:
        db.add(fuente)
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        db.refresh(fuente)
        return fuente

    def listar(
        self,
        db: Session,
        pagina: int,
        tamanio_pagina: int,
        canal_id: int | None = None,
        continente: str | None = None,
        categoria_iptc: str | None = None,
        activo: bool | None = None,
    ) -> tuple[list[FuenteRSS], int]:
        filtros = []
        if canal_id is not None:
            filtros.append(FuenteRSS.canal_id == canal_id)
        if continente is not None:
            filtros.append(func.lower(CanalNoticias.continente) == continente.lower())
        if categoria_iptc is not None:
            filtros.append(func.lower(FuenteRSS.categoria_iptc) == categoria_iptc.lower())
        if activo is not None:
            filtros.append(FuenteRSS.activo == activo)
        else:
            filtros.append(FuenteRSS.activo.is_(True))

        conteo = select(func.count(FuenteRSS.id)).select_from(FuenteRSS)
        consulta = select(FuenteRSS)
        if continente is not None:
            conteo = conteo.join(CanalNoticias, FuenteRSS.canal_id == CanalNoticias.id)
            consulta = consulta.join(CanalNoticias, FuenteRSS.canal_id == CanalNoticias.id)
        if filtros:
            conteo = conteo.where(*filtros)
            consulta = consulta.where(*filtros)

        total = db.execute(conteo).scalar_one()
        fuentes = db.execute(
            consulta.order_by(FuenteRSS.canal_id, FuenteRSS.url)
            .offset((pagina - 1) * tamanio_pagina)
            .limit(tamanio_pagina)
        ).scalars().all()
        return list(fuentes), total

    def buscar_por_id(self, db: Session, fuente_id: int) -> FuenteRSS | None:
        return db.execute(
            select(FuenteRSS).where(FuenteRSS.id == fuente_id)
        ).scalar_one_or_none()

    def buscar_activa(self, db: Session, fuente_id: int) -> FuenteRSS | None:
        return db.execute(
            select(FuenteRSS).where(
                FuenteRSS.id == fuente_id,
                FuenteRSS.activo.is_(True),
            )
        ).scalar_one_or_none()

    def listar_activas(self, db: Session) -> list[FuenteRSS]:
        return list(
            db.execute(
                select(FuenteRSS).where(FuenteRSS.activo.is_(True)).order_by(FuenteRSS.id)
            ).scalars().all()
        )

    def actualizar_estado_captura(
        self,
        db: Session,
        fuente: FuenteRSS,
        fecha_ultima_captura_exitosa: datetime | None,
        estado_circuit_breaker: EstadoCircuitBreaker,
    ) -> FuenteRSS:
        fuente.fecha_ultima_captura_exitosa = fecha_ultima_captura_exitosa
        fuente.estado_circuit_breaker = estado_circuit_breaker
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        db.refresh(fuente)
        return fuente

    def eliminar_logicamente(self, db: Session, fuente: FuenteRSS) -> None:
        fuente.activo = False
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise

    def actualizar(
        self,
        db: Session,
        fuente: FuenteRSS,
        cambios: dict,
    ) -> FuenteRSS:
        for campo, valor in cambios.items():
            setattr(fuente, campo, valor)
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        db.refresh(fuente)
        return fuente