"""
Pruebas del purgado de noticias antiguas.

Origina en: HU-ADMIN-001 (caducidad en /config), HU-ADMIN-002 (purgado
automático) y HU-ADMIN-003 (DELETE /api/v1/news). PDF §4.2.5.
SQLite en memoria; sin red ni scheduler real.
"""
from datetime import date, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.exceptions import FechaPurgadoInvalidaError
from app.jobs import scheduler as scheduler_module
from app.main import app
from app.models.canal import CanalNoticias
from app.models.coincidencia_termino import CoincidenciaTermino
from app.models.configuracion import Configuracion
from app.models.fuente import FuenteRSS
from app.models.noticia import Noticia
from app.models.termino_diccionario import TerminoDiccionario
from app.services.purgado_service import purgar_anteriores_a, purgar_por_caducidad

AHORA = datetime(2026, 10, 19, 12, 0, 0)


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


@pytest.fixture()
def fuente(db):
    canal = CanalNoticias(nombre="Canal purgado", continente="Europa")
    db.add(canal)
    db.flush()
    fuente = FuenteRSS(canal_id=canal.id, url="https://purgado.example.test", categoria_iptc="11000000")
    db.add(fuente)
    db.commit()
    return fuente


_n = [0]


def _noticia(db, fuente, registrada: datetime, terminos=()) -> Noticia:
    _n[0] += 1
    noticia = Noticia(
        fuente_rss_id=fuente.id,
        identificador_item_rss=f"purgado-{_n[0]}",
        titulo=f"Noticia {_n[0]}",
        enlace_original=f"https://purgado.example.test/{_n[0]}",
        fecha_registro=registrada,
        coincidencias=[CoincidenciaTermino(termino_id=t.id) for t in terminos],
    )
    db.add(noticia)
    db.commit()
    return noticia


def _config(db, caducidad=None, periodicidad=30):
    db.add(Configuracion(clave="periodicidad_cron_minutos", valor=periodicidad))
    if caducidad is not None:
        db.add(Configuracion(clave="caducidad_noticias_dias", valor=caducidad))
    db.commit()


def _cantidad(db, modelo) -> int:
    return db.execute(select(func.count()).select_from(modelo)).scalar_one()


# --- HU-ADMIN-002: purgado automático -------------------------------------

def test_purgado_elimina_solo_las_noticias_caducadas(db, fuente):
    _config(db, caducidad=90)
    vieja_id = _noticia(db, fuente, AHORA - timedelta(days=91)).id
    _noticia(db, fuente, AHORA - timedelta(days=89))
    _noticia(db, fuente, AHORA)

    resultado = purgar_por_caducidad(db, ahora=AHORA)

    assert resultado["noticias_eliminadas"] == 1
    assert resultado["fecha_limite"] == AHORA - timedelta(days=90)
    assert _cantidad(db, Noticia) == 2
    assert db.get(Noticia, vieja_id) is None


def test_purgado_respeta_el_limite_exacto(db, fuente):
    _config(db, caducidad=10)
    _noticia(db, fuente, AHORA - timedelta(days=10))  # justo en el límite: se conserva

    assert purgar_por_caducidad(db, ahora=AHORA)["noticias_eliminadas"] == 0
    assert _cantidad(db, Noticia) == 1


def test_purgado_borra_las_coincidencias_de_las_noticias_eliminadas(db, fuente):
    _config(db, caducidad=30)
    termino = TerminoDiccionario(palabra="guerra", idioma="es", valor=-8)
    db.add(termino)
    db.commit()
    _noticia(db, fuente, AHORA - timedelta(days=40), terminos=[termino])
    conservada_id = _noticia(db, fuente, AHORA, terminos=[termino]).id

    purgar_por_caducidad(db, ahora=AHORA)

    filas = db.execute(select(CoincidenciaTermino)).scalars().all()
    assert [f.noticia_id for f in filas] == [conservada_id]
    assert _cantidad(db, TerminoDiccionario) == 1  # el diccionario no se toca


def test_sin_fila_de_caducidad_usa_90_dias(db, fuente):
    _config(db)  # solo periodicidad: base sin la migración c3f8a2d6e9b1
    _noticia(db, fuente, AHORA - timedelta(days=91))
    _noticia(db, fuente, AHORA - timedelta(days=89))

    assert purgar_por_caducidad(db, ahora=AHORA)["noticias_eliminadas"] == 1


def test_purgado_sin_noticias_caducadas_no_falla(db, fuente):
    _config(db, caducidad=90)
    assert purgar_por_caducidad(db, ahora=AHORA)["noticias_eliminadas"] == 0


def test_el_scheduler_registra_el_job_de_purgado(monkeypatch):
    registrados = []

    class SchedulerFalso:
        running = False

        def add_job(self, func, **kwargs):
            registrados.append((kwargs["id"], kwargs))

        def start(self):
            pass

    monkeypatch.setattr(scheduler_module, "AsyncIOScheduler", SchedulerFalso)
    monkeypatch.setattr(scheduler_module, "scheduler", SchedulerFalso())
    monkeypatch.setattr(scheduler_module, "_obtener_periodicidad_actual", lambda: 30)

    scheduler_module.iniciar_scheduler()

    jobs = dict(registrados)
    assert scheduler_module.PURGADO_JOB_ID in jobs
    assert jobs[scheduler_module.PURGADO_JOB_ID]["hours"] == 24


# --- HU-ADMIN-003: purgado manual -----------------------------------------

def test_purgado_manual_por_fecha(db, fuente):
    _noticia(db, fuente, datetime(2026, 9, 30, 23, 59))
    _noticia(db, fuente, datetime(2026, 10, 1, 0, 0))  # el día indicado se conserva

    resultado = purgar_anteriores_a(db, date(2026, 10, 1), hoy=date(2026, 10, 19))

    assert resultado["noticias_eliminadas"] == 1
    assert _cantidad(db, Noticia) == 1


def test_purgado_manual_rechaza_fecha_futura(db, fuente):
    _noticia(db, fuente, AHORA)
    with pytest.raises(FechaPurgadoInvalidaError):
        purgar_anteriores_a(db, date(2026, 10, 20), hoy=date(2026, 10, 19))
    assert _cantidad(db, Noticia) == 1


def test_delete_news_con_fecha_responde_200_con_resumen(client, db, fuente):
    _noticia(db, fuente, datetime(2020, 1, 1))
    _noticia(db, fuente, datetime(2020, 1, 1))

    respuesta = client.delete("/api/v1/news", params={"fecha_anterior_a": "2021-01-01"})

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "noticias_eliminadas": 2,
        "fecha_limite": "2021-01-01T00:00:00",
    }
    assert _cantidad(db, Noticia) == 0


def test_delete_news_sin_fecha_aplica_la_caducidad(client, db, fuente):
    _config(db, caducidad=1)
    _noticia(db, fuente, datetime(2020, 1, 1))

    respuesta = client.delete("/api/v1/news")

    assert respuesta.status_code == 200
    assert respuesta.json()["noticias_eliminadas"] == 1


def test_delete_news_fecha_futura_responde_400(client, db, fuente):
    _noticia(db, fuente, datetime(2020, 1, 1))

    respuesta = client.delete("/api/v1/news", params={"fecha_anterior_a": "2999-01-01"})

    assert respuesta.status_code == 400
    assert respuesta.json()["codigo"] == "FECHA_INVALIDA"
    assert _cantidad(db, Noticia) == 1


def test_delete_news_fecha_mal_formada_responde_400(client, db, fuente):
    respuesta = client.delete("/api/v1/news", params={"fecha_anterior_a": "ayer"})
    assert respuesta.status_code == 400


# --- HU-ADMIN-001: caducidad en /config -----------------------------------

def test_get_config_incluye_la_caducidad(client, db):
    _config(db, caducidad=60, periodicidad=45)

    respuesta = client.get("/api/v1/config")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"periodicidad_cron_minutos": 45, "caducidad_noticias_dias": 60}


def test_put_config_actualiza_la_caducidad(client, db, monkeypatch):
    _config(db, caducidad=90)
    monkeypatch.setattr(scheduler_module, "reprogramar_periodicidad", lambda minutos: None)

    respuesta = client.put(
        "/api/v1/config",
        json={"periodicidad_cron_minutos": 30, "caducidad_noticias_dias": 15},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["caducidad_noticias_dias"] == 15
    assert db.get(Configuracion, "caducidad_noticias_dias").valor == 15


def test_put_config_sin_caducidad_la_conserva(client, db, monkeypatch):
    _config(db, caducidad=90)
    monkeypatch.setattr(scheduler_module, "reprogramar_periodicidad", lambda minutos: None)

    respuesta = client.put("/api/v1/config", json={"periodicidad_cron_minutos": 60})

    assert respuesta.status_code == 200
    assert respuesta.json() == {"periodicidad_cron_minutos": 60, "caducidad_noticias_dias": 90}


@pytest.mark.parametrize("caducidad", [0, -5])
def test_put_config_rechaza_caducidad_invalida_sin_cambiar_nada(client, db, caducidad):
    _config(db, caducidad=90, periodicidad=30)

    respuesta = client.put(
        "/api/v1/config",
        json={"periodicidad_cron_minutos": 45, "caducidad_noticias_dias": caducidad},
    )

    assert respuesta.status_code == 400
    assert db.get(Configuracion, "caducidad_noticias_dias").valor == 90
    assert db.get(Configuracion, "periodicidad_cron_minutos").valor == 30


def test_delete_news_es_idempotente(client, db, fuente):
    _noticia(db, fuente, datetime(2020, 1, 1))
    params = {"fecha_anterior_a": "2021-01-01"}

    assert client.delete("/api/v1/news", params=params).json()["noticias_eliminadas"] == 1
    segunda = client.delete("/api/v1/news", params=params)

    assert segunda.status_code == 200
    assert segunda.json()["noticias_eliminadas"] == 0
