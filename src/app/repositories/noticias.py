from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.noticia import Noticia


class NoticiaRepository:
    def buscar_por_identificador(
        self, db: Session, identificador_item_rss: str
    ) -> Noticia | None:
        return db.execute(
            select(Noticia).where(
                Noticia.identificador_item_rss == identificador_item_rss
            )
        ).scalar_one_or_none()

    def insertar(
        self,
        db: Session,
        noticia: Noticia,
    ) -> Noticia:
        db.add(noticia)
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        db.refresh(noticia)
        return noticia

    def insertar_lote(self, db: Session, noticias: list[Noticia]) -> None:
        if not noticias:
            return
        db.add_all(noticias)
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
