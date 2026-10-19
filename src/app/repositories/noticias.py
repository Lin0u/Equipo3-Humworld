from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.coincidencia_termino import CoincidenciaTermino
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

    def listar_pendientes_humor(self, db: Session, limite: int) -> list[Noticia]:
        """Noticias sin procesar por el cálculo de humor (HU-SENT-002-v2, barrido).

        La marca es metodo_calculo IS NULL y no valor_humor IS NULL: una noticia
        sin términos evaluables también queda con valor_humor NULL y no debe
        reprocesarse en cada barrido.
        """
        return list(
            db.execute(
                select(Noticia)
                .where(Noticia.metodo_calculo.is_(None))
                .order_by(Noticia.id)
                .limit(limite)
            ).scalars().all()
        )

    def guardar_resultado_humor(
        self,
        db: Session,
        noticia: Noticia,
        valor_humor: float | None,
        metodo_calculo: str,
        cantidad_terminos_evaluados: int,
        terminos_ids: tuple[int, ...] = (),
        polarizacion_terminos: float | None = None,
    ) -> None:
        """Persiste el resultado y sus coincidencias en una transacción propia.

        HU-SENT-002-v3 (resultado) y HU-SENT-008 (coincidencias): las
        coincidencias anteriores de la noticia se reemplazan, de modo que un
        reproceso nunca las duplica.
        """
        noticia.valor_humor = valor_humor
        noticia.metodo_calculo = metodo_calculo
        noticia.cantidad_terminos_evaluados = cantidad_terminos_evaluados
        noticia.polarizacion_terminos = polarizacion_terminos
        noticia.coincidencias = [
            CoincidenciaTermino(termino_id=termino_id) for termino_id in sorted(set(terminos_ids))
        ]
        try:
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise

    def marcar_para_recalculo(self, db: Session, metodo_calculo: str) -> int:
        """Vuelve pendientes las noticias calculadas con ese método.

        Solo borra metodo_calculo: valor_humor se conserva hasta que el
        barrido lo recalcule, para que los dashboards nunca queden vacíos.
        """
        try:
            resultado = db.execute(
                update(Noticia)
                .where(Noticia.metodo_calculo == metodo_calculo)
                .values(metodo_calculo=None)
                .execution_options(synchronize_session=False)
            )
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        return resultado.rowcount
