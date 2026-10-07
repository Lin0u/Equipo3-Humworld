## Why

El valor de humor calculado debe sobrevivir a la ejecución del proceso y estar disponible para consultas posteriores, junto con la señal de polarización definida por el método de diccionario. HU-SENT-003 formaliza la persistencia del resultado de HU-SENT-002-v2 en la misma `Noticia` capturada.

## What Changes

- Extender `Noticia` con `polarizacion_terminos` nullable, manteniendo `valor_humor` y añadiendo `metodo_calculo` para identificar `diccionario` o `ml`.
- Persistir humor y polarización calculados en el registro de noticia ya existente, sin endpoint nuevo.
- Usar `FLOAT NULL` para polarización: la desviación estándar es un valor real y queda nula cuando no hay términos evaluables; mantener `valor_humor=NULL` en ese caso.
- Añadir migración Alembic y actualizar el modelo ORM y documentación UML del modelo de datos.
- Mantener separadas las historias: persistir el resultado que entrega HU-SENT-002-v2; no implementar aquí el algoritmo/fallback de cálculo (HU-SENT-007/002-v2), el CRUD del diccionario (HU-SENT-001), agregaciones ni dashboard.
- Este cambio forma parte del incremento actual junto con HU-SENT-001 y HU-SENT-002-v2. Las demás HU-SENT permanecen fuera.
- No se requieren cambios a `docs/architecture.md` ni a ADR-03; el tipo propuesto sigue el valor real numérico ya usado por `Noticia.valor_humor`.

## Capabilities

### New Capabilities

- `persistencia-resultado-humor`: Persistencia y lectura del valor de humor, polarización y método de cálculo junto a cada `Noticia`.

### Modified Capabilities

<!-- No existen especificaciones base en openspec/specs/ para modificar. -->

## Impact

- Persistencia/ORM: extensión de `src/app/models/noticia.py` y migración Alembic para `polarizacion_terminos` y `metodo_calculo`.
- Repositorios: lectura/escritura transaccional de los campos de resultado sobre `Noticia`.
- Documentación: actualización de `docs/UML/diagrama-clases.md` para reflejar la entidad persistida.
- Pruebas: SQLite para round-trip y migración; fixtures deterministas con `TestClient` innecesario al no haber API nueva.
- Sin endpoints, dependencias ni cambios a tablas de entrenamiento ML.