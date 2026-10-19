"""
Pruebas de HU-SENT-008 (coincidencias término–noticia) y de
GET /api/v1/dashboards/word-cloud (HU-DASH-003-v2). SQLite en memoria; sin red.
"""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.database import Base, get_db
from app.main import app
from app.models.canal import CanalNoticias
from app.models.coincidencia_termino import CoincidenciaTermino
from app.models.fuente import FuenteRSS
from app.models.noticia import Noticia
from app.models.termino_diccionario import TerminoDiccionario
from app.services.dictionary_service import eliminar_termino
from app.services.sentimiento_service import METODO_ML, procesar_noticias, procesar_pendientes


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


_n = [0]


def _fuente(db, continente="Europa", pais=None):
    _n[0] += 1
    canal = CanalNoticias(nombre=f"C{_n[0]}", continente=continente, pais=pais)
    db.add(canal)
    db.flush()
    fuente = FuenteRSS(canal_id=canal.id, url=f"https://{_n[0]}.example.test", categoria_iptc="11000000")
    db.add(fuente)
    db.commit()
    return fuente


def _noticia(db, fuente, titulo, idioma=None):
    _n[0] += 1
    noticia = Noticia(
        fuente_rss_id=fuente.id,
        identificador_item_rss=f"n{_n[0]}",
        titulo=titulo,
        enlace_original="https://example.test",
        fecha_registro=datetime(2026, 10, 19, 12),
        idioma_detectado=idioma,
    )
    db.add(noticia)
    db.commit()
    return noticia


def _terminos(db, *pares):
    for palabra, valor, idioma in pares:
        db.add(TerminoDiccionario(palabra=palabra, valor=valor, idioma=idioma))
    db.commit()


def _coincidencias(db, noticia) -> set[str]:
    return set(
        db.scalars(
            select(TerminoDiccionario.palabra)
            .join(CoincidenciaTermino, CoincidenciaTermino.termino_id == TerminoDiccionario.id)
            .where(CoincidenciaTermino.noticia_id == noticia.id)
        )
    )


# --- HU-SENT-008 ------------------------------------------------------------

def test_registra_una_coincidencia_por_termino(db):
    _terminos(db, ("guerra", -8, "es"), ("victoria", 6, "es"), ("crisis", -6, "es"))
    noticia = _noticia(db, _fuente(db), "Guerra y victoria, guerra otra vez", "es")
    procesar_noticias(db, [noticia])
    assert _coincidencias(db, noticia) == {"guerra", "victoria"}


def test_sin_terminos_no_registra_coincidencias(db):
    _terminos(db, ("guerra", -8, "es"))
    noticia = _noticia(db, _fuente(db), "Nada relevante", "es")
    procesar_noticias(db, [noticia])
    assert _coincidencias(db, noticia) == set()


def test_respeta_el_idioma_de_la_noticia(db):
    _terminos(db, ("crisis", -6, "es"), ("war", -4, "en"))
    noticia = _noticia(db, _fuente(db), "crisis y war", "es")
    procesar_noticias(db, [noticia])
    assert _coincidencias(db, noticia) == {"crisis"}


def test_reproceso_no_duplica_y_actualiza(db):
    _terminos(db, ("guerra", -8, "es"))
    noticia = _noticia(db, _fuente(db), "guerra y paz", "es")
    procesar_noticias(db, [noticia])
    _terminos(db, ("paz", 4, "es"))
    noticia.metodo_calculo = None
    db.commit()

    procesar_pendientes(db)
    procesar_noticias(db, [noticia])

    assert _coincidencias(db, noticia) == {"guerra", "paz"}
    total = db.scalar(select(func.count()).select_from(CoincidenciaTermino))
    assert total == 2


class _ModeloOk:
    def predecir(self, texto):
        return 5.0


def test_con_modelo_ml_tambien_registra_coincidencias(db, monkeypatch):
    monkeypatch.setattr(settings, "sentimiento_timeout_ml_segundos", 1.0)
    _terminos(db, ("guerra", -8, "es"), ("victoria", 6, "es"))
    noticia = _noticia(db, _fuente(db), "guerra y victoria", "es")
    procesar_noticias(db, [noticia], proveedor_ml=_ModeloOk())
    assert (noticia.metodo_calculo, noticia.valor_humor) == (METODO_ML, 5.0)
    assert _coincidencias(db, noticia) == {"guerra", "victoria"}


def test_borrar_la_noticia_borra_sus_coincidencias(db):
    _terminos(db, ("guerra", -8, "es"))
    noticia = _noticia(db, _fuente(db), "guerra", "es")
    procesar_noticias(db, [noticia])
    db.delete(noticia)
    db.commit()
    assert db.scalar(select(func.count()).select_from(CoincidenciaTermino)) == 0


def test_borrar_el_termino_borra_sus_coincidencias(db):
    _terminos(db, ("guerra", -8, "es"), ("paz", 4, "es"))
    noticia = _noticia(db, _fuente(db), "guerra y paz", "es")
    procesar_noticias(db, [noticia])
    termino_id = db.scalar(select(TerminoDiccionario.id).where(TerminoDiccionario.palabra == "guerra"))

    eliminar_termino(db, termino_id)

    assert _coincidencias(db, noticia) == {"paz"}


# --- GET /dashboards/word-cloud ----------------------------------------------

@pytest.fixture()
def nube(db):
    _terminos(db, ("guerra", -8, "es"), ("paz", 4, "es"), ("war", -4, "en"))
    europa = _fuente(db, "Europa", "España")
    asia = _fuente(db, "Asia", "Japón")
    noticias = [
        _noticia(db, europa, "guerra y paz", "es"),
        _noticia(db, europa, "guerra", "es"),
        _noticia(db, asia, "war", "en"),
    ]
    procesar_noticias(db, noticias)


def test_nube_ordenada_por_peso(client, nube):
    cuerpo = client.get("/api/v1/dashboards/word-cloud").json()
    assert [(p["palabra"], p["peso"]) for p in cuerpo["items"]] == [
        ("guerra", 2), ("paz", 1), ("war", 1)
    ]
    assert cuerpo["items"][0]["valor"] == -8
    assert cuerpo["items"][0]["idioma"] == "es"


def test_nube_filtrada_por_continente_y_pais(client, nube):
    asia = client.get("/api/v1/dashboards/word-cloud?continente=Asia").json()
    assert [p["palabra"] for p in asia["items"]] == ["war"]
    espana = client.get("/api/v1/dashboards/word-cloud?pais=españa").json()
    assert {p["palabra"] for p in espana["items"]} == {"guerra", "paz"}


def test_nube_respeta_el_limite(client, nube):
    cuerpo = client.get("/api/v1/dashboards/word-cloud?limite=1").json()
    assert len(cuerpo["items"]) == 1


def test_nube_vacia_responde_200(client):
    cuerpo = client.get("/api/v1/dashboards/word-cloud?continente=África").json()
    assert cuerpo["items"] == []


@pytest.mark.parametrize("consulta", ["continente=Antártida", "limite=0", "limite=101"])
def test_nube_parametros_invalidos_responden_400(client, consulta):
    assert client.get(f"/api/v1/dashboards/word-cloud?{consulta}").status_code == 400
