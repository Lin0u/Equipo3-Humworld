from fastapi import APIRouter

from app.services.lematizacion import estado_modelos

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Health check simple — no depende de la base de datos.

    Informa además el estado de los modelos de spaCy (HU-SENT-007-v3), para
    confirmar desde el navegador que la lematización está activa.
    """
    return {"status": "ok", "lematizador": estado_modelos()}
