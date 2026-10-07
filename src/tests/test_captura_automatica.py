from datetime import datetime, timezone

import httpx
import pytest
import respx
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.canal import CanalNoticias
from app.models.fuente import EstadoCircuitBreaker, FuenteRSS
from app.models.noticia import Noticia
from app.services.captura_service import (
    ejecutar_captura,
    ejecutar_captura_multiple,
    ejecutar_captura_todas_las_activas,
)


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


def crear_fuente(database_session, fuente_id, url, activo=True, estado=EstadoCircuitBreaker.CERRADO):
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
        estado_circuit_breaker=estado,
    )
    database_session.add(fuente)
    database_session.commit()
    return fuente


def feed_xml(*items):
    chunks = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0"><channel><title>Prueba</title><link>https://example.test/</link></channel>',
    ]
    for item in items:
        chunks.append(
            '<item>'
            f'<guid>{item["guid"]}</guid>'
            f'<title>{item["title"]}</title>'
            f'<link>{item["link"]}</link>'
            f'<description>{item.get("description", "")}</description>'
            f'<pubDate>{item.get("pubDate", "Mon, 01 Jan 2024 00:00:00 GMT")}</pubDate>'
            '</item>'
        )
    chunks.append('</rss>')
    return "".join(chunks)


@pytest.mark.asyncio
@respx.mock
async def test_captura_persiste_noticias_y_deduplica(database_session):
    url = "https://example.test/feed.xml"
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            content=feed_xml(
                {"guid": "item-1", "title": "Noticia", "link": "https://example.test/1"}
            ),
            headers={"content-type": "application/rss+xml"},
        )
    )
    fuente = crear_fuente(database_session, 1, url)

    resultado = await ejecutar_captura(fuente.id, database_session)
    duplicado = await ejecutar_captura(fuente.id, database_session)

    noticias = database_session.execute(
        select(Noticia).where(Noticia.fuente_rss_id == fuente.id)
    ).scalars().all()
    assert resultado.estado.value == "exitosa"
    assert resultado.noticias_nuevas == 1
    assert duplicado.noticias_nuevas == 0
    assert len(noticias) == 1
    assert noticias[0].identificador_item_rss == "item-1"
    assert noticias[0].fecha_registro is not None
    assert fuente.fecha_ultima_captura_exitosa is not None


@pytest.mark.asyncio
@respx.mock
async def test_captura_multiple_aisla_fallos_y_continua(database_session):
    fuente_fallida = crear_fuente(database_session, 1, "https://example.test/fallida")
    fuente_valida = crear_fuente(database_session, 2, "https://example.test/valida")
    respx.get(fuente_fallida.url).mock(return_value=httpx.Response(500))
    respx.get(fuente_valida.url).mock(
        return_value=httpx.Response(
            200,
            content=feed_xml(
                {"guid": "item-2", "title": "Noticia válida", "link": "https://example.test/2"}
            ),
            headers={"content-type": "application/rss+xml"},
        )
    )

    resultados = await ejecutar_captura_multiple(
        [fuente_fallida.id, fuente_valida.id], database_session
    )

    assert {resultado.fuente_id: resultado.estado.value for resultado in resultados} == {
        1: "fallida_transitoria",
        2: "exitosa",
    }
    assert database_session.execute(
        select(Noticia).where(Noticia.fuente_rss_id == fuente_valida.id)
    ).scalars().one()


@pytest.mark.asyncio
@respx.mock
async def test_retry_recupera_captura_trasitoria(database_session, monkeypatch):
    url = "https://example.test/retry"
    fuente = crear_fuente(database_session, 1, url)
    respx.get(url).mock(
        side_effect=[
            httpx.Response(500),
            httpx.Response(
                200,
                content=feed_xml(
                    {"guid": "retry-item", "title": "Recuperado", "link": "https://example.test/retry-item"}
                ),
                headers={"content-type": "application/rss+xml"},
            ),
        ]
    )

    async def no_sleep(_delay):
        return None

    monkeypatch.setattr("app.services.captura_service.asyncio.sleep", no_sleep)
    resultado = await ejecutar_captura(fuente.id, database_session)

    assert resultado.estado.value == "exitosa"
    assert resultado.noticias_nuevas == 1
    assert len(respx.calls) == 2


@pytest.mark.asyncio
@respx.mock
async def test_timeout_agota_en_cuatro_intentos(database_session, monkeypatch):
    url = "https://example.test/timeout"
    fuente = crear_fuente(database_session, 1, url)
    respx.get(url).mock(side_effect=httpx.TimeoutException("timeout"))

    async def no_sleep(_delay):
        return None

    monkeypatch.setattr("app.services.captura_service.asyncio.sleep", no_sleep)
    resultado = await ejecutar_captura(fuente.id, database_session)

    assert resultado.estado.value == "fallida_transitoria"
    assert resultado.noticias_nuevas == 0
    assert len(respx.calls) == 4


@pytest.mark.asyncio
@respx.mock
async def test_captura_omite_feed_malformado_y_registra_item_invalido(database_session):
    url = "https://example.test/malformed"
    fuente = crear_fuente(database_session, 1, url)
    respx.get(url).mock(
        return_value=httpx.Response(
            200,
            content=feed_xml(
                {"guid": "item-1", "title": "Válido", "link": "https://example.test/1"},
                {"guid": "", "title": "Inválido", "link": "https://example.test/2"},
            ),
            headers={"content-type": "application/rss+xml"},
        )
    )

    resultado = await ejecutar_captura(fuente.id, database_session)

    assert resultado.estado.value == "exitosa"
    assert resultado.noticias_nuevas == 1
    assert database_session.execute(select(Noticia)).scalars().one().identificador_item_rss == "item-1"


@pytest.mark.asyncio
@respx.mock
async def test_circuit_breaker_abierto_omite_http(database_session):
    fuente = crear_fuente(database_session, 1, "https://example.test/closed", estado=EstadoCircuitBreaker.ABIERTO)

    resultado = await ejecutar_captura(fuente.id, database_session)

    assert resultado.estado.value == "fallida_circuito_abierto"
    assert resultado.noticias_nuevas == 0
    assert not respx.calls


@pytest.mark.asyncio
@respx.mock
async def test_captura_todas_las_activas_excluye_inactivas(database_session):
    activa = crear_fuente(database_session, 1, "https://example.test/activa")
    inactiva = crear_fuente(database_session, 2, "https://example.test/inactiva", activo=False)
    respx.get(activa.url).mock(
        return_value=httpx.Response(
            200,
            content=feed_xml(
                {"guid": "item-1", "title": "Noticias", "link": "https://example.test/1"}
            ),
            headers={"content-type": "application/rss+xml"},
        )
    )

    resultados = await ejecutar_captura_todas_las_activas(database_session)

    assert {resultado.fuente_id for resultado in resultados} == {activa.id}
    assert not any(call.request.url == inactiva.url for call in respx.calls)
    assert database_session.execute(
        select(Noticia).where(Noticia.fuente_rss_id == activa.id)
    ).scalars().one()
