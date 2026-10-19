"""Marca para recálculo las noticias calculadas por diccionario.

Origina en: HU-SENT-007-v3 (comparación de términos por lema con spaCy) y
ADR-003, punto 6. La regla de comparación cambia, así que el barrido de humor
(HU-SENT-002-v3) debe recalcular esas noticias; al hacerlo también detecta y
guarda su idioma (idioma_detectado). No cambia el esquema.
"""

from typing import Sequence, Union

from alembic import op


revision: str = "e1f4a8c2b6d9"
down_revision: Union[str, Sequence[str], None] = "d8b2f6a4c7e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE noticias SET metodo_calculo = NULL WHERE metodo_calculo = 'diccionario'"
    )


def downgrade() -> None:
    # Sin cambio de esquema: el barrido recalcula con la regla vigente.
    pass
