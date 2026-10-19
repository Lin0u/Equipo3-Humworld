"""Agrega el parámetro de caducidad de noticias a la configuración.

Origina en: HU-ADMIN-001 (parámetros generales) y HU-ADMIN-002 (purgado
automático). PDF §4.2.5: "Existirá un parámetro modificable por el usuario que
permite definir un valor de caducidad de las noticias".

Valor inicial: 90 días. Es un valor PROPUESTO (decisión de la PO del
2026-10-19), no fijado por el PDF; pendiente de ratificación del equipo.
"""

from typing import Sequence, Union

from alembic import op


revision: str = "c3f8a2d6e9b1"
down_revision: Union[str, Sequence[str], None] = "a7c3e9b5d1f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "INSERT INTO configuracion (clave, valor) "
        "VALUES ('caducidad_noticias_dias', 90)"
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM configuracion WHERE clave = 'caducidad_noticias_dias'"
    )
