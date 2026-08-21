"""
Configuración de la aplicación (variables de entorno).

Origina en: ADR-001 (stack backend) y ADR-002 (arquitectura de captura RSS).
Historias relacionadas: HU-RSS-006 (cron), HU-RSS-007 (periodicidad configurable).

TODO(equipo): HU-RSS-007 exige que la periodicidad del cron sea modificable en
caliente vía `GET/PUT /api/v1/config`, leyendo el valor desde la base de datos
(tabla de configuración), no solo desde una variable de entorno como se deja
aquí a modo de scaffold. Falta implementar el modelo/router de configuración.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Base de datos (ADR-001: MySQL vía PyMySQL/mysqlclient, a confirmar por el equipo)
    database_url: str = "mysql+pymysql://usuario:password@localhost:3306/humworld"

    # Captura RSS (ADR-002, sección 2 y 3 — valores por defecto NO fijados por el
    # PDF; el equipo debe validarlos antes de pasar a producción del prototipo)
    captura_periodicidad_minutos: int = 30  # TODO(equipo): validar valor por defecto
    captura_timeout_conexion_segundos: float = 5.0  # TODO(equipo): validar
    captura_timeout_lectura_segundos: float = 10.0  # TODO(equipo): validar
    captura_max_reintentos: int = 3  # TODO(equipo): validar (backoff exponencial acotado)
    captura_concurrencia_maxima: int = 10  # TODO(equipo): validar límite de semáforo
    circuit_breaker_umbral_fallos: int = 5  # TODO(equipo): validar umbral

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
