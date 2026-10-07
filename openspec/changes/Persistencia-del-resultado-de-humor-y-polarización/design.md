## Context

Ver [proposal.md](proposal.md) para motivación y alcance y [spec.md](specs/persistencia-resultado-humor/spec.md) para el contrato observable. `Noticia` ya contiene `valor_humor FLOAT NULL`, pero no `polarizacion_terminos` ni `metodo_calculo`. El ADR-03 define polarización como desviación estándar poblacional de los términos coincidentes y el diagrama UML actual refleja solo los campos de EPIC-RSS.

## Goals / Non-Goals

**Goals:**

- Persistir los tres atributos de resultado en la misma fila de `Noticia` y preservarlos en round-trip.
- Mantener nulos los valores de humor y polarización cuando no haya términos evaluables.
- Aplicar cambios de esquema con Alembic sobre MySQL y actualizar el UML de clases.
- Mantener el acceso a datos en Repositorios y delegar persistencia desde Servicios.

**Non-Goals:**

- Calcular humor/polarización, seleccionar método ML/diccionario o ejecutar fallback (HU-SENT-002-v2/HU-SENT-007).
- Cambiar el CRUD del diccionario, crear endpoints, consultas agregadas o persistir la versión ML, que pertenece a HU-SENT-006.
- Introducir tabla nueva: el resultado es parte de `Noticia`.

## Decisions

### Participación de capas

- **API:** no participa; HU-SENT-003 no expone endpoints. Los routers existentes no se modifican.
- **Servicios:** el flujo de sentimiento entrega al servicio/repositorio de noticias un resultado ya calculado; aquí no se implementa algoritmo. La capa de Servicio coordina el guardado y mantiene independencia de FastAPI.
- **Repositorios — `src/app/repositories/noticias.py`:** añade/ajusta la operación para persistir y recuperar `valor_humor`, `polarizacion_terminos` y `metodo_calculo`, con commit/rollback consistente. No contiene cálculo de sentimiento.
- **Persistencia — `src/app/models/noticia.py` + Alembic:** añade `polarizacion_terminos FLOAT NULL` y `metodo_calculo VARCHAR`/`String` con valores restringidos a `diccionario` o `ml` en la capa de dominio. Se conserva `valor_humor FLOAT NULL`. La polarización se define FLOAT nullable porque la desviación estándar puede ser decimal y no existe cuando no hay valores evaluados. No se agrega versión ML ni tabla de modelos.
- **Documentación de datos — `docs/UML/diagrama-clases.md`:** actualizar la clase `Noticia` para reflejar los dos campos nuevos, manteniendo relaciones actuales.

### Transacción y NULL

La escritura del resultado se realiza mediante repositorio y conserva atomicidad de los campos de resultado. Si el cálculo no encuentra términos evaluables, Servicio entrega `valor_humor=None` y `polarizacion_terminos=None`, junto con `metodo_calculo=diccionario`; cero neutral permanece `0.0`. Se descarta una tabla separada porque el PDF y HU-SENT-003 exigen que los resultados acompañen a la noticia.

### Estrategia de pruebas

- SQLite en memoria para crear y recuperar `Noticia` con valores mixtos, comprobando round-trip de `valor_humor`, polarización y método.
- Probar resultado con decimales, `NULL` para cero términos y `0.0` para neutral evaluado.
- Probar que un fallo de commit hace rollback del conjunto de campos, sin alterar los datos previos de la noticia.
- Validar la migración con generación de SQL offline MySQL y verificar que downgrade retira solo los campos añadidos.
- Verificar el diagrama UML actualizado; no se hacen llamadas HTTP ni mocks externos porque esta historia solo persiste datos.

### Ficheros afectados

- Modificar `src/app/models/noticia.py`.
- Modificar `src/app/repositories/noticias.py`.
- Añadir una migración Alembic encadenada a la revisión vigente.
- Actualizar `docs/UML/diagrama-clases.md`.
- Añadir/expandir pruebas en `src/tests/` para persistencia de resultados.
- Sin cambios a routers, schemas HTTP ni contratos OpenAPI.

## Risks / Trade-offs

- **[Riesgo]** El valor de polarización queda sin definir con cero términos → **Mitigación:** persistir `NULL` y cubrirlo explícitamente, diferenciándolo del humor neutral `0.0`.
- **[Riesgo]** Migración no coincide con tipos de MySQL del entorno → **Mitigación:** generar SQL offline, probar migración en CI/entorno MySQL antes de merge y mantener tipos compatibles con MySQL.
- **[Riesgo]** Método de cálculo recibe valores no permitidos → **Mitigación:** restringirlo a `diccionario`/`ml` en validación del Servicio y esquema de persistencia sin duplicar el algoritmo.

## Migration Plan

Crear migración Alembic que agregue `polarizacion_terminos FLOAT NULL` y `metodo_calculo` nullable inicialmente para no romper noticias existentes; tras despliegue, el flujo HU-SENT-002-v2 escribirá método en los nuevos cálculos. No hay backfill fiable para noticias antiguas. El downgrade elimina únicamente las dos columnas nuevas y debe ejecutarse solo si el equipo acepta perder esos datos.