"""Repositorio de versiones del modelo de ML (HU-SENT-006, ADR-004 punto 5)."""

from sqlalchemy import func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.modelo_sentimiento import ModeloSentimiento
from app.models.noticia import Noticia


class ModeloSentimientoRepository:
    def obtener_activo(self, db: Session) -> ModeloSentimiento | None:
        return db.execute(
            select(ModeloSentimiento)
            .where(ModeloSentimiento.activo.is_(True))
            .order_by(ModeloSentimiento.id.desc())
            .limit(1)
        ).scalar_one_or_none()

    def registrar_como_activo(self, db: Session, modelo: ModeloSentimiento) -> ModeloSentimiento:
        """Desactiva la versión anterior y activa la nueva en una sola transacción."""
        try:
            db.execute(
                update(ModeloSentimiento)
                .where(ModeloSentimiento.activo.is_(True))
                .values(activo=False)
                .execution_options(synchronize_session=False)
            )
            modelo.activo = True
            db.add(modelo)
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        db.refresh(modelo)
        return modelo

    def contar_datos_entrenamiento(self, db: Session) -> int:
        return db.execute(
            select(func.count()).select_from(Noticia).where(*_filtro_entrenamiento())
        ).scalar_one()

    def listar_datos_entrenamiento(self, db: Session) -> list[tuple[str, str | None, float]]:
        """(titulo, contenido, valor_humor) de las noticias evaluadas por diccionario."""
        filas = db.execute(
            select(Noticia.titulo, Noticia.contenido, Noticia.valor_humor)
            .where(*_filtro_entrenamiento())
            .order_by(Noticia.id)
        ).all()
        return [tuple(fila) for fila in filas]


def _filtro_entrenamiento():
    # ADR-004 (HU-SENT-003): solo noticias evaluadas por diccionario y con valor,
    # para no entrenar un modelo sobre las predicciones de otro modelo.
    return (Noticia.metodo_calculo == "diccionario", Noticia.valor_humor.is_not(None))
