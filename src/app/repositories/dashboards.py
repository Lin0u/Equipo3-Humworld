"""
Consultas agregadas para los dashboards.

Origina en: HU-DASH-001-v3 (mapa) y HU-DASH-003-v2 (nube de palabras).
Contrato: contrato-dashboards.openapi.yaml.
"""
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.canal import CanalNoticias
from app.models.coincidencia_termino import CoincidenciaTermino
from app.models.fuente import FuenteRSS
from app.models.noticia import Noticia
from app.models.termino_diccionario import TerminoDiccionario


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


class NubePalabrasRepository:
    """Consulta de HU-DASH-003-v2 sobre las coincidencias de HU-SENT-008."""

    def continentes_registrados(self, db: Session) -> list[str]:
        return list(db.execute(select(CanalNoticias.continente).distinct()).scalars().all())

    def palabras_influyentes(
        self,
        db: Session,
        continentes: list[str] | None,
        pais: str | None,
        limite: int,
    ) -> list[tuple[int, str, str, int, int]]:
        """(termino_id, palabra, idioma, valor, peso), peso descendente.

        peso = cantidad de noticias del filtro que contienen el término.
        """
        peso = func.count(func.distinct(CoincidenciaTermino.noticia_id))
        consulta = (
            select(
                TerminoDiccionario.id,
                TerminoDiccionario.palabra,
                TerminoDiccionario.idioma,
                TerminoDiccionario.valor,
                peso,
            )
            .join(CoincidenciaTermino, CoincidenciaTermino.termino_id == TerminoDiccionario.id)
            .join(Noticia, Noticia.id == CoincidenciaTermino.noticia_id)
            .join(FuenteRSS, Noticia.fuente_rss_id == FuenteRSS.id)
            .join(CanalNoticias, FuenteRSS.canal_id == CanalNoticias.id)
            .group_by(
                TerminoDiccionario.id,
                TerminoDiccionario.palabra,
                TerminoDiccionario.idioma,
                TerminoDiccionario.valor,
            )
            .order_by(peso.desc(), TerminoDiccionario.palabra, TerminoDiccionario.id)
            .limit(limite)
        )
        if continentes is not None:
            consulta = consulta.where(CanalNoticias.continente.in_(continentes))
        if pais is not None:
            consulta = consulta.where(func.lower(CanalNoticias.pais) == pais.lower())
        return [tuple(fila) for fila in db.execute(consulta).all()]
