"""
Consultas agregadas para los dashboards.

Origina en: HU-DASH-001-v3 (mapa mundial de humor).
Contrato: contrato-dashboards.openapi.yaml, GET /dashboards/map.
"""
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.canal import CanalNoticias
from app.models.fuente import FuenteRSS
from app.models.noticia import Noticia


def fecha_referencia():
    """Día de la noticia: su fecha de publicación o, si el feed no la trae, la de captura.

    Misma regla propuesta para HU-DASH-002 (COALESCE(fecha_publicacion,
    fecha_registro)). Fechas en UTC.
    """
    return func.date(func.coalesce(Noticia.fecha_publicacion, Noticia.fecha_registro))


class DashboardRepository:
    def rango_fechas_con_datos(self, db: Session) -> tuple[object, object]:
        """Primer y último día con al menos 1 noticia con humor."""
        dia = fecha_referencia()
        return db.execute(
            select(func.min(dia), func.max(dia)).where(Noticia.valor_humor.is_not(None))
        ).one()

    def humor_por_continente(self, db: Session, dia: date) -> list[tuple[str, float, int]]:
        """(continente, promedio de valor_humor, cantidad) de las noticias del día."""
        filas = db.execute(
            select(
                CanalNoticias.continente,
                func.avg(Noticia.valor_humor),
                func.count(Noticia.id),
            )
            .join(FuenteRSS, Noticia.fuente_rss_id == FuenteRSS.id)
            .join(CanalNoticias, FuenteRSS.canal_id == CanalNoticias.id)
            .where(Noticia.valor_humor.is_not(None))
            .where(fecha_referencia() == dia.isoformat())
            .group_by(CanalNoticias.continente)
        ).all()
        return [(continente, float(promedio), int(cantidad)) for continente, promedio, cantidad in filas]
