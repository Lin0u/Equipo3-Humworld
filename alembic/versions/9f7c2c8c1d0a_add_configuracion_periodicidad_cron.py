"""Añade la configuración de periodicidad del cron de captura.

Revision ID: 9f7c2c8c1d0a
Revises: head
Create Date: 2026-10-07 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9f7c2c8c1d0a"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "configuracion",
        sa.Column("clave", sa.String(length=100), nullable=False),
        sa.Column("valor", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("clave"),
    )
    op.execute(
        "INSERT INTO configuracion (clave, valor) "
        "VALUES ('periodicidad_cron_minutos', 30)"
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM configuracion "
        "WHERE clave = 'periodicidad_cron_minutos'"
    )
    op.drop_table("configuracion")
