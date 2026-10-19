import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.exceptions import (
    TerminoDiccionarioConflictError,
    TerminoDiccionarioNotFoundError,
)
from app.models.termino_diccionario import TerminoDiccionario
from app.repositories.dictionary import TerminoDiccionarioRepository
from app.services.sentimiento_service import invalidar_calculos_diccionario

logger = logging.getLogger(__name__)

IDIOMAS_SOPORTADOS = frozenset({"es", "en"})
VALOR_MINIMO = -10
VALOR_MAXIMO = 10


def validar_campos_termino(palabra: str, idioma: str, valor: int) -> None:
    if not palabra or not palabra.strip():
        raise ValueError("La palabra es obligatoria.")
    if idioma not in IDIOMAS_SOPORTADOS:
        raise ValueError("El idioma debe ser 'es' o 'en'.")
    if type(valor) is not int or not VALOR_MINIMO <= valor <= VALOR_MAXIMO:
        raise ValueError("El valor debe ser un entero entre -10 y 10.")


def _marcar_noticias_para_recalculo(db: Session) -> None:
    """HU-SENT-002-v2: un cambio en el diccionario cambia el humor calculado.

    El cambio del término ya quedó confirmado; si marcar las noticias falla,
    se registra y no se revierte la operación del diccionario.
    """
    try:
        invalidar_calculos_diccionario(db)
    except SQLAlchemyError:
        logger.exception("No se pudieron marcar las noticias para recálculo")


def listar_terminos(
    db: Session,
    busqueda: str | None = None,
    repository: TerminoDiccionarioRepository | None = None,
) -> list[TerminoDiccionario]:
    return (repository or TerminoDiccionarioRepository()).listar(db, busqueda)


def obtener_termino(
    db: Session,
    termino_id: int,
    repository: TerminoDiccionarioRepository | None = None,
) -> TerminoDiccionario:
    termino = (repository or TerminoDiccionarioRepository()).buscar_por_id(
        db, termino_id
    )
    if termino is None:
        raise TerminoDiccionarioNotFoundError(termino_id)
    return termino


def crear_termino(
    db: Session,
    palabra: str,
    idioma: str,
    valor: int,
    repository: TerminoDiccionarioRepository | None = None,
) -> TerminoDiccionario:
    validar_campos_termino(palabra, idioma, valor)
    termino_repository = repository or TerminoDiccionarioRepository()
    if termino_repository.buscar_por_palabra_idioma(db, palabra, idioma):
        raise TerminoDiccionarioConflictError
    termino = termino_repository.crear(
        db,
        TerminoDiccionario(palabra=palabra, idioma=idioma, valor=valor),
    )
    _marcar_noticias_para_recalculo(db)
    return termino


def actualizar_termino(
    db: Session,
    termino_id: int,
    cambios: dict[str, str | int],
    parcial: bool = False,
    repository: TerminoDiccionarioRepository | None = None,
) -> TerminoDiccionario:
    termino_repository = repository or TerminoDiccionarioRepository()
    termino = obtener_termino(db, termino_id, termino_repository)
    valores = {
        "palabra": cambios.get("palabra", termino.palabra),
        "idioma": cambios.get("idioma", termino.idioma),
        "valor": cambios.get("valor", termino.valor),
    }
    validar_campos_termino(valores["palabra"], valores["idioma"], valores["valor"])

    existente = termino_repository.buscar_por_palabra_idioma(
        db, valores["palabra"], valores["idioma"]
    )
    if existente is not None and existente.id != termino.id:
        raise TerminoDiccionarioConflictError

    cambios_validos = cambios if parcial else valores
    actualizado = termino_repository.actualizar(db, termino, cambios_validos)
    _marcar_noticias_para_recalculo(db)
    return actualizado


def eliminar_termino(
    db: Session,
    termino_id: int,
    repository: TerminoDiccionarioRepository | None = None,
) -> None:
    termino_repository = repository or TerminoDiccionarioRepository()
    termino = obtener_termino(db, termino_id, termino_repository)
    termino_repository.eliminar(db, termino)
    _marcar_noticias_para_recalculo(db)