"""Crea el diccionario de términos de sentimiento."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = "3c5e2a7b91df"
down_revision: Union[str, Sequence[str], None] = "9f7c2c8c1d0a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "terminos_diccionario",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "palabra",
            mysql.VARCHAR(255, collation="utf8mb4_bin"),
            nullable=False,
        ),
        sa.Column("idioma", sa.String(length=2), nullable=False),
        sa.Column("valor", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "palabra",
            "idioma",
            name="uq_termino_diccionario_palabra_idioma",
        ),
    )
    op.create_index(
        "ix_terminos_diccionario_id",
        "terminos_diccionario",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_terminos_diccionario_id", table_name="terminos_diccionario")
    op.drop_table("terminos_diccionario")
