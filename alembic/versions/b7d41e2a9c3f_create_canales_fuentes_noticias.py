"""Crea las tablas base del módulo de Captura RSS: canales, fuentes y noticias.

Origina en: HU-RSS-001 (CanalNoticias), HU-RSS-002 (FuenteRSS) y HU-RSS-006
(Noticia). Decisión de arquitectura: ADR-002 (composición CanalNoticias →
FuenteRSS; agregación FuenteRSS → Noticia).

Motivo: los modelos ORM de estas tres entidades existían desde Sprint 1, pero
ninguna migración las creaba. Las pruebas pasan porque usan SQLite con
`create_all`; en MySQL, en cambio, los endpoints /channels y /sources fallaban
con "Table doesn't exist". Esta migración se agrega al final de la cadena
(después de 3c5e2a7b91df) para no modificar migraciones ya existentes.

Revision ID: b7d41e2a9c3f
Revises: 3c5e2a7b91df
Create Date: 2026-10-18 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7d41e2a9c3f"
down_revision: Union[str, Sequence[str], None] = "3c5e2a7b91df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # HU-RSS-001 — CanalNoticias (entidad "todo" de la composición, ADR-002).
    op.create_table(
        "canales_noticias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=150), nullable=False),
        sa.Column("continente", sa.String(length=50), nullable=False),
        sa.Column("pais", sa.String(length=100), nullable=True),
        sa.Column("descripcion", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_canales_noticias_id", "canales_noticias", ["id"])
    op.create_index("ix_canales_noticias_nombre", "canales_noticias", ["nombre"], unique=True)
    op.create_index("ix_canales_noticias_continente", "canales_noticias", ["continente"])

    # HU-RSS-002 — FuenteRSS (parte de la composición con CanalNoticias, ADR-002).
    # El enum guarda los NOMBRES de EstadoCircuitBreaker, igual que el modelo ORM.
    op.create_table(
        "fuentes_rss",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("canal_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("categoria_iptc", sa.String(length=100), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("fecha_ultima_captura_exitosa", sa.DateTime(), nullable=True),
        sa.Column(
            "estado_circuit_breaker",
            sa.Enum("CERRADO", "ABIERTO", "SEMI_ABIERTO", name="estadocircuitbreaker"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["canal_id"], ["canales_noticias.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fuentes_rss_id", "fuentes_rss", ["id"])
    op.create_index("ix_fuentes_rss_canal_id", "fuentes_rss", ["canal_id"])

    # HU-RSS-006 — Noticia (agregación con FuenteRSS, ADR-002).
    op.create_table(
        "noticias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fuente_rss_id", sa.Integer(), nullable=False),
        sa.Column("identificador_item_rss", sa.String(length=255), nullable=False),
        sa.Column("titulo", sa.String(length=500), nullable=False),
        sa.Column("contenido", sa.Text(), nullable=True),
        sa.Column("enlace_original", sa.String(length=500), nullable=False),
        sa.Column("fecha_publicacion", sa.DateTime(), nullable=True),
        sa.Column("fecha_registro", sa.DateTime(), nullable=False),
        sa.Column("idioma_detectado", sa.String(length=10), nullable=True),
        sa.Column("categoria_iptc", sa.String(length=100), nullable=True),
        sa.Column("valor_humor", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["fuente_rss_id"], ["fuentes_rss.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_noticias_id", "noticias", ["id"])
    op.create_index("ix_noticias_fuente_rss_id", "noticias", ["fuente_rss_id"])
    op.create_index(
        "ix_noticias_identificador_item_rss",
        "noticias",
        ["identificador_item_rss"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_noticias_identificador_item_rss", table_name="noticias")
    op.drop_index("ix_noticias_fuente_rss_id", table_name="noticias")
    op.drop_index("ix_noticias_id", table_name="noticias")
    op.drop_table("noticias")
    op.drop_index("ix_fuentes_rss_canal_id", table_name="fuentes_rss")
    op.drop_index("ix_fuentes_rss_id", table_name="fuentes_rss")
    op.drop_table("fuentes_rss")
    op.drop_index("ix_canales_noticias_continente", table_name="canales_noticias")
    op.drop_index("ix_canales_noticias_nombre", table_name="canales_noticias")
    op.drop_index("ix_canales_noticias_id", table_name="canales_noticias")
    op.drop_table("canales_noticias")
    sa.Enum(name="estadocircuitbreaker").drop(op.get_bind(), checkfirst=True)
