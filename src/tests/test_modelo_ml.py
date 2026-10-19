"""
Pruebas del modelo de ML de humor (HU-SENT-006) y de su uso en el cálculo
híbrido (HU-SENT-002-v3). ADR-04.

DoD de HU-SENT-006: el servicio de embeddings siempre está mockeado (cliente
falso o respx); nunca hay llamadas reales a Google Gemini. SQLite en memoria y
archivos .joblib en un directorio temporal.
"""
import json
from datetime import datetime

import httpx
import joblib
import pytest
import respx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.database import Base, get_db
from app.main import app
from app.models.canal import CanalNoticias
from app.models.fuente import FuenteRSS
from app.models.modelo_sentimiento import ModeloSentimiento
from app.models.noticia import Noticia
from app.models.termino_diccionario import TerminoDiccionario
from app.services import modelo_ml_service
from app.services.embeddings_service import (
    CircuitBreaker,
    CircuitoAbiertoError,
    ClienteEmbeddingsGemini,
    ErrorServicioEmbeddings,
)
from app.services.modelo_ml_service import (
    DatosInsuficientesError,
    MLNoConfiguradoError,
    ProveedorRegresor,
    entrenar_modelo,
    proveedor_activo,
)
from app.services.sentimiento_service import METODO_DICCIONARIO, METODO_ML, procesar_noticias

URL = "https://gemini.example.test/v1beta"
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


@pytest.fixture(autouse=True)
def configuracion_ml(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "ml_directorio_modelos", str(tmp_path / "modelos"))
    monkeypatch.setattr(settings, "ml_umbral_entrenamiento", 10)
    monkeypatch.setattr(settings, "gemini_api_key", "")
    monkeypatch.setattr(settings, "gemini_url_base", URL)
    modelo_ml_service.invalidar_cache()
    yield
    modelo_ml_service.invalidar_cache()


@pytest.fixture()
def fuente(db):
    canal = CanalNoticias(nombre="Canal ML", continente="Europa")
    db.add(canal)
    db.flush()
    fuente = FuenteRSS(canal_id=canal.id, url="https://ml.example.test", categoria_iptc="11000000")
    db.add(fuente)
    db.commit()
    return fuente


_n = [0]


def _noticia(db, fuente, titulo, valor=None, metodo=METODO_DICCIONARIO):
    _n[0] += 1
    noticia = Noticia(
        fuente_rss_id=fuente.id,
        identificador_item_rss=f"ml-{_n[0]}",
        titulo=titulo,
        enlace_original=f"https://ml.example.test/{_n[0]}",
        fecha_registro=AHORA,
        valor_humor=valor,
        metodo_calculo=metodo,
    )
    db.add(noticia)
    db.commit()
    return noticia


class ClienteFalso:
    """Embeddings deterministas: el valor está codificado en el título "v=<n>"."""

    modelo = "embeddings-falso-1"

    def __init__(self, falla=False):
        self.falla = falla
        self.llamadas = 0

    def _vector(self, texto):
        valor = float(texto.split("v=")[1].split()[0]) if "v=" in texto else 0.0
        return [valor, 1.0, -valor]

    def embeber(self, texto):
        self.llamadas += 1
        if self.falla:
            raise ErrorServicioEmbeddings("caído")
        return self._vector(texto)

    def embeber_lote(self, textos):
        if self.falla:
            raise ErrorServicioEmbeddings("caído")
        return [self._vector(t) for t in textos]


def _datos(db, fuente, cantidad=20):
    for i in range(cantidad):
        valor = (i % 9) - 4
        _noticia(db, fuente, f"noticia v={valor}", valor=float(valor))


def _modelos(db):
    return db.execute(select(ModeloSentimiento).order_by(ModeloSentimiento.id)).scalars().all()


# --- HU-SENT-006: entrenamiento ---------------------------------------------

def test_entrenamiento_exitoso_registra_y_activa_una_version(db, fuente, tmp_path):
    _datos(db, fuente)

    modelo = entrenar_modelo(db, cliente=ClienteFalso(), ahora=AHORA)

    assert modelo.activo is True
    assert modelo.version == "20261019T120000000000Z"
    assert modelo.modelo_embeddings_usado == "embeddings-falso-1"
    assert modelo.fecha_entrenamiento == AHORA
    assert 0 <= modelo.mae_evaluacion < 0.5  # relación lineal: el regresor la aprende
    assert (tmp_path / "modelos" / f"modelo-sentimiento-{modelo.version}.joblib").exists()


def test_un_nuevo_entrenamiento_desactiva_la_version_anterior(db, fuente):
    _datos(db, fuente)
    primero = entrenar_modelo(db, cliente=ClienteFalso(), ahora=AHORA)
    segundo = entrenar_modelo(db, cliente=ClienteFalso(), ahora=datetime(2026, 10, 20))

    estados = {m.id: m.activo for m in _modelos(db)}
    assert estados == {primero.id: False, segundo.id: True}


def test_datos_insuficientes_no_afecta_al_modelo_activo(db, fuente):
    _datos(db, fuente)
    activo = entrenar_modelo(db, cliente=ClienteFalso(), ahora=AHORA)
    db.query(Noticia).delete()
    db.commit()
    _datos(db, fuente, cantidad=9)

    with pytest.raises(DatosInsuficientesError) as error:
        entrenar_modelo(db, cliente=ClienteFalso())

    assert (error.value.disponibles, error.value.umbral) == (9, 10)
    assert [(m.id, m.activo) for m in _modelos(db)] == [(activo.id, True)]


def test_solo_entrena_con_noticias_evaluadas_por_diccionario(db, fuente):
    _datos(db, fuente, cantidad=9)
    _noticia(db, fuente, "calculada por ml v=3", valor=3.0, metodo=METODO_ML)
    _noticia(db, fuente, "sin terminos", valor=None)

    with pytest.raises(DatosInsuficientesError):
        entrenar_modelo(db, cliente=ClienteFalso())


def test_fallo_de_embeddings_cancela_sin_afectar_el_modelo_activo(db, fuente, tmp_path):
    _datos(db, fuente)
    activo = entrenar_modelo(db, cliente=ClienteFalso(), ahora=AHORA)

    with pytest.raises(ErrorServicioEmbeddings):
        entrenar_modelo(db, cliente=ClienteFalso(falla=True), ahora=datetime(2026, 10, 20))

    assert [(m.id, m.activo) for m in _modelos(db)] == [(activo.id, True)]
    assert len(list((tmp_path / "modelos").iterdir())) == 1


def test_sin_api_key_no_se_puede_entrenar(db, fuente):
    _datos(db, fuente)
    with pytest.raises(MLNoConfiguradoError):
        entrenar_modelo(db)


# --- POST /api/v1/trainings ---------------------------------------------------

@pytest.fixture()
def client(db):
    def override():
        yield db

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_post_trainings_201(client, db, fuente, monkeypatch):
    _datos(db, fuente)
    monkeypatch.setattr(modelo_ml_service, "_cliente_por_defecto", lambda: ClienteFalso())

    respuesta = client.post("/api/v1/trainings")

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert set(cuerpo) == {
        "id", "version", "modelo_embeddings_usado", "mae_evaluacion", "fecha_entrenamiento", "activo",
    }
    assert cuerpo["activo"] is True


def test_post_trainings_409_con_datos_insuficientes(client, db, fuente):
    _datos(db, fuente, cantidad=3)
    respuesta = client.post("/api/v1/trainings")
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "DATOS_INSUFICIENTES"


def test_post_trainings_502_si_falla_el_servicio(client, db, fuente, monkeypatch):
    _datos(db, fuente)
    monkeypatch.setattr(modelo_ml_service, "_cliente_por_defecto", lambda: ClienteFalso(falla=True))
    respuesta = client.post("/api/v1/trainings")
    assert respuesta.status_code == 502
    assert respuesta.json()["codigo"] == "SERVICIO_EMBEDDINGS_NO_DISPONIBLE"
    assert db.execute(select(func.count()).select_from(ModeloSentimiento)).scalar_one() == 0


def test_post_trainings_503_sin_api_key(client, db, fuente):
    _datos(db, fuente)
    respuesta = client.post("/api/v1/trainings")
    assert respuesta.status_code == 503
    assert respuesta.json()["codigo"] == "ML_NO_CONFIGURADO"


# --- Cliente de Gemini (respx, sin red) --------------------------------------

def _cliente(esperas=None):
    return ClienteEmbeddingsGemini(
        api_key="clave-secreta",
        modelo="gemini-embedding-001",
        url_base=URL,
        esperar=(esperas.append if esperas is not None else lambda s: None),
    )


@respx.mock
def test_embeber_usa_la_cabecera_de_api_key_y_recorta_el_texto(monkeypatch):
    monkeypatch.setattr(settings, "embeddings_max_caracteres", 5)
    ruta = respx.post(f"{URL}/models/gemini-embedding-001:embedContent").mock(
        return_value=httpx.Response(200, json={"embedding": {"values": [0.1, 0.2]}})
    )

    assert _cliente().embeber("texto largo") == [0.1, 0.2]

    solicitud = ruta.calls.last.request
    assert solicitud.headers["x-goog-api-key"] == "clave-secreta"
    assert "clave-secreta" not in str(solicitud.url)
    assert b'"text":"texto"' in solicitud.content.replace(b" ", b"")


@respx.mock
def test_embeber_lote_divide_en_solicitudes(monkeypatch):
    monkeypatch.setattr(settings, "embeddings_lote", 2)
    def responder(request):
        cantidad = len(json.loads(request.content)["requests"])
        return httpx.Response(200, json={"embeddings": [{"values": [1.0]}] * cantidad})

    ruta = respx.post(f"{URL}/models/gemini-embedding-001:batchEmbedContents").mock(
        side_effect=responder
    )

    assert _cliente().embeber_lote(["a", "b", "c"]) == [[1.0], [1.0], [1.0]]
    assert ruta.call_count == 2


@respx.mock
def test_reintenta_con_backoff_exponencial_ante_fallos_transitorios():
    respx.post(f"{URL}/models/gemini-embedding-001:embedContent").mock(
        side_effect=[
            httpx.Response(503),
            httpx.TimeoutException("lento"),
            httpx.Response(200, json={"embedding": {"values": [1.0]}}),
        ]
    )
    esperas = []

    assert _cliente(esperas).embeber("hola") == [1.0]
    assert esperas == [0.5, 1.0]


@respx.mock
def test_reintentos_acotados_terminan_en_error():
    ruta = respx.post(f"{URL}/models/gemini-embedding-001:embedContent").mock(
        return_value=httpx.Response(429)
    )
    esperas = []

    with pytest.raises(ErrorServicioEmbeddings):
        _cliente(esperas).embeber("hola")

    assert ruta.call_count == settings.embeddings_max_reintentos + 1
    assert esperas == [0.5, 1.0, 2.0]


@respx.mock
def test_no_reintenta_errores_del_cliente():
    ruta = respx.post(f"{URL}/models/gemini-embedding-001:embedContent").mock(
        return_value=httpx.Response(400)
    )
    with pytest.raises(ErrorServicioEmbeddings):
        _cliente().embeber("hola")
    assert ruta.call_count == 1


@respx.mock
def test_respuesta_inesperada_es_error():
    respx.post(f"{URL}/models/gemini-embedding-001:embedContent").mock(
        return_value=httpx.Response(200, json={"otra": "cosa"})
    )
    with pytest.raises(ErrorServicioEmbeddings):
        _cliente().embeber("hola")


@respx.mock
def test_lote_con_cantidad_distinta_es_error():
    respx.post(f"{URL}/models/gemini-embedding-001:batchEmbedContents").mock(
        return_value=httpx.Response(200, json={"embeddings": [{"values": [1.0]}]})
    )
    with pytest.raises(ErrorServicioEmbeddings):
        _cliente().embeber_lote(["a", "b"])


def test_cliente_sin_api_key_es_error():
    with pytest.raises(ErrorServicioEmbeddings):
        ClienteEmbeddingsGemini(api_key="")


# --- Circuit Breaker -----------------------------------------------------------

def test_circuit_breaker_abre_rechaza_y_se_recupera():
    reloj = [0.0]
    circuito = CircuitBreaker(umbral_fallos=2, espera_segundos=60, reloj=lambda: reloj[0])

    def falla():
        raise RuntimeError("caído")

    for _ in range(2):
        with pytest.raises(RuntimeError):
            circuito.ejecutar(falla)
    assert circuito.abierto
    with pytest.raises(CircuitoAbiertoError):
        circuito.ejecutar(lambda: "no se llama")

    reloj[0] = 61.0  # semiabierto: un intento de prueba
    with pytest.raises(RuntimeError):
        circuito.ejecutar(falla)
    assert circuito.abierto  # el intento falló: vuelve a abrir

    reloj[0] = 130.0
    assert circuito.ejecutar(lambda: "ok") == "ok"
    assert not circuito.abierto


# --- HU-SENT-002-v3: uso del modelo activo -----------------------------------

def test_sin_api_key_no_hay_proveedor(db, fuente):
    _datos(db, fuente)
    entrenar_modelo(db, cliente=ClienteFalso(), ahora=AHORA)
    assert proveedor_activo(db) is None


def test_con_api_key_y_sin_modelo_no_hay_proveedor(db, monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "clave")
    assert proveedor_activo(db) is None


def test_proveedor_carga_el_modelo_activo_y_lo_cachea(db, fuente, monkeypatch):
    _datos(db, fuente)
    modelo = entrenar_modelo(db, cliente=ClienteFalso(), ahora=AHORA)
    monkeypatch.setattr(settings, "gemini_api_key", "clave")

    proveedor = proveedor_activo(db)

    assert isinstance(proveedor, ProveedorRegresor)
    assert proveedor.modelo_id == modelo.id
    assert proveedor.cliente.modelo == "embeddings-falso-1"
    assert proveedor_activo(db) is proveedor


def test_archivo_del_modelo_ilegible_vuelve_al_diccionario(db, fuente, monkeypatch, tmp_path):
    _datos(db, fuente)
    modelo = entrenar_modelo(db, cliente=ClienteFalso(), ahora=AHORA)
    open(modelo.ruta_archivo, "wb").write(b"no es un joblib")
    modelo_ml_service.invalidar_cache()
    monkeypatch.setattr(settings, "gemini_api_key", "clave")

    assert proveedor_activo(db) is None


def test_prediccion_se_limita_a_la_escala_del_diccionario():
    class Regresor:
        def predict(self, x):
            return [25.0]

    proveedor = ProveedorRegresor(1, Regresor(), ClienteFalso(), CircuitBreaker(5, 60))
    assert proveedor.predecir("v=1") == 10.0


def test_noticia_calculada_con_ml_guarda_la_version_del_modelo(db, fuente, monkeypatch):
    _datos(db, fuente)
    modelo = entrenar_modelo(db, cliente=ClienteFalso(), ahora=AHORA)
    db.add(TerminoDiccionario(palabra="guerra", idioma="es", valor=-8))
    db.commit()
    nueva = _noticia(db, fuente, "guerra v=3", metodo=None)
    regresor = joblib.load(modelo.ruta_archivo)
    proveedor = ProveedorRegresor(modelo.id, regresor, ClienteFalso(), CircuitBreaker(5, 60))

    procesar_noticias(db, [nueva], proveedor_ml=proveedor)

    db.refresh(nueva)
    assert nueva.metodo_calculo == METODO_ML
    assert nueva.modelo_sentimiento_id == modelo.id
    assert nueva.valor_humor == pytest.approx(3.0, abs=0.5)
    assert nueva.polarizacion_terminos == 0.0  # HU-SENT-003: sale del diccionario
    assert len(nueva.coincidencias) == 1  # HU-SENT-008: también en el camino ML


def test_con_el_circuito_abierto_se_usa_el_diccionario(db, fuente):
    db.add(TerminoDiccionario(palabra="guerra", idioma="es", valor=-8))
    db.commit()
    nueva = _noticia(db, fuente, "guerra", metodo=None)
    cliente = ClienteFalso(falla=True)
    circuito = CircuitBreaker(umbral_fallos=1, espera_segundos=60)

    class Regresor:
        def predict(self, x):
            return [0.0]

    proveedor = ProveedorRegresor(1, Regresor(), cliente, circuito)
    procesar_noticias(db, [nueva], proveedor_ml=proveedor)  # falla y abre el circuito
    otra = _noticia(db, fuente, "guerra otra vez", metodo=None)
    procesar_noticias(db, [otra], proveedor_ml=proveedor)

    db.refresh(nueva)
    db.refresh(otra)
    assert (nueva.metodo_calculo, otra.metodo_calculo) == (METODO_DICCIONARIO, METODO_DICCIONARIO)
    assert otra.valor_humor == -8.0
    assert otra.modelo_sentimiento_id is None
    assert cliente.llamadas == 1  # con el circuito abierto ya no se llamó al servicio
