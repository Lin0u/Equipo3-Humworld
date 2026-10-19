"""
Pruebas de GET /api/v1/dashboards/map (HU-DASH-001-v3) y de los campos de
captura que lo alimentan. SQLite en memoria; sin red.
"""
from datetime import date, datetime, timezone

import httpx
import pytest
import respx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.canal import CanalNoticias
from app.models.fuente import FuenteRSS
from app.models.noticia import Noticia
from app.services.captura_service import ejecutar_captura


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


_contador = [0]


def _fuente(db, continente: str) -> FuenteRSS:
    _contador[0] += 1
    canal = CanalNoticias(nombre=f"Canal {_contador[0]}", continente=continente)
    db.add(canal)
    db.flush()
    fuente = FuenteRSS(
        canal_id=canal.id, url=f"https://{_contador[0]}.example.test/rss", categoria_iptc="11000000"
    )
    db.add(fuente)
    db.commit()
    return fuente


def _noticia(db, fuente, humor, publicada=None, registrada=datetime(2026, 10, 18, 12)):
    _contador[0] += 1
    db.add(
        Noticia(
            fuente_rss_id=fuente.id,
            identificador_item_rss=f"n{_contador[0]}",
            titulo="t",
            enlace_original="https://example.test/n",
            fecha_publicacion=publicada,
            fecha_registro=registrada,
            valor_humor=humor,
        )
    )
    db.commit()


def test_mapa_sin_datos_responde_200_con_nulos(client):
    cuerpo = client.get("/api/v1/dashboards/map").json()
    assert cuerpo["fecha"] is None
    assert cuerpo["fecha_minima_con_datos"] is None
    assert cuerpo["global"] == {"humor_promedio": None, "cantidad_noticias_evaluadas": 0}
    assert [c["continente"] for c in cuerpo["continentes"]] == [
        "América", "Europa", "Asia", "África", "Oceanía"
    ]
    assert all(c["humor_promedio"] is None for c in cuerpo["continentes"])


def test_mapa_agrega_por_continente_y_global(client, db):
    europa, asia = _fuente(db, "Europa"), _fuente(db, "Asia")
    _noticia(db, europa, 4.0)
    _noticia(db, europa, 2.0)
    _noticia(db, asia, -6.0)
    _noticia(db, asia, None)  # sin humor: no cuenta

    cuerpo = client.get("/api/v1/dashboards/map?fecha=2026-10-18").json()

    por_nombre = {c["continente"]: c for c in cuerpo["continentes"]}
    assert por_nombre["Europa"] == {"continente": "Europa", "humor_promedio": 3.0, "cantidad_noticias_evaluadas": 2}
    assert por_nombre["Asia"]["humor_promedio"] == -6.0
    assert por_nombre["África"] == {"continente": "África", "humor_promedio": None, "cantidad_noticias_evaluadas": 0}
    assert cuerpo["global"] == {"humor_promedio": 0.0, "cantidad_noticias_evaluadas": 3}


def test_continente_sin_tilde_o_en_mayusculas_se_reconoce(client, db):
    _noticia(db, _fuente(db, "AMERICA"), 1.0)
    _noticia(db, _fuente(db, "oceania"), 3.0)
    cuerpo = client.get("/api/v1/dashboards/map?fecha=2026-10-18").json()
    por_nombre = {c["continente"]: c["humor_promedio"] for c in cuerpo["continentes"]}
    assert (por_nombre["América"], por_nombre["Oceanía"]) == (1.0, 3.0)


def test_continente_desconocido_solo_cuenta_en_el_global(client, db):
    _noticia(db, _fuente(db, "Antártida"), 5.0)
    cuerpo = client.get("/api/v1/dashboards/map?fecha=2026-10-18").json()
    assert cuerpo["global"]["cantidad_noticias_evaluadas"] == 1
    assert all(c["cantidad_noticias_evaluadas"] == 0 for c in cuerpo["continentes"])


def test_usa_fecha_de_publicacion_y_si_falta_la_de_registro(client, db):
    fuente = _fuente(db, "Europa")
    _noticia(db, fuente, 2.0, publicada=datetime(2026, 10, 16, 9), registrada=datetime(2026, 10, 18, 9))
    _noticia(db, fuente, 6.0, publicada=None, registrada=datetime(2026, 10, 17, 9))

    cuerpo = client.get("/api/v1/dashboards/map?fecha=2026-10-16").json()
    assert cuerpo["global"] == {"humor_promedio": 2.0, "cantidad_noticias_evaluadas": 1}
    assert (cuerpo["fecha_minima_con_datos"], cuerpo["fecha_maxima_con_datos"]) == ("2026-10-16", "2026-10-17")


def test_sin_fecha_usa_el_ultimo_dia_con_datos(client, db):
    fuente = _fuente(db, "Europa")
    _noticia(db, fuente, 2.0, registrada=datetime(2026, 10, 16, 9))
    _noticia(db, fuente, -4.0, registrada=datetime(2026, 10, 17, 9))
    cuerpo = client.get("/api/v1/dashboards/map").json()
    assert cuerpo["fecha"] == "2026-10-17"
    assert cuerpo["global"]["humor_promedio"] == -4.0


def test_fecha_sin_datos_devuelve_nulos(client, db):
    _noticia(db, _fuente(db, "Europa"), 2.0)
    cuerpo = client.get("/api/v1/dashboards/map?fecha=2026-01-01").json()
    assert cuerpo["fecha"] == "2026-01-01"
    assert cuerpo["global"]["humor_promedio"] is None


def test_fecha_invalida_responde_400(client):
    respuesta = client.get("/api/v1/dashboards/map?fecha=18-10-2026")
    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "DATOS_INVALIDOS"


FEED = """<?xml version="1.0"?><rss version="2.0"><channel><title>T</title>
<item><guid>a</guid><title>Uno</title><link>https://example.test/1</link>
<pubDate>Fri, 16 Oct 2026 22:30:00 -0300</pubDate></item>
<item><guid>b</guid><title>Dos</title><link>https://example.test/2</link></item>
</channel></rss>"""


@pytest.mark.asyncio
@respx.mock
async def test_captura_guarda_fecha_de_publicacion_y_categoria(db):
    fuente = _fuente(db, "América")
    respx.get(fuente.url).mock(return_value=httpx.Response(200, content=FEED))

    await ejecutar_captura(fuente.id, db)

    noticias = {n.identificador_item_rss: n for n in db.scalars(select(Noticia))}
    # 22:30 -03:00 = 01:30 UTC del día siguiente.
    assert noticias["a"].fecha_publicacion.replace(tzinfo=None) == datetime(2026, 10, 17, 1, 30)
    assert noticias["b"].fecha_publicacion is None
    assert {n.categoria_iptc for n in noticias.values()} == {"11000000"}
