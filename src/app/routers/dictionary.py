from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import (
    TerminoDiccionarioConflictError,
    TerminoDiccionarioNotFoundError,
)
from app.schemas.common import Error
from app.schemas.dictionary import (
    TerminoDiccionario as TerminoDiccionarioSchema,
    TerminoDiccionarioActualizar,
    TerminoDiccionarioActualizarParcial,
    TerminoDiccionarioCrear,
)
from app.services.dictionary_service import (
    actualizar_termino,
    crear_termino,
    eliminar_termino,
    listar_terminos,
    obtener_termino,
)

router = APIRouter(prefix="/dictionary", tags=["dictionary"])


def _error(status_code: int, codigo: str, mensaje: str) -> JSONResponse:
    error = Error(codigo=codigo, mensaje=mensaje)
    return JSONResponse(status_code=status_code, content=error.model_dump())


@router.get("", response_model=list[TerminoDiccionarioSchema])
def listar(busqueda: str | None = Query(default=None), db: Session = Depends(get_db)):
    return listar_terminos(db, busqueda)


@router.get(
    "/{termino_id}",
    response_model=TerminoDiccionarioSchema,
    responses={404: {"model": Error}},
)
def obtener(termino_id: int, db: Session = Depends(get_db)):
    try:
        return obtener_termino(db, termino_id)
    except TerminoDiccionarioNotFoundError:
        return _error(404, "TERMINO_NO_ENCONTRADO", "El término no existe.")


@router.post(
    "",
    response_model=TerminoDiccionarioSchema,
    status_code=201,
    responses={
        400: {"model": Error},
        409: {"model": Error},
    },
)
def crear(payload: TerminoDiccionarioCrear, db: Session = Depends(get_db)):
    try:
        return crear_termino(db, **payload.model_dump())
    except TerminoDiccionarioConflictError:
        return _error(
            409,
            "TERMINO_DUPLICADO",
            "Ya existe un término con esa palabra e idioma.",
        )


@router.put(
    "/{termino_id}",
    response_model=TerminoDiccionarioSchema,
    responses={400: {"model": Error}, 404: {"model": Error}, 409: {"model": Error}},
)
def actualizar(
    termino_id: int,
    payload: TerminoDiccionarioActualizar,
    db: Session = Depends(get_db),
):
    try:
        return actualizar_termino(
            db, termino_id, payload.model_dump(), parcial=False
        )
    except TerminoDiccionarioNotFoundError:
        return _error(404, "TERMINO_NO_ENCONTRADO", "El término no existe.")
    except TerminoDiccionarioConflictError:
        return _error(
            409,
            "TERMINO_DUPLICADO",
            "Ya existe un término con esa palabra e idioma.",
        )
    except ValueError as error:
        return _error(400, "DATOS_INVALIDOS", str(error))


@router.patch(
    "/{termino_id}",
    response_model=TerminoDiccionarioSchema,
    responses={400: {"model": Error}, 404: {"model": Error}, 409: {"model": Error}},
)
def actualizar_parcial(
    termino_id: int,
    payload: TerminoDiccionarioActualizarParcial,
    db: Session = Depends(get_db),
):
    try:
        return actualizar_termino(
            db,
            termino_id,
            payload.model_dump(exclude_unset=True),
            parcial=True,
        )
    except TerminoDiccionarioNotFoundError:
        return _error(404, "TERMINO_NO_ENCONTRADO", "El término no existe.")
    except TerminoDiccionarioConflictError:
        return _error(
            409,
            "TERMINO_DUPLICADO",
            "Ya existe un término con esa palabra e idioma.",
        )
    except ValueError as error:
        return _error(400, "DATOS_INVALIDOS", str(error))


@router.delete(
    "/{termino_id}",
    status_code=204,
    responses={404: {"model": Error}},
)
def eliminar(termino_id: int, db: Session = Depends(get_db)):
    try:
        eliminar_termino(db, termino_id)
    except TerminoDiccionarioNotFoundError:
        return _error(404, "TERMINO_NO_ENCONTRADO", "El término no existe.")
    return Response(status_code=204)