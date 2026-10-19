"""
Utilidades compartidas por las consultas de humor agregado.

Usadas por HU-DASH-001-v3 (GET /dashboards/map) y HU-SENT-004 (GET /sentiment).
"""
import unicodedata
from datetime import date

# Decimales con que se informan los promedios de humor.
DECIMALES = 2


def clave_continente(texto: str) -> str:
    """Minúsculas y sin tildes: "America", "AMÉRICA" y "américa" son iguales."""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return sin_tildes.strip().casefold()


def a_fecha(valor) -> date | None:
    """Convierte el día devuelto por la base: MySQL entrega date; SQLite, texto."""
    if valor is None or isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor)[:10])
