from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.exceptions import CanalNoticiasNotFoundError
from app.main import app
from app.models.canal import CanalNoticias
from app.models.fuente import EstadoCircuitBreaker, FuenteRSS
from app.models.noticia import Noticia
from app.schemas.fuente import (
    FuenteRSS as FuenteRSSSchema,
    FuenteRSSCrear,
    FuenteRSSActualizarParcial,
    FuenteRSSListado,
)
from app.repositories.fuentes import FuenteRSSRepository
from app.services.fuente_service import actualizar_fuente, crear_fuente, eliminar_fuente


@pytest.fixture()
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


@pytest.fixture()
def client(database_session):
    def override_get_db():
        yield database_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def crear_canal(database_session, canal_id=42):
    canal = CanalNoticias(
        id=canal_id,
        nombre="Noticias Globales",
        continente="Europa",
    )
    database_session.add(canal)
    database_session.commit()
    return canal


def crear_fuente_registrada(
    database_session,
    fuente_id,
    canal_id,
    url,
    continente="Europa",
    categoria_iptc="07000000",
    activo=True,
):
    canal = database_session.get(CanalNoticias, canal_id)
    if canal is None:
        canal = CanalNoticias(
            id=canal_id,
            nombre=f"Noticias {canal_id}",
            continente=continente,
        )
        database_session.add(canal)
        database_session.flush()
    fuente = FuenteRSS(
        id=fuente_id,
        canal_id=canal_id,
        url=url,
        categoria_iptc=categoria_iptc,
        activo=activo,
        estado_circuit_breaker=EstadoCircuitBreaker.CERRADO,
    )
    database_session.add(fuente)
    database_session.commit()
    return fuente


def test_alta_fuente_asocia_canal_y_normaliza_datos(client, database_session):
    crear_canal(database_session)

    response = client.post(
        "/api/v1/sources",
        json={
            "canal_id": 42,
            "url": "  https://example.com/feed.xml  ",
            "categoria_iptc": " 07000000 ",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["canal_id"] == 42
    assert body["url"] == "https://example.com/feed.xml"
    assert body["categoria_iptc"] == "07000000"
    assert body["activo"] is True

    fuente = database_session.execute(select(FuenteRSS)).scalar_one()
    assert fuente.canal_id == 42
    assert fuente.canal.id == 42


def test_alta_fuente_rechaza_canal_inexistente(client, database_session):
    response = client.post(
        "/api/v1/sources",
        json={
            "canal_id": 999999,
            "url": "https://example.com/feed.xml",
            "categoria_iptc": "07000000",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "codigo": "CANAL_NOTICIAS_NO_ENCONTRADO",
        "mensaje": "El canal de noticias indicado no existe.",
    }
    assert database_session.execute(select(FuenteRSS)).first() is None


@pytest.mark.parametrize(
    "payload",
    [
        {
            "canal_id": 42,
            "url": "ftp://example.com/feed.xml",
            "categoria_iptc": "07000000",
        },
        {
            "canal_id": 42,
            "url": "not-a-url",
            "categoria_iptc": "07000000",
        },
        {
            "canal_id": 42,
            "url": "https://example.com/feed.xml",
            "categoria_iptc": "99999999",
        },
    ],
)
def test_alta_fuente_rechaza_datos_invalidos_con_error(client, database_session, payload):
    crear_canal(database_session)

    response = client.post("/api/v1/sources", json=payload)

    assert response.status_code == 400
    assert set(response.json()) == {"codigo", "mensaje"}
    assert database_session.execute(select(FuenteRSS)).first() is None


def test_openapi_declara_respuestas_del_alta():
    operation = app.openapi()["paths"]["/api/v1/sources"]["post"]

    assert operation["responses"]["201"]["description"]
    assert operation["responses"]["400"]["content"]["application/json"]["schema"]
    assert operation["responses"]["404"]["content"]["application/json"]["schema"]


def test_servicio_crea_fuente_con_activo_true():
    canal = CanalNoticias(id=42, nombre="Noticias", continente="Europa")
    persisted = []

    class FakeRepository:
        def buscar_canal(self, db, canal_id):
            return canal if canal_id == 42 else None

        def crear(self, db, fuente):
            persisted.append(fuente)
            return fuente

    result = crear_fuente(
        object(),
        FuenteRSSCrear(
            canal_id=42,
            url="https://example.com/feed.xml",
            categoria_iptc="07000000",
        ),
        repository=FakeRepository(),
    )

    assert result.canal_id == 42
    assert result.activo is True
    assert persisted == [result]


def test_servicio_rechaza_canal_inexistente():
    class MissingChannelRepository:
        def buscar_canal(self, db, canal_id):
            return None

    with pytest.raises(CanalNoticiasNotFoundError):
        crear_fuente(
            object(),
            FuenteRSSCrear(
                canal_id=999999,
                url="https://example.com/feed.xml",
                categoria_iptc="07000000",
            ),
            repository=MissingChannelRepository(),
        )


def test_listar_fuentes_devuelve_respuesta_paginada_y_ordenada(client, database_session):
    crear_fuente_registrada(database_session, 1, 2, "https://z.example/feed")
    crear_fuente_registrada(database_session, 2, 1, "https://b.example/feed")
    crear_fuente_registrada(database_session, 3, 1, "https://a.example/feed")

    response = client.get("/api/v1/sources?tamanio_pagina=2")

    assert response.status_code == 200
    assert response.json()["pagina"] == 1
    assert response.json()["tamanio_pagina"] == 2
    assert response.json()["total"] == 3
    assert [item["id"] for item in response.json()["items"]] == [3, 2]


def test_schema_paginado_serializa_cero_y_23_elementos():
    fuente = FuenteRSSSchema(
        id=1,
        canal_id=1,
        url="https://example.com/feed",
        categoria_iptc="07000000",
        activo=True,
        estado_circuit_breaker=EstadoCircuitBreaker.CERRADO,
    )

    vacio = FuenteRSSListado(items=[], pagina=1, tamanio_pagina=10, total=0)
    completo = FuenteRSSListado(
        items=[fuente] * 23,
        pagina=1,
        tamanio_pagina=50,
        total=23,
    )

    assert vacio.model_dump()["items"] == []
    assert len(completo.model_dump()["items"]) == 23


def test_listar_fuentes_aplica_filtros_combinados_case_insensitive(client, database_session):
    crear_fuente_registrada(
        database_session,
        1,
        1,
        "https://america.example/feed",
        continente="America",
        categoria_iptc="07000000",
        activo=True,
    )
    crear_fuente_registrada(
        database_session,
        2,
        2,
        "https://america.example/other",
        continente="America",
        categoria_iptc="07000000",
        activo=False,
    )
    crear_fuente_registrada(
        database_session,
        3,
        3,
        "https://europe.example/feed",
        continente="Europa",
        categoria_iptc="01000000",
        activo=True,
    )

    response = client.get(
        "/api/v1/sources?continente=%20america%20&categoria_iptc=07000000&activo=true"
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert [item["id"] for item in response.json()["items"]] == [1]


def test_listar_fuentes_ignora_filtros_textuales_vacios(client, database_session):
    crear_fuente_registrada(database_session, 1, 1, "https://example.com/feed")

    response = client.get("/api/v1/sources?continente=&categoria_iptc=")

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_listar_fuentes_sin_resultados_devuelve_pagina_vacia(client):
    response = client.get("/api/v1/sources")

    assert response.status_code == 200
    assert response.json() == {
        "items": [],
        "pagina": 1,
        "tamanio_pagina": 10,
        "total": 0,
    }


@pytest.mark.parametrize("query", ["pagina=0", "tamanio_pagina=0", "tamanio_pagina=51"])
def test_listar_fuentes_rechaza_paginacion_invalida(client, query):
    response = client.get(f"/api/v1/sources?{query}")

    assert response.status_code == 400
    assert set(response.json()) == {"codigo", "mensaje"}


def test_obtener_fuente_existente_devuelve_todos_los_campos(client, database_session):
    crear_fuente_registrada(database_session, 42, 1, "https://example.com/feed")

    response = client.get("/api/v1/sources/42")

    assert response.status_code == 200
    assert set(response.json()) == {
        "id",
        "canal_id",
        "url",
        "categoria_iptc",
        "activo",
        "fecha_ultima_captura_exitosa",
        "estado_circuit_breaker",
    }


def test_obtener_fuente_inexistente_devuelve_404(client):
    response = client.get("/api/v1/sources/999999")

    assert response.status_code == 404
    assert response.json() == {
        "codigo": "FUENTE_RSS_NO_ENCONTRADA",
        "mensaje": "La fuente RSS indicada no existe.",
    }


def test_openapi_declara_listado_y_detalle_de_fuentes():
    openapi = app.openapi()
    listado = openapi["paths"]["/api/v1/sources"]["get"]
    detalle = openapi["paths"]["/api/v1/sources/{fuente_id}"]["get"]

    assert listado["responses"]["200"]["content"]["application/json"]["schema"]
    assert listado["responses"]["400"]["content"]["application/json"]["schema"]
    assert detalle["responses"]["404"]["content"]["application/json"]["schema"]


def test_put_fuente_reemplaza_campos_y_es_idempotente(client, database_session):
    fuente = crear_fuente_registrada(
        database_session, 42, 1, "https://old.example/feed", categoria_iptc="01000000"
    )
    fuente.fecha_ultima_captura_exitosa = datetime(2026, 9, 5, 12, 0, 0)
    database_session.commit()

    payload = {
        "url": "  https://new.example/feed  ",
        "categoria_iptc": " 07000000 ",
        "activo": False,
    }
    primera = client.put("/api/v1/sources/42", json=payload)
    segunda = client.put("/api/v1/sources/42", json=payload)

    assert primera.status_code == 200
    assert segunda.status_code == 200
    assert primera.json() == segunda.json()
    assert segunda.json()["canal_id"] == 1
    assert segunda.json()["url"] == "https://new.example/feed"
    assert segunda.json()["categoria_iptc"] == "07000000"
    assert segunda.json()["activo"] is False
    assert segunda.json()["fecha_ultima_captura_exitosa"] == "2026-09-05T12:00:00"


def test_patch_fuente_modifica_unicamente_activo(client, database_session):
    crear_fuente_registrada(
        database_session, 42, 1, "https://old.example/feed", categoria_iptc="01000000"
    )

    response = client.patch("/api/v1/sources/42", json={"activo": False})

    assert response.status_code == 200
    assert response.json()["activo"] is False
    assert response.json()["url"] == "https://old.example/feed"
    assert response.json()["categoria_iptc"] == "01000000"
    assert response.json()["canal_id"] == 1


@pytest.mark.parametrize(
    "method, payload",
    [
        ("put", {"url": "https://example.com/feed", "activo": True}),
        (
            "put",
            {
                "url": "https://example.com/feed",
                "categoria_iptc": "07000000",
                "activo": True,
                "canal_id": 2,
            },
        ),
        ("patch", {}),
        ("patch", {"activo": None}),
        ("patch", {"canal_id": 2}),
        ("patch", {"categoria_iptc": "99999999"}),
    ],
)
def test_actualizacion_fuente_rechaza_payload_invalido(client, database_session, method, payload):
    crear_fuente_registrada(database_session, 42, 1, "https://old.example/feed")

    response = getattr(client, method)("/api/v1/sources/42", json=payload)

    assert response.status_code == 400
    assert set(response.json()) == {"codigo", "mensaje"}


@pytest.mark.parametrize("method", ["put", "patch"])
def test_actualizacion_fuente_inexistente_devuelve_404(client, method):
    payload = {
        "url": "https://example.com/feed",
        "categoria_iptc": "07000000",
        "activo": True,
    }
    if method == "patch":
        payload = {"activo": False}

    response = getattr(client, method)("/api/v1/sources/999999", json=payload)

    assert response.status_code == 404
    assert response.json() == {
        "codigo": "FUENTE_RSS_NO_ENCONTRADA",
        "mensaje": "La fuente RSS indicada no existe.",
    }


def test_openapi_declara_actualizacion_completa_y_parcial():
    openapi = app.openapi()

    for method in ("put", "patch"):
        operation = openapi["paths"]["/api/v1/sources/{fuente_id}"][method]
        assert operation["responses"]["200"]["description"]
        assert operation["responses"]["400"]["content"]["application/json"]["schema"]
        assert operation["responses"]["404"]["content"]["application/json"]["schema"]


def test_repositorio_actualiza_y_persiste_fuente(database_session):
    fuente = crear_fuente_registrada(
        database_session, 42, 1, "https://old.example/feed", categoria_iptc="01000000"
    )

    actualizado = FuenteRSSRepository().actualizar(
        database_session,
        fuente,
        {"url": "https://new.example/feed", "activo": False},
    )

    assert actualizado.url == "https://new.example/feed"
    assert actualizado.activo is False
    assert actualizado.canal_id == 1


def test_servicio_patch_aplica_solo_campos_presentes():
    fuente = FuenteRSS(
        id=42,
        canal_id=1,
        url="https://old.example/feed",
        categoria_iptc="01000000",
        activo=True,
    )
    cambios = []

    class FakeRepository:
        def buscar_por_id(self, db, fuente_id):
            return fuente

        def actualizar(self, db, fuente_objetivo, valores):
            cambios.append(valores)
            return fuente_objetivo

    actualizar_fuente(
        object(),
        42,
        FuenteRSSActualizarParcial(activo=False),
        repository=FakeRepository(),
    )

    assert cambios == [{"activo": False}]


def test_servicio_elimina_logicamente_sin_borrar_fila(database_session):
    crear_fuente_registrada(database_session, 42, 1, "https://example.com/feed")

    eliminar_fuente(database_session, 42)

    fuente = database_session.get(FuenteRSS, 42)
    assert fuente is not None
    assert fuente.activo is False


def test_delete_fuente_marca_inactiva_y_conserva_noticia(client, database_session):
    crear_fuente_registrada(database_session, 42, 1, "https://example.com/feed")
    noticia = Noticia(
        id=7,
        fuente_rss_id=42,
        identificador_item_rss="item-7",
        titulo="Noticia histórica",
        enlace_original="https://example.com/news/7",
        fecha_registro=datetime(2026, 9, 5, 12, 0, 0),
    )
    database_session.add(noticia)
    database_session.commit()

    response = client.delete("/api/v1/sources/42")

    assert response.status_code == 204
    assert response.content == b""
    assert database_session.get(FuenteRSS, 42).activo is False
    noticia_persistida = database_session.get(Noticia, 7)
    assert noticia_persistida is not None
    assert noticia_persistida.fuente_rss_id == 42


def test_delete_fuente_oculta_detalle_y_listado(client, database_session):
    crear_fuente_registrada(database_session, 42, 1, "https://example.com/feed")

    assert client.delete("/api/v1/sources/42").status_code == 204
    detalle = client.get("/api/v1/sources/42")
    listado = client.get("/api/v1/sources")
    auditoria = client.get("/api/v1/sources?activo=false")

    assert detalle.status_code == 404
    assert listado.json()["items"] == []
    assert listado.json()["total"] == 0
    assert [item["id"] for item in auditoria.json()["items"]] == [42]


def test_delete_fuente_inexistente_o_repetida_devuelve_404(client, database_session):
    assert client.delete("/api/v1/sources/999999").status_code == 404
    crear_fuente_registrada(database_session, 42, 1, "https://example.com/feed")

    assert client.delete("/api/v1/sources/42").status_code == 204
    response = client.delete("/api/v1/sources/42")

    assert response.status_code == 404
    assert response.json() == {
        "codigo": "FUENTE_RSS_NO_ENCONTRADA",
        "mensaje": "La fuente RSS indicada no existe.",
    }


def test_openapi_declara_eliminacion_de_fuentes():
    operation = app.openapi()["paths"]["/api/v1/sources/{fuente_id}"]["delete"]

    assert operation["responses"]["204"]["description"]
    assert operation["responses"]["404"]["content"]["application/json"]["schema"]
