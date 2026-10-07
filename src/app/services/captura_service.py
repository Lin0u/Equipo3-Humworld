"""Servicio de captura RSS y composición del cron automático."""

import asyncio
import logging
from datetime import datetime, timezone

import feedparser
import httpx
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.exceptions import FuenteRSSInactiveError, FuenteRSSNotFoundError
from app.models.fuente import EstadoCircuitBreaker, FuenteRSS
from app.models.noticia import Noticia
from app.repositories.fuentes import FuenteRSSRepository
from app.repositories.noticias import NoticiaRepository
from app.schemas.captura import EstadoResultadoCaptura, ResultadoCaptura

logger = logging.getLogger(__name__)


def _identificador_item(item: dict) -> str | None:
    identificador = item.get("guid") or item.get("id")
    if not identificador:
        return None
    return str(identificador).strip() or None


def _mapear_item(item: dict, fuente: FuenteRSS, fecha_registro: datetime) -> Noticia | None:
    identificador = _identificador_item(item)
    titulo = str(item.get("title") or "").strip()
    enlace = str(item.get("link") or "").strip()
    if not identificador or not titulo or not enlace:
        return None

    contenido = item.get("content") or item.get("summary") or item.get("description")
    if isinstance(contenido, list):
        contenido = contenido[0].get("value") if contenido else None
    elif isinstance(contenido, dict):
        contenido = contenido.get("value")

    return Noticia(
        fuente_rss_id=fuente.id,
        identificador_item_rss=identificador,
        titulo=titulo,
        contenido=contenido,
        enlace_original=enlace,
        fecha_publicacion=None,
        fecha_registro=fecha_registro,
        idioma_detectado=None,
        categoria_iptc=None,
    )


async def _descargar_feed(fuente: FuenteRSS) -> feedparser.FeedParserDict:
    timeout = httpx.Timeout(
        connect=settings.captura_timeout_conexion_segundos,
        read=settings.captura_timeout_lectura_segundos,
        write=settings.captura_timeout_lectura_segundos,
        pool=settings.captura_timeout_conexion_segundos,
    )
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(fuente.url)
        response.raise_for_status()
        return feedparser.parse(response.content)


async def _capturar_con_retries(
    fuente: FuenteRSS,
) -> tuple[bool, str | None, list[dict]]:
    ultimo_error: Exception | None = None
    for intento in range(settings.captura_max_reintentos + 1):
        try:
            parsed = await _descargar_feed(fuente)
            if parsed.bozo or not parsed.feed and not parsed.entries:
                raise ValueError("El feed no contiene contenido válido")
            return True, None, list(parsed.entries)
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            ultimo_error = exc
            if intento >= settings.captura_max_reintentos:
                break
            delay = min(0.5 * (2**intento), 5.0)
            logger.warning(
                "Reintento fuente_id=%s intento=%s motivo=%s",
                fuente.id,
                intento + 1,
                type(exc).__name__,
            )
            await asyncio.sleep(delay)
    return False, str(ultimo_error), []


async def _persistir_captura(
    db: Session,
    fuente: FuenteRSS,
    entries: list[dict],
    fecha_registro: datetime,
) -> tuple[int, bool]:
    noticias: list[Noticia] = []
    noticias_repository = NoticiaRepository()
    for entry in entries:
        noticia = _mapear_item(entry, fuente, fecha_registro)
        if noticia is None:
            logger.warning("Omitido ítem inválido fuente_id=%s", fuente.id)
            continue
        if noticias_repository.buscar_por_identificador(db, noticia.identificador_item_rss):
            continue
        noticias.append(noticia)

    try:
        noticias_repository.insertar_lote(db, noticias)
        fuente.fecha_ultima_captura_exitosa = fecha_registro
        fuente.estado_circuit_breaker = EstadoCircuitBreaker.CERRADO
        db.commit()
        return len(noticias), True
    except IntegrityError:
        db.rollback()
        return 0, False


async def ejecutar_captura(fuente_id: int, db: Session) -> ResultadoCaptura:
    """Ejecuta una captura de una fuente activa y devuelve su resultado."""
    fuente = FuenteRSSRepository().buscar_activa(db, fuente_id)
    if fuente is None:
        return ResultadoCaptura(
            fuente_id=fuente_id,
            estado=EstadoResultadoCaptura.FALLIDA_TRANSITORIA,
            noticias_nuevas=0,
            mensaje="La fuente no existe o está inactiva",
        )

    if fuente.estado_circuit_breaker == EstadoCircuitBreaker.ABIERTO:
        return ResultadoCaptura(
            fuente_id=fuente_id,
            estado=EstadoResultadoCaptura.FALLIDA_CIRCUITO_ABIERTO,
            noticias_nuevas=0,
            mensaje="Circuit breaker abierto",
        )

    try:
        capturado, error, entries = await _capturar_con_retries(fuente)
        if not capturado:
            logger.error("Fallo de captura fuente_id=%s motivo=%s", fuente_id, error)
            return ResultadoCaptura(
                fuente_id=fuente_id,
                estado=EstadoResultadoCaptura.FALLIDA_TRANSITORIA,
                noticias_nuevas=0,
                mensaje=error or "Error de captura",
            )

        noticias_nuevas, persistido = await _persistir_captura(
            db, fuente, entries, datetime.now(timezone.utc)
        )
        if not persistido:
            return ResultadoCaptura(
                fuente_id=fuente_id,
                estado=EstadoResultadoCaptura.FALLIDA_TRANSITORIA,
                noticias_nuevas=0,
                mensaje="Error de persistencia",
            )
        return ResultadoCaptura(
            fuente_id=fuente_id,
            estado=EstadoResultadoCaptura.EXITOSA,
            noticias_nuevas=noticias_nuevas,
        )
    except Exception as exc:
        logger.exception("Fallo inesperado fuente_id=%s", fuente_id)
        return ResultadoCaptura(
            fuente_id=fuente_id,
            estado=EstadoResultadoCaptura.FALLIDA_TRANSITORIA,
            noticias_nuevas=0,
            mensaje=type(exc).__name__,
        )


async def ejecutar_captura_manual_fuente(
    fuente_id: int, db: Session
) -> ResultadoCaptura:
    """Valida la fuente solicitada y ejecuta la captura compartida."""
    fuente = FuenteRSSRepository().buscar_por_id(db, fuente_id)
    if fuente is None:
        raise FuenteRSSNotFoundError(fuente_id)
    if not fuente.activo:
        raise FuenteRSSInactiveError(fuente_id)
    return await ejecutar_captura(fuente_id, db)


async def ejecutar_captura_manual_multiple(
    fuente_ids: list[int], db: Session
) -> list[ResultadoCaptura]:
    """Captura el lote de forma aislada usando una única sesión de DB."""
    resultados: list[ResultadoCaptura] = []
    for fuente_id in fuente_ids:
        try:
            resultados.append(await ejecutar_captura(fuente_id, db))
        except Exception as exc:
            logger.exception("La captura manual falló fuente_id=%s", fuente_id)
            resultados.append(
                ResultadoCaptura(
                    fuente_id=fuente_id,
                    estado=EstadoResultadoCaptura.FALLIDA_TRANSITORIA,
                    noticias_nuevas=0,
                    mensaje=type(exc).__name__,
                )
            )
    return resultados


async def ejecutar_captura_multiple(
    fuente_ids: list[int], db: Session
) -> list[ResultadoCaptura]:
    """Ejecuta varias fuentes con concurrencia acotada y aislamiento."""
    semaphore = asyncio.Semaphore(settings.captura_concurrencia_maxima)

    async def capturar(fuente_id: int) -> ResultadoCaptura:
        async with semaphore:
            try:
                return await ejecutar_captura(fuente_id, db)
            except Exception as exc:
                logger.exception("La fuente_id=%s no pudo completarse", fuente_id)
                return ResultadoCaptura(
                    fuente_id=fuente_id,
                    estado=EstadoResultadoCaptura.FALLIDA_TRANSITORIA,
                    noticias_nuevas=0,
                    mensaje=type(exc).__name__,
                )

    return await asyncio.gather(*(capturar(fuente_id) for fuente_id in fuente_ids))


async def ejecutar_captura_todas_las_activas(
    db: Session,
) -> list[ResultadoCaptura]:
    """Recorre todas las fuentes activas para el cron automático."""
    fuentes = FuenteRSSRepository().listar_activas(db)
    return await ejecutar_captura_multiple([fuente.id for fuente in fuentes], db)
