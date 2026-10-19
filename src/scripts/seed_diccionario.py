"""
Carga inicial del diccionario de términos de sentimiento.

Origina en: PDF, sección 4.2.2, y HU-SENT-001. Dataset propuesto en
docs/Backlog/Dataset-diccionario-inicial.md (pendiente de aprobación del
equipo): AFINN-en-165 en inglés (valores × 2) y una traducción al español
de un subconjunto orientado a noticias.

Licencia de los datos: scripts/data/diccionario_seed.csv es una base de
datos derivada de AFINN-en-165 (© Finn Årup Nielsen, Technical University of
Denmark) y se distribuye bajo la Open Database License (ODbL) v1.0, igual
que el original. Ver scripts/data/AFINN-LICENSE.txt.

Uso (desde src/, o dentro del contenedor):
    python -m scripts.seed_diccionario
    docker compose exec api python -m scripts.seed_diccionario
"""
import sys
from pathlib import Path

from app.database import SessionLocal
from app.services.seed_diccionario_service import cargar_diccionario, leer_csv

RUTA_DATASET = Path(__file__).parent / "data" / "diccionario_seed.csv"


def main(ruta: Path = RUTA_DATASET, session_factory=SessionLocal) -> int:
    """Ejecuta la carga y devuelve el código de salida (0 = éxito)."""
    db = session_factory()
    try:
        resultado = cargar_diccionario(db, leer_csv(ruta))
    except Exception as error:  # noqa: BLE001 - se informa y se termina con código 1
        db.rollback()
        print(f"Carga del diccionario cancelada: {error}", file=sys.stderr)
        return 1
    finally:
        db.close()

    print(
        f"Diccionario cargado: {resultado.creados} términos creados, "
        f"{resultado.omitidos} ya existían."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
