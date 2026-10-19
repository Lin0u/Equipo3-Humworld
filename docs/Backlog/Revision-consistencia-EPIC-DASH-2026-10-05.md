# Revisión de consistencia — EPIC-DASH (HU-DASH-001 a 003 y ADR-05)

**Proyecto:** HumWorld — Equipo 3
**Fecha:** 2026-10-05
**Documentos revisados:** `HU-DASH-dashboards.md` (v1.0) y `ADR-05-stack-frontend-dashboards.md` (v1.0, recibido como `ADR-05`).
**Contrastados contra:** `HU-SENT-motor-sentimiento.md` (v1.5), `ADR-01`, `ADR-03`, `ADR-04`, `contrato-sentimiento-diccionario.openapi.yaml` (v1.0.0), `contrato-canales-fuentes-rss.openapi.yaml` (v1.6.0), `diagrama-clases.md`, `diagrama-clases-sentimiento.md` (v1.1), `HU-RSS-captura.md` (HU-RSS-009) y `Anexo-I-Planificacion-entregado-P3.md`.

**Alcance de lo aplicado:** solo se normalizó la nomenclatura (v1.1 editorial de ambos documentos). Ningún hallazgo de fondo fue corregido en los documentos: todos requieren decisión del equipo.

**No verificado:** las citas a secciones del PDF (el Proyecto tiene la versión `260714`; los documentos citan `260821`), ni las referencias a archivos del repositorio (`docs/architecture.md`, `openspec/config.yaml`, rama `feature/frontend-dashboards`, versiones de React y Vite).

---

## 1. Inconsistencias que contradicen decisiones ya tomadas

### H-1. Lista de continentes: 6 en HU-DASH-001, 5 ya confirmados en EPIC-RSS (Alta)

> **Resuelto el 2026-10-05:** el equipo optó por alinear el mapa a 5 continentes. HU-DASH-001 quedó Deprecada y se creó HU-DASH-001-v2 (`HU-DASH-dashboards.md` v1.2; referencias actualizadas en ADR-05 v1.2). Queda pendiente ajustar la maqueta y convertir `continente` en `enum` en los contratos.

HU-DASH-001 afirma que la carga inicial "aún no fija la lista definitiva" y asume seis continentes (América del Norte y América del Sur separadas). El equipo ya confirmó el 2026-09-28 **cinco**: América, Europa, Asia, África y Oceanía (`HU-RSS-captura.md`, HU-RSS-009; `contrato-canales-fuentes-rss.openapi.yaml` v1.6.0).

Afecta: punto pendiente 1, los escenarios Gherkin "6 continentes" y "1 marcador por cada uno de los 6", y los datos de ejemplo de la maqueta. El filtro `continente=América del Norte` no devolvería ninguna noticia.

Resolución: alinear HU-DASH-001 a 5 continentes, o reabrir la decisión de HU-RSS-009 (lo que obliga a versionar esa historia y el seed). La recomendación de convertir `continente` en `enum` sigue siendo válida y aplica a ambos contratos.

### H-2. La nube de palabras depende de un dato que el backend no persiste (Alta, bloqueante)

> **Resuelto el 2026-10-05:** se creó HU-SENT-008 (tabla de unión, poblada también en el camino de ML) y HU-DASH-003-v2 depende de ella. HU-SENT-008 está sin estimar y sin sprint.

HU-DASH-003 declara que "necesita el diccionario y sus coincidencias en las noticias" (HU-SENT-001, HU-SENT-007). `diagrama-clases-sentimiento.md` establece que **no existe relación persistida entre `Noticia` y `TerminoDiccionario`**: la comparación ocurre en el momento del cálculo y no se guarda. Ninguna HU-SENT cubre hoy esa persistencia.

Además, cuando `metodo_calculo = "ml"` el método de diccionario no se ejecuta, así que esas noticias no tendrían coincidencias (punto pendiente 2 de HU-DASH-003, que este hallazgo agrava).

Resolución: se necesita trabajo nuevo en EPIC-SENT (extensión de HU-SENT-007 o una historia nueva, con su estimación) antes de poder integrar HU-DASH-003. Los 5 puntos de HU-DASH-003 no incluyen ese trabajo de backend.

### H-3. "Frecuencia de aparición" como peso choca con el criterio de HU-SENT-007 (Media)

> **Resuelto el 2026-10-05:** peso = cantidad de noticias que contienen el término (HU-DASH-003-v2, `contrato-dashboards.openapi.yaml`).

HU-DASH-003 propone como ejemplo de peso la "frecuencia de aparición". HU-SENT-007 y ADR-03 fijaron que cada término cuenta una sola vez por noticia (`n` = términos únicos) y descartaron ponderar por repeticiones. Para no contradecirlo, la frecuencia debe definirse como **cantidad de noticias en que aparece el término**, no como apariciones totales en el texto.

## 2. Vacíos y ambigüedades

### H-4. Chart.js y `serie_temporal` no tienen historia que los respalde (Media)

> **Resuelto el 2026-10-05:** se agregó el gráfico de evolución temporal en HU-DASH-001-v3, que debe reestimarse.

ADR-05 adopta Chart.js para la serie temporal de humor, pero ningún escenario de HU-DASH-001 a 003 pide un gráfico ni consume `serie_temporal`. Es una dependencia aprobada sin requisito. Opciones: agregar un escenario de evolución temporal a HU-DASH-001 (nueva versión, reestimación) o retirar Chart.js del ADR.

### H-5. Fecha única frente a rango `desde`/`hasta` (Baja)

> **Resuelto el 2026-10-05:** endpoint único `GET /api/v1/dashboards/map` (HU-DASH-001-v3), que también entrega el rango de fechas con datos.

HU-DASH-001 trabaja con una fecha; el contrato solo ofrece rango. Falta explicitar que la consulta es `desde = hasta = fecha` y que el humor global es la misma llamada sin `continente`. Con el contrato actual el mapa requiere 6 llamadas por fecha (5 continentes más global), dato útil para decidir el punto pendiente 2.

### H-6. "Fuente" de una noticia no tiene nombre en el modelo (Baja)

HU-DASH-002 exige mostrar la "fuente". `FuenteRSS` solo tiene `url`; el nombre legible está en `CanalNoticias.nombre`. El contrato de `/news` debe definir cuál se expone.

### H-7. Idioma en la nube de palabras (Baja)

Los términos son únicos por `palabra + idioma` (HU-SENT-001). HU-DASH-003 no indica si la nube mezcla español e inglés ni cómo trata una misma palabra presente en ambos idiomas.

### H-8. Polarización no considerada en "influyente" (Informativo)

ADR-03 anticipó que `polarizacion_terminos` permitiría destacar noticias controversiales en el listado de influyentes. HU-DASH-002 define influencia solo por valor absoluto de `valor_humor`. No es un error; es una opción que el equipo debería descartar o adoptar explícitamente al ratificar el punto pendiente 1.

### H-9. Google Fonts aparece como dependencia sin estar decidida (Baja)

ADR-05 la evalúa en resiliencia y consecuencias, pero la Decisión (punto 7, estilos) no la menciona. Debe figurar en la Decisión o eliminarse alojando las tipografías localmente.

### H-10. Stack de frontend ausente de las instrucciones del Proyecto (Informativo)

La sección 8 de las instrucciones no lista tecnologías de frontend. Si ADR-05 se acepta, conviene actualizarla (nueva versión del prompt) junto con los documentos que el propio ADR ya enumera.

## 3. Verificado como consistente

- Títulos, puntos (5 + 2 + 5 = 12) y Sprint 3 coinciden con el Anexo I de P3; HU-ADMIN-004 en Sprint 4.
- Campos de `SentimientoAgregado` (`humor_promedio`, `cantidad_noticias_evaluadas`, `serie_temporal`) y el caso `null` con 0 noticias coinciden con el contrato y con HU-SENT-004.
- Exclusión de noticias con `valor_humor = null` coherente con HU-SENT-003.
- `enlace_original` y `categoria_iptc` coinciden con `diagrama-clases.md`; `CanalNoticias.pais` es efectivamente opcional.
- Convención de paginación (`items`, `pagina`, `tamanio_pagina`, `total`) y recursos en inglés bajo `/api/v1` coinciden con los contratos existentes.
- Regla "el frontend no calcula humor" coherente con ADR-03 y ADR-04.
- ADR-05 respeta la estructura fija de ADR y evalúa los cuatro patrones de resiliencia; las referencias a ADR-01 (FastAPI) y ADR-04 (Circuit Breaker en embeddings) son correctas.
- Estado "Propuesto" de ambos documentos es correcto: ninguno ha sido ratificado.

## 4. Riesgo de calendario

El Sprint 3 terminó el 2026-10-04 con las tres historias en maqueta. Dependen de HU-SENT-004 (Sprint 2, sin terminar), de dos contratos inexistentes (`/news`, `/dashboards`), de la herramienta de pruebas de frontend sin decidir y, para HU-DASH-003, del trabajo de backend no planificado de H-2. La verificación formal es el 2026-11-02.

## 5. Decisiones que el equipo debe tomar

| # | Decisión | Hallazgo |
|---|---|---|
| 1 | ~~5 continentes en HU-DASH-001 o reabrir HU-RSS-009~~ — resuelto: 5 continentes (HU-DASH-001-v2) | H-1 |
| 2 | Cómo y dónde se persisten las coincidencias término–noticia, y quién lo estima | H-2 |
| 3 | Definición del peso de una palabra | H-3 |
| 4 | Gráfico temporal: se agrega a una historia o se retira Chart.js | H-4 |
| 5 | Herramienta de pruebas de frontend (propuesta: Vitest con React Testing Library) | ADR-05 |
| 6 | Ratificación formal de ADR-05 | ADR-05 |
