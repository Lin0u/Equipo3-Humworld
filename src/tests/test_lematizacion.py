"""
Pruebas de la comparación por lema y de la detección de idioma
(HU-SENT-007-v3; ADR-003, punto 6). Usan los modelos reales de spaCy, que
son locales y deterministas (no hay llamadas de red).
"""
import pytest

from app.models.noticia import Noticia
from app.models.termino_diccionario import TerminoDiccionario
from app.services import lematizacion
from app.services.sentimiento_service import (
    calcular_humor,
    calcular_humor_diccionario,
    terminos_coincidentes,
)

_ids = [0]


def _t(palabra, valor, idioma="es"):
    _ids[0] += 1
    return TerminoDiccionario(id=_ids[0], palabra=palabra, valor=valor, idioma=idioma)


def test_verbo_conjugado_coincide_con_su_infinitivo():
    assert calcular_humor_diccionario("Murieron diez personas", [_t("morir", -7)]) == (-7.0, 1)


def test_ingles_por_lema():
    terminos = [_t("kill", -3, "en"), _t("victory", 3, "en")]
    assert calcular_humor_diccionario("Two victories, but the war killed many", terminos) == (0.0, 2)


def test_la_forma_exacta_sigue_coincidiendo():
    # Aunque el lematizador dé otro lema, la forma literal del término basta.
    assert calcular_humor_diccionario("Una crisis grave", [_t("crisis", -6)]) == (-6.0, 1)


def test_la_forma_exacta_tiene_prioridad_sobre_el_lema():
    # Cada palabra del texto aporta un solo término: si existe uno con su
    # forma exacta ("abandoned"), no se suma además el de su lema ("abandon").
    terminos = [_t("abandon", -2, "en"), _t("abandoned", -3, "en")]
    encontrados = terminos_coincidentes("They abandoned the plan", terminos)
    assert [t.palabra for t in encontrados] == ["abandoned"]
    encontrados = terminos_coincidentes("He abandons the plan", terminos)
    assert [t.palabra for t in encontrados] == ["abandon"]


def test_los_terminos_no_se_lematizan_fuera_de_contexto():
    # Fuera de contexto spaCy lematiza "best" como "well"; como los términos
    # no se lematizan, "well" no activa el término "best".
    terminos = [_t("best", 3, "en")]
    assert terminos_coincidentes("All is well", terminos) == []
    assert [t.palabra for t in terminos_coincidentes("The best team", terminos)] == ["best"]


def test_sigue_sin_coincidir_por_subcadena():
    assert calcular_humor_diccionario("Las guerrillas avanzan", [_t("guerra", -8)]) == (None, 0)


def test_frase_de_varias_palabras_por_lema():
    assert calcular_humor_diccionario("Firmaron acuerdos de paz", [_t("acuerdo de paz", 7)]) == (7.0, 1)


def test_sin_modelo_vuelve_a_la_forma_exacta(monkeypatch):
    monkeypatch.setattr(lematizacion, "tokens", lambda texto, idioma: None)
    assert calcular_humor_diccionario("Dos guerras", [_t("guerra", -8)]) == (None, 0)
    assert calcular_humor_diccionario("Una guerra", [_t("guerra", -8)]) == (-8.0, 1)
    assert calcular_humor_diccionario("Hubo un acuerdo de paz", [_t("acuerdo de paz", 7)]) == (7.0, 1)


def test_modelo_inexistente_devuelve_none():
    assert lematizacion.cargar_modelo("fr") is None


@pytest.mark.parametrize(
    "texto, idioma",
    [
        ("El gobierno anunció que las medidas entrarán en vigor esta semana", "es"),
        ("The government said that the new measures will take effect this week", "en"),
        ("guerra", None),
        ("guerra and peace", None),
    ],
)
def test_detectar_idioma(texto, idioma):
    assert lematizacion.detectar_idioma(texto) == idioma


def test_el_idioma_detectado_limita_el_diccionario_y_se_guarda():
    # HU-SENT-008, escenario "Coincidencia limitada al idioma de la noticia".
    terminos = {"es": [_t("crisis", -6)], "en": [_t("crisis", -4, "en")]}
    noticia = Noticia(titulo="La crisis de los mercados se agrava en toda la región", idioma_detectado=None)

    resultado = calcular_humor(noticia, terminos)

    assert noticia.idioma_detectado == "es"
    assert (resultado.valor_humor, resultado.cantidad_terminos_evaluados) == (-6.0, 1)


def test_idioma_ya_informado_no_se_vuelve_a_detectar():
    terminos = {"es": [_t("crisis", -6)], "en": [_t("crisis", -4, "en")]}
    noticia = Noticia(titulo="La crisis de los mercados se agrava en toda la región", idioma_detectado="en")
    assert calcular_humor(noticia, terminos).valor_humor == -4.0


# --- Verificación de los modelos al arrancar (HU-SENT-007-v3) ---------------

def test_los_modelos_de_spacy_estan_instalados():
    # Si falla en CI, requirements.lock no instaló los modelos: la lematización
    # quedaría desactivada sin aviso.
    assert lematizacion.verificar_modelos(obligatoria=True) == {"es": "ok", "en": "ok"}


def test_sin_modelo_y_obligatoria_no_arranca(monkeypatch):
    monkeypatch.setattr(lematizacion, "cargar_modelo", lambda idioma: None if idioma == "es" else object())
    with pytest.raises(lematizacion.ModelosNoDisponiblesError, match="es_core_news_sm"):
        lematizacion.verificar_modelos(obligatoria=True)


def test_sin_modelo_y_no_obligatoria_solo_advierte(monkeypatch, caplog):
    monkeypatch.setattr(lematizacion, "cargar_modelo", lambda idioma: None)
    estado = lematizacion.verificar_modelos(obligatoria=False)
    assert estado == {"es": "no_disponible", "en": "no_disponible"}
    assert "Faltan modelos de spaCy" in caplog.text


def test_la_api_no_arranca_sin_modelos(monkeypatch):
    from fastapi.testclient import TestClient

    from app.core.config import settings
    from app.main import app

    monkeypatch.setattr(lematizacion, "cargar_modelo", lambda idioma: None)
    monkeypatch.setattr(settings, "lematizacion_obligatoria", True)
    with pytest.raises(lematizacion.ModelosNoDisponiblesError):
        with TestClient(app):
            pass
