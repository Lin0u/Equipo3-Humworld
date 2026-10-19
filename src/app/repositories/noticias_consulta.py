"""
Consultas de lectura de noticias para el listado y el detalle.

Origina en: HU-DASH-002-v2 (listado de noticias más influyentes).
Contrato: contrato-noticias.openapi.yaml, GET /news y GET /news/{id}.
"""
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.canal import CanalNoticias
from app.models.fuente import FuenteRSS
from app.models.noticia import Noticia
from app.repositories.dashboards import fecha_referencia

_COLUMNAS = (
    Noticia,
    CanalNoticias.nombre,
    CanalNoticias.continente,
    CanalNoticias.pais,
)


class NoticiaConsultaRepository:
    def continentes_registrados(self, db: Session) -> list[str]:
        return list(db.execute(select(CanalNoticias.continente).distinct()).scalars().all())

    def _base(self):
        return (
            select(*_COLUMNAS)
            .join(FuenteRSS, Noticia.fuente_rss_id == FuenteRSS.id)
            .join(CanalNoticias, FuenteRSS.canal_id == CanalNoticias.id)
        )

    def listar(
        self,
        db: Session,
        orden: str,
        signo: str,
        continentes: list[str] | None,
        pais: str | None,
        dia: date | None,
        pagina: int,
        tamanio_pagina: int,
    ) -> tuple[list[tuple], int]:
        filtros = [Noticia.valor_humor.is_not(None)]
        if signo == "positivas":
            filtros.append(Noticia.valor_humor > 0)
        elif signo == "negativas":
            filtros.append(Noticia.valor_humor < 0)
        if continentes is not None:
            filtros.append(CanalNoticias.continente.in_(continentes))
        if pais is not None:
            filtros.append(func.lower(CanalNoticias.pais) == pais.lower())
        if dia is not None:
            filtros.append(fecha_referencia() == dia.isoformat())

        referencia = func.coalesce(Noticia.fecha_publicacion, Noticia.fecha_registro)
        if orden == "influencia":
            criterio = (func.abs(Noticia.valor_humor).desc(), referencia.desc(), Noticia.id.desc())
        else:
            criterio = (referencia.desc(), Noticia.id.desc())

        total = db.execute(
            select(func.count(Noticia.id))
            .join(FuenteRSS, Noticia.fuente_rss_id == FuenteRSS.id)
            .join(CanalNoticias, FuenteRSS.canal_id == CanalNoticias.id)
            .where(*filtros)
        ).scalar_one()
        filas = db.execute(
            self._base()
            .where(*filtros)
            .order_by(*criterio)
            .offset((pagina - 1) * tamanio_pagina)
            .limit(tamanio_pagina)
        ).all()
        return [tuple(f) for f in filas], total

    def buscar(self, db: Session, noticia_id: int) -> tuple | None:
        fila = db.execute(self._base().where(Noticia.id == noticia_id)).first()
        return tuple(fila) if fila else None
