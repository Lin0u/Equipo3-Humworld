import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.exceptions import ChannelNameConflictError, UniqueConstraintViolation
from app.main import app
from app.models.canal import CanalNoticias
from app.repositories.canales import CanalNoticiasRepository
from app.schemas.canal import CanalNoticiasCrear
from app.services.canal_service import crear_canal


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


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