"""
Caso de uso: datos del mapa mundial de humor.

Origina en: HU-DASH-001-v3 (mapa) y HU-DASH-003-v2 (nube de palabras). Contrato: contrato-dashboards.openapi.yaml,
GET /dashboards/map. Los agregados siguen la definición de HU-SENT-004:
promedio de valor_humor de las noticias con valor_humor no nulo.
El frontend no calcula humor (ADR-005, Decisión, punto 9).
"""
from datetime import date

from sqlalchemy.orm import Session

from app.repositories.dashboards import DashboardRepository, NubePalabrasRepository
from app.schemas.dashboard import (
    Continente,
    HumorAgregado,
    HumorContinente,
    MapaHumor,
    NubePalabras,
    PalabraInfluyente,
)
from app.services.agregados_comun import DECIMALES, a_fecha, clave_continente

# "America", "AMÉRICA" o "américa" cuentan como América (mismo criterio que el
# filtro de HU-RSS-003-v2 y HU-RSS-010).
_CONTINENTE_POR_CLAVE = {clave_continente(c.value): c for c in Continente}


def _agregado(suma: float, cantidad: int) -> HumorAgregado:
    promedio = round(suma / cantidad, DECIMALES) if cantidad else None
    return HumorAgregado(humor_promedio=promedio, cantidad_noticias_evaluadas=cantidad)


def obtener_mapa(
    db: Session,
    fecha: date | None = None,
    repository: DashboardRepository | None = None,
) -> MapaHumor:
    repositorio = repository or DashboardRepository()
    minima, maxima = (a_fecha(v) for v in repositorio.rango_fechas_con_datos(db))
    dia = fecha or maxima

    sumas = {c: 0.0 for c in Continente}
    cantidades = {c: 0 for c in Continente}
    suma_global, cantidad_global = 0.0, 0
    if dia is not None:
        for nombre, promedio, cantidad in repositorio.humor_por_continente(db, dia):
            suma_global += promedio * cantidad
            cantidad_global += cantidad
            continente = _CONTINENTE_POR_CLAVE.get(clave_continente(nombre))
            if continente is not None:
                sumas[continente] += promedio * cantidad
                cantidades[continente] += cantidad

    return MapaHumor(
        fecha=dia,
        fecha_minima_con_datos=minima,
        fecha_maxima_con_datos=maxima,
        global_=_agregado(suma_global, cantidad_global),
        continentes=[
            HumorContinente(continente=c, **_agregado(sumas[c], cantidades[c]).model_dump())
            for c in Continente
        ],
    )


# Cantidad de palabras de la nube: decisión de equipo del 2026-10-19.
LIMITE_NUBE_POR_DEFECTO = 50
LIMITE_NUBE_MAXIMO = 100


def obtener_nube(
    db: Session,
    continente: Continente | None = None,
    pais: str | None = None,
    limite: int = LIMITE_NUBE_POR_DEFECTO,
    repository: NubePalabrasRepository | None = None,
) -> NubePalabras:
    """HU-DASH-003-v2: palabras del diccionario con más noticias coincidentes.

    Mezcla ambos idiomas: cada término (palabra + idioma) es una entrada.
    """
    repositorio = repository or NubePalabrasRepository()
    pais = (pais or "").strip() or None

    continentes = None
    if continente is not None:
        buscado = clave_continente(continente.value)
        continentes = [
            c for c in repositorio.continentes_registrados(db) if clave_continente(c) == buscado
        ]

    filas = []
    if continentes != []:
        filas = repositorio.palabras_influyentes(db, continentes, pais, limite)

    return NubePalabras(
        continente=continente,
        pais=pais,
        items=[
            PalabraInfluyente(termino_id=i, palabra=p, idioma=idi, valor=v, peso=w)
            for i, p, idi, v, w in filas
        ],
    )
