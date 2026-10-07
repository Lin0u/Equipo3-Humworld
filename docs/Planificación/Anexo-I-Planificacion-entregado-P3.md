# Anexo I — Planificación (entregado en P3), transcrito desde el .xlsx oficial

**Origen:** `HumWorld_Anexo_I_Planificacion_1.xlsx`, subido por el usuario el 2026-08-19 como el entregable oficial de la Práctica P3.

## Hoja "Backlog"

| EPICA | HISTORIAS DE USUARIO |
|---|---|
| EPIC-RSS — Captura y Gestión de Fuentes RSS | HU-RSS-001: Alta de fuentes RSS |
| EPIC-RSS — Captura y Gestión de Fuentes RSS | HU-RSS-002: Listado y filtrado de fuentes RSS |
| EPIC-RSS — Captura y Gestión de Fuentes RSS | HU-RSS-003: Actualización y eliminación de fuentes RSS |
| EPIC-RSS — Captura y Gestión de Fuentes RSS | HU-RSS-004: Captura automática periódica de noticias (cron) [Enabler] |
| EPIC-RSS — Captura y Gestión de Fuentes RSS | HU-RSS-005: Actualización manual de una o varias fuentes RSS |
| EPIC-SENT — Motor de Análisis de Sentimiento (Humor) | HU-SENT-001: Gestión CRUD del diccionario de términos |
| EPIC-SENT — Motor de Análisis de Sentimiento (Humor) | HU-SENT-002-v2: Cálculo híbrido de humor (diccionario + ML) [Enabler] |
| EPIC-SENT — Motor de Análisis de Sentimiento (Humor) | HU-SENT-003: Persistencia del resultado de humor y polarización [Enabler] |
| EPIC-SENT — Motor de Análisis de Sentimiento (Humor) | HU-SENT-004: Consulta de análisis de sentimiento (global/continente/país/timeline) |
| EPIC-SENT — Motor de Análisis de Sentimiento (Humor) | HU-SENT-005: Análisis de sentimiento de un texto arbitrario (endpoint) |
| EPIC-SENT — Motor de Análisis de Sentimiento (Humor) | HU-SENT-006: Entrenamiento y versionado del modelo de ML [Enabler] |
| EPIC-SENT — Motor de Análisis de Sentimiento (Humor) | HU-SENT-007: Fallback determinista con diccionario [Enabler] |
| EPIC-DASH — Dashboards y Visualización | HU-DASH-001: Dashboard mapa mundial de humor |
| EPIC-DASH — Dashboards y Visualización | HU-DASH-002: Listado de noticias más influyentes |
| EPIC-DASH — Dashboards y Visualización | HU-DASH-003: Nube de palabras influyentes con filtros |
| EPIC-ADMIN — Administración y Configuración | HU-ADMIN-001: Configuración de parámetros generales del sistema |
| EPIC-ADMIN — Administración y Configuración | HU-ADMIN-002: Purgado automático de noticias antiguas [Enabler] |
| EPIC-ADMIN — Administración y Configuración | HU-ADMIN-003: Purgado manual de noticias antiguas |
| EPIC-ADMIN — Administración y Configuración | HU-ADMIN-004: Panel de administración unificado |

## Hoja "Planificacion-Calendario"

| Sprint | Sprint GOAL |
|---|---|
| SPRINT 0 | Configuración del entorno, arquitectura base y CI/CD mínimo |
| SPRINT 1 | Captura y gestión de fuentes RSS (HU-RSS-001 a 005) |
| SPRINT 2 | Motor de análisis de sentimiento y diccionario (HU-SENT-001 a 005) |
| SPRINT 3 | Dashboards e interfaz de visualización (HU-DASH-001 a 003) |
| SPRINT 4 | Administración, configuración y purgado (HU-ADMIN-001 a 004) |
| SPRINT 5 | Estabilización, pruebas de aceptación/carga y documentación final |
| — | VERIFICACIÓN FORMAL DEL SISTEMA |

Calendario cubre semanas del 10-ago-26 al 07-dic-26 (celdas de semana quedaron sin marcar en el Excel entregado — no se registró el rango exacto de columnas pintadas por sprint).

## Hoja "Historias-Estimacion"

| Sprint | Sprint GOAL | Historias incluidas | Estimación Puntos de Historia |
|---|---|---|---|
| SPRINT 0 | Configuración del entorno, arquitectura base y CI/CD mínimo | Sin historias de producto (tareas técnicas de fundación) | N/A |
| SPRINT 1 | Contar con un sistema funcional de captura y gestión de fuentes RSS | HU-RSS-001 (1), HU-RSS-002 (2), HU-RSS-003 (2), HU-RSS-004 (3), HU-RSS-005 (3) | 11 |
| SPRINT 2 | Motor de sentimiento funcional vía fallback de diccionario (ADR-002) | HU-SENT-001 (5), HU-SENT-002-v2 (5), HU-SENT-003 (3), HU-SENT-004 (1), HU-SENT-005 (2), HU-SENT-007 (2) | 18 |
| SPRINT 3 | Ofrecer dashboards interactivos sobre los datos de humor calculados | HU-DASH-001 (5), HU-DASH-002 (2), HU-DASH-003 (5) | 12 |
| SPRINT 4 | Administración + entrenamiento del modelo de ML (HU-SENT-006, con data ya acumulada) | HU-ADMIN-001 (2), HU-ADMIN-002 (2), HU-ADMIN-003 (1), HU-ADMIN-004 (2), HU-SENT-006 (5) | 12 |
| SPRINT 5 | Estabilización, integración del modelo ML entrenado, pruebas y documentación final | Sin historias nuevas — cierre de HU-SENT-002-v2 (activar camino de modelo) | N/A |
| **TOTAL** | (Sprints 1 a 4, propuesta, tras ADR-002) | | **53** |

> Nota: el total de 53 en el Excel difiere del total de 50 calculado en el cuerpo del .md entregado (11+17+11+11=50 con estimaciones ligeramente distintas para Sprint 2 y 4). El Excel usa 11+18+12+12=53. **Discrepancia menor entre ambos archivos del mismo entregable — a aclarar con el equipo si se requiere para la corrección.**
