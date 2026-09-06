import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.exceptions import (
    CanalNoticiasNotFoundError,
    ChannelNameConflictError,
    UniqueConstraintViolation,
)
from app.main import app
from app.models.canal import CanalNoticias
from app.repositories.canales import CanalNoticiasRepository
from app.schemas.canal import (
    CanalNoticias as CanalNoticiasSchema,
    CanalNoticiasCrear,
    CanalNoticiasListado,
)
from app.services.canal_service import crear_canal, listar_canales, obtener_canal


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


def crear_canal_registrado(
    database_session,
    canal_id,
    nombre,
    continente="Europa",
    pais=None,
    descripcion=None,
):
    canal = CanalNoticias(
        id=canal_id,
        nombre=nombre,
        continente=continente,
        pais=pais,
        descripcion=descripcion,
    )
    database_session.add(canal)
    database_session.commit()
    return canal


def test_crear_canal_normaliza_todos_los_campos_y_acepta_continente_libre(client):
    response = client.post(
        "/api/v1/channels",
        json={
            "nombre": "  Noticias Globales  ",
            "continente": "  Oceania Sur  ",
            "pais": "  Aotearoa  ",
            "descripcion": "  Noticias regionales  ",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "nombre": "Noticias Globales",
        "continente": "Oceania Sur",
        "pais": "Aotearoa",
        "descripcion": "Noticias regionales",
    }


def test_crear_canal_acepta_campos_opcionales_ausentes(client):
    response = client.post(
        "/api/v1/channels",
        json={"nombre": "Noticias Breves", "continente": "Europa"},
    )

    assert response.status_code == 201
    assert response.json()["pais"] is None
    assert response.json()["descripcion"] is None


@pytest.mark.parametrize(
    "payload",
    [
        {"nombre": "   ", "continente": "Europa"},
        {"nombre": "Noticias", "continente": "   "},
        {"nombre": "x" * 151, "continente": "Europa"},
    ],
)
def test_crear_canal_rechaza_datos_invalidos_con_error_de_contrato(client, payload):
    response = client.post("/api/v1/channels", json=payload)

    assert response.status_code == 400
    assert set(response.json()) == {"codigo", "mensaje"}


def test_crear_canal_rechaza_nombre_duplicado_sin_distinguir_mayusculas(client):
    client.post(
        "/api/v1/channels",
        json={"nombre": "Noticias Globales", "continente": "Europa"},
    )

    response = client.post(
        "/api/v1/channels",
        json={"nombre": "  noticias globales  ", "continente": "Europa"},
    )

    assert response.status_code == 409
    assert response.json() == {
        "codigo": "NOMBRE_CANAL_DUPLICADO",
        "mensaje": "Ya existe un canal con ese nombre.",
    }


def test_repositorio_traduce_violacion_de_unicidad():
    repository = CanalNoticiasRepository()

    def commit_with_conflict(self):
        raise IntegrityError("insert", {}, Exception("duplicate"))

    class FakeSession:
        def add(self, canal):
            pass

        commit = commit_with_conflict

        def rollback(self):
            pass

    with pytest.raises(UniqueConstraintViolation):
        repository.crear(FakeSession(), CanalNoticias(nombre="Noticias", continente="Europa"))


def test_servicio_traduce_carrera_de_unicidad_a_conflicto():
    class ConflictingRepository:
        def buscar_por_nombre(self, db, nombre):
            return None

        def crear(self, db, canal):
            raise UniqueConstraintViolation

    with pytest.raises(ChannelNameConflictError):
        crear_canal(
            object(),
            CanalNoticiasCrear(nombre="Noticias", continente="Europa"),
            repository=ConflictingRepository(),
        )


# --- HU-RSS-010: listado paginado ---------------------------------------


def test_listar_canales_devuelve_respuesta_paginada_por_defecto(client, database_session):
    for indice in range(15):
        crear_canal_registrado(database_session, indice + 1, f"Canal {indice:02d}")

    response = client.get("/api/v1/channels")

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 10
    assert body["pagina"] == 1
    assert body["tamanio_pagina"] == 10
    assert body["total"] == 15


def test_listar_canales_ordena_alfabeticamente_insensible_a_mayusculas(client, database_session):
    crear_canal_registrado(database_session, 1, "zebra News")
    crear_canal_registrado(database_session, 2, "Al Jazeera")
    crear_canal_registrado(database_session, 3, "bbc News")

    response = client.get("/api/v1/channels")

    assert response.status_code == 200
    nombres = [item["nombre"] for item in response.json()["items"]]
    assert nombres == ["Al Jazeera", "bbc News", "zebra News"]


def test_listar_canales_pagina_especifica(client, database_session):
    for indice in range(23):
        crear_canal_registrado(database_session, indice + 1, f"Canal {indice:02d}")

    response = client.get("/api/v1/channels?pagina=2")

    assert response.status_code == 200
    body = response.json()
    assert body["pagina"] == 2
    assert len(body["items"]) == 10


def test_listar_canales_tamanio_pagina_personalizado_dentro_del_maximo(client, database_session):
    for indice in range(60):
        crear_canal_registrado(database_session, indice + 1, f"Canal {indice:03d}")

    response = client.get("/api/v1/channels?tamanio_pagina=50")

    assert response.status_code == 200
    assert len(response.json()["items"]) == 50


def test_listar_canales_pagina_posterior_a_la_ultima_devuelve_vacio(client, database_session):
    for indice in range(5):
        crear_canal_registrado(database_session, indice + 1, f"Canal {indice}")

    response = client.get("/api/v1/channels?pagina=3")

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["pagina"] == 3
    assert body["total"] == 5


def test_listar_canales_sin_registros_devuelve_pagina_vacia(client):
    response = client.get("/api/v1/channels")

    assert response.status_code == 200
    assert response.json() == {
        "items": [],
        "pagina": 1,
        "tamanio_pagina": 10,
        "total": 0,
    }


def test_listar_canales_con_volumen_alto_mantiene_la_forma_esperada(client, database_session):
    canales = [
        CanalNoticias(id=indice + 1, nombre=f"Canal {indice:04d}", continente="Europa")
        for indice in range(500)
    ]
    database_session.bulk_save_objects(canales)
    database_session.commit()

    response = client.get("/api/v1/channels")

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 10
    assert body["pagina"] == 1
    assert body["tamanio_pagina"] == 10
    assert body["total"] == 500


@pytest.mark.parametrize(
    "query",
    [
        "pagina=0",
        "pagina=-1",
        "tamanio_pagina=0",
        "tamanio_pagina=51",
        "pagina=abc",
        "tamanio_pagina=abc",
    ],
)
def test_listar_canales_rechaza_paginacion_invalida(client, query):
    response = client.get(f"/api/v1/channels?{query}")

    assert response.status_code == 400
    assert set(response.json()) == {"codigo", "mensaje"}


def test_listar_canales_rechaza_combinacion_de_paginacion_invalida_con_error_unico(client):
    response = client.get("/api/v1/channels?pagina=-1&tamanio_pagina=999")

    assert response.status_code == 400
    body = response.json()
    assert set(body) == {"codigo", "mensaje"}
    assert "detalles" not in body


def test_listar_canales_filtra_por_continente_combinado_con_paginacion(client, database_session):
    crear_canal_registrado(database_session, 1, "Canal America 1", continente="America")
    crear_canal_registrado(database_session, 2, "Canal America 2", continente="america")
    crear_canal_registrado(database_session, 3, "Canal Europa", continente="Europa")

    response = client.get("/api/v1/channels?continente=America&pagina=1")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert all(item["continente"].lower() == "america" for item in body["items"])


def test_listar_canales_filtra_continente_insensible_a_diacriticos(client, database_session):
    crear_canal_registrado(database_session, 1, "Canal Latino", continente="América")
    crear_canal_registrado(database_session, 2, "Canal Europeo", continente="Europa")

    response = client.get("/api/v1/channels?continente=America")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["continente"] == "América"


def test_listar_canales_continente_vacio_no_aplica_filtro(client, database_session):
    crear_canal_registrado(database_session, 1, "Canal Europa", continente="Europa")

    response = client.get("/api/v1/channels?continente=")

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_listar_canales_continente_sin_coincidencias(client, database_session):
    crear_canal_registrado(database_session, 1, "Canal Europa", continente="Europa")

    response = client.get("/api/v1/channels?continente=Antartida")

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0


def test_schema_canal_listado_serializa_cero_y_23_elementos():
    canal = CanalNoticiasSchema(id=1, nombre="Canal", continente="Europa")

    vacio = CanalNoticiasListado(items=[], pagina=1, tamanio_pagina=10, total=0)
    completo = CanalNoticiasListado(items=[canal] * 23, pagina=1, tamanio_pagina=50, total=23)

    assert vacio.model_dump()["items"] == []
    assert len(completo.model_dump()["items"]) == 23


def test_repositorio_lista_ordenado_alfabeticamente_case_insensitive(database_session):
    crear_canal_registrado(database_session, 1, "zebra")
    crear_canal_registrado(database_session, 2, "Alfa")

    items, total = CanalNoticiasRepository().listar(database_session, 1, 10)

    assert total == 2
    assert [canal.nombre for canal in items] == ["Alfa", "zebra"]


def test_repositorio_filtra_por_continente_sin_coincidencias_devuelve_vacio(database_session):
    crear_canal_registrado(database_session, 1, "Canal", continente="Europa")

    items, total = CanalNoticiasRepository().listar(database_session, 1, 10, continente="Asia")

    assert items == []
    assert total == 0


def test_repositorio_buscar_por_id_existente_e_inexistente(database_session):
    crear_canal_registrado(database_session, 42, "Canal")

    repository = CanalNoticiasRepository()

    assert repository.buscar_por_id(database_session, 42) is not None
    assert repository.buscar_por_id(database_session, 999999) is None


def test_servicio_listar_canales_delega_en_el_repositorio_y_recorta_continente():
    llamadas = []

    class FakeRepository:
        def listar(self, db, pagina, tamanio_pagina, continente=None):
            llamadas.append((pagina, tamanio_pagina, continente))
            return [], 0

    resultado = listar_canales(
        object(), 2, 10, continente="  America  ", repository=FakeRepository()
    )

    assert llamadas == [(2, 10, "America")]
    assert resultado == {"items": [], "pagina": 2, "tamanio_pagina": 10, "total": 0}


def test_servicio_listar_canales_trata_continente_de_solo_espacios_como_ausente():
    llamadas = []

    class FakeRepository:
        def listar(self, db, pagina, tamanio_pagina, continente=None):
            llamadas.append(continente)
            return [], 0

    listar_canales(object(), 1, 10, continente="   ", repository=FakeRepository())

    assert llamadas == [None]


def test_servicio_obtener_canal_traduce_ausencia_a_error_de_dominio():
    class FakeRepository:
        def buscar_por_id(self, db, canal_id):
            return None

    with pytest.raises(CanalNoticiasNotFoundError):
        obtener_canal(object(), 999999, repository=FakeRepository())


# --- HU-RSS-010: detalle de canal ---------------------------------------


def test_obtener_canal_existente_devuelve_todos_los_campos(client, database_session):
    crear_canal_registrado(
        database_session,
        42,
        "Noticias Globales",
        continente="Europa",
        pais="España",
        descripcion="Canal de prueba",
    )

    response = client.get("/api/v1/channels/42")

    assert response.status_code == 200
    assert response.json() == {
        "id": 42,
        "nombre": "Noticias Globales",
        "continente": "Europa",
        "pais": "España",
        "descripcion": "Canal de prueba",
    }


def test_obtener_canal_inexistente_devuelve_404(client):
    response = client.get("/api/v1/channels/999999")

    assert response.status_code == 404
    assert response.json() == {
        "codigo": "CANAL_NOTICIAS_NO_ENCONTRADO",
        "mensaje": "El canal de noticias indicado no existe.",
    }


def test_obtener_canal_con_id_no_numerico_devuelve_404(client):
    response = client.get("/api/v1/channels/abc")

    assert response.status_code == 404
    assert response.json() == {
        "codigo": "CANAL_NOTICIAS_NO_ENCONTRADO",
        "mensaje": "El canal de noticias indicado no existe.",
    }


def test_openapi_declara_listado_y_detalle_de_canales():
    openapi = app.openapi()
    listado = openapi["paths"]["/api/v1/channels"]["get"]
    detalle = openapi["paths"]["/api/v1/channels/{canal_id}"]["get"]

    assert listado["responses"]["200"]["content"]["application/json"]["schema"]
    assert listado["responses"]["400"]["content"]["application/json"]["schema"]
    assert detalle["responses"]["404"]["content"]["application/json"]["schema"]
