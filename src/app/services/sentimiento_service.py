"""
Cálculo de humor de las noticias capturadas.

Origina en:
- HU-SENT-007: método determinista por diccionario. Promedio simple de los
  valores de los términos ÚNICOS coincidentes (ADR-03): Σ(valores) / n.
- HU-SENT-002-v2: cálculo híbrido síncrono tras la captura, con punto de
  extensión ML (ADR-04), timeout explícito, fallback a diccionario y barrido
  de respaldo. OpenSpec: openspec/changes/Cálculo híbrido de humor.

AVISO (instrucciones del proyecto, sección 12): este módulo contiene lógica
de negocio del algoritmo de sentimiento. Debe ser revisado por el equipo
antes de fusionarse.

Alcance de este incremento: el camino efectivo es el diccionario. El camino
ML queda definido como interfaz (ProveedorModeloML) pero no hay proveedor
real hasta que HU-SENT-006 entregue el modelo activo y su versionado.
No calcula polarización (HU-SENT-003). Persiste las coincidencias de HU-SENT-008
junto con el resultado.

Comparación de términos (decisión de equipo del 2026-10-18; HU-SENT-007 no
la fijaba):
- Palabra o frase completa: "guerra" no coincide con "guerrilla".
- Sin distinguir mayúsculas ni tildes: "POLITICA" coincide con "política".
  La ñ se conserva: "pena" no coincide con "peña".
- Sin lematización: singular y plural se cargan como términos distintos en
  el diccionario ("guerra" y "guerras").
- Se quitan las etiquetas HTML del resumen del feed antes de comparar.
- Si dos términos del mismo idioma quedan iguales al normalizar (p. ej.
  "política" y "politica"), cuenta solo el primero (menor id).
"""
import logging
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from dataclasses import dataclass
from html import unescape
from typing import Protocol

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.noticia import Noticia
from app.models.termino_diccionario import TerminoDiccionario
from app.repositories.dictionary import TerminoDiccionarioRepository
from app.repositories.noticias import NoticiaRepository

logger = logging.getLogger(__name__)

IDIOMAS_SOPORTADOS: tuple[str, ...] = ("es", "en")
METODO_DICCIONARIO = "diccionario"
METODO_ML = "ml"

_ETIQUETA_HTML = re.compile(r"<[^>]+>")
_PALABRA = re.compile(r"\w+")


@dataclass(frozen=True)
class ResultadoHumor:
    valor_humor: float | None
    metodo_calculo: str
    cantidad_terminos_evaluados: int
    # Ids de los términos coincidentes (HU-SENT-008). Se registran siempre,
    # también cuando el humor lo calcula el modelo de ML.
    terminos_ids: tuple[int, ...] = ()


class ProveedorModeloML(Protocol):
    """Punto de extensión para HU-SENT-006 (ADR-04: embeddings + regresor).

    La implementación real debe aplicar su propio timeout y reintentos
    acotados al servicio de embeddings; este módulo agrega un timeout total.
    """

    def predecir(self, texto: str) -> float: ...


def obtener_proveedor_ml_activo() -> ProveedorModeloML | None:
    """Devuelve el modelo ML activo. Sin HU-SENT-006 aún, no hay ninguno."""
    return None


# --- HU-SENT-007: método de diccionario -------------------------------------

def _quitar_tildes(texto: str) -> str:
    """Quita las marcas diacríticas excepto la de la ñ."""
    descompuesto = unicodedata.normalize("NFD", texto)
    caracteres: list[str] = []
    for caracter in descompuesto:
        if unicodedata.combining(caracter):
            es_enie = caracter == "\u0303" and caracteres and caracteres[-1] == "n"
            if not es_enie:
                continue
        caracteres.append(caracter)
    return unicodedata.normalize("NFC", "".join(caracteres))


def _normalizar(texto: str) -> str:
    """Minúsculas, sin tildes (salvo ñ), sin HTML ni puntuación."""
    sin_html = _ETIQUETA_HTML.sub(" ", unescape(texto))
    return " ".join(_PALABRA.findall(_quitar_tildes(sin_html.casefold())))


def texto_de_noticia(noticia: Noticia) -> str:
    return f"{noticia.titulo or ''} {noticia.contenido or ''}"


def terminos_coincidentes(
    texto: str, terminos: list[TerminoDiccionario]
) -> list[TerminoDiccionario]:
    """Términos únicos del diccionario que aparecen en el texto (HU-SENT-007-v2).

    Cada término (palabra + idioma) cuenta una sola vez aunque se repita.
    También es la base de las coincidencias que persiste HU-SENT-008.
    """
    texto_normalizado = f" {_normalizar(texto)} "
    encontrados: list[TerminoDiccionario] = []
    vistos: set[tuple[str, str]] = set()
    for termino in terminos:
        clave = (_normalizar(termino.palabra), termino.idioma)
        if not clave[0] or clave in vistos:
            continue
        if f" {clave[0]} " in texto_normalizado:
            vistos.add(clave)
            encontrados.append(termino)
    return encontrados


def calcular_humor_diccionario(
    texto: str, terminos: list[TerminoDiccionario]
) -> tuple[float | None, int]:
    """Promedio simple de los términos únicos que aparecen en el texto.

    Devuelve (valor_humor, n). Si n = 0, valor_humor es None.
    """
    valores = [termino.valor for termino in terminos_coincidentes(texto, terminos)]
    if not valores:
        return None, 0
    return sum(valores) / len(valores), len(valores)


def idiomas_a_evaluar(idioma_detectado: str | None) -> tuple[str, ...]:
    """El idioma de la noticia si es es/en; si no se conoce, ambos (ADR-03)."""
    if idioma_detectado in IDIOMAS_SOPORTADOS:
        return (idioma_detectado,)
    return IDIOMAS_SOPORTADOS


# --- HU-SENT-002-v2: orquestación híbrida -----------------------------------

def _predecir_con_timeout(proveedor: ProveedorModeloML, texto: str) -> float:
    executor = ThreadPoolExecutor(max_workers=1)
    try:
        futuro = executor.submit(proveedor.predecir, texto)
        return float(futuro.result(timeout=settings.sentimiento_timeout_ml_segundos))
    finally:
        # No esperar al hilo si se agotó el timeout.
        executor.shutdown(wait=False, cancel_futures=True)


def calcular_humor(
    noticia: Noticia,
    terminos_por_idioma: dict[str, list[TerminoDiccionario]],
    proveedor_ml: ProveedorModeloML | None = None,
) -> ResultadoHumor:
    """ML si hay modelo activo; diccionario si no lo hay, falla o excede el timeout."""
    texto = texto_de_noticia(noticia)
    terminos = [
        termino
        for idioma in idiomas_a_evaluar(noticia.idioma_detectado)
        for termino in terminos_por_idioma.get(idioma, [])
    ]
    coincidentes = terminos_coincidentes(texto, terminos)
    ids = tuple(t.id for t in coincidentes if t.id is not None)

    if proveedor_ml is not None:
        try:
            valor = _predecir_con_timeout(proveedor_ml, texto)
            return ResultadoHumor(valor, METODO_ML, 0, ids)
        except FuturesTimeoutError:
            logger.warning("Timeout del modelo ML noticia_id=%s; se usa diccionario", noticia.id)
        except Exception as exc:  # noqa: BLE001 - cualquier fallo activa el fallback
            logger.warning(
                "Fallo del modelo ML noticia_id=%s motivo=%s; se usa diccionario",
                noticia.id,
                type(exc).__name__,
            )

    valores = [t.valor for t in coincidentes]
    valor = sum(valores) / len(valores) if valores else None
    return ResultadoHumor(valor, METODO_DICCIONARIO, len(valores), ids)


def _cargar_terminos(db: Session) -> dict[str, list[TerminoDiccionario]]:
    terminos = TerminoDiccionarioRepository().listar_por_idiomas(db, IDIOMAS_SOPORTADOS)
    por_idioma: dict[str, list[TerminoDiccionario]] = {idioma: [] for idioma in IDIOMAS_SOPORTADOS}
    for termino in terminos:
        por_idioma.setdefault(termino.idioma, []).append(termino)
    return por_idioma


def procesar_noticias(
    db: Session,
    noticias: list[Noticia],
    proveedor_ml: ProveedorModeloML | None = None,
) -> int:
    """Calcula y persiste el humor de cada noticia, aislando los fallos.

    Cada noticia se guarda en su propia transacción: un error en una no
    revierte la noticia capturada ni impide procesar las demás. Devuelve la
    cantidad de noticias procesadas con éxito.
    """
    if not noticias:
        return 0
    proveedor = proveedor_ml if proveedor_ml is not None else obtener_proveedor_ml_activo()
    terminos_por_idioma = _cargar_terminos(db)
    repositorio = NoticiaRepository()
    procesadas = 0
    for noticia in noticias:
        try:
            resultado = calcular_humor(noticia, terminos_por_idioma, proveedor)
            repositorio.guardar_resultado_humor(
                db,
                noticia,
                resultado.valor_humor,
                resultado.metodo_calculo,
                resultado.cantidad_terminos_evaluados,
                resultado.terminos_ids,
            )
            procesadas += 1
        except Exception:  # noqa: BLE001 - el barrido la reintentará
            logger.exception("No se pudo calcular el humor noticia_id=%s", noticia.id)
    return procesadas


def procesar_pendientes(db: Session, limite: int | None = None) -> int:
    """Barrido de respaldo: procesa noticias sin metodo_calculo."""
    pendientes = NoticiaRepository().listar_pendientes_humor(
        db, limite or settings.sentimiento_barrido_lote
    )
    return procesar_noticias(db, pendientes)


def invalidar_calculos_diccionario(db: Session) -> int:
    """Marca para recálculo las noticias calculadas con diccionario.

    Se invoca tras cada alta, modificación o baja de un término (HU-SENT-001):
    el humor de esas noticias depende del diccionario vigente. El barrido de
    respaldo las recalcula en su próxima ejecución; varios cambios seguidos
    se resuelven con un único recálculo. Las noticias calculadas con ML no
    se tocan. Decisión de equipo del 2026-10-18 (cierra el punto pendiente 2
    de HU-SENT-008).
    """
    marcadas = NoticiaRepository().marcar_para_recalculo(db, METODO_DICCIONARIO)
    logger.info("Diccionario modificado: %s noticias marcadas para recálculo", marcadas)
    return marcadas
