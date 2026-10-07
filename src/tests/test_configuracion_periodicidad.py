from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.jobs.scheduler import reprogramar_periodicidad
from app.main import app
from app.models.configuracion import Configuracion
from app.repositories.configuracion import ConfiguracionRepository
from app.services.configuracion_service import actualizar_configuracion, consultar_configuracion


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


def crear_configuracion(database_session, valor=30):
    configuracion = Configuracion(
        clave="periodicidad_cron_minutos",
        valor=valor,
    )
    database_session.add(configuracion)
    database_session.commit()
    return configuracion


def test_get_config_devuelve_periodicidad_actual(client, database_session):
    crear_configuracion(database_session, 45)

    response = client.get("/api/v1/config")

    assert response.status_code == 200
    assert response.json() == {"periodicidad_cron_minutos": 45}


def test_put_config_actualiza_periodicidad_y_reprograma_scheduler(client, database_session):
    crear_configuracion(database_session, 30)

    with patch("app.jobs.scheduler.reprogramar_periodicidad") as reprogramar:
        response = client.put(
            "/api/v1/config",
            json={"periodicidad_cron_minutos": 60},
        )

    assert response.status_code == 200
    assert response.json() == {"periodicidad_cron_minutos": 60}
    persisted = database_session.execute(
        select(Configuracion).where(
            Configuracion.clave == "periodicidad_cron_minutos"
        )
    ).scalar_one()
    assert persisted.valor == 60
    reprogramar.assert_called_once_with(60)


@pytest.mark.parametrize("valor", [0, -1])
def test_put_config_rechaza_valor_invalido_y_conserva_anterior(
    client, database_session, valor
):
    crear_configuracion(database_session, 30)

    response = client.put(
        "/api/v1/config",
        json={"periodicidad_cron_minutos": valor},
    )

    assert response.status_code == 400
    assert set(response.json()) == {"codigo", "mensaje"}
    persisted = database_session.execute(
        select(Configuracion).where(
            Configuracion.clave == "periodicidad_cron_minutos"
        )
    ).scalar_one()
    assert persisted.valor == 30


def test_servicio_actualiza_conRepositorio_real_y_no_modifica_en_error(database_session):
    crear_configuracion(database_session, 30)
    repository = ConfiguracionRepository()

    result = actualizar_configuracion(
        database_session,
        45,
        repository=repository,
        reprogramar=lambda minutos: None,
    )

    assert result == {"periodicidad_cron_minutos": 45}
    assert consultar_configuracion(database_session, repository=repository) == 45


def test_repositorio_no_escribe_configuracion_invalida(database_session):
    crear_configuracion(database_session, 30)
    repository = ConfiguracionRepository()

    with pytest.raises(ValueError):
        repository.actualizar(
            database_session,
            0,
        )

    persisted = database_session.execute(
        select(Configuracion).where(
            Configuracion.clave == "periodicidad_cron_minutos"
        )
    ).scalar_one()
    assert persisted.valor == 30


def test_reprogramar_periodicidad_modifica_job_existente(monkeypatch):
    scheduler_instance = type(
        "SchedulerStub",
        (),
        {
            "running": True,
            "_eventloop": None,
            "modify_job": Mock(),
        },
    )()
    monkeypatch.setattr("app.jobs.scheduler.scheduler", scheduler_instance)

    reprogramar_periodicidad(90)

    scheduler_instance.modify_job.assert_called_once()
    kwargs = scheduler_instance.modify_job.call_args.kwargs
    assert kwargs["trigger"] == "interval"
    assert kwargs["minutes"] == 90
    assert kwargs["max_instances"] == 1
    assert kwargs["coalesce"] is True
