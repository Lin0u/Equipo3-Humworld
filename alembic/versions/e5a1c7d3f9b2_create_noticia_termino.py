"""Crea la tabla de coincidencias término–noticia.

Origina en: HU-SENT-008. Clave primaria compuesta (noticia_id, termino_id);
borrado en cascada desde la noticia (composición) y desde el término
(decisión de equipo del 2026-10-19).

Datos: marca como pendientes las noticias ya calculadas por diccionario para
que el barrido de humor las reprocese una vez y registre sus coincidencias
(punto pendiente 1 de HU-SENT-008, decisión de equipo del 2026-10-19).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5a1c7d3f9b2"
down_revision: Union[str, Sequence[str], None] = "d2e8f4a6b1c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "noticia_termino",
        sa.Column("noticia_id", sa.Integer(), nullable=False),
        sa.Column("termino_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["noticia_id"], ["noticias.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["termino_id"], ["terminos_diccionario.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("noticia_id", "termino_id"),
    )
    op.create_index(
        op.f("ix_noticia_termino_termino_id"), "noticia_termino", ["termino_id"], unique=False
    )
    op.execute(
        "UPDATE noticias SET metodo_calculo = NULL WHERE metodo_calculo = 'diccionario'"
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_noticia_termino_termino_id"), table_name="noticia_termino")
    op.drop_table("noticia_termino")
