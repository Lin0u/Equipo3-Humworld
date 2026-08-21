"""
Servicio de captura RSS (capa de lógica de negocio).

Origina en: HU-RSS-006 (cron automático), HU-RSS-008 (captura manual).
ADR relacionado: ADR-002, secciones 2, 3 y 4.

IMPORTANTE (sección 12 de las instrucciones del proyecto): este archivo es
ANDAMIAJE. No se implementa aquí la lógica de negocio real (parseo de feeds,
deduplicación, aplicación de Circuit Breaker/Retry/Timeout) — eso queda para
el equipo, apoyado en GitHub Copilot, y debe ser revisado antes de mergear.

Patrones de resiliencia a aplicar aquí (ADR-002, sección 3 — decisión ya
tomada, pendiente de implementación):
- Timeout explícito en cada llamada httpx (ver app/core/config.py).
- Retry con backoff exponencial acotado (nunca infinito).
- Circuit Breaker por fuente RSS individual (estado_circuit_breaker en el
  modelo FuenteRSS).
- Límite de concurrencia vía semáforo asíncrono (Bulkhead mitigado, no
  formal — ver ADR-002, tabla de patrones).
"""
from sqlalchemy.orm import Session

from app.schemas.captura import EstadoResultadoCaptura, ResultadoCaptura


async def ejecutar_captura(fuente_id: int, db: Session) -> ResultadoCaptura:
    """
    Ejecuta la captura de una única fuente RSS.

    TODO(equipo):
    1. Cargar la FuenteRSS por id (404 si no existe).
    2. Verificar activo=True (409 si está inactiva) — ver HU-RSS-008.
    3. Verificar estado_circuit_breaker (omitir si está "abierto").
    4. Descargar el feed con httpx + timeout (ver settings).
    5. Parsear con feedparser.
    6. Para cada ítem: deduplicar por identificador_item_rss antes de insertar.
    7. Actualizar fecha_ultima_captura_exitosa y estado_circuit_breaker según
       resultado (éxito -> cerrado; fallo -> incrementar contador; ver ADR-002).
    """
    raise NotImplementedError(
        "Servicio de captura pendiente de implementación — HU-RSS-006/HU-RSS-008, ADR-002"
    )


async def ejecutar_captura_multiple(fuente_ids: list[int], db: Session) -> list[ResultadoCaptura]:
    """
    Ejecuta la captura de un conjunto de fuentes, con concurrencia acotada.

    Criterio de aceptación (HU-RSS-008): el fallo de una fuente del conjunto
    no debe impedir el procesamiento del resto — cada fuente debe capturarse
    de forma aislada (try/except por fuente), nunca dejar que una excepción
    de una fuente aborte el procesamiento de las demás.
    """
    raise NotImplementedError(
        "Servicio de captura múltiple pendiente de implementación — HU-RSS-008, ADR-002"
    )


async def ejecutar_captura_todas_las_activas(db: Session) -> list[ResultadoCaptura]:
    """
    Punto de entrada del cron automático (HU-RSS-006).

    Recorre todas las FuenteRSS con activo=True. Reutiliza el mismo
    procedimiento que ejecutar_captura_multiple (ver ADR-002, sección 2:
    "la actualización manual reutiliza exactamente el mismo procedimiento
    de captura y deduplicación que utiliza el cron automático").
    """
    raise NotImplementedError(
        "Job de captura automática pendiente de implementación — HU-RSS-006, ADR-002"
    )
