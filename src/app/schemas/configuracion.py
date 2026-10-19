"""Esquemas Pydantic de la configuración general (GET/PUT /api/v1/config).

Origina en: HU-RSS-007 (periodicidad del cron) y HU-ADMIN-001 (caducidad de
noticias, PDF §4.2.5).
"""

from typing import Optional

from pydantic import BaseModel, Field, StrictInt


class Configuracion(BaseModel):
    periodicidad_cron_minutos: StrictInt = Field(ge=1)
    caducidad_noticias_dias: StrictInt = Field(ge=1)


class ConfiguracionActualizar(BaseModel):
    periodicidad_cron_minutos: StrictInt = Field(ge=1)
    # Opcional para no romper a los clientes de HU-RSS-007 que solo envían la
    # periodicidad; si se omite, se conserva el valor vigente.
    caducidad_noticias_dias: Optional[StrictInt] = Field(default=None, ge=1)
