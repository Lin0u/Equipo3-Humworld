"""
Modelo ORM: CoincidenciaTermino (tabla noticia_termino).

Origina en: HU-SENT-008 (persistencia de coincidencias término–noticia), que
alimenta la nube de palabras (HU-DASH-003-v2, GET /dashboards/word-cloud).

- Una fila por término único del diccionario que aparece en una noticia
  (clave primaria compuesta): nunca por cantidad de apariciones (HU-SENT-007-v2).
- Composición con Noticia: al eliminarse la noticia (purgado) se eliminan sus
  coincidencias.
- Al eliminarse un término se eliminan sus coincidencias en cascada (decisión
  de equipo del 2026-10-19, punto pendiente 3 de HU-SENT-008).
"""
from sqlalchemy import Column, ForeignKey, Integer

from app.database import Base


class CoincidenciaTermino(Base):
    __tablename__ = "noticia_termino"

    noticia_id = Column(
        Integer, ForeignKey("noticias.id", ondelete="CASCADE"), primary_key=True
    )
    termino_id = Column(
        Integer,
        ForeignKey("terminos_diccionario.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
