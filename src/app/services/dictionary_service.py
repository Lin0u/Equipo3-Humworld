from sqlalchemy.orm import Session

from app.exceptions import (
    TerminoDiccionarioConflictError,
    TerminoDiccionarioNotFoundError,
)
from app.models.termino_diccionario import TerminoDiccionario
from app.repositories.dictionary import TerminoDiccionarioRepository

IDIOMAS_SOPORTADOS = frozenset({"es", "en"})
VALOR_MINIMO = -10
VALOR_MAXIMO = 10


def _validar_campos(palabra: str, idioma: str, valor: int) -> None:
    if not palabra or not palabra.strip():
        raise ValueError("La palabra es obligatoria.")
    if idioma not in IDIOMAS_SOPORTADOS:
        raise ValueError("El idioma debe ser 'es' o 'en'.")
    if type(valor) is not int or not VALOR_MINIMO <= valor <= VALOR_MAXIMO:
        raise ValueError("El valor debe ser un entero entre -10 y 10.")


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
    _validar_campos(palabra, idioma, valor)
    termino_repository = repository or TerminoDiccionarioRepository()
    if termino_repository.buscar_por_palabra_idioma(db, palabra, idioma):
        raise TerminoDiccionarioConflictError
    return termino_repository.crear(
        db,
        TerminoDiccionario(palabra=palabra, idioma=idioma, valor=valor),
    )


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
    _validar_campos(valores["palabra"], valores["idioma"], valores["valor"])

    existente = termino_repository.buscar_por_palabra_idioma(
        db, valores["palabra"], valores["idioma"]
    )
    if existente is not None and existente.id != termino.id:
        raise TerminoDiccionarioConflictError

    cambios_validos = cambios if parcial else valores
    return termino_repository.actualizar(db, termino, cambios_validos)


def eliminar_termino(
    db: Session,
    termino_id: int,
    repository: TerminoDiccionarioRepository | None = None,
) -> None:
    termino_repository = repository or TerminoDiccionarioRepository()
    termino = obtener_termino(db, termino_id, termino_repository)
    termino_repository.eliminar(db, termino)