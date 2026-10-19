## Context

Ver [proposal.md](proposal.md) para motivación, alcance y discrepancia registrada; [spec.md](specs/carga-inicial-fuentes-por-continente/spec.md) define el comportamiento esperado. `src/scripts/seed.py` es actualmente una plantilla vacía. Ya existen Servicios para crear `CanalNoticias` y `FuenteRSS`, Repositorios SQLAlchemy para persistirlos y restricciones de unicidad usadas por las altas normales.

## Goals / Non-Goals

**Goals:**

- Mantener un punto de entrada interno repetible que delegue la lógica de negocio y el acceso a datos en sus capas propietarias.
- Garantizar idempotencia por nombre de `CanalNoticias` y URL de `FuenteRSS`, incluida la reutilización de un canal existente cuando falten sus fuentes.
- Verificar la cobertura de América, Europa, Asia, África y Oceanía sin acceder a feeds externos durante la carga ni las pruebas.
- Hacer que la ausencia de datos RSS aprobados sea visible como bloqueo, no como un seed aparentemente completo.

**Non-Goals:**

- Exponer `POST /api/v1/seeds`. Quedó retirado al deprecarse HU-RSS-009 en favor de HU-RSS-009-v2 (contrato v1.7.0). Como la lógica vive en Servicios, un endpoint podría agregarse después con un router que invoque el mismo caso de uso.
- Inventar, descubrir en ejecución o validar por red URLs de feeds.
- Cargar noticias, modificar el cron, cambiar esquema de persistencia o añadir dependencias.

## Decisions

### Participación de capas

- **API:** no participa; esta definición trata el seed como procedimiento interno y no añade router ni endpoint.
- **Servicios:** `src/app/services/canal_service.py` y `fuente_service.py` siguen siendo responsables de validaciones y casos de uso de creación. El script los invoca en lugar de recrear reglas de unicidad o validación.
- **Repositorios:** `src/app/repositories/canales.py` y `fuentes.py` concentran las consultas por nombre/URL, inserciones y transacciones. Cualquier consulta para comprobar existencia queda en estos módulos; el script no ejecuta SQL ni accede directamente a modelos ORM para persistir.
- **Persistencia:** MySQL conserva los registros en las tablas existentes y sus restricciones de unicidad. SQLite en memoria se usa para pruebas aisladas. No se necesita Alembic ni una migración.
- **Script de inicialización:** `src/scripts/seed.py` contiene solo el conjunto de datos aprobado, invoca Servicios en una sesión controlada y presenta un resumen de altas; no conoce consultas SQL.

### Idempotencia y datos

La identidad funcional de un canal semilla es su `nombre`; la de una fuente es su `url`, conforme a las decisiones registradas en HU-RSS-009. Si el canal ya existe, el seed lo reutiliza para asociar fuentes aún ausentes. La ejecución debe ser transaccional o hacer rollback ante un error de persistencia para no dejar una carga parcialmente inconsistente.

No hay todavía una lista aprobada de URLs en el script. Existe un dataset propuesto de 20 fuentes verificadas (`docs/Backlog/Dataset-fuentes-RSS-seed-HU-RSS-009.md`), pendiente de aprobación del equipo; mientras no se apruebe, no se agregan URLs reales al diseño ni a los fixtures. La especificación exige que los datos se validen y aprueben antes de considerar el seed listo. La implementación que intente completar datos reales queda bloqueada hasta que el equipo proporcione el dataset.

### Estrategia de pruebas

- Usar SQLite en memoria y los repositorios/servicios reales para probar la primera carga, repetición idempotente, canal preexistente con fuente faltante, asociación de FK y cobertura de los cinco continentes.
- Usar un dataset pequeño de URLs sintéticas bajo `example.test` solo dentro de pruebas, sin solicitudes HTTP; verificar las claves nombre/URL y cantidades creadas.
- Comprobar rollback o ausencia de duplicados cuando una inserción ya existe.
- No mockear ni invocar Internet: el seed solo registra URL y no descarga feeds.
- Separar la validación del dataset real aprobado del test funcional con fixture sintética; la primera requiere evidencia de validación/ratificación del equipo antes de completar la implementación.

### Ficheros previstos

- Completar `src/scripts/seed.py`.
- Reutilizar o ampliar `src/app/services/canal_service.py` y `fuente_service.py` solo si hace falta un caso de uso idempotente común.
- Reutilizar o ampliar `src/app/repositories/canales.py` y `fuentes.py` para las consultas de existencia necesarias.
- Añadir pruebas en `src/tests/test_seed.py`.
- No modificar routers ni `docs/Contratos/contrato-canales-fuentes-rss.openapi.yaml` bajo el alcance actual.

## Risks / Trade-offs

- **[Riesgo]** La falta de feeds reales impide cumplir cobertura continental en datos de producción → **Mitigación:** mantener la carga de dataset real bloqueada hasta recibir URLs verificadas y aprobadas; no sustituirlas por ejemplos.
- **[Riesgo]** Ejecuciones concurrentes podrían competir por nombres/URLs → **Mitigación:** conservar restricciones de unicidad y tratar colisiones como entidades existentes; probar repetición secuencial y documentar que el seed se ejecuta como tarea administrativa controlada.
- **[Trade-off]** Reutilizar Servicios puede requerir un caso de uso idempotente de seed que no existe hoy; se acepta una ampliación mínima de Servicios/Repositorios antes que duplicar validaciones en el script.

## Migration Plan

No hay migración de esquema. Una vez aprobado el dataset, ejecutar el script contra una base preparada; revisar el resumen de registros creados y la cobertura continental. El rollback de aplicación es retirar el cambio del script. No se borran automáticamente registros creados; si se requiere revertir datos, debe hacerse mediante un procedimiento explícito aprobado por el equipo.