"""
Pruebas del cálculo de humor.

Origina en: HU-SENT-007 (método de diccionario) y HU-SENT-002-v2 (cálculo
híbrido, fallback y barrido). OpenSpec: "Cálculo híbrido de humor".
SQLite en memoria; el modelo ML es siempre un doble de prueba, nunca real.
"""
import time
from datetime import datetime, timezone

import httpx
import pytest
import respx
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.database import Base
from app.models.canal import CanalNoticias
from app.models.fuente import FuenteRSS
from app.models.noticia import Noticia
from app.models.termino_diccionario import TerminoDiccionario
from app.repositories.noticias import NoticiaRepository
from app.services import sentimiento_service
from app.services.captura_service import ejecutar_captura
from app.services.sentimiento_service import (
    METODO_DICCIONARIO,
    METODO_ML,
    calcular_humor,
    calcular_humor_diccionario,
    idiomas_a_evaluar,
    procesar_noticias,
    procesar_pendientes,
)


def _t(palabra: str, valor: int, idioma: str = "es") -> TerminoDiccionario:
    return TerminoDiccionario(palabra=palabra, valor=valor, idioma=idioma)


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def fuente(db):
    canal = CanalNoticias(nombre="Canal", continente="Europa")
    db.add(canal)
    db.flush()
    fuente = FuenteRSS(canal_id=canal.id, url="https://feed.example.test/rss", categoria_iptc="11000000")
    db.add(fuente)
    db.commit()
    return fuente


def _noticia(db, fuente, titulo, contenido=None, idioma=None, n=[0]) -> Noticia:
    n[0] += 1
    noticia = Noticia(
        fuente_rss_id=fuente.id,
        identificador_item_rss=f"item-{n[0]}",
        titulo=titulo,
        contenido=contenido,
        enlace_original="https://example.test/n",
        fecha_registro=datetime.now(timezone.utc),
        idioma_detectado=idioma,
    )
    db.add(noticia)
    db.commit()
    return noticia


# --- HU-SENT-007: diccionario ------------------------------------------------

def test_promedio_de_terminos_unicos():
    valor, n = calcular_humor_diccionario(
        "La guerra terminó con una victoria", [_t("guerra", -8), _t("victoria", 6)]
    )
    assert (valor, n) == (-1.0, 2)


def test_termino_repetido_cuenta_una_vez():
    valor, n = calcular_humor_diccionario("Crisis, crisis y más CRISIS", [_t("crisis", -6)])
    assert (valor, n) == (-6.0, 1)


def test_sin_coincidencias_devuelve_none():
    assert calcular_humor_diccionario("Nada relevante", [_t("guerra", -8)]) == (None, 0)


def test_coincide_palabra_completa_no_subcadena():
    assert calcular_humor_diccionario("Las guerrillas avanzan", [_t("guerra", -8)]) == (None, 0)


def test_coincide_frase_de_varias_palabras_y_quita_html():
    valor, n = calcular_humor_diccionario(
        "<p>Hubo un <b>acuerdo de paz</b> histórico</p>", [_t("acuerdo de paz", 7)]
    )
    assert (valor, n) == (7.0, 1)


def test_mismo_texto_en_dos_idiomas_cuenta_por_palabra_e_idioma():
    valor, n = calcular_humor_diccionario(
        "crisis", [_t("crisis", -6, "es"), _t("crisis", -4, "en")]
    )
    assert (valor, n) == (-5.0, 2)


def test_no_distingue_tildes_ni_mayusculas():
    terminos = [_t("política", -2), _t("crisis económica", -7)]
    valor, n = calcular_humor_diccionario("POLITICA y Crisis Economica", terminos)
    assert (valor, n) == (-4.5, 2)


def test_conserva_la_enie():
    assert calcular_humor_diccionario("Una pena enorme", [_t("peña", 3)]) == (None, 0)
    assert calcular_humor_diccionario("La PEÑA del barrio", [_t("peña", 3)]) == (3.0, 1)


def test_plural_es_un_termino_distinto():
    assert calcular_humor_diccionario("Dos guerras", [_t("guerra", -8)]) == (None, 0)
    valor, n = calcular_humor_diccionario(
        "Dos guerras", [_t("guerra", -8), _t("guerras", -8)]
    )
    assert (valor, n) == (-8.0, 1)


def test_terminos_iguales_al_normalizar_cuentan_una_vez():
    valor, n = calcular_humor_diccionario(
        "La política", [_t("política", -2), _t("politica", -4)]
    )
    assert (valor, n) == (-2.0, 1)


def test_idiomas_a_evaluar():
    assert idiomas_a_evaluar("es") == ("es",)
    assert idiomas_a_evaluar("en") == ("en",)
    assert idiomas_a_evaluar(None) == ("es", "en")
    assert idiomas_a_evaluar("fr") == ("es", "en")


# --- HU-SENT-002-v2: orquestación --------------------------------------------

TERMINOS = {"es": [_t("guerra", -8)], "en": [_t("war", -4, "en")]}


def test_idioma_conocido_limita_el_diccionario():
    noticia = Noticia(titulo="guerra y war", idioma_detectado="es")
    resultado = calcular_humor(noticia, TERMINOS)
    assert (resultado.valor_humor, resultado.cantidad_terminos_evaluados) == (-8.0, 1)
    assert resultado.metodo_calculo == METODO_DICCIONARIO


def test_idioma_desconocido_usa_ambos_diccionarios():
    resultado = calcular_humor(Noticia(titulo="guerra y war"), TERMINOS)
    assert (resultado.valor_humor, resultado.cantidad_terminos_evaluados) == (-6.0, 2)


class _ModeloOk:
    def predecir(self, texto):
        return 4.5


class _ModeloFalla:
    def predecir(self, texto):
        raise RuntimeError("modelo caído")


class _ModeloLento:
    def predecir(self, texto):
        time.sleep(1)
        return 9.0


def test_sin_modelo_activo_usa_diccionario():
    assert sentimiento_service.obtener_proveedor_ml_activo() is None


def test_modelo_ml_disponible_se_usa():
    resultado = calcular_humor(Noticia(titulo="guerra"), TERMINOS, _ModeloOk())
    assert (resultado.valor_humor, resultado.metodo_calculo) == (4.5, METODO_ML)


def test_fallo_del_modelo_activa_diccionario():
    resultado = calcular_humor(Noticia(titulo="guerra"), TERMINOS, _ModeloFalla())
    assert (resultado.valor_humor, resultado.metodo_calculo) == (-8.0, METODO_DICCIONARIO)


def test_timeout_del_modelo_activa_diccionario(monkeypatch):
    monkeypatch.setattr(settings, "sentimiento_timeout_ml_segundos", 0.05)
    inicio = time.monotonic()
    resultado = calcular_humor(Noticia(titulo="guerra"), TERMINOS, _ModeloLento())
    assert time.monotonic() - inicio < 0.9
    assert resultado.metodo_calculo == METODO_DICCIONARIO


# --- Persistencia y barrido -------------------------------------------------

def test_procesar_persiste_resultado(db, fuente):
    db.add_all([_t("guerra", -8), _t("victoria", 6)])
    db.commit()
    con = _noticia(db, fuente, "Guerra y victoria", idioma="es")
    sin = _noticia(db, fuente, "Nada que evaluar", idioma="es")

    assert procesar_noticias(db, [con, sin]) == 2

    assert (con.valor_humor, con.metodo_calculo, con.cantidad_terminos_evaluados) == (-1.0, "diccionario", 2)
    assert (sin.valor_humor, sin.metodo_calculo, sin.cantidad_terminos_evaluados) == (None, "diccionario", 0)


def test_procesar_lista_vacia(db):
    assert procesar_noticias(db, []) == 0


def test_fallo_en_una_noticia_no_afecta_a_las_demas(db, fuente, monkeypatch):
    db.add(_t("guerra", -8))
    db.commit()
    a = _noticia(db, fuente, "guerra uno")
    b = _noticia(db, fuente, "guerra dos")
    original = NoticiaRepository.guardar_resultado_humor

    def fallar_en_a(self, sesion, noticia, *args):
        if noticia.id == a.id:
            raise RuntimeError("fallo puntual")
        return original(self, sesion, noticia, *args)

    monkeypatch.setattr(NoticiaRepository, "guardar_resultado_humor", fallar_en_a)

    assert procesar_noticias(db, [a, b]) == 1
    assert db.get(Noticia, a.id) is not None
    assert a.metodo_calculo is None
    assert b.metodo_calculo == "diccionario"


def test_barrido_procesa_solo_pendientes(db, fuente):
    db.add(_t("guerra", -8))
    db.commit()
    pendiente = _noticia(db, fuente, "guerra")
    ya_procesada = _noticia(db, fuente, "sin términos")
    procesar_noticias(db, [ya_procesada])

    assert procesar_pendientes(db) == 1
    assert pendiente.valor_humor == -8.0
    # La procesada con 0 coincidencias no vuelve a ser pendiente.
    assert procesar_pendientes(db) == 0


def test_barrido_respeta_el_limite(db, fuente):
    for i in range(3):
        _noticia(db, fuente, f"noticia {i}")
    assert procesar_pendientes(db, limite=2) == 2
    assert procesar_pendientes(db, limite=2) == 1


# --- Integración con la captura ----------------------------------------------

FEED = """<?xml version="1.0"?><rss version="2.0"><channel><title>T</title>
<item><guid>g1</guid><title>Guerra en la frontera</title><link>https://example.test/1</link></item>
<item><guid>g2</guid><title>Victoria del equipo</title><link>https://example.test/2</link></item>
</channel></rss>"""


@pytest.mark.asyncio
@respx.mock
async def test_captura_calcula_humor_de_noticias_nuevas(db, fuente):
    db.add_all([_t("guerra", -8), _t("victoria", 6)])
    db.commit()
    respx.get(fuente.url).mock(return_value=httpx.Response(200, content=FEED))

    resultado = await ejecutar_captura(fuente.id, db)

    assert resultado.noticias_nuevas == 2
    valores = {
        n.identificador_item_rss: (n.valor_humor, n.metodo_calculo)
        for n in db.scalars(select(Noticia))
    }
    assert valores == {"g1": (-8.0, "diccionario"), "g2": (6.0, "diccionario")}


@pytest.mark.asyncio
@respx.mock
async def test_fallo_del_calculo_no_revierte_la_captura(db, fuente, monkeypatch):
    respx.get(fuente.url).mock(return_value=httpx.Response(200, content=FEED))

    def explotar(*args, **kwargs):
        raise RuntimeError("fallo del análisis")

    monkeypatch.setattr("app.services.captura_service.procesar_noticias", explotar)

    resultado = await ejecutar_captura(fuente.id, db)

    assert resultado.noticias_nuevas == 2
    noticias = db.scalars(select(Noticia)).all()
    assert len(noticias) == 2
    assert all(n.metodo_calculo is None for n in noticias)


# --- Recálculo al modificar el diccionario (decisión 2026-10-18) -------------

from app.services.dictionary_service import (  # noqa: E402
    actualizar_termino,
    crear_termino,
    eliminar_termino,
)


def _noticias_calculadas(db, fuente):
    crear_termino(db, "guerra", "es", -8)
    con_diccionario = _noticia(db, fuente, "guerra y crisis")
    con_ml = _noticia(db, fuente, "otra noticia")
    procesar_noticias(db, [con_diccionario])
    NoticiaRepository().guardar_resultado_humor(db, con_ml, 3.0, METODO_ML, 0)
    return con_diccionario, con_ml


def test_alta_de_termino_recalcula_noticias_de_diccionario(db, fuente):
    noticia, con_ml = _noticias_calculadas(db, fuente)
    assert noticia.valor_humor == -8.0

    crear_termino(db, "crisis", "es", -6)

    db.refresh(noticia)
    # Queda pendiente, pero conserva su valor anterior hasta el barrido.
    assert (noticia.metodo_calculo, noticia.valor_humor) == (None, -8.0)
    db.refresh(con_ml)
    assert con_ml.metodo_calculo == METODO_ML

    assert procesar_pendientes(db) == 1
    assert (noticia.valor_humor, noticia.cantidad_terminos_evaluados) == (-7.0, 2)


def test_edicion_de_termino_recalcula(db, fuente):
    noticia, _ = _noticias_calculadas(db, fuente)
    termino_id = db.scalars(select(TerminoDiccionario.id)).one()

    actualizar_termino(db, termino_id, {"valor": -2}, parcial=True)
    procesar_pendientes(db)

    assert noticia.valor_humor == -2.0


def test_baja_de_termino_recalcula(db, fuente):
    noticia, _ = _noticias_calculadas(db, fuente)
    termino_id = db.scalars(select(TerminoDiccionario.id)).one()

    eliminar_termino(db, termino_id)
    procesar_pendientes(db)

    assert (noticia.valor_humor, noticia.cantidad_terminos_evaluados) == (None, 0)
    assert noticia.metodo_calculo == METODO_DICCIONARIO


def test_fallo_al_marcar_no_revierte_el_cambio_del_diccionario(db, monkeypatch):
    from sqlalchemy.exc import OperationalError

    def fallar(*args, **kwargs):
        raise OperationalError("UPDATE", {}, Exception("base caída"))

    monkeypatch.setattr(NoticiaRepository, "marcar_para_recalculo", fallar)

    termino = crear_termino(db, "paz", "es", 7)

    assert db.get(TerminoDiccionario, termino.id) is not None
