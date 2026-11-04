# Organización real de los sprints ejecutados — HumWorld

**Proyecto:** HumWorld — Equipo 3
**Propósito:** entregable de §4.7 punto 7 ("Organización del proyecto en sprints con *sprint goals* e historias de usuario por Sprint"), reflejando lo que **efectivamente se ejecutó**, no solo lo planificado.
**Relación con los documentos de P3:** este documento **no modifica** los entregables de la Práctica P3 (`PLANIFICACION-AGIL-HUMWORLD-ENTREGADO-P3.md` y `Anexo-I-Planificacion-entregado-P3.md`), que se conservan como la planificación oficial. Aquí se registra la ejecución real y las desviaciones respecto de esa planificación.

**Fuentes (reconstrucción):**
- Historial de commits y ramas de la rama `main` del repositorio (`git log`, `git for-each-ref`).
- Tablas de control de versiones de cada documento del backlog (`docs/Backlog/`), que registran fecha/sesión y motivo de cada cambio por historia.
- Calendario de sprints oficial del Anexo I de P3 (sprints de 2 semanas, del 10-ago al 01-nov-2026).

**Advertencia de método:** la asignación de cada commit a un sprint se hace por su fecha dentro del calendario oficial. El historial de git muestra que buena parte de la implementación de EPIC-SENT, EPIC-DASH y EPIC-ADMIN se integró a `main` de forma concentrada entre el 18 y el 20 de octubre (Sprint 5), aunque su diseño y backlog se habían preparado en sprints anteriores. Donde el commit no permite afirmar con certeza cuándo se hizo el trabajo, se indica explícitamente.

**Calendario oficial de sprints (Anexo I, P3):**

| Sprint | Inicio | Fin |
|---|---|---|
| Sprint 0 | 10-ago-26 | 23-ago-26 |
| Sprint 1 | 24-ago-26 | 06-sep-26 |
| Sprint 2 | 07-sep-26 | 20-sep-26 |
| Sprint 3 | 21-sep-26 | 04-oct-26 |
| Sprint 4 | 05-oct-26 | 18-oct-26 |
| Sprint 5 | 19-oct-26 | 01-nov-26 |
| — | 02-nov-26 | Verificación formal del sistema |

---

## Sprint 0 — Configuración del entorno, arquitectura base y CI/CD mínimo

**Goal planificado (P3):** configuración del entorno, definición de arquitectura, repositorio y herramientas.

**Ejecutado:**
- Commit inicial del repositorio (`08f9a61`, 12-ago).
- Scaffolding inicial del módulo de captura RSS (`7a39592`, 21-ago).
- Inicialización de OpenSpec para SDD y primera propuesta OpenSpec de HU-RSS-001 (`e85188c`, `09d8606`, 21-ago).
- Configuración del pipeline de CI/CD con SonarQube: `sonar-project.properties` y actualización de la action de SonarQube (`8233b61`, `51fa76c`, 23-ago).

**Historias incluidas:** sin historias de producto (tareas técnicas de fundación), según el Anexo I.

**Observación:** coincide con lo planificado. El pipeline quedó operativo al final del sprint; la historia de control de versiones de `HU-RSS-captura.md` registra que los runs de CI quedaron en verde a partir del #5 (posterior al 23-ago).

---

## Sprint 1 — Captura y gestión de fuentes RSS

**Goal planificado (P3):** disponer de un sistema funcional de gestión de fuentes RSS y captura automática/manual de noticias, con persistencia en base de datos. Historias HU-RSS-001 a HU-RSS-005.

**Ejecutado:**
- Configuración de OpenSpec y Copilot para el módulo de captura (`625d59b`, 31-ago).
- Documentos de arquitectura (`bf3543f`, 02-sep).
- Implementación de HU-RSS-001 a HU-RSS-005 (`f25f376`, 05-sep) y de HU-RSS-010 (`1be0dd2`, rama `feature/consulta-listado-canales-noticias`, merge `5189b81`, 05-sep).
- Pruebas de las historias 1-5 y 10 del Sprint 1 (`bf31e3e`, 06-sep); ajuste de `ci.yml` (`7a5c18b`, 06-sep); documentación y detalles UML (`f872007`, `2b8468f`, 06-sep).

**Historias incluidas (ejecutadas):** HU-RSS-001, HU-RSS-002, HU-RSS-003-v2, HU-RSS-004, HU-RSS-005, HU-RSS-010.

**Desviaciones respecto de P3:**
- Se añadió **HU-RSS-010** (listado y detalle de canales), no contemplada en el Anexo I original, para cubrir el requisito de consulta de canales (§4.2.1) con criterios propios.
- **HU-RSS-003** se versionó a **HU-RSS-003-v2** (se agregó paginación). La numeración del Anexo I de P3 difiere de la del backlog vigente (ver nota al final).
- Evidencia de DoD en CI (cobertura ≥80% y build con `needs`) registrada en `HU-RSS-captura.md` para estas 6 historias (run #16, commit `7a5c18b`).

---

## Sprint 2 — Motor de análisis de sentimiento y diccionario

**Goal planificado (P3):** motor de sentimiento funcional vía fallback de diccionario. Historias HU-SENT-001 a HU-SENT-005 y HU-SENT-007.

**Ejecutado (preparación de backlog y diseño):**
- Borrador de nuevos ADRs (`971d40d`, 23-sep).
- Historias HU-SENT-001 a HU-SENT-007 agregadas al backlog (`7b1b4e6`, `81fca7d`, 28-sep) y actualización de HU-RSS (`324b694`, 28-sep).
- ADR-004 (arquitectura del modelo de ML), ADR de algoritmo de agregación de sentimiento, y contrato OpenSpec de EPIC-SENT (`d92b0aa`, `dc46af3`, `fb313ec`, 29-sep); nuevos diagramas UML de sentimiento (`9bebce4`, 29-sep).

**Historias incluidas (diseño/backlog):** HU-SENT-001 a HU-SENT-007 (definición de historias, ADRs y contrato).

**Desviación respecto de P3:** en este sprint se consolidó el **diseño** de EPIC-SENT (historias, ADRs, contrato, UML), pero la **implementación** del motor de sentimiento se integró a `main` más tarde (Sprint 5, ver abajo). El historial de git no muestra código de cálculo de humor mergeado en las fechas de Sprint 2.

---

## Sprint 3 — Dashboards e interfaz de visualización

**Goal planificado (P3):** ofrecer dashboards interactivos sobre los datos de humor. Historias HU-DASH-001 a HU-DASH-003.

**Ejecutado (diseño y maqueta):**
- Rama `feature/frontend-dashboards` (primer commit 04-oct): maqueta del frontend React con las tres vistas.
- Renombrado de ADR-003 para consistencia (`2a4c910`, 03-oct) y arreglo de trazabilidad por cambios a ADRs (`ddd1aaa`, 03-oct).
- Revisión de consistencia de EPIC-DASH (`Revision-consistencia-EPIC-DASH-2026-10-05.md`), que originó HU-SENT-008 y las deprecaciones que llevaron a HU-DASH-001-v3, HU-DASH-002-v2 y HU-DASH-003-v2.

**Historias incluidas (diseño):** HU-DASH-001-v3, HU-DASH-002-v2, HU-DASH-003-v2 (y HU-SENT-008 como historia técnica derivada).

**Desviación respecto de P3:** en este sprint se construyó la **maqueta** del frontend y se cerró el **diseño** de los dashboards, pero la conexión real con el backend se integró en Sprint 5.

---

## Sprint 4 — Administración, configuración y modelo de ML

**Goal planificado (P3):** administración + entrenamiento del modelo de ML con datos acumulados. Historias HU-ADMIN-001 a HU-ADMIN-004 y HU-SENT-006.

**Ejecutado (diseño/backlog) y cierre de sesión PO:**
- Sesión del PO del 2026-10-18 (`cbe4cfb`, rama `docs/po-2026-10-18`): actualización de backlog, contratos y OpenSpec. En esta sesión se formalizó EPIC-ADMIN (HU-ADMIN-001 a 003), se deprecó HU-RSS-009 en favor de HU-RSS-009-v2, y se actualizaron las historias de EPIC-SENT a sus versiones vigentes (HU-SENT-002-v3, HU-SENT-007-v3).

**Historias incluidas (diseño/backlog):** HU-ADMIN-001, HU-ADMIN-002, HU-ADMIN-003 (formalización); HU-SENT-006 (arquitectura en ADR-004).

**Desviaciones respecto de P3:**
- **HU-ADMIN-004 (panel de administración unificado)** quedó **sin iniciar** en este sprint. Se formalizó el 2026-10-20 y se implementó en el cierre del Sprint 5 (2026-11-04).
- La implementación efectiva de EPIC-ADMIN y del modelo de ML se integró a `main` en Sprint 5.

---

## Sprint 5 — Estabilización, integración e implementación final

**Goal planificado (P3):** estabilización, integración del modelo ML entrenado, pruebas y documentación final; cierre de HU-SENT-002-v2 (activar camino del modelo).

**Ejecutado (integración masiva a `main`, 18-20 oct):** este sprint concentró la integración a `main` de la implementación real de los módulos de sentimiento, dashboards y administración, preparados en los sprints anteriores:
- Despliegue con Docker: migraciones al arrancar, healthcheck de MySQL, dependencia `cryptography` (`a324aa4`, 18-oct).
- Carga inicial de fuentes RSS (HU-RSS-009-v2) y CORS para el frontend (`6245c7a`, 18-oct).
- Cálculo de humor por diccionario (HU-SENT-002-v3, HU-SENT-007-v2) (`ccc87c5`, 19-oct) y carga inicial del diccionario (`2c81f05`, 19-oct).
- `GET /dashboards/map` y conexión del mapa (HU-DASH-001-v3) (`fa3c626`, 19-oct); `GET /sentiment` y gráfico de evolución (HU-SENT-004, HU-DASH-001-v3) (`f640ebf`, 19-oct).
- Coincidencias término–noticia y nube de palabras (HU-SENT-008, HU-DASH-003-v2) (`f637249`, 19-oct); `GET /news` y listado de noticias (HU-DASH-002-v2) (`549d8a3`, 19-oct).
- Polarización de términos y análisis de texto libre (HU-SENT-003, HU-SENT-005) (`3b60980`, 19-oct).
- Purgado automático y manual (HU-ADMIN-001 a 003) (`88b14c4`, 19-oct); filtro por país en nube y listado (`c7860fd`, 19-oct).
- Pruebas del frontend con Vitest y Testing Library, con job en CI (`c68d373`, 19-oct).
- Entrenamiento y versionado del modelo de ML (HU-SENT-006, ADR-004) (`52a7912`, 19-oct).
- Renombrado de ADR a tres dígitos (ADR-001 a ADR-005) (`96e5722`, 19-oct) y actualización del README y `.env.example` (`7ef5f84`, 19-oct).
- Comparación por lema con spaCy y detección de idioma (HU-SENT-007-v3) (`23afb88`, 20-oct); corrección de hallazgos de SonarQube y medición de cobertura (`a3e191b`, 20-oct); exigir modelos de spaCy al arrancar y ejecutar la API sin usuario root (`f94027a`, 20-oct).
- Paginación de `GET /dictionary` (HU-SENT-001-v2) (`a500d86`, 20-oct) y panel de administración unificado (HU-ADMIN-004) (rama `feature/panel-admin`, 04-nov).

**Historias incluidas (implementadas e integradas):** HU-RSS-009-v2; HU-SENT-002-v3, HU-SENT-003, HU-SENT-004, HU-SENT-005, HU-SENT-006, HU-SENT-007-v3, HU-SENT-008; HU-DASH-001-v3, HU-DASH-002-v2, HU-DASH-003-v2; HU-ADMIN-001, HU-ADMIN-002, HU-ADMIN-003, HU-ADMIN-004; HU-SENT-001-v2.

**Observación:** el Sprint 5 absorbió la implementación de lo diseñado en los Sprints 2-4. El cierre del camino de ML (HU-SENT-002-v3 / HU-SENT-006) se ejecutó aquí, en línea con el goal planificado de "activar el camino del modelo".

---

## Resumen: planificado vs. ejecutado

| Sprint | Goal (P3) | Estado de ejecución | Historias vigentes asociadas |
|---|---|---|---|
| Sprint 0 | Entorno, arquitectura, CI/CD | Ejecutado conforme a lo planificado | — (fundación) |
| Sprint 1 | Captura y gestión RSS | Ejecutado; +HU-RSS-010; HU-RSS-003→003-v2 | HU-RSS-001, 002, 003-v2, 004, 005, 010 |
| Sprint 2 | Motor de sentimiento | Diseño/backlog ejecutado; implementación diferida a Sprint 5 | HU-SENT-001 a 007 (diseño) |
| Sprint 3 | Dashboards | Maqueta + diseño ejecutados; integración diferida a Sprint 5 | HU-DASH-001-v3, 002-v2, 003-v2; HU-SENT-008 |
| Sprint 4 | Administración + ML | Backlog formalizado; implementación diferida a Sprint 5 (HU-ADMIN-004 incluida, 04-nov) | HU-ADMIN-001, 002, 003; HU-SENT-006 |
| Sprint 5 | Estabilización e integración | Ejecutado; concentró la integración a `main` de Sprints 2-5 | Todas las anteriores + cargas iniciales |

**Historias planificadas no ejecutadas:** ninguna. HU-ADMIN-004 (panel de administración unificado), la última pendiente, se implementó el 2026-11-04.

---

## Nota de consistencia sobre la numeración de historias

El Anexo I de P3 usa una numeración de HU-RSS distinta a la del backlog vigente (p. ej. en el Anexo, "HU-RSS-002: Listado y filtrado"; en el backlog vigente, el listado de fuentes es HU-RSS-003-v2 y el de canales HU-RSS-010). Esta divergencia proviene de la reconciliación de backlog registrada en `PLANIFICACION-AGIL-HUMWORLD-ENTREGADO-P3.md` (nota de consistencia) y en las tablas de control de versiones de `HU-RSS-captura.md`. Este documento usa la **numeración vigente** del backlog para la trazabilidad, sin alterar los documentos de P3.

---

## Tabla de control de versiones

| Versión | Fecha | Motivo del cambio |
|---|---|---|
| v1.0 | 2026-10-29 | Creación. Reconstrucción de la organización real de los sprints a partir del historial de git y de las tablas de control de versiones del backlog, con goals planificados, ejecución real, desviaciones e historias por sprint. Entregable de §4.7 punto 7. No modifica los documentos de P3. |
| v1.1 | 2026-11-04 | HU-ADMIN-004 implementada en el cierre del Sprint 5; se agrega también la paginación del diccionario (HU-SENT-001-v2). Ya no quedan historias planificadas sin ejecutar. |
