"""
Script de carga inicial (seed) de canales y fuentes RSS por continente.

Origina en: HU-RSS-009 (Historia Técnica/Enabler Story).
Fuente: PDF de especificaciones, sección 4.2.1 ("Deberá existir una carga
inicial de fuentes RSS por continente") y sección 5 (Fuentes de Información,
ejemplos de medios españoles — ilustrativos, no exhaustivos).

Nota de alcance (grounding, ver HU-RSS-009): el PDF NO especifica el listado
exacto ni el número mínimo de fuentes por continente. El listado definitivo
de fuentes semilla DEBE ser definido por el equipo, cuidando cubrir todos
los continentes contemplados. Este script queda con una lista vacía a modo
de plantilla — TODO(equipo).

Uso previsto (una vez implementado):
    python -m scripts.seed
"""
from app.database import SessionLocal

# TODO(equipo): completar con canales y fuentes reales por continente,
# cuidando cobertura de todos los continentes exigida por HU-RSS-009.
# Ejemplo de estructura esperada (NO usar estos datos como definitivos):
CANALES_SEED: list[dict] = [
    # {
    #     "nombre": "RTVE",
    #     "continente": "Europa",
    #     "pais": "España",
    #     "fuentes": [
    #         {"url": "https://www.rtve.es/rss/", "categoria_iptc": "..."},
    #     ],
    # },
]


def ejecutar_seed() -> None:
    """
    Idempotente: no debe crear registros duplicados si se ejecuta más de
    una vez (criterio de aceptación de HU-RSS-009, escenario "Ejecución
    repetida del script de carga inicial").
    """
    db = SessionLocal()
    try:
        # TODO(equipo): implementar inserción idempotente (verificar
        # existencia por "nombre" de canal antes de crear).
        raise NotImplementedError("Script de seed pendiente de implementación — HU-RSS-009")
    finally:
        db.close()


if __name__ == "__main__":
    ejecutar_seed()
