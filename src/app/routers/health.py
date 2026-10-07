from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Health check simple — no depende de la base de datos."""
    return {"status": "ok"}
