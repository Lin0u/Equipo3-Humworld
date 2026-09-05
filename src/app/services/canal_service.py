from sqlalchemy.orm import Session

from app.exceptions import ChannelNameConflictError, UniqueConstraintViolation
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