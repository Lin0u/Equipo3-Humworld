"""Esquemas Pydantic para la configuración del cron."""

from pydantic import BaseModel, Field, StrictInt


class Configuracion(BaseModel):
    periodicidad_cron_minutos: StrictInt = Field(ge=1)


class ConfiguracionActualizar(BaseModel):
    periodicidad_cron_minutos: StrictInt = Field(ge=1)
