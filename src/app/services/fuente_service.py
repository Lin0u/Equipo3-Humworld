from sqlalchemy.orm import Session

from app.exceptions import CanalNoticiasNotFoundError, FuenteRSSNotFoundError
from app.models.fuente import FuenteRSS
from app.repositories.fuentes import FuenteRSSRepository
from app.schemas.fuente import (
    FuenteRSSActualizar,
    FuenteRSSActualizarParcial,
    FuenteRSSCrear,
)


def crear_fuente(
    db: Session,
    payload: FuenteRSSCrear,
    repository: FuenteRSSRepository | None = None,
) -> FuenteRSS:
    fuente_repository = repository or FuenteRSSRepository()
    canal = fuente_repository.buscar_canal(db, payload.canal_id)
    if canal is None:
        raise CanalNoticiasNotFoundError

    fuente = FuenteRSS(
        canal_id=canal.id,
        url=str(payload.url),
        categoria_iptc=payload.categoria_iptc,
        activo=True,
    )
    return fuente_repository.crear(db, fuente)


def listar_fuentes(
    db: Session,
    pagina: int,
    tamanio_pagina: int,
    canal_id: int | None = None,
    continente: str | None = None,
    categoria_iptc: str | None = None,
    activo: bool | None = None,
    repository: FuenteRSSRepository | None = None,
) -> dict:
    fuente_repository = repository or FuenteRSSRepository()
    filtros_texto = {
        "continente": continente.strip() if continente else None,
        "categoria_iptc": categoria_iptc.strip() if categoria_iptc else None,
    }
    items, total = fuente_repository.listar(
        db,
        pagina,
        tamanio_pagina,
        canal_id=canal_id,
        activo=activo,
        **filtros_texto,
    )
    return {
        "items": items,
        "pagina": pagina,
        "tamanio_pagina": tamanio_pagina,
        "total": total,
    }


def obtener_fuente(
    db: Session,
    fuente_id: int,
    repository: FuenteRSSRepository | None = None,
) -> FuenteRSS:
    fuente_repository = repository or FuenteRSSRepository()
    fuente = fuente_repository.buscar_activa(db, fuente_id)
    if fuente is None:
        raise FuenteRSSNotFoundError
    return fuente


def eliminar_fuente(
    db: Session,
    fuente_id: int,
    repository: FuenteRSSRepository | None = None,
) -> None:
    fuente_repository = repository or FuenteRSSRepository()
    fuente = fuente_repository.buscar_activa(db, fuente_id)
    if fuente is None:
        raise FuenteRSSNotFoundError
    fuente_repository.eliminar_logicamente(db, fuente)


def actualizar_fuente(
    db: Session,
    fuente_id: int,
    payload: FuenteRSSActualizar | FuenteRSSActualizarParcial,
    repository: FuenteRSSRepository | None = None,
) -> FuenteRSS:
    fuente_repository = repository or FuenteRSSRepository()
    fuente = fuente_repository.buscar_por_id(db, fuente_id)
    if fuente is None:
        raise FuenteRSSNotFoundError

    cambios = payload.model_dump(exclude_unset=True)
    cambios["url"] = str(cambios["url"]) if "url" in cambios else None
    cambios = {campo: valor for campo, valor in cambios.items() if valor is not None}
    return fuente_repository.actualizar(db, fuente, cambios)