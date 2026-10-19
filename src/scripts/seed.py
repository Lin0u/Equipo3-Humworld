"""
Script de carga inicial (seed) de canales y fuentes RSS por continente.

Origina en: HU-RSS-009-v2 (Historia Técnica/Enabler Story), que reemplaza a
HU-RSS-009 (Deprecada, endpoint POST /api/v1/seeds retirado en el contrato
v1.7.0). PDF de especificaciones, sección 4.2.1.
Dataset: docs/Backlog/Dataset-fuentes-RSS-seed-HU-RSS-009.md (v2.1): 20 feeds
de sección en 11 canales, 4 por continente, verificados el 2026-10-18.
Estado del dataset: propuesto por el PO; su aprobación queda en la revisión
del pull request. Los feeds RSS cambian de dirección sin aviso: re-verificar
la lista la misma semana en que se ejecute contra una base compartida.

El script solo contiene los datos y el punto de entrada. La lógica
(idempotencia, cobertura de continentes, transacción) está en
app/services/seed_service.py. No descarga ningún feed.

Uso (desde src/, o dentro del contenedor):
    python -m scripts.seed
    docker compose exec api python -m scripts.seed
"""
import sys

from app.database import SessionLocal
from app.services.seed_service import ContinenteFaltanteError, cargar_dataset

# Códigos IPTC Media Topics de primer nivel usados:
# 04000000 economía, negocios y finanzas; 07000000 salud; 11000000 política;
# 13000000 ciencia y tecnología; 15000000 deporte.
CANALES_SEED: list[dict] = [
    # --- América ---
    {
        "nombre": "El Tiempo",
        "continente": "América",
        "pais": "Colombia",
        "fuentes": [
            {"url": "https://www.eltiempo.com/rss/politica.xml", "categoria_iptc": "11000000"},
            {"url": "https://www.eltiempo.com/rss/economia.xml", "categoria_iptc": "04000000"},
        ],
    },
    {
        "nombre": "NPR",
        "continente": "América",
        "pais": "Estados Unidos",
        "fuentes": [
            {"url": "https://feeds.npr.org/1014/rss.xml", "categoria_iptc": "11000000"},
            {"url": "https://feeds.npr.org/1128/rss.xml", "categoria_iptc": "07000000"},
        ],
    },
    # --- Europa ---
    {
        "nombre": "El Mundo",
        "continente": "Europa",
        "pais": "España",
        "fuentes": [
            {"url": "https://e00-elmundo.uecdn.es/elmundo/rss/economia.xml", "categoria_iptc": "04000000"},
            {"url": "https://e00-elmundo.uecdn.es/elmundo/rss/ciencia.xml", "categoria_iptc": "13000000"},
        ],
    },
    {
        "nombre": "Sky News",
        "continente": "Europa",
        "pais": "Reino Unido",
        "fuentes": [
            {"url": "https://feeds.skynews.com/feeds/rss/politics.xml", "categoria_iptc": "11000000"},
            {"url": "https://feeds.skynews.com/feeds/rss/technology.xml", "categoria_iptc": "13000000"},
        ],
    },
    # --- Asia ---
    {
        "nombre": "Japan Today",
        "continente": "Asia",
        "pais": "Japón",
        "fuentes": [
            {"url": "https://japantoday.com/category/politics/feed", "categoria_iptc": "11000000"},
            {"url": "https://japantoday.com/category/tech/feed", "categoria_iptc": "13000000"},
        ],
    },
    {
        "nombre": "Dawn",
        "continente": "Asia",
        "pais": "Pakistán",
        "fuentes": [
            {"url": "https://www.dawn.com/feeds/business", "categoria_iptc": "04000000"},
            {"url": "https://www.dawn.com/feeds/sport", "categoria_iptc": "15000000"},
        ],
    },
    # --- África ---
    {
        "nombre": "Premium Times",
        "continente": "África",
        "pais": "Nigeria",
        "fuentes": [
            {"url": "https://www.premiumtimesng.com/category/health/feed", "categoria_iptc": "07000000"},
            {"url": "https://www.premiumtimesng.com/category/sports/feed", "categoria_iptc": "15000000"},
        ],
    },
    {
        # Agregador de cobertura continental: sin país único (pais es opcional).
        "nombre": "AllAfrica",
        "continente": "África",
        "pais": None,
        "fuentes": [
            {"url": "https://allafrica.com/tools/headlines/rdf/business/headlines.rdf", "categoria_iptc": "04000000"},
        ],
    },
    {
        "nombre": "TechCentral",
        "continente": "África",
        "pais": "Sudáfrica",
        "fuentes": [
            {"url": "https://techcentral.co.za/feed/", "categoria_iptc": "13000000"},
        ],
    },
    # --- Oceanía ---
    {
        "nombre": "ABC News",
        "continente": "Oceanía",
        "pais": "Australia",
        "fuentes": [
            {"url": "https://www.abc.net.au/news/feed/104217372/rss.xml", "categoria_iptc": "11000000"},
        ],
    },
    {
        "nombre": "RNZ",
        "continente": "Oceanía",
        "pais": "Nueva Zelanda",
        "fuentes": [
            {"url": "https://www.rnz.co.nz/rss/political.xml", "categoria_iptc": "11000000"},
            {"url": "https://www.rnz.co.nz/rss/business.xml", "categoria_iptc": "04000000"},
            {"url": "https://www.rnz.co.nz/rss/sport.xml", "categoria_iptc": "15000000"},
        ],
    },
]


def main(dataset: list[dict] | None = None, session_factory=SessionLocal) -> int:
    """Ejecuta la carga y devuelve el código de salida (0 = éxito)."""
    db = session_factory()
    try:
        resultado = cargar_dataset(db, CANALES_SEED if dataset is None else dataset)
    except ContinenteFaltanteError as error:
        print(f"Carga inicial cancelada: {error}. No se creó ningún registro.", file=sys.stderr)
        return 1
    except Exception as error:  # noqa: BLE001 - se informa y se termina con código 1
        print(f"Carga inicial revertida por un error: {error}", file=sys.stderr)
        return 1
    finally:
        db.close()

    print(
        f"Carga inicial completada: {resultado.canales_creados} canales y "
        f"{resultado.fuentes_creadas} fuentes creados."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
