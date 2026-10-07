## 1. Decisiones y datos de entrada bloqueantes

- [x] 1.1 Reconciliar con el equipo la discrepancia entre esta solicitud (procedimiento interno sin endpoint) y el HU-RSS-009 vigente (`POST /api/v1/seeds`); verificar el alcance aprobado actualizando backlog/contrato o confirmando formalmente que quedan fuera de este cambio. Confirmado por el usuario: este cambio cubre solo el procedimiento interno; el endpoint queda fuera.
- [ ] 1.2 Obtener del equipo un dataset de feeds RSS reales verificados y aprobados, con al menos un `CanalNoticias` y una `FuenteRSS` por América, Europa, Asia, África y Oceanía; verificar URL, continente, canal asociado y categoría IPTC de cada elemento. No iniciar las tareas de implementación mientras este insumo esté pendiente.

## 2. Servicios y Repositorios

- [ ] 2.1 Definir un caso de uso idempotente para crear/reutilizar canales por `nombre` y fuentes por `url`, delegando validación y persistencia; verificarlo con pruebas de servicio sobre SQLite.
- [ ] 2.2 Añadir o reutilizar operaciones de Repositorio para consultar por nombre de `CanalNoticias` y URL de `FuenteRSS`; verificar que todo acceso SQL queda en `app/repositories/`.
- [ ] 2.3 Verificar que una fuente semilla faltante se asocia al canal existente y que una colisión de unicidad no deja transacciones abiertas ni duplicados.

## 3. Script de carga inicial

- [ ] 3.1 Completar `src/scripts/seed.py` con el dataset aprobado y coordinación mediante Servicios, sin SQL ni acceso directo a persistencia desde el script; verificar el comando de ejecución en una base SQLite de prueba.
- [ ] 3.2 Informar cantidades de `CanalNoticias` y `FuenteRSS` creados y verificar que una primera carga deja al menos un canal y una fuente asociada por cada continente contemplado.

## 4. Pruebas y calidad

- [ ] 4.1 Añadir pruebas con dataset sintético de prueba y SQLite para base vacía, ejecución repetida, canal existente con fuente faltante, asociación válida y cobertura de los cinco continentes; asegurar que no hay solicitudes HTTP reales.
- [ ] 4.2 Ejecutar `pytest` y `pytest-cov`; verificar que toda la suite pasa y alcanza cobertura mínima del 80%.
- [ ] 4.3 Revisar conformidad final con `docs/architecture.md`, `openspec/config.yaml` y los ADR vigentes; verificar separación API/Servicios/Repositorios/Persistencia, ausencia de endpoint bajo el alcance confirmado y que los feeds ejecutables fueron aprobados por el equipo.