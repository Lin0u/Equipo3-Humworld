"""
Caso de uso: carga inicial del diccionario de términos de sentimiento.

Origina en: PDF de especificaciones, sección 4.2.2 ("Deberá existir un
diccionario de términos con palabras y su valor para el cálculo del humor")
y HU-SENT-001 (diccionario de términos). Dataset: docs/Backlog/
Dataset-diccionario-inicial.md.

Reglas:
- Idempotente por (palabra, idioma) literal, igual que la clave de unicidad
  de HU-SENT-001: lo que ya existe se omite y nunca se sobrescribe, para no
  pisar valores ajustados a mano por el administrador.
- Mismas validaciones que el alta por API (idioma es/en, valor entero -10..+10).
- Transacción única: si una fila falla, no se crea ningún término.
- Al terminar, marca una sola vez las noticias para recálculo (HU-SENT-002-v3),
  en vez de una vez por término.
"""
import csv
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.termino_diccionario import TerminoDiccionario
from app.repositories.dictionary import TerminoDiccionarioRepository
from app.services.dictionary_service import validar_campos_termino
from app.services.sentimiento_service import invalidar_calculos_diccionario


@dataclass
class ResultadoSeedDiccionario:
    creados: int = 0
    omitidos: int = 0


def leer_csv(ruta: Path) -> list[dict]:
    """Lee el CSV del dataset (columnas: palabra, idioma, valor, origen)."""
    with ruta.open(encoding="utf-8", newline="") as archivo:
        filas = []
        for numero, fila in enumerate(csv.DictReader(archivo), start=2):
            try:
                valor = int(fila["valor"])
            except (TypeError, ValueError) as error:
                raise ValueError(f"Línea {numero}: valor no entero") from error
            filas.append({"palabra": fila["palabra"], "idioma": fila["idioma"], "valor": valor})
        return filas


def cargar_diccionario(
    db: Session,
    filas: list[dict],
    repository: TerminoDiccionarioRepository | None = None,
) -> ResultadoSeedDiccionario:
    repositorio = repository or TerminoDiccionarioRepository()
    existentes = repositorio.claves_existentes(db)
    nuevos: list[TerminoDiccionario] = []
    resultado = ResultadoSeedDiccionario()

    for fila in filas:
        validar_campos_termino(fila["palabra"], fila["idioma"], fila["valor"])
        clave = (fila["palabra"], fila["idioma"])
        if clave in existentes:
            resultado.omitidos += 1
            continue
        existentes.add(clave)
        nuevos.append(
            TerminoDiccionario(palabra=fila["palabra"], idioma=fila["idioma"], valor=fila["valor"])
        )

    if nuevos:
        repositorio.agregar_lote(db, nuevos)
        resultado.creados = len(nuevos)
        invalidar_calculos_diccionario(db)
    return resultado
