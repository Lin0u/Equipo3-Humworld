import httpx
import pytest
import respx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models.canal import CanalNoticias
from app.models.fuente import EstadoCircuitBreaker, FuenteRSS
from app.models.noticia import Noticia
from app.repositories.fuentes import FuenteRSSRepository
from app.services.captura_service import ejecutar_captura
from app.main import app


@pytest.fixture
def database_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(database_session):
    def override_get_db():
        yield database_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def crear_fuente(database_session, fuente_id, url, activo=True):
    canal = CanalNoticias(
        id=100,
        nombre="Canal de pruebas",
        continente="Europa",
    )
    database_session.merge(canal)
    database_session.flush()
    fuente = FuenteRSS(
        id=fuente_id,
        canal_id=canal.id,
        url=url,
        categoria_iptc="07000000",
        activo=activo,
        estado_circuit_breaker=EstadoCircuitBreaker.CERRADO,
    )
    database_session.add(fuente)
    database_session.commit()
    return fuente


def feed_xml(guid, title, link):
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0"><channel><title>Prueba</title>'
        '<link>https://example.test/</link><item>'
        f"<guid>{guid}</guid><title>{title}</title><link>{link}</link>"
        "</item></channel></rss>"
    )


def test_repositorio_distingue_fuente_activa_inactiva_e_inexistente():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = session_factory()
    try:
        canal = CanalNoticias(id=1, nombre="Canal", continente="Europa")
        db.add(canal)
        db.flush()
        db.add_all(
            [
                FuenteRSS(
                    id=1,
                    canal_id=canal.id,
                    url="https://example.test/activa",
                    categoria_iptc="07000000",
                    activo=True,
                    estado_circuit_breaker=EstadoCircuitBreaker.CERRADO,
                ),
                FuenteRSS(
                    id=2,
                    canal_id=canal.id,
                    url="https://example.test/inactiva",
                    categoria_iptc="07000000",
                    activo=False,
                    estado_circuit_breaker=EstadoCircuitBreaker.CERRADO,
                ),
            ]
        )
        db.commit()

        repository = FuenteRSSRepository()
        assert repository.buscar_por_id(db, 1).activo is True
        assert repository.buscar_por_id(db, 2).activo is False
        assert repository.buscar_por_id(db, 3) is None
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.asyncio
@respx.mock
async def test_captura_manual_individual_devuelve_resultado_y_deduplica(
    client, database_session
):
    url = "https://example.test/manual.xml"
    crear_fuente(database_session, 11, url)
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            content=feed_xml("manual-1", "Noticia", "https://example.test/1"),
            headers={"content-type": "application/rss+xml"},
        )
    )

    response = client.post("/api/v1/sources/11/captures")
    duplicate = client.post("/api/v1/sources/11/captures")

    assert response.status_code == 201
    assert response.json()["fuente_id"] == 11
    assert response.json()["estado"] == "exitosa"
    assert response.json()["noticias_nuevas"] == 1
    assert duplicate.status_code == 201
    assert duplicate.json()["noticias_nuevas"] == 0
    assert database_session.execute(select(Noticia)).scalars().one()


@pytest.mark.parametrize(
    ("fuente_id", "activo", "expected_status", "expected_code"),
    [
        (999, True, 404, "FUENTE_RSS_NO_ENCONTRADA"),
        (12, False, 409, "FUENTE_RSS_INACTIVA"),
    ],
)
def test_captura_manual_rechaza_fuente_inexistente_o_inactiva_sin_http(
    client, database_session, fuente_id, activo, expected_status, expected_code
):
    if fuente_id != 999:
        crear_fuente(database_session, fuente_id, "https://example.test/inactiva", activo)

    with respx.mock:
        response = client.post(f"/api/v1/sources/{fuente_id}/captures")

    assert response.status_code == expected_status
    assert response.json()["codigo"] == expected_code
    assert not respx.calls


def test_captura_manual_lote_rechaza_lista_vacia(client):
    response = client.post("/api/v1/captures", json={"fuente_ids": []})

    assert response.status_code == 400


@pytest.mark.parametrize("payload", [None, {}, {"fuente_ids": "no-es-lista"}])
def test_captura_manual_lote_rechaza_body_ausente_o_invalido(client, payload):
    response = client.post("/api/v1/captures", json=payload)

    assert response.status_code == 400


@pytest.mark.asyncio
@respx.mock
async def test_captura_manual_lote_aisla_fallo_y_procesa_todas_las_fuentes(
    client, database_session, monkeypatch
):
    fallida = crear_fuente(database_session, 21, "https://example.test/fallida")
    valida = crear_fuente(database_session, 22, "https://example.test/valida")
    respx.get(fallida.url).mock(return_value=httpx.Response(500))
    respx.get(valida.url).mock(
        return_value=httpx.Response(
            200,
            content=feed_xml("lote-1", "Noticia válida", "https://example.test/lote-1"),
            headers={"content-type": "application/rss+xml"},
        )
    )

    async def no_sleep(_delay):
        return None

    monkeypatch.setattr("app.services.captura_service.asyncio.sleep", no_sleep)
    response = client.post("/api/v1/captures", json={"fuente_ids": [21, 22]})

    assert response.status_code == 201
    resultados = {item["fuente_id"]: item for item in response.json()}
    assert set(resultados) == {fallida.id, valida.id}
    assert resultados[fallida.id]["estado"] == "fallida_transitoria"
    assert resultados[valida.id]["estado"] == "exitosa"
    assert resultados[valida.id]["noticias_nuevas"] == 1
    assert respx.calls.call_count == 4 + 1
    assert database_session.execute(
        select(Noticia).where(Noticia.fuente_rss_id == valida.id)
    ).scalars().one()