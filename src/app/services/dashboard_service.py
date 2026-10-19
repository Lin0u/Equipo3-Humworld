"""
Caso de uso: datos del mapa mundial de humor.

Origina en: HU-DASH-001-v3. Contrato: contrato-dashboards.openapi.yaml,
GET /dashboards/map. Los agregados siguen la definición de HU-SENT-004:
promedio de valor_humor de las noticias con valor_humor no nulo.
El frontend no calcula humor (ADR-05, Decisión, punto 9).
"""
from datetime import date

from sqlalchemy.orm import Session

from app.repositories.dashboards import DashboardRepository
from app.schemas.dashboard import Continente, HumorAgregado, HumorContinente, MapaHumor
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
