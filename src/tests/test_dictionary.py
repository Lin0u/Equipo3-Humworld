import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models.termino_diccionario import TerminoDiccionario
from app.repositories.dictionary import TerminoDiccionarioRepository
from app.services.dictionary_service import crear_termino, listar_terminos


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


def termino_crear(client, palabra, idioma="es", valor=0):
    return client.post(
        "/api/v1/dictionary",
        json={"palabra": palabra, "idioma": idioma, "valor": valor},
    )


def test_termino_diccionario_round_trip_y_clave_case_sensitive(database_session):
    database_session.add_all(
        [
            TerminoDiccionario(palabra="guerra", idioma="es", valor=-8),
            TerminoDiccionario(palabra="Guerra", idioma="es", valor=-7),
        ]
    )
    database_session.commit()

    terminos = database_session.execute(
        select(TerminoDiccionario).order_by(TerminoDiccionario.id)
    ).scalars().all()

    assert [(termino.palabra, termino.idioma, termino.valor) for termino in terminos] == [
        ("guerra", "es", -8),
        ("Guerra", "es", -7),
    ]


def test_termino_diccionario_rechaza_clave_literal_duplicada(database_session):
    database_session.add(
        TerminoDiccionario(palabra="guerra", idioma="es", valor=-8)
    )
    database_session.commit()
    database_session.add(
        TerminoDiccionario(palabra="guerra", idioma="es", valor=-7)
    )

    with pytest.raises(IntegrityError):
        database_session.commit()
    database_session.rollback()


@pytest.mark.parametrize("valor", [-10, 0, 10])
def test_servicio_acepta_limites_de_valor(database_session, valor):
    termino = crear_termino(
        database_session,
        palabra=f"limite-{valor}",
        idioma="es",
        valor=valor,
    )

    assert termino.valor == valor


@pytest.mark.parametrize("valor", [-11, 11, True, 1.5])
def test_servicio_rechaza_valor_fuera_de_rango_o_no_entero(database_session, valor):
    with pytest.raises(ValueError):
        crear_termino(database_session, "invalido", "es", valor)


def test_busqueda_parcial_ignora_mayusculas(database_session):
    crear_termino(database_session, "Guerra civil", "es", -8)
    crear_termino(database_session, "Guerra", "en", -7)
    crear_termino(database_session, "Paz", "es", 8)

    resultados = listar_terminos(database_session, "gUeRr")

    assert [termino.palabra for termino in resultados] == ["Guerra civil", "Guerra"]


def test_repositorio_clave_es_literal_y_sensible_a_mayusculas(database_session):
    crear_termino(database_session, "guerra", "es", -8)
    crear_termino(database_session, "Guerra", "es", -7)
    repository = TerminoDiccionarioRepository()

    assert repository.buscar_por_palabra_idioma(database_session, "guerra", "es").valor == -8
    assert repository.buscar_por_palabra_idioma(database_session, "Guerra", "es").valor == -7
    assert repository.buscar_por_palabra_idioma(database_session, "GUERRA", "es") is None


def test_api_crud_completo_y_respuestas_contractuales(client):
    creado = termino_crear(client, "guerra", valor=-8)
    assert creado.status_code == 201
    termino_id = creado.json()["id"]

    assert client.get("/api/v1/dictionary").status_code == 200
    listado = client.get("/api/v1/dictionary?busqueda=GUERR")
    assert listado.status_code == 200
    assert [item["id"] for item in listado.json()] == [termino_id]
    assert client.get(f"/api/v1/dictionary/{termino_id}").status_code == 200

    actualizado = client.put(
        f"/api/v1/dictionary/{termino_id}",
        json={"palabra": "conflicto", "idioma": "es", "valor": -9},
    )
    assert actualizado.status_code == 200
    parcial = client.patch(
        f"/api/v1/dictionary/{termino_id}", json={"valor": -6}
    )
    assert parcial.status_code == 200
    assert parcial.json()["palabra"] == "conflicto"
    assert parcial.json()["valor"] == -6

    eliminado = client.delete(f"/api/v1/dictionary/{termino_id}")
    assert eliminado.status_code == 204
    assert eliminado.content == b""
    assert client.get(f"/api/v1/dictionary/{termino_id}").status_code == 404
    assert client.delete(f"/api/v1/dictionary/{termino_id}").status_code == 404


@pytest.mark.parametrize("valor", [-11, 11, True, 1.5])
def test_api_rechaza_valores_invalidos(client, valor):
    assert termino_crear(client, "palabra", valor=valor).status_code == 400


def test_api_rechaza_duplicados_compuestos_y_permite_idioma_distinto(client):
    assert termino_crear(client, "guerra", "es", -8).status_code == 201
    assert termino_crear(client, "guerra", "es", -7).status_code == 409
    assert termino_crear(client, "guerra", "en", -7).status_code == 201
    assert termino_crear(client, "Guerra", "es", -6).status_code == 201


def test_api_rechaza_actualizacion_duplicada_y_preserva_terminos(client):
    primero = termino_crear(client, "guerra", "es", -8).json()
    segundo = termino_crear(client, "paz", "es", 8).json()

    put_response = client.put(
        f"/api/v1/dictionary/{segundo['id']}",
        json={"palabra": "guerra", "idioma": "es", "valor": 5},
    )
    patch_response = client.patch(
        f"/api/v1/dictionary/{segundo['id']}", json={"palabra": "guerra"}
    )

    assert put_response.status_code == 409
    assert patch_response.status_code == 409
    assert client.get(f"/api/v1/dictionary/{primero['id']}").json()["valor"] == -8
    assert client.get(f"/api/v1/dictionary/{segundo['id']}").json()["palabra"] == "paz"


@pytest.mark.parametrize("payload", [None, {}, {"palabra": " ", "idioma": "es", "valor": 1}, {"palabra": "x", "idioma": "fr", "valor": 1}])
def test_api_rechaza_body_o_campos_invalidos(client, payload):
    response = client.post("/api/v1/dictionary", json=payload)
    assert response.status_code == 400


def test_api_rechaza_patch_vacio_o_null(client):
    termino_id = termino_crear(client, "guerra").json()["id"]

    assert client.patch(f"/api/v1/dictionary/{termino_id}", json={}).status_code == 400
    assert client.patch(
        f"/api/v1/dictionary/{termino_id}", json={"valor": None}
    ).status_code == 400


def test_api_rechaza_busqueda_vacia_y_palabra_vacia_en_put_patch(client):
    termino_id = termino_crear(client, "guerra").json()["id"]

    assert client.get("/api/v1/dictionary?busqueda=").status_code == 200
    assert client.put(
        f"/api/v1/dictionary/{termino_id}",
        json={"palabra": " ", "idioma": "es", "valor": 1},
    ).status_code == 400
    assert client.patch(
        f"/api/v1/dictionary/{termino_id}", json={"palabra": " "}
    ).status_code == 400


def test_openapi_documenta_las_seis_operaciones_del_diccionario(client):
    paths = client.get("/api/openapi.json").json()["paths"]

    assert set(paths["/api/v1/dictionary"]) == {"get", "post"}
    assert set(paths["/api/v1/dictionary/{termino_id}"]) == {
        "get",
        "put",
        "patch",
        "delete",
    }
    assert "idioma" not in [
        parameter["name"]
        for parameter in paths["/api/v1/dictionary"]["get"].get("parameters", [])
    ]


def test_api_actualizacion_y_consulta_de_ids_inexistentes(client):
    assert client.put(
        "/api/v1/dictionary/77",
        json={"palabra": "x", "idioma": "es", "valor": 1},
    ).status_code == 404
    assert client.patch("/api/v1/dictionary/77", json={"valor": 1}).status_code == 404