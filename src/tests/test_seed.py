"""
Pruebas de la carga inicial de fuentes RSS por continente.

Origina en: HU-RSS-009-v2 (criterios de aceptación Gherkin).
Usan SQLite en memoria y un dataset sintético bajo example.test, salvo la
prueba que valida la forma del dataset real. Ninguna prueba hace HTTP.
"""
import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.canal import CanalNoticias
from app.models.fuente import FuenteRSS
from app.repositories.fuentes import FuenteRSSRepository
from app.services.seed_service import (
    CONTINENTES_REQUERIDOS,
    ContinenteFaltanteError,
    cargar_dataset,
)
from scripts import seed as script_seed


def _dataset_sintetico() -> list[dict]:
    return [
        {
            # Nombre ASCII: el lower() de SQLite no convierte letras con tilde
            # (en MySQL sí), y buscar_por_nombre compara en minúsculas.
            "nombre": f"Canal {i}",
            "continente": continente,
            "pais": None,
            "fuentes": [
                {"url": f"https://{i}-a.example.test/rss", "categoria_iptc": "11000000"},
                {"url": f"https://{i}-b.example.test/rss", "categoria_iptc": "04000000"},
            ],
        }
        for i, continente in enumerate(CONTINENTES_REQUERIDOS)
    ]


@pytest.fixture()
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db(session_factory):
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def _contar(db, modelo) -> int:
    return db.execute(select(func.count()).select_from(modelo)).scalar_one()


def test_carga_en_base_vacia_cubre_los_5_continentes(db):
    resultado = cargar_dataset(db, _dataset_sintetico())

    assert resultado.canales_creados == 5
    assert resultado.fuentes_creadas == 10
    for continente in CONTINENTES_REQUERIDOS:
        canal = db.execute(
            select(CanalNoticias).where(CanalNoticias.continente == continente)
        ).scalar_one()
        assert len(canal.fuentes) == 2
    assert all(f.canal_id is not None and f.activo for f in db.scalars(select(FuenteRSS)))


def test_ejecucion_repetida_no_duplica(db):
    cargar_dataset(db, _dataset_sintetico())
    resultado = cargar_dataset(db, _dataset_sintetico())

    assert (resultado.canales_creados, resultado.fuentes_creadas) == (0, 0)
    assert _contar(db, CanalNoticias) == 5
    assert _contar(db, FuenteRSS) == 10


def test_canal_existente_con_fuente_faltante(db):
    dataset = _dataset_sintetico()
    parcial = _dataset_sintetico()
    parcial[0]["fuentes"] = parcial[0]["fuentes"][:1]
    cargar_dataset(db, parcial)
    canal_id = db.execute(
        select(CanalNoticias.id).where(CanalNoticias.nombre == dataset[0]["nombre"])
    ).scalar_one()

    resultado = cargar_dataset(db, dataset)

    assert (resultado.canales_creados, resultado.fuentes_creadas) == (0, 1)
    nueva = db.execute(
        select(FuenteRSS).where(FuenteRSS.url == dataset[0]["fuentes"][1]["url"])
    ).scalar_one()
    assert nueva.canal_id == canal_id


def test_dataset_sin_un_continente_no_crea_nada(db):
    dataset = [c for c in _dataset_sintetico() if c["continente"] != "Oceanía"]

    with pytest.raises(ContinenteFaltanteError) as error:
        cargar_dataset(db, dataset)

    assert error.value.faltantes == ["Oceanía"]
    assert _contar(db, CanalNoticias) == 0


def test_canal_sin_fuentes_no_cuenta_como_cobertura(db):
    dataset = _dataset_sintetico()
    dataset[1]["fuentes"] = []

    with pytest.raises(ContinenteFaltanteError) as error:
        cargar_dataset(db, dataset)

    assert error.value.faltantes == ["Europa"]


def test_fallo_de_persistencia_revierte_toda_la_carga(db, monkeypatch):
    original = FuenteRSSRepository.agregar_sin_confirmar
    llamadas = {"n": 0}

    def fallar_en_la_tercera(self, sesion, fuente):
        llamadas["n"] += 1
        if llamadas["n"] == 3:
            raise OperationalError("INSERT", {}, Exception("base caída"))
        return original(self, sesion, fuente)

    monkeypatch.setattr(FuenteRSSRepository, "agregar_sin_confirmar", fallar_en_la_tercera)

    with pytest.raises(OperationalError):
        cargar_dataset(db, _dataset_sintetico())

    assert _contar(db, CanalNoticias) == 0
    assert _contar(db, FuenteRSS) == 0


def test_categoria_iptc_invalida_revierte_toda_la_carga(db):
    dataset = _dataset_sintetico()
    dataset[-1]["fuentes"][0]["categoria_iptc"] = "99999999"

    with pytest.raises(ValidationError):
        cargar_dataset(db, dataset)

    assert _contar(db, CanalNoticias) == 0


def test_la_carga_no_consulta_los_feeds(db, monkeypatch):
    import httpx

    def prohibido(*args, **kwargs):
        raise AssertionError("El seed no debe hacer solicitudes HTTP")

    monkeypatch.setattr(httpx.Client, "send", prohibido)
    monkeypatch.setattr(httpx.AsyncClient, "send", prohibido)

    resultado = cargar_dataset(db, _dataset_sintetico())

    assert resultado.fuentes_creadas == 10


def test_dataset_real_es_valido():
    dataset = script_seed.CANALES_SEED
    nombres = [c["nombre"] for c in dataset]
    urls = [f["url"] for c in dataset for f in c["fuentes"]]

    assert len(nombres) == len(set(nombres)) == 11
    assert len(urls) == len(set(urls)) == 20
    for continente in CONTINENTES_REQUERIDOS:
        fuentes = [f for c in dataset if c["continente"] == continente for f in c["fuentes"]]
        assert len(fuentes) == 4


def test_script_informa_y_termina_con_0(session_factory, capsys):
    assert script_seed.main(_dataset_sintetico(), session_factory) == 0
    assert "5 canales y 10 fuentes creados" in capsys.readouterr().out

    assert script_seed.main(_dataset_sintetico(), session_factory) == 0
    assert "0 canales y 0 fuentes creados" in capsys.readouterr().out


def test_script_con_continente_faltante_termina_con_1(session_factory, capsys):
    dataset = [c for c in _dataset_sintetico() if c["continente"] != "Asia"]

    assert script_seed.main(dataset, session_factory) == 1
    assert "Asia" in capsys.readouterr().err


def test_script_con_error_termina_con_1(session_factory, capsys):
    dataset = _dataset_sintetico()
    dataset[0]["fuentes"][0]["url"] = "no-es-una-url"

    assert script_seed.main(dataset, session_factory) == 1
    assert "revertida" in capsys.readouterr().err


def test_script_carga_el_dataset_real(session_factory, capsys):
    assert script_seed.main(None, session_factory) == 0
    assert "11 canales y 20 fuentes creados" in capsys.readouterr().out
