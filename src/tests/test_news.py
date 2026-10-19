"""
Pruebas de GET /api/v1/news y GET /api/v1/news/{id} (HU-DASH-002-v2).
SQLite en memoria; sin red.
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


def _fuente(db, nombre, continente, pais=None):
    canal = CanalNoticias(nombre=nombre, continente=continente, pais=pais)
    db.add(canal)
    db.flush()
    _n[0] += 1
    fuente = FuenteRSS(canal_id=canal.id, url=f"https://{_n[0]}.example.test", categoria_iptc="11000000")
    db.add(fuente)
    db.commit()
    return fuente


def _noticia(db, fuente, titulo, humor, dia, publicada=None):
    _n[0] += 1
    noticia = Noticia(
        fuente_rss_id=fuente.id,
        identificador_item_rss=f"n{_n[0]}",
        titulo=titulo,
        contenido=f"Texto de {titulo}",
        enlace_original=f"https://example.test/{_n[0]}",
        fecha_publicacion=publicada,
        fecha_registro=datetime(2026, 10, dia, 12),
        categoria_iptc="11000000",
        valor_humor=humor,
        metodo_calculo="diccionario" if humor is not None else None,
    )
    db.add(noticia)
    db.commit()
    return noticia


@pytest.fixture()
def datos(db):
    rnz = _fuente(db, "RNZ", "Oceanía", "Nueva Zelanda")
    elmundo = _fuente(db, "El Mundo", "Europa", "España")
    _noticia(db, rnz, "A", 7.5, 17)
    _noticia(db, elmundo, "B", -7.2, 18)
    _noticia(db, elmundo, "C", -6.8, 19)
    _noticia(db, rnz, "D", 3.9, 19)
    _noticia(db, rnz, "Sin humor", None, 19)
    _noticia(db, rnz, "Neutra", 0.0, 16)


def _titulos(respuesta):
    return [n["titulo"] for n in respuesta.json()["items"]]


def test_orden_por_influencia(client, datos):
    r = client.get("/api/v1/news?orden=influencia")
    assert _titulos(r) == ["A", "B", "C", "D", "Neutra"]


def test_orden_por_fecha_por_defecto(client, datos):
    # 19: C y D (D tiene id mayor) · 18: B · 17: A · 16: Neutra
    assert _titulos(client.get("/api/v1/news")) == ["D", "C", "B", "A", "Neutra"]


def test_noticias_sin_humor_no_aparecen(client, datos):
    cuerpo = client.get("/api/v1/news").json()
    assert "Sin humor" not in [n["titulo"] for n in cuerpo["items"]]
    assert cuerpo["total"] == 5


def test_filtro_positivas_y_negativas_excluye_neutras(client, datos):
    assert _titulos(client.get("/api/v1/news?orden=influencia&signo=positivas")) == ["A", "D"]
    assert _titulos(client.get("/api/v1/news?orden=influencia&signo=negativas")) == ["B", "C"]


def test_filtros_por_continente_pais_y_fecha(client, datos):
    assert set(_titulos(client.get("/api/v1/news?continente=Europa"))) == {"B", "C"}
    assert set(_titulos(client.get("/api/v1/news?pais=nueva zelanda"))) == {"A", "D", "Neutra"}
    assert set(_titulos(client.get("/api/v1/news?fecha=2026-10-19"))) == {"C", "D"}


def test_fecha_de_publicacion_tiene_prioridad(client, db):
    fuente = _fuente(db, "NPR", "América")
    _noticia(db, fuente, "Publicada antes", 2.0, 19, publicada=datetime(2026, 10, 15, 8))
    assert _titulos(client.get("/api/v1/news?fecha=2026-10-15")) == ["Publicada antes"]
    assert _titulos(client.get("/api/v1/news?fecha=2026-10-19")) == []


def test_paginacion_estable(client, datos):
    p1 = client.get("/api/v1/news?orden=influencia&tamanio_pagina=2&pagina=1").json()
    p2 = client.get("/api/v1/news?orden=influencia&tamanio_pagina=2&pagina=2").json()
    p3 = client.get("/api/v1/news?orden=influencia&tamanio_pagina=2&pagina=3").json()
    vistos = [n["titulo"] for p in (p1, p2, p3) for n in p["items"]]
    assert vistos == ["A", "B", "C", "D", "Neutra"]
    assert (p1["pagina"], p1["tamanio_pagina"], p1["total"]) == (1, 2, 5)


def test_datos_de_cada_noticia(client, datos):
    item = client.get("/api/v1/news?orden=influencia").json()["items"][0]
    assert item["canal"] == "RNZ"
    assert item["continente"] == "Oceanía"
    assert item["pais"] == "Nueva Zelanda"
    assert item["categoria_iptc"] == "11000000"
    assert item["enlace_original"].startswith("https://example.test/")
    assert "contenido" not in item


def test_filtro_sin_resultados(client, datos):
    cuerpo = client.get("/api/v1/news?continente=África").json()
    assert (cuerpo["items"], cuerpo["total"]) == ([], 0)


@pytest.mark.parametrize(
    "consulta",
    ["orden=azar", "signo=neutras", "continente=Antártida", "tamanio_pagina=51", "pagina=0", "fecha=ayer"],
)
def test_parametros_invalidos_responden_400(client, consulta):
    assert client.get(f"/api/v1/news?{consulta}").status_code == 400


def test_detalle(client, db):
    noticia = _noticia(db, _fuente(db, "Dawn", "Asia", "Pakistán"), "Detalle", -2.0, 19)
    cuerpo = client.get(f"/api/v1/news/{noticia.id}").json()
    assert cuerpo["titulo"] == "Detalle"
    assert cuerpo["contenido"] == "Texto de Detalle"
    assert cuerpo["canal"] == "Dawn"


def test_detalle_inexistente_responde_404(client):
    respuesta = client.get("/api/v1/news/999")
    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "NOTICIA_NO_ENCONTRADA"
