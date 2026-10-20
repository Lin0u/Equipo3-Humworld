"""
Lematización y detección de idioma para el método de diccionario.

Origina en: HU-SENT-007-v3 (comparación de términos por lema) y ADR-003,
punto 6 (decisión de la PO del 2026-10-19, por sugerencia del profesor).

- Lematizador: spaCy con los modelos chicos es_core_news_sm y en_core_web_sm.
  Se cargan sin "parser" ni "ner" (no se usan): solo el etiquetado
  morfológico que el lematizador necesita para elegir el lema según el
  contexto de la oración ("fue" → "ser" o "ir").
- Detección de idioma (PDF §4.4: inglés y español): conteo de palabras vacías
  (stop words de spaCy) exclusivas de cada idioma. Si el texto no da una señal
  clara, el idioma queda desconocido y se evalúan ambos diccionarios, como
  antes (ADR-003, punto 1).
- Si un modelo no está instalado, el lematizador de ese idioma queda
  desactivado y la comparación vuelve a ser por forma exacta (HU-SENT-007-v2).
  Con LEMATIZACION_OBLIGATORIA=true (valor por defecto) la API no arranca en
  ese caso (verificar_modelos), y /health informa el estado de cada modelo.
"""
import logging
import re
from functools import lru_cache

logger = logging.getLogger(__name__)

MODELOS = {"es": "es_core_news_sm", "en": "en_core_web_sm"}

# Señal mínima para decidir el idioma: al menos 2 palabras vacías exclusivas y
# el doble que las del otro idioma. Valores propuestos, a ratificar.
MINIMO_PALABRAS_VACIAS = 2
PROPORCION_MINIMA = 2.0

_PALABRA = re.compile(r"\w+")


@lru_cache(maxsize=None)
def cargar_modelo(idioma: str):
    """Modelo spaCy del idioma, o None si spaCy o el modelo no están instalados."""
    nombre = MODELOS.get(idioma)
    if nombre is None:
        return None
    try:
        import spacy

        return spacy.load(nombre, exclude=["parser", "ner"])
    except (ImportError, OSError) as exc:
        logger.warning("Lematizador %s no disponible (%s); se compara por forma exacta", nombre, exc)
        return None


@lru_cache(maxsize=1)
def _palabras_vacias_exclusivas() -> dict[str, frozenset[str]]:
    try:
        from spacy.lang.en.stop_words import STOP_WORDS as EN
        from spacy.lang.es.stop_words import STOP_WORDS as ES
    except ImportError:
        return {"es": frozenset(), "en": frozenset()}
    es, en = {p.casefold() for p in ES}, {p.casefold() for p in EN}
    return {"es": frozenset(es - en), "en": frozenset(en - es)}


def detectar_idioma(texto: str) -> str | None:
    """'es', 'en' o None si el texto no permite decidir."""
    vacias = _palabras_vacias_exclusivas()
    palabras = _PALABRA.findall(texto.casefold())
    conteo = {idioma: sum(p in conjunto for p in palabras) for idioma, conjunto in vacias.items()}
    (primero, n1), (_, n2) = sorted(conteo.items(), key=lambda item: item[1], reverse=True)
    if n1 >= MINIMO_PALABRAS_VACIAS and n1 >= PROPORCION_MINIMA * n2:
        return primero
    return None


def tokens(texto: str, idioma: str) -> list[tuple[str, str]] | None:
    """(forma, lema) de cada palabra del texto, sin puntuación.

    None si el idioma no tiene lematizador. El lema se elige según el
    contexto de la oración, que es lo que aporta spaCy frente a un
    lematizador palabra por palabra.
    """
    modelo = cargar_modelo(idioma)
    if modelo is None:
        return None
    return [
        (token.text, token.lemma_)
        for token in modelo(texto)
        if not (token.is_punct or token.is_space)
    ]


class ModelosNoDisponiblesError(RuntimeError):
    """Faltan modelos de spaCy y la lematización es obligatoria."""


def estado_modelos() -> dict[str, str]:
    """'ok' o 'no_disponible' por idioma (para /health)."""
    return {
        idioma: "ok" if cargar_modelo(idioma) is not None else "no_disponible"
        for idioma in MODELOS
    }


def verificar_modelos(obligatoria: bool) -> dict[str, str]:
    """Carga los modelos al arrancar la API.

    Con obligatoria=True lanza ModelosNoDisponiblesError si falta alguno, con
    el comando para instalarlo; con False solo deja una advertencia en el log.
    """
    estado = estado_modelos()
    faltantes = [MODELOS[idioma] for idioma, valor in estado.items() if valor != "ok"]
    if faltantes:
        mensaje = (
            f"Faltan modelos de spaCy: {', '.join(faltantes)}. "
            "Instálalos con: pip install -r requirements.txt"
        )
        if obligatoria:
            raise ModelosNoDisponiblesError(mensaje)
        logger.warning("%s La comparación de términos será por forma exacta.", mensaje)
    return estado
