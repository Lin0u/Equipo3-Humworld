"""
Punto de entrada de la aplicación FastAPI — Módulo Captura RSS (Sprint 1).

Origina en: HU-RSS-001 a HU-RSS-009.
ADRs relacionados: ADR-001 (stack backend), ADR-002 (arquitectura de captura RSS).
Contrato: contrato-canales-fuentes-rss.openapi.yaml.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.common import Error
from app.routers import captures, channels, health, sources


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    TODO(equipo): descomentar cuando el scheduler (HU-RSS-006) esté
    implementado — se deja deshabilitado por defecto para que el resto de
    endpoints y el health check funcionen sin depender de él.

    from app.jobs.scheduler import iniciar_scheduler
    iniciar_scheduler()
    """
    yield


app = FastAPI(
    title="HumWorld API — Módulo Captura RSS",
    description="Gestión de canales, fuentes RSS y captura de noticias (Sprint 1).",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
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
