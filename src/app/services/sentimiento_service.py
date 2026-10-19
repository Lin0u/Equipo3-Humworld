"""
Cálculo de humor de las noticias capturadas.

Origina en:
- HU-SENT-007: método determinista por diccionario. Promedio simple de los
  valores de los términos ÚNICOS coincidentes (ADR-003): Σ(valores) / n.
- HU-SENT-002-v2: cálculo híbrido síncrono tras la captura, con punto de
  extensión ML (ADR-004), timeout explícito, fallback a diccionario y barrido
  de respaldo. OpenSpec: openspec/changes/Cálculo híbrido de humor.

AVISO (instrucciones del proyecto, sección 12): este módulo contiene lógica
de negocio del algoritmo de sentimiento. Debe ser revisado por el equipo
antes de fusionarse.

Camino ML (HU-SENT-006, ADR-004): si hay GEMINI_API_KEY y un modelo activo en
modelos_sentimiento, se usa su regresor (modelo_ml_service.proveedor_activo);
si no, o si falla o excede el timeout, el diccionario.
Calcula la polarización (HU-SENT-003) y persiste las coincidencias de HU-SENT-008
junto con el resultado.

Comparación de términos (HU-SENT-007-v3; ADR-003, punto 6):
- Palabra o frase completa: "guerra" no coincide con "guerrilla".
- Sin distinguir mayúsculas ni tildes: "POLITICA" coincide con "política".
  La ñ se conserva: "pena" no coincide con "peña".
- Con lematización (spaCy, decisión de la PO del 2026-10-19): se lematiza el
  TEXTO de la noticia, en contexto, y cada palabra se compara con los
  términos del diccionario primero por su forma y, si no hay ninguno con esa
  forma, por su lema. "guerras" y "murieron" coinciden con los términos
  "guerra" y "morir". Los términos del diccionario NO se lematizan (fuera de
  contexto el lema es poco fiable: "best" → "well"), así que deben cargarse en
  su forma base; las formas flexionadas ya cargadas siguen funcionando.
- Las frases de varias palabras coinciden si aparecen en el texto o en la
  secuencia de sus lemas ("acuerdos de paz" → "acuerdo de paz").
- Se quitan las etiquetas HTML del resumen del feed antes de comparar.
- Idioma: si la noticia no lo trae, se detecta (lematizacion.detectar_idioma)
  y se guarda en idioma_detectado; si no se puede decidir, se evalúan ambos.
"""
import logging
import re
import unicodedata
from functools import lru_cache
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
from app.services import lematizacion

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
    # HU-SENT-003: polarización de los términos del diccionario coincidentes.
    # Se calcula también cuando el humor lo da el modelo de ML, porque las
    # coincidencias se registran siempre (HU-SENT-008).
    polarizacion_terminos: float | None = None
    # HU-SENT-006: versión del modelo usada cuando metodo_calculo = "ml".
    modelo_sentimiento_id: int | None = None


class ProveedorModeloML(Protocol):
    """Punto de extensión para HU-SENT-006 (ADR-004: embeddings + regresor).

    La implementación real debe aplicar su propio timeout y reintentos
    acotados al servicio de embeddings; este módulo agrega un timeout total.
    """

    def predecir(self, texto: str) -> float: ...


def obtener_proveedor_ml_activo(db: Session | None = None) -> ProveedorModeloML | None:
    """Devuelve el modelo ML activo (HU-SENT-006) o None si no hay ninguno utilizable."""
    if db is None:
        return None
    from app.services.modelo_ml_service import proveedor_activo

    return proveedor_activo(db)


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


def _sin_html(texto: str) -> str:
    return _ETIQUETA_HTML.sub(" ", unescape(texto))


@lru_cache(maxsize=50000)
def _normalizar(texto: str) -> str:
    """Minúsculas, sin tildes (salvo ñ), sin HTML ni puntuación."""
    return " ".join(_PALABRA.findall(_quitar_tildes(_sin_html(texto).casefold())))


def _palabras_del_texto(texto_limpio: str, idioma: str) -> list[tuple[str, str | None]]:
    """(forma, lema) normalizados de cada palabra; lema None sin lematizador."""
    tokens = lematizacion.tokens(texto_limpio, idioma)
    if tokens is None:
        return [(forma, None) for forma in _normalizar(texto_limpio).split()]
    palabras: list[tuple[str, str | None]] = []
    for texto_token, lema in tokens:
        formas = _normalizar(texto_token).split()
        if len(formas) == 1:
            palabras.append((formas[0], _normalizar(lema) or None))
        else:  # p. ej. "e-mail": se compara solo por forma
            palabras.extend((forma, None) for forma in formas)
    return palabras


def texto_de_noticia(noticia: Noticia) -> str:
    return f"{noticia.titulo or ''} {noticia.contenido or ''}"


def terminos_coincidentes(
    texto: str, terminos: list[TerminoDiccionario]
) -> list[TerminoDiccionario]:
    """Términos únicos del diccionario que aparecen en el texto (HU-SENT-007-v3).

    Cada concepto (lema + idioma) cuenta una sola vez aunque aparezca varias
    veces o en varias formas. También es la base de las coincidencias que
    persiste HU-SENT-008. Los términos se recorren en el orden recibido (por
    id), así que ante un empate gana el de menor id.
    """
    texto_limpio = _sin_html(texto)
    por_idioma: dict[str, list[TerminoDiccionario]] = {}
    for termino in terminos:
        por_idioma.setdefault(termino.idioma, []).append(termino)

    elegidos: set[int] = set()
    for idioma, del_idioma in por_idioma.items():
        palabras_por_forma: dict[str, TerminoDiccionario] = {}
        frases: dict[str, TerminoDiccionario] = {}
        for termino in del_idioma:  # setdefault: ante formas iguales gana el menor id
            forma = _normalizar(termino.palabra)
            if not forma:
                continue
            destino = frases if " " in forma else palabras_por_forma
            destino.setdefault(forma, termino)

        palabras = _palabras_del_texto(texto_limpio, idioma)
        for forma, lema in palabras:
            termino = palabras_por_forma.get(forma) or (lema and palabras_por_forma.get(lema))
            if termino is not None:
                elegidos.add(id(termino))
        if frases:
            superficie = " " + " ".join(f for f, _ in palabras) + " "
            lemas = " " + " ".join(l or f for f, l in palabras) + " "
            for forma, termino in frases.items():
                if f" {forma} " in superficie or f" {forma} " in lemas:
                    elegidos.add(id(termino))

    encontrados = [termino for termino in terminos if id(termino) in elegidos]
    return encontrados


def polarizacion(valores: list[int]) -> float | None:
    """Desviación estándar poblacional de los valores (ADR-003, HU-SENT-003).

    None si no hay valores; 0.0 con un solo valor. Ejemplo de HU-SENT-007:
    [-8, 6] -> 7.0.
    """
    if not valores:
        return None
    media = sum(valores) / len(valores)
    return (sum((v - media) ** 2 for v in valores) / len(valores)) ** 0.5


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
    """El idioma de la noticia si es es/en; si no se conoce, ambos (ADR-003)."""
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
    if noticia.idioma_detectado is None:
        # PDF §4.4 / ADR-003 punto 1: se detecta una vez y queda guardado.
        noticia.idioma_detectado = lematizacion.detectar_idioma(_sin_html(texto))
    terminos = [
        termino
        for idioma in idiomas_a_evaluar(noticia.idioma_detectado)
        for termino in terminos_por_idioma.get(idioma, [])
    ]
    coincidentes = terminos_coincidentes(texto, terminos)
    ids = tuple(t.id for t in coincidentes if t.id is not None)
    valores = [t.valor for t in coincidentes]
    polar = polarizacion(valores)

    if proveedor_ml is not None:
        try:
            valor = _predecir_con_timeout(proveedor_ml, texto)
            modelo_id = getattr(proveedor_ml, "modelo_id", None)
            return ResultadoHumor(valor, METODO_ML, 0, ids, polar, modelo_id)
        except FuturesTimeoutError:
            logger.warning("Timeout del modelo ML noticia_id=%s; se usa diccionario", noticia.id)
        except Exception as exc:  # noqa: BLE001 - cualquier fallo activa el fallback
            logger.warning(
                "Fallo del modelo ML noticia_id=%s motivo=%s; se usa diccionario",
                noticia.id,
                type(exc).__name__,
            )

    valor = sum(valores) / len(valores) if valores else None
    return ResultadoHumor(valor, METODO_DICCIONARIO, len(valores), ids, polar)


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
    proveedor = proveedor_ml if proveedor_ml is not None else obtener_proveedor_ml_activo(db)
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
                resultado.polarizacion_terminos,
                resultado.modelo_sentimiento_id,
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


def analizar_texto(db: Session, texto: str) -> ResultadoHumor:
    """HU-SENT-005: humor de un texto arbitrario, siempre por diccionario.

    Sin idioma conocido, compara con los términos de ambos idiomas (ADR-003).
    No persiste nada.
    """
    noticia = Noticia(titulo=texto, contenido=None, idioma_detectado=None)
    return calcular_humor(noticia, _cargar_terminos(db), proveedor_ml=None)
