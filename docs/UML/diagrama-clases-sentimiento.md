# Modelo de Clases / Entidad-Relación — Módulo Motor de Análisis de Sentimiento (EPIC-SENT)

**Proyecto:** HumWorld — Equipo 3
**Origen:** PDF de especificaciones, sección 4.7.3.b ("Documentación UML de diseño → Modelo Entidad/Relación o diagrama de clases"). Modelo decidido y justificado en `ADR-03-eleccion-algoritmo-agregacion-sentimiento.md` (algoritmo de diccionario) y `ADR-04-arquitectura-modelo-ml-sentimiento.md` (arquitectura del modelo de ML), y detallado por historia en `HU-SENT-motor-sentimiento.md` y en `contrato-sentimiento-diccionario.openapi.yaml`.
**Estado de implementación:** **Diseño — pendiente de implementación en código.** A diferencia de `diagrama-clases.md` (EPIC-RSS, que documenta el modelo ya implementado en el repositorio, Sprint 1), este diagrama refleja las decisiones de arquitectura ya tomadas para EPIC-SENT (Sprint 2 en adelante) pero que todavía no tienen código correspondiente en el repositorio. Debe actualizarse para reflejar el código real una vez implementado, siguiendo el mismo criterio que se usó para `diagrama-clases.md`.

## Diagrama

```mermaid
classDiagram
    class Noticia {
        <<extendida por EPIC-SENT>>
        +float valor_humor
        +MetodoCalculo metodo_calculo
        +int cantidad_terminos_evaluados
        +float polarizacion_terminos
        +int modelo_sentimiento_id
    }

    class MetodoCalculo {
        <<enumeration>>
        DICCIONARIO
        ML
    }

    class TerminoDiccionario {
        +int id
        +string palabra
        +Idioma idioma
        +int valor
    }

    class Idioma {
        <<enumeration>>
        ES
        EN
    }

    class ModeloSentimiento {
        +int id
        +string version
        +string ruta_archivo
        +string modelo_embeddings_usado
        +float mae_evaluacion
        +datetime fecha_entrenamiento
        +bool activo
    }

    Noticia --> MetodoCalculo : usa
    TerminoDiccionario --> Idioma : usa
    ModeloSentimiento "0..1" o-- "0..*" Noticia : calculó (agregación)
```

## Notas de grounding y campos pendientes de confirmación

- **`Noticia` es la misma entidad ya definida en `diagrama-clases.md` (EPIC-RSS)** — este diagrama no la redefine, solo muestra los atributos que EPIC-SENT le agrega o le da uso. `valor_humor` ya existía, nullable, reservado para este módulo (ver `diagrama-clases.md`).
- **`metodo_calculo`** (`"diccionario"` | `"ml"`): exigido explícitamente por el Gherkin de HU-SENT-002-v2 y HU-SENT-003 ("se registra el metodo_calculo usado"). Nullable mientras la noticia no tenga humor calculado (indicador de "pendiente", ver HU-SENT-002-v2 y HU-SENT-003).
- **`cantidad_terminos_evaluados`** (int): cantidad de términos únicos del diccionario que coincidieron en la noticia (divisor `n` del promedio, HU-SENT-007). Lo exigen el Gherkin de HU-SENT-007 ("cantidad_terminos_evaluados = 0") y el contrato de sentimiento (`AnalisisTextoResultado`).
- **Migraciones (decisión de equipo, 2026-10-18):** la migración de HU-SENT-002-v2 crea `metodo_calculo` y `cantidad_terminos_evaluados`; la de HU-SENT-003 crea solo `polarizacion_terminos` y se encadena después de la anterior. Así ninguna de las dos intenta crear una columna que ya existe.
- **`polarizacion_terminos`** (float, nullable): nombre propuesto por `ADR-03-eleccion-algoritmo-agregacion-sentimiento.md` (sección "Indicador complementario de polarización"). **Implementado el 2026-10-19** (HU-SENT-003, migración `a7c3e9b5d1f4`) como desviación estándar poblacional de los valores de los términos coincidentes; NULL si no hay términos.
- **`CoincidenciaTermino`** (tabla `noticia_termino`, HU-SENT-008, migración `e5a1c7d3f9b2`): composición con `Noticia` (`ON DELETE CASCADE`) y referencia a `TerminoDiccionario` (también en cascada al eliminar el término). Ver el diagrama en `HU-SENT-008-coincidencias-terminos.md`.
- **`modelo_sentimiento_id`** (int, nullable, FK a `ModeloSentimiento`): el Gherkin de HU-SENT-002-v2 exige persistir "el identificador de versión del modelo usado" cuando `metodo_calculo="ml"`, pero ninguna HU ni ADR le asigna todavía un nombre de campo formal. **El nombre `modelo_sentimiento_id` es una propuesta de este diagrama, no una decisión ya tomada por el equipo** — debe confirmarse junto con `polarizacion_terminos` antes de la migración de base de datos.
- **`TerminoDiccionario`** corresponde 1:1 al esquema `TerminoDiccionario` de `contrato-sentimiento-diccionario.openapi.yaml` (HU-SENT-001). `idioma` está acotado a español/inglés por el alcance del PDF (sección 3, punto 2).
- **`ModeloSentimiento`** corresponde a la tabla de metadatos `modelos_sentimiento` definida en `ADR-04-arquitectura-modelo-ml-sentimiento.md`, sección "Esquema de versionado de modelos" — mismos campos, mismos tipos.
- **No existe una relación persistida entre `Noticia` y `TerminoDiccionario`.** El método de diccionario (HU-SENT-007) compara el texto de la noticia contra el diccionario **en el momento del cálculo**, sin persistir una tabla de unión — por eso no se dibuja ninguna asociación entre ambas clases. Si en el futuro se necesitara auditar qué términos específicos coincidieron en cada noticia, sería una extensión nueva de HU-SENT-007, no contemplada hoy. **Actualización (2026-10-05):** HU-SENT-008 (Propuesta, pendiente de ratificación) propone persistir esas coincidencias en una tabla de unión para la nube de palabras de HU-DASH-003-v2; si se ratifica, este diagrama debe incorporarla.
- **`ModeloSentimiento` "0..1" o-- "0..\*" `Noticia` (agregación, no composición):** una `Noticia` calculada con un modelo no depende de que ese modelo exista para seguir teniendo sentido (su `valor_humor` ya quedó fijado); y un `ModeloSentimiento` puede existir con cero noticias calculadas aún (justo después de entrenarse). Ninguna de las dos vive ni muere por la otra — de ahí la agregación, coherente con el mismo criterio ya aplicado a `FuenteRSS`──`Noticia` en `diagrama-clases.md`.
- **`ruta_archivo`** es la ubicación en disco/volumen Docker del regresor serializado (`.joblib`, ver ADR-04) — es un dato interno del backend, no se expone en la respuesta de `POST /api/v1/trainings` (ver `contrato-sentimiento-diccionario.openapi.yaml`, esquema `ModeloSentimiento`, nota de diseño).

## Historial de revisión

| Versión | Fecha | Motivo del cambio |
|---|---|---|
| v1.0 | 2026-09-29 | Creación inicial. Modela la extensión de `Noticia` (metodo_calculo, polarizacion_terminos, modelo_sentimiento_id — estos dos últimos como nombres de campo propuestos, no confirmados) y las nuevas entidades `TerminoDiccionario` y `ModeloSentimiento`, a partir de `ADR-03`, `ADR-04`, `HU-SENT-motor-sentimiento.md` y `contrato-sentimiento-diccionario.openapi.yaml`. Diagrama de diseño, sin código correspondiente todavía. |
| v1.1 | 2026-10-18 | Corrección de multiplicidad: `ModeloSentimiento "1" o-- "0..*" Noticia` pasa a `"0..1"`, porque `modelo_sentimiento_id` es nullable (solo se informa cuando `metodo_calculo="ml"`). Esta corrección existía en la copia del Proyecto de Claude desde el 2026-09-29 y se incorpora aquí. |
| v1.2 | 2026-10-18 | Se agrega `cantidad_terminos_evaluados` (int) a `Noticia`, que usan HU-SENT-007, el contrato de sentimiento y la propuesta OpenSpec de HU-SENT-002-v2. Decisión de equipo sobre migraciones: la de HU-SENT-002-v2 crea `metodo_calculo` y `cantidad_terminos_evaluados`; la de HU-SENT-003 crea solo `polarizacion_terminos`, encadenada después. |
| v1.3 | 2026-10-19 | `polarizacion_terminos` deja de ser nombre propuesto: se implementa en HU-SENT-003. Se documenta la entidad `CoincidenciaTermino` (`noticia_termino`) de HU-SENT-008. |
