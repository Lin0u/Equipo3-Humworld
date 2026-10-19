"""
Caso de uso: listado y detalle de noticias.

Origina en: HU-DASH-002-v2 (listado de noticias más influyentes; PDF §4.3.2 y
§10.2 "/news: GET (lista, detalle, filtros, influyentes)").
- Influencia = |valor_humor| (propuesta de Valentín García, ratificada por la PO).
- Solo noticias con valor_humor calculado.
- Día de referencia = COALESCE(fecha_publicacion, fecha_registro), en UTC.
- Desempate estable por id, para que la paginación no repita ni salte noticias.
"""
from datetime import date

from sqlalchemy.orm import Session

from app.exceptions import NoticiaNotFoundError
from app.repositories.noticias_consulta import NoticiaConsultaRepository
from app.schemas.dashboard import Continente
from app.schemas.noticia import (
    NoticiaDetalle,
    NoticiaListado,
    NoticiaResumen,
    OrdenNoticias,
    SignoHumor,
)
from app.services.agregados_comun import clave_continente


def _a_dict(fila: tuple) -> dict:
    noticia, canal, continente, pais = fila
    return {
        "id": noticia.id,
        "titulo": noticia.titulo,
        "enlace_original": noticia.enlace_original,
        "canal": canal,
        "continente": continente,
        "pais": pais,
        "categoria_iptc": noticia.categoria_iptc,
        "fecha_publicacion": noticia.fecha_publicacion,
        "fecha_registro": noticia.fecha_registro,
        "valor_humor": noticia.valor_humor,
        "metodo_calculo": noticia.metodo_calculo,
        "contenido": noticia.contenido,
        "cantidad_terminos_evaluados": noticia.cantidad_terminos_evaluados,
    }


def listar_noticias(
    db: Session,
    orden: OrdenNoticias = OrdenNoticias.FECHA,
    signo: SignoHumor = SignoHumor.TODAS,
    continente: Continente | None = None,
    pais: str | None = None,
    fecha: date | None = None,
    pagina: int = 1,
    tamanio_pagina: int = 10,
    repository: NoticiaConsultaRepository | None = None,
) -> NoticiaListado:
    repositorio = repository or NoticiaConsultaRepository()
    pais = (pais or "").strip() or None

    continentes = None
    if continente is not None:
        buscado = clave_continente(continente.value)
        continentes = [
            c for c in repositorio.continentes_registrados(db) if clave_continente(c) == buscado
        ]

    filas, total = [], 0
    if continentes != []:
        filas, total = repositorio.listar(
            db, orden.value, signo.value, continentes, pais, fecha, pagina, tamanio_pagina
        )

    return NoticiaListado(
        items=[NoticiaResumen(**_a_dict(f)) for f in filas],
        pagina=pagina,
        tamanio_pagina=tamanio_pagina,
        total=total,
    )


def obtener_noticia(
    db: Session, noticia_id: int, repository: NoticiaConsultaRepository | None = None
) -> NoticiaDetalle:
    fila = (repository or NoticiaConsultaRepository()).buscar(db, noticia_id)
    if fila is None:
        raise NoticiaNotFoundError(noticia_id)
    return NoticiaDetalle(**_a_dict(fila))
