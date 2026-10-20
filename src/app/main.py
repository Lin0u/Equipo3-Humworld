"""
Punto de entrada de la aplicación FastAPI — Módulo Captura RSS (Sprint 1).

Origina en: HU-RSS-001 a HU-RSS-009.
ADRs relacionados: ADR-001 (stack backend), ADR-002 (arquitectura de captura RSS).
Contrato: contrato-canales-fuentes-rss.openapi.yaml.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.schemas.common import Error
from app.routers import (
    captures,
    channels,
    configuracion,
    dashboards,
    dictionary,
    health,
    news,
    sentiment,
    sources,
    trainings,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verifica los modelos de spaCy e inicia/detiene el scheduler interno."""
    from app.jobs.scheduler import detener_scheduler, iniciar_scheduler
    from app.services.lematizacion import verificar_modelos

    # HU-SENT-007-v3: falla al arrancar, no en silencio, si faltan los modelos.
    verificar_modelos(settings.lematizacion_obligatoria)
    iniciar_scheduler()
    try:
        yield
    finally:
        detener_scheduler()


app = FastAPI(
    title="HumWorld API — Módulo Captura RSS",
    description="Gestión de canales, fuentes RSS y captura de noticias (Sprint 1).",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS: el frontend (ADR-005, React + Vite) corre en otro origen y el navegador
# bloquea sus llamadas a la API sin estas cabeceras. Solo orígenes listados en
# CORS_ORIGENES; sin credenciales, porque la API no usa cookies.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origenes_lista,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc: RequestValidationError):
    error = Error(
        codigo="DATOS_INVALIDOS",
        mensaje="Los datos enviados no son válidos.",
    )
    return JSONResponse(
        status_code=400,
        content=error.model_dump(exclude_none=True),
    )

api_v1_prefix = "/api/v1"

app.include_router(health.router, prefix=api_v1_prefix)
app.include_router(channels.router, prefix=api_v1_prefix)
app.include_router(sources.router, prefix=api_v1_prefix)
app.include_router(captures.router, prefix=api_v1_prefix)
app.include_router(configuracion.router, prefix=api_v1_prefix)
app.include_router(dictionary.router, prefix=api_v1_prefix)
app.include_router(dashboards.router, prefix=api_v1_prefix)
app.include_router(sentiment.router, prefix=api_v1_prefix)
app.include_router(news.router, prefix=api_v1_prefix)
app.include_router(trainings.router, prefix=api_v1_prefix)
