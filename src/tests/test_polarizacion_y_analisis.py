"""
Pruebas de HU-SENT-003 (polarización persistida) y HU-SENT-005
(POST /api/v1/sentiment). SQLite en memoria; sin red.
"""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.database import Base, get_db
from app.main import app
from app.models.canal import CanalNoticias
from app.models.fuente import FuenteRSS
from app.models.noticia import Noticia
from app.models.termino_diccionario import TerminoDiccionario
from app.services.sentimiento_service import METODO_ML, polarizacion, procesar_noticias


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
def client(db):
    def override():
        yield db

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def _terminos(db, *pares):
    for palabra, valor, idioma in pares:
        db.add(TerminoDiccionario(palabra=palabra, valor=valor, idioma=idioma))
    db.commit()


def _noticia(db, titulo):
    canal = CanalNoticias(nombre=f"C {titulo}", continente="Europa")
    db.add(canal)
    db.flush()
    fuente = FuenteRSS(canal_id=canal.id, url=f"https://{canal.id}.example.test", categoria_iptc="11000000")
    db.add(fuente)
    db.flush()
    noticia = Noticia(
        fuente_rss_id=fuente.id,
        identificador_item_rss=titulo,
        titulo=titulo,
        enlace_original="https://example.test",
        fecha_registro=datetime(2026, 10, 19, 12),
        idioma_detectado="es",
    )
    db.add(noticia)
    db.commit()
    return noticia


# --- HU-SENT-003 / ADR-003 ---------------------------------------------------

def test_polarizacion_formula():
    assert polarizacion([-8, 6]) == 7.0
    assert polarizacion([6]) == 0.0
    assert polarizacion([]) is None


def test_persiste_humor_y_polarizacion(db):
    _terminos(db, ("guerra", -8, "es"), ("victoria", 6, "es"))
    noticia = _noticia(db, "guerra y victoria")
    procesar_noticias(db, [noticia])
    db.refresh(noticia)
    assert (noticia.valor_humor, noticia.polarizacion_terminos) == (-1.0, 7.0)
    assert noticia.metodo_calculo == "diccionario"


def test_un_termino_polarizacion_cero(db):
    _terminos(db, ("victoria", 6, "es"))
    noticia = _noticia(db, "victoria")
    procesar_noticias(db, [noticia])
    assert (noticia.valor_humor, noticia.polarizacion_terminos) == (6.0, 0.0)


def test_sin_terminos_ambos_nulos(db):
    _terminos(db, ("guerra", -8, "es"))
    noticia = _noticia(db, "nada")
    procesar_noticias(db, [noticia])
    assert (noticia.valor_humor, noticia.polarizacion_terminos) == (None, None)
    assert noticia.metodo_calculo == "diccionario"


class _ModeloOk:
    def predecir(self, texto):
        return 2.5


def test_con_modelo_ml_la_polarizacion_sale_del_diccionario(db, monkeypatch):
    monkeypatch.setattr(settings, "sentimiento_timeout_ml_segundos", 1.0)
    _terminos(db, ("guerra", -8, "es"), ("victoria", 6, "es"))
    noticia = _noticia(db, "guerra y victoria")
    procesar_noticias(db, [noticia], proveedor_ml=_ModeloOk())
    assert (noticia.metodo_calculo, noticia.valor_humor) == (METODO_ML, 2.5)
    assert noticia.polarizacion_terminos == 7.0


# --- HU-SENT-005: POST /sentiment ------------------------------------------

def test_analisis_de_texto(client, db):
    _terminos(db, ("victoria", 6, "es"), ("guerra", -8, "es"))
    respuesta = client.post(
        "/api/v1/sentiment", json={"texto": "Gran victoria, aunque hubo momentos de guerra"}
    )
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "valor_humor": -1.0,
        "cantidad_terminos_evaluados": 2,
        "polarizacion_terminos": 7.0,
    }


def test_analisis_usa_ambos_idiomas(client, db):
    _terminos(db, ("guerra", -8, "es"), ("peace", 4, "en"))
    cuerpo = client.post("/api/v1/sentiment", json={"texto": "guerra and peace"}).json()
    assert cuerpo["cantidad_terminos_evaluados"] == 2


def test_texto_sin_terminos(client, db):
    _terminos(db, ("guerra", -8, "es"))
    cuerpo = client.post("/api/v1/sentiment", json={"texto": "Un día cualquiera"}).json()
    assert cuerpo == {"valor_humor": None, "cantidad_terminos_evaluados": 0, "polarizacion_terminos": None}


def test_analisis_no_persiste_noticias(client, db):
    _terminos(db, ("guerra", -8, "es"))
    client.post("/api/v1/sentiment", json={"texto": "guerra"})
    assert db.query(Noticia).count() == 0


@pytest.mark.parametrize("cuerpo", [{"texto": ""}, {"texto": "   "}, {}, {"texto": 5}])
def test_texto_vacio_o_invalido_responde_400(client, cuerpo):
    assert client.post("/api/v1/sentiment", json=cuerpo).status_code == 400
