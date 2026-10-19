"""
Caso de uso: consulta del humor agregado (global, continente, país, timeline).

Origina en: HU-SENT-004. Contrato: contrato-sentimiento-diccionario.openapi.yaml,
GET /sentiment. Mismas definiciones que GET /dashboards/map (HU-DASH-001-v3):
- Agregado = promedio de valor_humor de las noticias con valor_humor no nulo.
- Día de una noticia = COALESCE(fecha_publicacion, fecha_registro), en UTC.
- El continente se compara sin distinguir mayúsculas ni tildes.
"""
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.exceptions import RangoFechasInvalidoError
from app.repositories.sentimiento import SentimientoRepository
from app.schemas.sentimiento import SentimientoAgregado, SentimientoPorFecha
from app.services.agregados_comun import DECIMALES, a_fecha, clave_continente

# Tope de días de la serie temporal, para que una consulta no genere una
# respuesta desmedida. Valor propuesto, a ratificar por el equipo.
MAXIMO_DIAS_SERIE = 366


def consultar_sentimiento(
    db: Session,
    continente: str | None = None,
    pais: str | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    repository: SentimientoRepository | None = None,
) -> SentimientoAgregado:
    if desde and hasta and desde > hasta:
        raise RangoFechasInvalidoError("'desde' no puede ser posterior a 'hasta'.")
    if desde and hasta and (hasta - desde).days + 1 > MAXIMO_DIAS_SERIE:
        raise RangoFechasInvalidoError(f"El rango no puede superar {MAXIMO_DIAS_SERIE} días.")

    repositorio = repository or SentimientoRepository()
    continente = (continente or "").strip() or None
    pais = (pais or "").strip() or None

    continentes = None
    if continente is not None:
        buscado = clave_continente(continente)
        continentes = [c for c in repositorio.continentes_registrados(db) if clave_continente(c) == buscado]

    filas = []
    if continentes != []:
        filas = repositorio.humor_por_dia(db, continentes, pais, desde, hasta)

    por_dia = {a_fecha(d): (p, c) for d, p, c in filas}
    cantidad = sum(c for _, c in por_dia.values())
    suma = sum(p * c for p, c in por_dia.values())

    serie = None
    if desde and hasta:
        serie = []
        dia = desde
        while dia <= hasta:
            promedio, n = por_dia.get(dia, (None, 0))
            serie.append(
                SentimientoPorFecha(
                    fecha=dia,
                    humor_promedio=round(promedio, DECIMALES) if promedio is not None else None,
                    cantidad_noticias_evaluadas=n,
                )
            )
            dia += timedelta(days=1)

    return SentimientoAgregado(
        continente=continente,
        pais=pais,
        desde=desde,
        hasta=hasta,
        humor_promedio=round(suma / cantidad, DECIMALES) if cantidad else None,
        cantidad_noticias_evaluadas=cantidad,
        serie_temporal=serie,
    )
