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

    # Cálculo de humor (HU-SENT-002-v2, ADR-04). Valores PROPUESTOS en el
    # backlog, pendientes de ratificación del equipo.
    sentimiento_timeout_ml_segundos: float = 3.0  # TODO(equipo): ratificar
    sentimiento_barrido_minutos: int = 30  # TODO(equipo): ratificar
    sentimiento_barrido_lote: int = 500  # noticias por ejecución del barrido

    # Purgado de noticias (HU-ADMIN-002, PDF §4.2.5). La caducidad vigente se
    # lee de la tabla configuracion (GET/PUT /api/v1/config); este valor solo
    # se usa si la fila no existe. 90 días y 24 horas son valores PROPUESTOS
    # (sesión PO 2026-10-19), pendientes de ratificación del equipo.
    purgado_caducidad_dias_defecto: int = 90
    purgado_intervalo_horas: int = 24

    # Modelo de ML (HU-SENT-006, ADR-04): embeddings de Google Gemini + regresor
    # Ridge local. Sin GEMINI_API_KEY el camino ML queda desactivado y todo el
    # humor se calcula por diccionario. La cuenta y la clave las gestiona el
    # equipo (ADR-04, punto 2); nunca se versionan en el repositorio.
    gemini_api_key: str = ""
    gemini_url_base: str = "https://generativelanguage.googleapis.com/v1beta"
    gemini_modelo_embeddings: str = "gemini-embedding-001"
    # ADR-04, punto 7. Valores PROPUESTOS, pendientes de ratificación.
    embeddings_timeout_segundos: float = 3.0
    embeddings_max_reintentos: int = 3  # backoff exponencial acotado
    embeddings_backoff_base_segundos: float = 0.5
    embeddings_lote: int = 100  # textos por solicitud batchEmbedContents
    embeddings_max_caracteres: int = 8000  # ~2.048 tokens de entrada del modelo
    ml_circuit_umbral_fallos: int = 5
    ml_circuit_espera_segundos: int = 60
    # ADR-04, punto 4: umbral mínimo de entrenamiento (valor propuesto).
    ml_umbral_entrenamiento: int = 1000
    ml_proporcion_validacion: float = 0.2
    ml_directorio_modelos: str = "modelos"

    # CORS (ADR-05, stack de frontend): orígenes autorizados a llamar a la API
    # desde el navegador, separados por coma. Por defecto, el servidor de
    # desarrollo de Vite. TODO(equipo): agregar el origen del frontend desplegado.
    cors_origenes: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def cors_origenes_lista(self) -> list[str]:
        return [origen.strip() for origen in self.cors_origenes.split(",") if origen.strip()]


settings = Settings()
