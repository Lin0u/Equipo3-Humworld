# Plan de Pruebas — Sprint 1 (Módulo Captura RSS)

**Proyecto:** HumWorld — Equipo 3
**Módulo:** Captura RSS (EPIC-RSS) — gestión de canales y fuentes RSS
**Alcance de este plan:** HU-RSS-001, HU-RSS-002, HU-RSS-003-v2, HU-RSS-004, HU-RSS-005 y HU-RSS-010
**Rol responsable:** QA / Documentación
**Versión del documento:** v1 — Sesión 2026-09-06
**Estado:** Vigente para Sprint 1

**Referencias:**
- Historias de usuario y criterios Gherkin: `docs/Backlog/HU-RSS-captura.md`
- Arquitectura y reglas de capas: `docs/architecture.md`
- Decisiones de stack y arquitectura: `docs/Adr/ADR-001-stack-backend.md`, `docs/Adr/ADR-002-arquitectura-captura-rss.md`
- Definition of Done: `docs/Planificación/PLANIFICACION-AGIL-HUMWORLD-ENTREGADO-P3.md` (Paso 5) e instrucciones del proyecto (sección 14)
- Guía operativa de ejecución: `README-despliegue-captura-rss.md` (sección "Ejecutar las pruebas")

---

## 1. Objetivo

Documentar **cómo se prueba** el módulo de Captura RSS en el Sprint 1 y dejar
constancia trazable de que cada criterio de aceptación (Gherkin) de las
historias entregadas está cubierto por al menos una prueba automatizada. Este
documento es el puente entre el backlog (qué se pide) y la suite de pruebas
(cómo se verifica).

## 2. Alcance

**Dentro de alcance (historias con lógica y pruebas implementadas):**

| Historia | Descripción | Archivo de pruebas |
|---|---|---|
| HU-RSS-001 | Alta de canal de noticias | `src/tests/test_channels.py` |
| HU-RSS-010 | Consulta y listado paginado de canales | `src/tests/test_channels.py` |
| HU-RSS-002 | Alta de fuente RSS dentro de un canal | `src/tests/test_sources.py` |
| HU-RSS-003-v2 | Consulta y filtrado paginado de fuentes RSS | `src/tests/test_sources.py` |
| HU-RSS-004 | Modificación de fuente RSS (PUT/PATCH) | `src/tests/test_sources.py` |
| HU-RSS-005 | Eliminación de fuente RSS (borrado lógico) | `src/tests/test_sources.py` |

**Fuera de alcance (scaffolding intencional, sin pruebas todavía):**
HU-RSS-006 (cron), HU-RSS-007 (configuración), HU-RSS-008 (captura manual) y
HU-RSS-009 (seed). Sus módulos (`app/routers/captures.py`,
`app/services/captura_service.py`, `app/jobs/scheduler.py`) lanzan
`NotImplementedError` a propósito (sección 12 de las instrucciones del
proyecto) y se excluyen de la medición de cobertura (ver sección 6).

## 3. Estrategia de pruebas

- **Nivel:** pruebas de API (vía `TestClient` de FastAPI) combinadas con pruebas
  unitarias de las capas de servicio y repositorio.
- **Base de datos:** SQLite en memoria (`create_engine("sqlite://")` con
  `StaticPool`), inyectada mediante `dependency_overrides` de `get_db`. **No se
  requiere MySQL ni Docker** para ejecutar la suite; cada prueba parte de un
  esquema limpio creado y destruido por el fixture.
- **Aislamiento de dependencias externas:** las llamadas a feeds RSS se aíslan
  con mocks (`respx`, ya declarado en `requirements.txt`). **Nunca** se realizan
  llamadas HTTP reales, conforme a la sección 14 de las instrucciones del
  proyecto. (En Sprint 1 las 6 historias no invocan feeds; el aislamiento aplica
  cuando se implementen HU-RSS-006/008.)
- **Contrato de API:** varias pruebas verifican que el documento OpenAPI
  autogenerado declara las respuestas esperadas (201/400/404/409/204), para
  mantener el código coherente con `contrato-canales-fuentes-rss.openapi.yaml`.
- **Cobertura por capas:** cada historia se prueba en la capa de API y, cuando
  aplica, también en servicio y repositorio de forma independiente.

## 4. Entorno y ejecución

```bash
cd src
python -m venv venv
venv\Scripts\activate        # Windows (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt

pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

Configuración relevante en `src/`:
- `pytest.ini` — fija `testpaths=tests` y el loop scope de asyncio.
- `.coveragerc` — define la exclusión de cobertura (ver sección 6).

## 5. Resultado de la última ejecución (2026-09-06)

- **78 pruebas** ejecutadas, **todas en verde**.
- **Cobertura del módulo: 95.90%** (umbral de la DoD: ≥80%, alcanzado).
- Desglose: `test_channels.py` (39 pruebas), `test_sources.py` (38 pruebas),
  `test_health.py` (1 prueba).

## 6. Alcance de la medición de cobertura

El archivo `src/.coveragerc` excluye del cálculo los tres módulos de scaffolding
de historias aún no implementadas, de forma que el umbral del 80% se mida solo
sobre el código realmente entregado en Sprint 1:

- `app/routers/captures.py`
- `app/services/captura_service.py`
- `app/jobs/scheduler.py`

`pytest-cov` lee `.coveragerc` automáticamente al ejecutarse desde `src/`, en
local y en CI. **Cuando se implementen HU-RSS-006 a 009, esos archivos deben
retirarse del `omit` y cubrirse con sus propias pruebas.**

Las líneas no cubiertas restantes dentro del alcance corresponden a ramas
defensivas de infraestructura (manejo de errores de base de datos, `get_db`
real no ejercitado bajo SQLite, ramas de validación para entradas no textuales)
y no a escenarios de aceptación; no se fuerzan con pruebas de relleno.

## 7. Matriz de trazabilidad — HU-RSS ↔ escenario ↔ prueba

Cada prueba lleva en el código un comentario `# HU-RSS-00X — Escenario: …` que
la vincula con su criterio Gherkin en `docs/Backlog/HU-RSS-captura.md`.

### HU-RSS-001 — Alta de canal de noticias

| Escenario / aspecto | Prueba |
|---|---|
| Alta exitosa (con normalización de campos) | `test_crear_canal_normaliza_todos_los_campos_y_acepta_continente_libre` |
| Alta exitosa con campos opcionales ausentes | `test_crear_canal_acepta_campos_opcionales_ausentes` |
| Rechazo por datos obligatorios faltantes/inválidos (400) | `test_crear_canal_rechaza_datos_invalidos_con_error_de_contrato` |
| Rechazo por nombre duplicado (409) | `test_crear_canal_rechaza_nombre_duplicado_sin_distinguir_mayusculas` |
| Duplicado — capa repositorio traduce unicidad de la BD | `test_repositorio_traduce_violacion_de_unicidad` |
| Duplicado en condición de carrera — capa servicio (409) | `test_servicio_traduce_carrera_de_unicidad_a_conflicto` |

### HU-RSS-010 — Consulta y listado de canales

| Escenario / aspecto | Prueba |
|---|---|
| Listado paginado por defecto | `test_listar_canales_devuelve_respuesta_paginada_por_defecto` |
| Orden alfabético por "nombre" (insensible a mayúsculas) | `test_listar_canales_ordena_alfabeticamente_insensible_a_mayusculas` |
| Página específica | `test_listar_canales_pagina_especifica` |
| tamanio_pagina dentro del máximo (50) | `test_listar_canales_tamanio_pagina_personalizado_dentro_del_maximo` |
| Página posterior a la última devuelve vacío | `test_listar_canales_pagina_posterior_a_la_ultima_devuelve_vacio` |
| Listado vacío (items=[], total=0) | `test_listar_canales_sin_registros_devuelve_pagina_vacia` |
| Volumen alto mantiene la forma de respuesta | `test_listar_canales_con_volumen_alto_mantiene_la_forma_esperada` |
| Paginación fuera de rango o no numérica (400) | `test_listar_canales_rechaza_paginacion_invalida` |
| Paginación inválida combinada — error único de contrato | `test_listar_canales_rechaza_combinacion_de_paginacion_invalida_con_error_unico` |
| Filtrado por continente combinado con paginación | `test_listar_canales_filtra_por_continente_combinado_con_paginacion` |
| Filtrado por continente insensible a diacríticos | `test_listar_canales_filtra_continente_insensible_a_diacriticos` |
| Filtro de continente vacío no aplica filtro | `test_listar_canales_continente_vacio_no_aplica_filtro` |
| Filtro por continente sin coincidencias | `test_listar_canales_continente_sin_coincidencias` |
| Serialización del schema (0 y 23 elementos) | `test_schema_canal_listado_serializa_cero_y_23_elementos` |
| Orden alfabético — capa repositorio | `test_repositorio_lista_ordenado_alfabeticamente_case_insensitive` |
| Filtro sin coincidencias — capa repositorio | `test_repositorio_filtra_por_continente_sin_coincidencias_devuelve_vacio` |
| Detalle existente/inexistente — capa repositorio | `test_repositorio_buscar_por_id_existente_e_inexistente` |
| Filtrado por continente — capa servicio (delega y recorta) | `test_servicio_listar_canales_delega_en_el_repositorio_y_recorta_continente` |
| Filtro en blanco tratado como ausente — capa servicio | `test_servicio_listar_canales_trata_continente_de_solo_espacios_como_ausente` |
| Detalle inexistente traducido a error de dominio (404) | `test_servicio_obtener_canal_traduce_ausencia_a_error_de_dominio` |
| Detalle de canal existente (todos los campos) | `test_obtener_canal_existente_devuelve_todos_los_campos` |
| Detalle de canal inexistente (404) | `test_obtener_canal_inexistente_devuelve_404` |
| Detalle con id no numérico responde 404 (no 422) | `test_obtener_canal_con_id_no_numerico_devuelve_404` |
| OpenAPI declara listado y detalle | `test_openapi_declara_listado_y_detalle_de_canales` |

### HU-RSS-002 — Alta de fuente RSS

| Escenario / aspecto | Prueba |
|---|---|
| Alta exitosa (asocia canal, normaliza, activo=true) | `test_alta_fuente_asocia_canal_y_normaliza_datos` |
| Rechazo por canal inexistente (404) | `test_alta_fuente_rechaza_canal_inexistente` |
| Rechazo por URL inválida y categoría IPTC no reconocida (400) | `test_alta_fuente_rechaza_datos_invalidos_con_error` |
| Alta inicializa "activo" en verdadero — capa servicio | `test_servicio_crea_fuente_con_activo_true` |
| Rechazo por canal inexistente — capa servicio | `test_servicio_rechaza_canal_inexistente` |
| OpenAPI declara respuestas 201/400/404 del alta | `test_openapi_declara_respuestas_del_alta` |

### HU-RSS-003-v2 — Consulta y filtrado de fuentes RSS

| Escenario / aspecto | Prueba |
|---|---|
| Listado paginado por defecto y orden por "canal_id" + "url" | `test_listar_fuentes_devuelve_respuesta_paginada_y_ordenada` |
| Filtrado por canal propietario (canal_id) | `test_listar_fuentes_filtra_por_canal_id` |
| Filtrado combinado (continente+categoria+activo) insensible a mayúsculas | `test_listar_fuentes_aplica_filtros_combinados_case_insensitive` |
| Filtros textuales vacíos no producen error 500 | `test_listar_fuentes_ignora_filtros_textuales_vacios` |
| Listado vacío (items=[], total=0) | `test_listar_fuentes_sin_resultados_devuelve_pagina_vacia` |
| Paginación fuera de rango (400) | `test_listar_fuentes_rechaza_paginacion_invalida` |
| Detalle de fuente existente (sin envoltorio de paginación) | `test_obtener_fuente_existente_devuelve_todos_los_campos` |
| Detalle de fuente inexistente (404) | `test_obtener_fuente_inexistente_devuelve_404` |
| Serialización del schema paginado (0 y 23 elementos) | `test_schema_paginado_serializa_cero_y_23_elementos` |
| OpenAPI declara listado y detalle | `test_openapi_declara_listado_y_detalle_de_fuentes` |

### HU-RSS-004 — Modificación de fuente RSS

| Escenario / aspecto | Prueba |
|---|---|
| Actualización completa (PUT) exitosa e idempotente | `test_put_fuente_reemplaza_campos_y_es_idempotente` |
| Actualización parcial (PATCH) solo de "activo" | `test_patch_fuente_modifica_unicamente_activo` |
| Rechazo de payload inválido en PUT/PATCH (400) | `test_actualizacion_fuente_rechaza_payload_invalido` |
| Actualización de fuente inexistente (404) | `test_actualizacion_fuente_inexistente_devuelve_404` |
| Actualización persiste los cambios — capa repositorio | `test_repositorio_actualiza_y_persiste_fuente` |
| PATCH aplica solo los campos presentes — capa servicio | `test_servicio_patch_aplica_solo_campos_presentes` |
| OpenAPI declara respuestas de PUT y PATCH | `test_openapi_declara_actualizacion_completa_y_parcial` |

### HU-RSS-005 — Eliminación de fuente RSS

| Escenario / aspecto | Prueba |
|---|---|
| Eliminación exitosa (204): marca inactiva y conserva la noticia asociada | `test_delete_fuente_marca_inactiva_y_conserva_noticia` |
| Tras eliminar, detalle responde 404 y desaparece del listado activo | `test_delete_fuente_oculta_detalle_y_listado` |
| Eliminación de fuente inexistente o ya eliminada (404) | `test_delete_fuente_inexistente_o_repetida_devuelve_404` |
| Eliminación lógica (soft delete) sin borrar la fila — capa servicio | `test_servicio_elimina_logicamente_sin_borrar_fila` |
| OpenAPI declara respuestas 204/404 | `test_openapi_declara_eliminacion_de_fuentes` |

### Pruebas de integración adicionales (persistencia observable vía API)

Cubren de forma conjunta el flujo POST → GET a través de la API pública, en
lugar de sembrar datos directamente en la base de datos de prueba.

| Aspecto | Prueba |
|---|---|
| Canal creado por POST aparece en listado y detalle (HU-RSS-001 + HU-RSS-010) | `test_canal_creado_via_post_aparece_en_listado_y_detalle` |
| Fuente creada por POST aparece en listado y detalle (HU-RSS-002 + HU-RSS-003-v2) | `test_fuente_creada_via_post_aparece_en_listado_y_detalle` |

### Prueba del scaffold

| Aspecto | Prueba |
|---|---|
| Health check del servicio (arranque sin BD ni mocks) | `test_health_check_responde_ok` |

## 8. Cumplimiento de la Definition of Done (testing)

| Criterio de la DoD (sección 14 / Paso 5) | Estado |
|---|---|
| Pruebas unitarias con mocks/stubs para dependencias externas | Cumplido (mocks disponibles vía `respx`; sin llamadas reales) |
| Cobertura ≥ 80%, verificada en GitHub Actions | Cumplido en local (95.90%); pendiente de confirmación en CI (ver sección 9) |
| Códigos HTTP coherentes con el contrato OpenAPI | Cumplido (pruebas de contrato por endpoint) |
| Swagger/OpenAPI actualizado | Cumplido (verificado por las pruebas `test_openapi_*`) |
| No exponer trazas internas | Cumplido (respuestas de error con `{codigo, mensaje}`) |

Criterios de la DoD que **no dependen de QA** (revisión por PR, SonarQube sin
issues críticos, build/deploy Docker con `needs: [test, sonarqube]`) quedan a
cargo de los roles correspondientes del equipo.

## 9. Recomendación al equipo — alineación del pipeline de CI

QA **no modifica** `.github/workflows/ci.yml` ni credenciales. Se recomienda al
responsable de CI/DevOps:

1. Confirmar que el paso de `pytest` del CI se ejecuta desde `src/` (ya es el
   caso), de modo que recoja automáticamente `src/.coveragerc` y `--cov-fail-under=80`
   se mida sobre el módulo entregado.
2. Retirar del `ci.yml` el comentario que indica que el job falla de forma
   intencional, una vez confirmado el punto anterior: HU-RSS-001 a 005 y 010 ya
   cuentan con lógica y pruebas reales.
3. Mantener el `omit` de `.coveragerc` actualizado a medida que se implementen
   HU-RSS-006 a 009.

## 10. Historial de revisión

| Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|
| v1 | 2026-09-06 | Creación del plan de pruebas del Sprint 1: estrategia, entorno, alcance de cobertura y matriz de trazabilidad HU-RSS ↔ escenario ↔ prueba para HU-RSS-001, 002, 003-v2, 004, 005 y 010. |
