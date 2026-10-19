"""
Caso de uso: carga inicial de canales y fuentes RSS por continente.

Origina en: HU-RSS-009-v2 (Historia Técnica/Enabler Story), que reemplaza a
HU-RSS-009 (Deprecada). PDF de especificaciones, sección 4.2.1 ("carga
inicial de fuentes RSS por continente").
ADR relacionado: ADR-02 (arquitectura de captura RSS, modelo de datos).
Diseño: openspec/changes/Carga-inicial-de-fuentes-RSS-por-continente/design.md.

La lógica vive en la capa de Servicios para que un endpoint pueda invocarla
más adelante sin rehacerla. Reglas:
- Idempotencia: un canal se identifica por su `nombre` y una fuente por su
  `url`. Lo que ya existe se reutiliza o se omite, nunca se duplica.
- Cobertura: el dataset debe incluir los 5 continentes; si falta alguno no se
  crea ningún registro.
- Transacción única: un error de persistencia revierte toda la ejecución.
- Sin red: solo registra URLs, no descarga feeds.
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.canal import CanalNoticias
from app.models.fuente import FuenteRSS
from app.repositories.canales import CanalNoticiasRepository
from app.repositories.fuentes import FuenteRSSRepository
from app.schemas.canal import CanalNoticiasCrear
from app.schemas.fuente import FuenteRSSCrear

# Literales con tilde, decisión de equipo del 2026-10-18 (HU-RSS-009-v2).
CONTINENTES_REQUERIDOS: tuple[str, ...] = ("América", "Europa", "Asia", "África", "Oceanía")


class ContinenteFaltanteError(Exception):
    """El dataset no cubre al menos uno de los 5 continentes requeridos."""

    def __init__(self, faltantes: list[str]):
        self.faltantes = faltantes
        super().__init__(
            "El dataset no incluye fuentes para: " + ", ".join(faltantes)
        )


@dataclass
class ResultadoSeed:
    canales_creados: int = 0
    fuentes_creadas: int = 0


def validar_cobertura(dataset: list[dict]) -> None:
    """Exige al menos 1 canal con al menos 1 fuente por continente requerido."""
    cubiertos = {
        canal["continente"] for canal in dataset if canal.get("fuentes")
    }
    faltantes = [c for c in CONTINENTES_REQUERIDOS if c not in cubiertos]
    if faltantes:
        raise ContinenteFaltanteError(faltantes)


def cargar_dataset(
    db: Session,
    dataset: list[dict],
    canal_repository: CanalNoticiasRepository | None = None,
    fuente_repository: FuenteRSSRepository | None = None,
) -> ResultadoSeed:
    """Carga el dataset de forma idempotente y en una sola transacción.

    Lanza ContinenteFaltanteError (sin escribir nada) si falta un continente,
    pydantic.ValidationError si un registro no cumple las mismas reglas que
    las altas normales (HU-RSS-001, HU-RSS-002), y relanza SQLAlchemyError
    tras revertir la transacción.
    """
    canales_repo = canal_repository or CanalNoticiasRepository()
    fuentes_repo = fuente_repository or FuenteRSSRepository()

    validar_cobertura(dataset)
    resultado = ResultadoSeed()

    try:
        for datos_canal in dataset:
            datos_fuentes = datos_canal.get("fuentes", [])
            payload_canal = CanalNoticiasCrear(
                **{k: v for k, v in datos_canal.items() if k != "fuentes"}
            )

            canal = canales_repo.buscar_por_nombre(db, payload_canal.nombre)
            if canal is None:
                canal = canales_repo.agregar_sin_confirmar(
                    db, CanalNoticias(**payload_canal.model_dump())
                )
                resultado.canales_creados += 1

            for datos_fuente in datos_fuentes:
                payload_fuente = FuenteRSSCrear(canal_id=canal.id, **datos_fuente)
                url = str(payload_fuente.url)
                if fuentes_repo.buscar_por_url(db, url) is not None:
                    continue
                fuentes_repo.agregar_sin_confirmar(
                    db,
                    FuenteRSS(
                        canal_id=canal.id,
                        url=url,
                        categoria_iptc=payload_fuente.categoria_iptc,
                        activo=True,
                    ),
                )
                resultado.fuentes_creadas += 1

        db.commit()
    except Exception:
        db.rollback()
        raise

    return resultado
