"""
Router: /api/v1/trainings

Origina en: HU-SENT-006 (entrenamiento manual del modelo de ML). ADR-004.
Contrato: contrato-sentimiento-diccionario.openapi.yaml, tag trainings.

Códigos de error (decisión de implementación, pendiente de ratificación):
- 409 DATOS_INSUFICIENTES: no se alcanza el umbral de noticias evaluadas.
- 502 SERVICIO_EMBEDDINGS_NO_DISPONIBLE: Gemini falló tras agotar los
  reintentos (el fallo es del servicio externo: "Bad Gateway").
- 503 ML_NO_CONFIGURADO: falta GEMINI_API_KEY en este despliegue.
En los tres casos el modelo activo previo no cambia.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import Error
from app.schemas.modelo_sentimiento import ModeloSentimientoLeer
from app.services.embeddings_service import ErrorServicioEmbeddings
from app.services.modelo_ml_service import (
    DatosInsuficientesError,
    MLNoConfiguradoError,
    entrenar_modelo,
)

router = APIRouter(prefix="/trainings", tags=["trainings"])


def _error(status: int, codigo: str, mensaje: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content=Error(codigo=codigo, mensaje=mensaje).model_dump(exclude_none=True),
    )


@router.post(
    "",
    status_code=201,
    response_model=ModeloSentimientoLeer,
    responses={409: {"model": Error}, 502: {"model": Error}, 503: {"model": Error}},
)
def entrenar(db: Session = Depends(get_db)):
    """Entrena y activa una nueva versión del modelo de humor (HU-SENT-006)."""
    try:
        return entrenar_modelo(db)
    except DatosInsuficientesError as exc:
        return _error(
            409,
            "DATOS_INSUFICIENTES",
            f"Hay {exc.disponibles} noticias evaluadas por diccionario; se requieren {exc.umbral}.",
        )
    except MLNoConfiguradoError:
        return _error(503, "ML_NO_CONFIGURADO", "El servicio de embeddings no está configurado (GEMINI_API_KEY).")
    except ErrorServicioEmbeddings:
        return _error(
            502,
            "SERVICIO_EMBEDDINGS_NO_DISPONIBLE",
            "El servicio de embeddings falló tras agotar los reintentos; el modelo activo no cambió.",
        )
