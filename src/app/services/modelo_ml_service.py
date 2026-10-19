"""
Entrenamiento, versionado y uso del modelo de ML de humor.

Origina en: HU-SENT-006 (entrenamiento y versionado, POST /api/v1/trainings) y
HU-SENT-002-v3 (camino ML del cálculo híbrido). Arquitectura: ADR-004.

AVISO (instrucciones del proyecto, sección 12): este módulo contiene lógica de
negocio del modelo de sentimiento. Debe ser revisado por el equipo antes de
fusionarse. Las cifras (umbral 1.000, validación 20 %, alpha de Ridge 1.0) son
valores propuestos, no ratificados.

Resumen del flujo de entrenamiento (ADR-004):
1. Datos: noticias con metodo_calculo = "diccionario" y valor_humor no nulo.
   Si no alcanzan ml_umbral_entrenamiento → DatosInsuficientesError (409).
2. Features: embeddings de "título + contenido" (Google Gemini Embedding).
3. Regresor Ridge de scikit-learn, con partición fija entrenamiento/validación
   (semilla 42, reproducible).
4. Evaluación: MAE contra el valor del diccionario en validación. Limitación
   metodológica (ADR-004, punto 6): el diccionario es la única referencia de
   verdad; el MAE mide cuánto se aproxima el modelo al diccionario, no si lo
   supera.
5. Versionado: .joblib en ml_directorio_modelos + fila en modelos_sentimiento,
   que pasa a ser la versión activa. Si algo falla antes del registro, el
   modelo activo previo no cambia.
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.modelo_sentimiento import ModeloSentimiento
from app.repositories.modelos_sentimiento import ModeloSentimientoRepository
from app.services.embeddings_service import (
    CircuitBreaker,
    ClienteEmbeddingsGemini,
    ErrorServicioEmbeddings,
)

logger = logging.getLogger(__name__)

ESCALA_MIN, ESCALA_MAX = -10.0, 10.0  # escala del diccionario (ADR-003)
SEMILLA = 42
ALPHA_RIDGE = 1.0


class DatosInsuficientesError(Exception):
    """No hay suficientes noticias evaluadas por diccionario (HU-SENT-006)."""

    def __init__(self, disponibles: int, umbral: int) -> None:
        super().__init__(f"{disponibles} noticias evaluadas; se requieren {umbral}.")
        self.disponibles = disponibles
        self.umbral = umbral


class MLNoConfiguradoError(Exception):
    """Falta GEMINI_API_KEY: el camino ML está desactivado."""


def _texto(titulo: str | None, contenido: str | None) -> str:
    return f"{titulo or ''} {contenido or ''}".strip()


def _ahora_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _cliente_por_defecto() -> ClienteEmbeddingsGemini:
    if not settings.gemini_api_key:
        raise MLNoConfiguradoError("GEMINI_API_KEY no está configurada.")
    return ClienteEmbeddingsGemini()


def entrenar_modelo(
    db: Session,
    cliente: ClienteEmbeddingsGemini | None = None,
    ahora: datetime | None = None,
    repository: ModeloSentimientoRepository | None = None,
) -> ModeloSentimiento:
    """Entrena, evalúa y activa una nueva versión del modelo (HU-SENT-006)."""
    repositorio = repository or ModeloSentimientoRepository()
    umbral = settings.ml_umbral_entrenamiento
    disponibles = repositorio.contar_datos_entrenamiento(db)
    if disponibles < umbral:
        raise DatosInsuficientesError(disponibles, umbral)

    cliente = cliente or _cliente_por_defecto()
    filas = repositorio.listar_datos_entrenamiento(db)
    textos = [_texto(titulo, contenido) for titulo, contenido, _ in filas]
    objetivos = np.array([valor for _, _, valor in filas], dtype=float)

    # ErrorServicioEmbeddings se propaga: el router responde 502 y no se toca
    # el modelo activo (Gherkin "Fallo del servicio externo de embeddings").
    matriz = np.array(cliente.embeber_lote(textos), dtype=float)

    x_ent, x_val, y_ent, y_val = train_test_split(
        matriz, objetivos, test_size=settings.ml_proporcion_validacion, random_state=SEMILLA
    )
    regresor = Ridge(alpha=ALPHA_RIDGE)
    regresor.fit(x_ent, y_ent)
    predicciones = np.clip(regresor.predict(x_val), ESCALA_MIN, ESCALA_MAX)
    mae = float(mean_absolute_error(y_val, predicciones))

    fecha = ahora or _ahora_utc()
    version = fecha.strftime("%Y%m%dT%H%M%S%fZ")
    directorio = Path(settings.ml_directorio_modelos)
    directorio.mkdir(parents=True, exist_ok=True)
    ruta = directorio / f"modelo-sentimiento-{version}.joblib"
    joblib.dump(regresor, ruta)

    modelo = ModeloSentimiento(
        version=version,
        ruta_archivo=str(ruta),
        modelo_embeddings_usado=cliente.modelo,
        mae_evaluacion=mae,
        fecha_entrenamiento=fecha,
    )
    try:
        modelo = repositorio.registrar_como_activo(db, modelo)
    except Exception:
        ruta.unlink(missing_ok=True)
        raise
    invalidar_cache()
    logger.info(
        "Modelo de humor %s entrenado con %s noticias (MAE vs. diccionario = %.3f)",
        version,
        len(filas),
        mae,
    )
    return modelo


# --- HU-SENT-002-v3: proveedor del modelo activo ------------------------------

# El Circuit Breaker vive a nivel de módulo: protege todas las predicciones
# del proceso, que son las llamadas de alta frecuencia (ADR-004, punto 7).
_circuito = CircuitBreaker(settings.ml_circuit_umbral_fallos, settings.ml_circuit_espera_segundos)


@dataclass
class ProveedorRegresor:
    """Predice el humor de un texto con el regresor activo (ProveedorModeloML)."""

    modelo_id: int
    regresor: object
    cliente: ClienteEmbeddingsGemini
    circuito: CircuitBreaker

    def predecir(self, texto: str) -> float:
        vector = self.circuito.ejecutar(lambda: self.cliente.embeber(texto))
        valor = float(self.regresor.predict(np.array([vector], dtype=float))[0])
        return float(np.clip(valor, ESCALA_MIN, ESCALA_MAX))


_cache: dict[str, object] = {}


def invalidar_cache() -> None:
    _cache.clear()


def proveedor_activo(db: Session) -> ProveedorRegresor | None:
    """Proveedor del modelo activo, o None si el camino ML no está disponible.

    None (y por tanto diccionario) cuando: no hay GEMINI_API_KEY, no hay modelo
    activo, o su archivo .joblib no se puede cargar. Nunca lanza excepciones:
    el cálculo de humor no debe fallar por el camino ML.
    """
    if not settings.gemini_api_key:
        return None
    try:
        modelo = ModeloSentimientoRepository().obtener_activo(db)
        if modelo is None:
            return None
        if _cache.get("id") != modelo.id:
            _cache.update(
                id=modelo.id,
                proveedor=ProveedorRegresor(
                    modelo_id=modelo.id,
                    regresor=joblib.load(modelo.ruta_archivo),
                    cliente=ClienteEmbeddingsGemini(modelo=modelo.modelo_embeddings_usado),
                    circuito=_circuito,
                ),
            )
        return _cache["proveedor"]
    except (OSError, ErrorServicioEmbeddings, ValueError) as exc:
        logger.warning("No se pudo cargar el modelo de ML activo: %s; se usa diccionario", exc)
        return None
    except Exception:  # noqa: BLE001 - p. ej. tabla inexistente sin migrar
        logger.exception("Error al obtener el modelo de ML activo; se usa diccionario")
        return None
