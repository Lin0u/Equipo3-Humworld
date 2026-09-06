# PLANIFICACIÓN ÁGIL DE HUMWORLD — DOCUMENTO ENTREGADO EN P3 (fuente de verdad oficial)

**Estado:** Entregado — este es el documento que el equipo efectivamente subió como entregable de la Práctica P3 "Planificación Ágil de HumWorld".
**Registrado en el Proyecto Claude:** 2026-08-19, a partir del archivo `HumWorld_Planificacion_Agil_HUMWORLD_1.md` subido por el usuario.

> **Nota de consistencia (importante):** este documento contiene una versión de las Historias de Usuario del módulo RSS (HU-RSS-001 a HU-RSS-005) y una numeración de ADRs (ADR-001, ADR-002 "Elección del método de cálculo del humor", ADR-003 "Patrones de resiliencia para captura RSS") que **difieren** de los documentos previamente generados en este Proyecto (`HU-RSS-captura.md` con HU-RSS-001 a 009, y `ADR-002-arquitectura-captura-rss.md`). Ver conversación del 2026-08-19 para el detalle de las discrepancias y la decisión pendiente de reconciliación del equipo.

---

# PLANIFICACIÓN ÁGIL DE HUMWORLD — DOCUMENTO COMPLETO (PASOS 1 A 6)

**Equipo:** Equipo 3 Commit
**Referencia:** `P3__ESPEC_Y_PLANIFICACIÓN.pdf` (Workshop) + `0_PROYECTO_FINAL_HUMWORLD_260714.pdf` (Especificación)
**Fecha límite de desarrollo (fija):** 02-nov-2026 — Verificación formal del sistema
**Duración de sprint:** 2 semanas (recomendado en syllabus §8.1)
**Versión del documento:** 2.0 (consolida en un único archivo los Pasos 1-6, generados en dos sesiones)

---

## ÍNDICE

- **PASO 1** — Creación del Backlog Inicial (Épicas + Historias de Usuario)
- **PASO 2** — Backlog Definitivo (revisión crítica)
- **PASO 3** — Planificación de Sprints
- **PASO 4** — Estimación de Esfuerzo (Planning Poker)
- **PASO 5** — Definition of Done (DoD)

---

## PASO 1 — CREACIÓN DEL BACKLOG INICIAL (Agente Product Owner y Arquitecto)

> **Épicas y estructura general:** el proyecto se organiza en 4 épicas — EPIC-RSS (captura de noticias), EPIC-SENT (motor de análisis de sentimiento/humor), EPIC-DASH (dashboards) y EPIC-ADMIN (administración y configuración).

## 1. Épicas principales

| ID Épica | Nombre | Descripción | Referencia PDF |
|---|---|---|---|
| EPIC-RSS | Captura y Gestión de Fuentes RSS | Alta/gestión de canales y fuentes RSS, captura automática y manual de noticias, almacenamiento con metadatos | §4.1, §4.2.1, §4.2.3, §4.2.4 |
| EPIC-SENT | Motor de Análisis de Sentimiento (Humor) | Diccionario de términos evaluables, cálculo del valor de humor por noticia, consulta agregada del sentimiento | §4.2.2, §4.2.4, §10.4 |
| EPIC-DASH | Dashboards y Visualización | Mapa mundial de humor, nube de palabras influyentes, listado de noticias influyentes | §4.3, §4.3.1, §4.3.2 |
| EPIC-ADMIN | Administración y Configuración | Panel de administración, parámetros generales, purgado de información antigua | §4.2.5, §4.3 (punto 1) |

---

## PASO 3 — PLANIFICACIÓN DE SPRINTS

**Duración de sprint:** 2 semanas (6 sprints, 10-ago a 01-nov).

### Calendario de Sprints

| Sprint | Fecha inicio | Fecha fin |
|---|---|---|
| Sprint 0 | 10-ago-26 | 23-ago-26 |
| Sprint 1 | 24-ago-26 | 06-sep-26 |
| Sprint 2 | 07-sep-26 | 20-sep-26 |
| Sprint 3 | 21-sep-26 | 04-oct-26 |
| Sprint 4 | 05-oct-26 | 18-oct-26 |
| Sprint 5 | 19-oct-26 | 01-nov-26 |
| — | **02-nov-26** | **VERIFICACIÓN FORMAL** |

### Sprint 1 — "Captura de noticias" (oficial, según entregable P3)

- **Sprint Goal:** Disponer de un sistema funcional de gestión de fuentes RSS y captura automática/manual de noticias, con persistencia en base de datos.
- **Historias incluidas:** HU-RSS-001, HU-RSS-002, HU-RSS-003, HU-RSS-004, HU-RSS-005.
- **Bloqueante a resolver antes de HU-RSS-004:** ADR-003 "Patrones de resiliencia para captura RSS" (Aceptado).
- **Estimación (Planning Poker, Fibonacci):** HU-RSS-001 (1), HU-RSS-002 (2), HU-RSS-003 (2), HU-RSS-004 (3), HU-RSS-005 (3) — **Total: 11 puntos**.
- **Entregables:** API REST de `/fuentes-rss` documentada en Swagger, cron de captura operativo, contrato OpenSpec de la épica RSS.

(Ver el archivo original subido por el usuario, `HumWorld_Planificacion_Agil_HUMWORLD_1.md`, para el detalle completo de las 19 historias, Gherkin, Sprints 2-5, y la Definition of Done consolidada del Paso 5.)

---

## PASO 5 — DEFINITION OF DONE (DoD) — resumen

1. Código revisado vía PR (≥1 revisión).
2. Pruebas unitarias con Mocks/Stubs para dependencias externas.
3. Cobertura ≥ 80%, verificada en GitHub Actions.
4. SonarQube sin issues críticos.
5. Swagger/OpenAPI actualizado.
6. ADRs relacionados en estado Aceptado.
7. Contratos OpenSpec aprobados.
8. Documentación `/docs` actualizada.
9. Build y despliegue Docker exitosos (`needs: [test, sonarqube]`).
10. Validación visual (solo historias de UI/dashboard).
