"""Crea modelos_sentimiento y agrega noticias.modelo_sentimiento_id.

Origina en: HU-SENT-006 (entrenamiento y versionado del modelo de ML) y
ADR-04, punto 5. noticias.modelo_sentimiento_id registra la versión del
modelo usada cuando metodo_calculo = "ml" (HU-SENT-002-v3).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d8b2f6a4c7e3"
down_revision: Union[str, Sequence[str], None] = "c3f8a2d6e9b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "modelos_sentimiento",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("version", sa.String(50), nullable=False, unique=True),
        sa.Column("ruta_archivo", sa.String(500), nullable=False),
        sa.Column("modelo_embeddings_usado", sa.String(100), nullable=False),
        sa.Column("mae_evaluacion", sa.Float(), nullable=False),
        sa.Column("fecha_entrenamiento", sa.DateTime(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_modelos_sentimiento_id", "modelos_sentimiento", ["id"])
    op.create_index("ix_modelos_sentimiento_activo", "modelos_sentimiento", ["activo"])
    op.add_column("noticias", sa.Column("modelo_sentimiento_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_noticias_modelo_sentimiento",
        "noticias",
        "modelos_sentimiento",
        ["modelo_sentimiento_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_noticias_modelo_sentimiento", "noticias", type_="foreignkey")
    op.drop_column("noticias", "modelo_sentimiento_id")
    op.drop_index("ix_modelos_sentimiento_activo", table_name="modelos_sentimiento")
    op.drop_index("ix_modelos_sentimiento_id", table_name="modelos_sentimiento")
    op.drop_table("modelos_sentimiento")
