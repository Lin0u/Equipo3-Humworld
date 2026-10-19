"""Completa la categoría IPTC de las noticias capturadas antes de heredarla.

Origina en: HU-DASH-002-v2 (la vista muestra la categoría) y HU-RSS-002 (la
categoría de la noticia es la de su fuente). Las noticias capturadas antes del
cambio de captura del 2026-10-19 quedaron con categoria_iptc NULL. Solo datos;
no cambia el esquema.
"""

from typing import Sequence, Union

from alembic import op


revision: str = "f2b6d8e4a1c3"
down_revision: Union[str, Sequence[str], None] = "e5a1c7d3f9b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE noticias SET categoria_iptc = ("
        "SELECT fuentes_rss.categoria_iptc FROM fuentes_rss "
        "WHERE fuentes_rss.id = noticias.fuente_rss_id"
        ") WHERE categoria_iptc IS NULL"
    )


def downgrade() -> None:
    # No reversible de forma segura: no se distingue qué filas se completaron.
    pass
