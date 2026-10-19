"""
Pruebas de la carga inicial del diccionario (PDF §4.2.2, HU-SENT-001).
SQLite en memoria; sin red.
"""
import csv
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.canal import CanalNoticias
from app.models.fuente import FuenteRSS
from app.models.noticia import Noticia
from app.models.termino_diccionario import TerminoDiccionario
from app.services.seed_diccionario_service import cargar_diccionario, leer_csv
from app.services.sentimiento_service import procesar_noticias, procesar_pendientes
from scripts import seed_diccionario


@pytest.fixture()
def session_factory():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
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


def _contar(db) -> int:
    return db.execute(select(func.count()).select_from(TerminoDiccionario)).scalar_one()


FILAS = [
    {"palabra": "war", "idioma": "en", "valor": -4},
    {"palabra": "peace", "idioma": "en", "valor": 4},
    {"palabra": "guerra", "idioma": "es", "valor": -4},
]


def test_dataset_real_es_valido():
    filas = leer_csv(seed_diccionario.RUTA_DATASET)
    claves = [(f["palabra"], f["idioma"]) for f in filas]
    assert len(claves) == len(set(claves))
    assert {f["idioma"] for f in filas} == {"es", "en"}
    assert all(-10 <= f["valor"] <= 10 and f["valor"] != 0 for f in filas)
    assert all(f["valor"] % 2 == 0 for f in filas)  # AFINN (-5..+5) × 2
    assert sum(f["idioma"] == "es" for f in filas) >= 400
    assert sum(f["idioma"] == "en" for f in filas) >= 3000


def test_carga_en_diccionario_vacio(db):
    resultado = cargar_diccionario(db, FILAS)
    assert (resultado.creados, resultado.omitidos) == (3, 0)
    assert _contar(db) == 3


def test_ejecucion_repetida_no_duplica(db):
    cargar_diccionario(db, FILAS)
    resultado = cargar_diccionario(db, FILAS)
    assert (resultado.creados, resultado.omitidos) == (0, 3)
    assert _contar(db) == 3


def test_no_sobrescribe_un_termino_ajustado_a_mano(db):
    db.add(TerminoDiccionario(palabra="war", idioma="en", valor=-10))
    db.commit()

    resultado = cargar_diccionario(db, FILAS)

    assert (resultado.creados, resultado.omitidos) == (2, 1)
    valor = db.scalars(
        select(TerminoDiccionario.valor).where(TerminoDiccionario.palabra == "war")
    ).one()
    assert valor == -10


def test_fila_invalida_no_crea_nada(db):
    filas = FILAS + [{"palabra": "terrible", "idioma": "en", "valor": 12}]
    with pytest.raises(ValueError):
        cargar_diccionario(db, filas)
    assert _contar(db) == 0


def test_filas_repetidas_en_el_dataset_se_crean_una_vez(db):
    resultado = cargar_diccionario(db, FILAS + FILAS[:1])
    assert (resultado.creados, resultado.omitidos) == (3, 1)


def test_la_carga_marca_noticias_para_recalculo(db):
    canal = CanalNoticias(nombre="Canal", continente="Europa")
    db.add(canal)
    db.flush()
    fuente = FuenteRSS(canal_id=canal.id, url="https://f.example.test/rss", categoria_iptc="11000000")
    db.add(fuente)
    db.flush()
    noticia = Noticia(
        fuente_rss_id=fuente.id,
        identificador_item_rss="n1",
        titulo="War ends with peace",
        enlace_original="https://example.test/1",
        fecha_registro=datetime.now(timezone.utc),
    )
    db.add(noticia)
    db.commit()
    procesar_noticias(db, [noticia])
    assert noticia.valor_humor is None

    cargar_diccionario(db, FILAS)
    procesar_pendientes(db)

    assert (noticia.valor_humor, noticia.cantidad_terminos_evaluados) == (0.0, 2)


def test_leer_csv_rechaza_valor_no_entero(tmp_path):
    ruta = tmp_path / "malo.csv"
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["palabra", "idioma", "valor", "origen"])
        escritor.writerow(["war", "en", "muy malo", "x"])
    with pytest.raises(ValueError):
        leer_csv(ruta)


def test_script_carga_el_dataset_real_y_es_idempotente(session_factory, capsys):
    assert seed_diccionario.main(session_factory=session_factory) == 0
    salida = capsys.readouterr().out
    assert "términos creados, 0 ya existían" in salida

    assert seed_diccionario.main(session_factory=session_factory) == 0
    assert " 0 términos creados" in capsys.readouterr().out


def test_script_con_error_termina_con_1(session_factory, tmp_path, capsys):
    ruta = tmp_path / "malo.csv"
    ruta.write_text("palabra,idioma,valor,origen\nwar,fr,-4,x\n", encoding="utf-8")
    assert seed_diccionario.main(ruta, session_factory) == 1
    assert "cancelada" in capsys.readouterr().err
