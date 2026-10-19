"""
Consultas de humor agregado.

Origina en: HU-SENT-004 (consulta global, por continente, por país y timeline).
Contrato: contrato-sentimiento-diccionario.openapi.yaml, GET /sentiment.
"""
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.canal import CanalNoticias
from app.models.fuente import FuenteRSS
from app.models.noticia import Noticia
from app.repositories.dashboards import fecha_referencia


class SentimientoRepository:
    def continentes_registrados(self, db: Session) -> list[str]:
        return list(db.execute(select(CanalNoticias.continente).distinct()).scalars().all())

    def humor_por_dia(
        self,
        db: Session,
        continentes: list[str] | None = None,
        pais: str | None = None,
        desde: date | None = None,
        hasta: date | None = None,
    ) -> list[tuple[object, float, int]]:
        """(día, promedio de valor_humor, cantidad) de las noticias que cumplen el filtro."""
        dia = fecha_referencia()
        consulta = (
            select(dia, func.avg(Noticia.valor_humor), func.count(Noticia.id))
            .join(FuenteRSS, Noticia.fuente_rss_id == FuenteRSS.id)
            .join(CanalNoticias, FuenteRSS.canal_id == CanalNoticias.id)
            .where(Noticia.valor_humor.is_not(None))
            .group_by(dia)
            .order_by(dia)
        )
        if continentes is not None:
            consulta = consulta.where(CanalNoticias.continente.in_(continentes))
        if pais is not None:
            consulta = consulta.where(func.lower(CanalNoticias.pais) == pais.lower())
        if desde is not None:
            consulta = consulta.where(dia >= desde.isoformat())
        if hasta is not None:
            consulta = consulta.where(dia <= hasta.isoformat())
        return [(d, float(p), int(c)) for d, p, c in db.execute(consulta).all()]
