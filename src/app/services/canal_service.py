from sqlalchemy.orm import Session

from app.exceptions import (
    CanalNoticiasNotFoundError,
    ChannelNameConflictError,
    UniqueConstraintViolation,
)
from app.models.canal import CanalNoticias
from app.repositories.canales import CanalNoticiasRepository
from app.schemas.canal import CanalNoticiasCrear


def crear_canal(
    db: Session,
    payload: CanalNoticiasCrear,
    repository: CanalNoticiasRepository | None = None,
) -> CanalNoticias:
    canal_repository = repository or CanalNoticiasRepository()
    if canal_repository.buscar_por_nombre(db, payload.nombre) is not None:
        raise ChannelNameConflictError

    canal = CanalNoticias(**payload.model_dump())
    try:
        return canal_repository.crear(db, canal)
    except UniqueConstraintViolation as error:
        raise ChannelNameConflictError from error


def listar_canales(
    db: Session,
    pagina: int,
    tamanio_pagina: int,
    continente: str | None = None,
    repository: CanalNoticiasRepository | None = None,
) -> dict:
    canal_repository = repository or CanalNoticiasRepository()
    continente_normalizado = (continente or "").strip() or None
    items, total = canal_repository.listar(
        db, pagina, tamanio_pagina, continente=continente_normalizado
    )
    return {
        "items": items,
        "pagina": pagina,
        "tamanio_pagina": tamanio_pagina,
        "total": total,
    }


def obtener_canal(
    db: Session,
    canal_id: int,
    repository: CanalNoticiasRepository | None = None,
) -> CanalNoticias:
    canal_repository = repository or CanalNoticiasRepository()
    canal = canal_repository.buscar_por_id(db, canal_id)
    if canal is None:
        raise CanalNoticiasNotFoundError
    return canal