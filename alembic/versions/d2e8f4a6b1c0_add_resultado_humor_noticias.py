"""Agrega el resultado del cálculo de humor a noticias.

Origina en: HU-SENT-002-v2 (cálculo híbrido de humor), OpenSpec
"Cálculo híbrido de humor", tarea 2.2. Solo los campos mínimos de esa
historia: metodo_calculo y cantidad_terminos_evaluados (valor_humor ya
existe). No incluye polarizacion_terminos (HU-SENT-003) ni la versión del
modelo ML (HU-SENT-006).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d2e8f4a6b1c0"
down_revision: Union[str, Sequence[str], None] = "b7d41e2a9c3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("noticias", sa.Column("metodo_calculo", sa.String(length=20), nullable=True))
    op.add_column(
        "noticias",
        sa.Column("cantidad_terminos_evaluados", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_noticias_metodo_calculo"), "noticias", ["metodo_calculo"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_noticias_metodo_calculo"), table_name="noticias")
    op.drop_column("noticias", "cantidad_terminos_evaluados")
    op.drop_column("noticias", "metodo_calculo")
