"""Agrega la polarización de los términos a noticias.

Origina en: HU-SENT-003 (persistencia del resultado de humor y polarización),
ADR-003 (desviación estándar poblacional de los términos coincidentes).
OpenSpec: "Persistencia-del-resultado-de-humor-y-polarización".

Datos: marca como pendientes las noticias calculadas por diccionario para que
el barrido de humor (HU-SENT-002-v3) les calcule la polarización.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7c3e9b5d1f4"
down_revision: Union[str, Sequence[str], None] = "f2b6d8e4a1c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("noticias", sa.Column("polarizacion_terminos", sa.Float(), nullable=True))
    op.execute(
        "UPDATE noticias SET metodo_calculo = NULL WHERE metodo_calculo = 'diccionario'"
    )


def downgrade() -> None:
    op.drop_column("noticias", "polarizacion_terminos")
