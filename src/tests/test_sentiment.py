"""
Pruebas de GET /api/v1/sentiment (HU-SENT-004). SQLite en memoria; sin red.
"""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.canal import CanalNoticias
from app.models.fuente import FuenteRSS
from app.models.noticia import Noticia


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


def _fuente(db, continente, pais=None):
    _n[0] += 1
    canal = CanalNoticias(nombre=f"C{_n[0]}", continente=continente, pais=pais)
    db.add(canal)
    db.flush()
    fuente = FuenteRSS(canal_id=canal.id, url=f"https://{_n[0]}.example.test", categoria_iptc="11000000")
    db.add(fuente)
    db.commit()
    return fuente


def _noticia(db, fuente, humor, dia):
    _n[0] += 1
    db.add(
        Noticia(
            fuente_rss_id=fuente.id,
            identificador_item_rss=f"n{_n[0]}",
            titulo="t",
            enlace_original="https://example.test",
            fecha_registro=datetime(2026, 10, dia, 12),
            valor_humor=humor,
        )
    )
    db.commit()


@pytest.fixture()
def datos(db):
    chile = _fuente(db, "América", "Chile")
    espana = _fuente(db, "Europa", "España")
    _noticia(db, chile, 4.0, 16)
    _noticia(db, chile, 2.0, 17)
    _noticia(db, espana, -6.0, 17)
    _noticia(db, espana, None, 17)


def test_global_sin_parametros(client, datos):
    cuerpo = client.get("/api/v1/sentiment").json()
    assert cuerpo["humor_promedio"] == 0.0
    assert cuerpo["cantidad_noticias_evaluadas"] == 3
    assert cuerpo["serie_temporal"] is None


def test_filtro_por_continente_sin_tilde(client, datos):
    cuerpo = client.get("/api/v1/sentiment?continente=america").json()
    assert (cuerpo["humor_promedio"], cuerpo["cantidad_noticias_evaluadas"]) == (3.0, 2)
    assert cuerpo["continente"] == "america"


def test_filtro_por_pais(client, datos):
    cuerpo = client.get("/api/v1/sentiment?pais=españa").json()
    assert (cuerpo["humor_promedio"], cuerpo["cantidad_noticias_evaluadas"]) == (-6.0, 1)


def test_timeline_incluye_todos_los_dias_del_rango(client, datos):
    cuerpo = client.get("/api/v1/sentiment?desde=2026-10-15&hasta=2026-10-17").json()
    assert cuerpo["serie_temporal"] == [
        {"fecha": "2026-10-15", "humor_promedio": None, "cantidad_noticias_evaluadas": 0},
        {"fecha": "2026-10-16", "humor_promedio": 4.0, "cantidad_noticias_evaluadas": 1},
        {"fecha": "2026-10-17", "humor_promedio": -2.0, "cantidad_noticias_evaluadas": 2},
    ]
    assert cuerpo["cantidad_noticias_evaluadas"] == 3


def test_rango_limita_el_agregado(client, datos):
    cuerpo = client.get("/api/v1/sentiment?desde=2026-10-17&hasta=2026-10-17").json()
    assert (cuerpo["humor_promedio"], cuerpo["cantidad_noticias_evaluadas"]) == (-2.0, 2)


def test_filtro_sin_datos_responde_200_con_null(client, datos):
    cuerpo = client.get("/api/v1/sentiment?continente=Oceanía").json()
    assert cuerpo["humor_promedio"] is None
    assert cuerpo["cantidad_noticias_evaluadas"] == 0


def test_desde_posterior_a_hasta_responde_400(client):
    respuesta = client.get("/api/v1/sentiment?desde=2026-10-18&hasta=2026-10-01")
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "RANGO_FECHAS_INVALIDO"


def test_rango_demasiado_largo_responde_400(client):
    respuesta = client.get("/api/v1/sentiment?desde=2025-01-01&hasta=2026-10-01")
    assert respuesta.status_code == 400


def test_fecha_con_formato_invalido_responde_400(client):
    assert client.get("/api/v1/sentiment?desde=ayer").status_code == 400
