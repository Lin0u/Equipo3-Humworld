from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import TerminoDiccionarioConflictError
from app.models.termino_diccionario import TerminoDiccionario


class TerminoDiccionarioRepository:
    def buscar_por_id(self, db: Session, termino_id: int) -> TerminoDiccionario | None:
        return db.execute(
            select(TerminoDiccionario).where(TerminoDiccionario.id == termino_id)
        ).scalar_one_or_none()

    def buscar_por_palabra_idioma(
        self, db: Session, palabra: str, idioma: str
    ) -> TerminoDiccionario | None:
        columna_palabra = TerminoDiccionario.palabra
        if db.get_bind().dialect.name == "mysql":
            comparacion_palabra = func.binary(columna_palabra) == palabra
        else:
            comparacion_palabra = columna_palabra.collate("BINARY") == palabra
        return db.execute(
            select(TerminoDiccionario).where(
                comparacion_palabra,
                TerminoDiccionario.idioma == idioma,
            )
        ).scalar_one_or_none()

    def listar_por_idiomas(
        self, db: Session, idiomas: tuple[str, ...]
    ) -> list[TerminoDiccionario]:
        """Términos de los idiomas indicados (HU-SENT-007, ADR-003 punto 1)."""
        return list(
            db.execute(
                select(TerminoDiccionario)
                .where(TerminoDiccionario.idioma.in_(idiomas))
                .order_by(TerminoDiccionario.id)
            ).scalars().all()
        )

    def claves_existentes(self, db: Session) -> set[tuple[str, str]]:
        """Pares (palabra, idioma) ya registrados, comparados de forma literal."""
        return {
            (palabra, idioma)
            for palabra, idioma in db.execute(
                select(TerminoDiccionario.palabra, TerminoDiccionario.idioma)
            ).all()
        }

    def agregar_lote(self, db: Session, terminos: list[TerminoDiccionario]) -> None:
        """Inserta varios términos en una sola transacción (carga inicial)."""
        db.add_all(terminos)
        try:
            db.commit()
        except IntegrityError as error:
            db.rollback()
            raise TerminoDiccionarioConflictError from error

    def listar(self, db: Session, busqueda: str | None = None) -> list[TerminoDiccionario]:
        consulta = select(TerminoDiccionario)
        if busqueda:
            consulta = consulta.where(
                func.lower(TerminoDiccionario.palabra).contains(
                    busqueda.lower(), autoescape=True
                )
            )
        return list(
            db.execute(consulta.order_by(TerminoDiccionario.id)).scalars().all()
        )

    def crear(self, db: Session, termino: TerminoDiccionario) -> TerminoDiccionario:
        db.add(termino)
        try:
            db.commit()
        except IntegrityError as error:
            db.rollback()
            raise TerminoDiccionarioConflictError from error
        db.refresh(termino)
        return termino

    def actualizar(
        self,
        db: Session,
        termino: TerminoDiccionario,
        cambios: dict[str, str | int],
    ) -> TerminoDiccionario:
        for campo, valor in cambios.items():
            setattr(termino, campo, valor)
        try:
            db.commit()
        except IntegrityError as error:
            db.rollback()
            raise TerminoDiccionarioConflictError from error
        db.refresh(termino)
        return termino

    def eliminar(self, db: Session, termino: TerminoDiccionario) -> None:
        db.delete(termino)
        db.commit()
