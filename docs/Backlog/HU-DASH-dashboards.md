# Historias de Usuario — Módulo Dashboards y Visualización (EPIC-DASH, Sprint 3)

**Proyecto:** HumWorld — Equipo 3
**Origen:** PDF de especificaciones (`0 PROYECTO_FINAL_HUMWORLD 260821.pdf`), secciones 4.1 (Procesos principales, punto de visualización), 4.3 (Interfaces y experiencia de usuario), 4.3.1 (Dashboard de palabras influyentes), 4.3.2 (Dashboard de Humor), 6.1 (Capa de presentación) y 10.2 (Endpoints mínimos obligatorios: `/sentiment`, `/news`, `/dashboards`). Stack de la capa de presentación decidido y justificado en `ADR-05-stack-frontend-dashboards.md`.
**Estado general:** Propuesto — historias generadas a partir de los títulos ya oficializados en el backlog del entregable P3 (`Anexo-I-Planificacion-entregado-P3.md`: HU-DASH-001, HU-DASH-002 y HU-DASH-003; versiones vigentes: HU-DASH-001-v3, HU-DASH-002-v2 y HU-DASH-003-v2) y de la estimación en puntos ya realizada en Planning Poker (Sprint 3 = 12 puntos). Pendiente de revisión crítica del equipo.
**Versión del documento:** v1.6. Ver la Tabla de control de versiones al final del documento.

> **Nota de grounding general:** el PDF exige "dashboards interactivos que visualicen el humor global y por regiones" (Objetivos específicos, punto 3) y enumera las vistas en la sección 4.3: Dashboard de humor (mapa mundial interactivo con selector de fecha), Nube de palabras (términos influyentes con filtros por país/continente) y Listado de noticias (detalle de las noticias más relevantes para el humor calculado). Este documento formaliza esas tres vistas; no agrega ninguna vista nueva. El Panel de administración (cuarta vista de la sección 4.3) pertenece a EPIC-ADMIN (HU-ADMIN-004, Sprint 4) y queda fuera de este documento.

> **Nota sobre el algoritmo de humor (sección 11 de las instrucciones del proyecto):** ninguna historia de EPIC-DASH calcula humor. La capa de presentación solo muestra valores ya calculados y persistidos por el backend: `valor_humor` por noticia (HU-SENT-002-v2, cálculo híbrido: modelo de ML cuando está disponible, o promedio simple de diccionario como fallback según HU-SENT-007 y `ADR-03-eleccion-algoritmo-agregacion-sentimiento.md`) y `humor_promedio` agregado (HU-SENT-004). Cada historia indica abajo qué valor consume.

> **Estado de implementación (2026-10-19):** las tres vistas están conectadas al backend real en la carpeta `frontend/` del repositorio principal (ramas `feature/mapa-humor`, `feature/humor-temporal`, `feature/nube-palabras` y `feature/noticias`, con sus Pull Requests): mapa y gráfico temporal (HU-DASH-001-v3), nube de palabras (HU-DASH-003-v2) y listado de noticias (HU-DASH-002-v2). Faltan las pruebas automatizadas del frontend (herramienta pendiente de decisión, ADR-05) y el filtro por país, por lo que ninguna de las tres cumple todavía la Definition of Done.

---

## HU-DASH-001-v3 — Dashboard mapa mundial de humor y evolución temporal

**Reemplaza a:** HU-DASH-001-v2 (Deprecada). **Qué cambió:** (a) el mapa obtiene sus datos de un endpoint único, `GET /api/v1/dashboards/map`, que entrega el humor global, el de los 5 continentes y el rango de fechas con información, en lugar de una llamada a `/sentiment` por continente; (b) se agrega un gráfico de evolución temporal del humor global. **Por qué:** decisiones de equipo de la sesión del 2026-10-05, que cierran los puntos pendientes 2 y 3 y dan respaldo funcional a Chart.js, aprobado en ADR-05 sin historia que lo pidiera (hallazgos H-4 y H-5 de `Revision-consistencia-EPIC-DASH-2026-10-05.md`).

**Tipo:** Historia de Usuario
**Como** analista de medios o usuario interesado en la evolución del sentimiento global *(PDF, sección 4.1)*,
**quiero** ver en un mapa del mundo el humor de cada continente en una fecha que yo elija dentro del rango con información disponible,
**para** identificar de un vistazo qué regiones están de mejor o peor humor y cómo cambia ese humor de un día a otro.

**Prioridad:** Alta *(es la vista principal del proyecto: PDF, sección 4.3.2)*
**Estimación (Planning Poker P3):** 5 puntos *(valor estimado en P3 para el alcance original. Esta versión agrega el gráfico de evolución temporal, por lo que el alcance creció y los 5 puntos ya no son representativos: el equipo debe reestimar la historia en Planning Poker. No se propone aquí una cifra nueva)*
**Depende de contrato de API:** Sí — (1) `GET /api/v1/dashboards/map` con parámetro de query `fecha` — ver `contrato-dashboards.openapi.yaml`, esquema `MapaHumor` (`global`, `continentes`, `fecha_minima_con_datos`, `fecha_maxima_con_datos`); (2) `GET /api/v1/sentiment` con `desde` y `hasta` (HU-SENT-004) para el gráfico temporal — ver `contrato-sentimiento-diccionario.openapi.yaml`, esquema `SentimientoAgregado`, campo `serie_temporal`.
**Valor de humor que consume:** `humor_promedio` (promedio de `valor_humor` de las noticias que cumplen el filtro), calculado por el backend. No aplica ninguna variante propia del algoritmo.

**Puntos pendientes de decisión del equipo** (no resueltos por este documento):
1. **Lista de continentes: resuelta; `enum` pendiente.** La lista es la confirmada por el equipo el 2026-09-28 en HU-RSS-009 (`HU-RSS-captura.md`; `contrato-canales-fuentes-rss.openapi.yaml` v1.6.0): los 5 continentes habitados — América, Europa, Asia, África y Oceanía. La maqueta, que asumía seis (América del Norte y América del Sur por separado), debe ajustarse a estos cinco. Sigue pendiente: los contratos definen `continente` como `string` libre; se recomienda convertirlo en un `enum` con esos cinco valores en ambos contratos, para que backend y frontend usen exactamente los mismos literales.
2. **Origen de los datos del mapa: resuelto.** Endpoint único `GET /api/v1/dashboards/map` (decisión de equipo, 2026-10-05), previsto por el PDF en la sección 10.2. Una sola llamada por fecha.
3. **Rango de fechas con información: resuelto.** Lo entrega el mismo endpoint en `fecha_minima_con_datos` y `fecha_maxima_con_datos`. Sigue pendiente confirmar la fecha que se muestra al abrir la vista: el contrato propone la fecha máxima con datos.
4. **Rangos de color.** La maqueta clasifica solo por signo (mayor que 0 positivo, menor que 0 negativo, igual a 0 neutro). El equipo no ha definido umbrales oficiales para "positivo", "neutro" o "negativo".

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Visualización del humor por continente en la fecha elegida
  Dado que el backend dispone de humor agregado para la fecha 2026-10-02 en los 5 continentes (América, Europa, Asia, África, Oceanía)
  Cuando el usuario abre el dashboard "Mapa de humor" con esa fecha seleccionada
  Entonces el mapa muestra exactamente 1 marcador por cada uno de los 5 continentes
  Y cada marcador muestra el humor_promedio de su continente con 1 decimal y signo explícito cuando es positivo

Escenario: Humor global de la fecha elegida
  Dado que el backend dispone de humor agregado global para la fecha seleccionada
  Cuando el usuario abre el dashboard "Mapa de humor"
  Entonces la vista muestra el humor_promedio global con 1 decimal
  Y muestra la cantidad_noticias_evaluadas que sustenta ese valor

Escenario: Cambio de fecha dentro del rango con información
  Dado que el dashboard está mostrando la fecha 2026-10-02
  Cuando el usuario selecciona la fecha 2026-09-28, que pertenece al rango con información
  Entonces los valores de todos los marcadores y del humor global pasan a ser los de 2026-09-28
  Y la página no se recarga

Escenario: Selector de fecha limitado al rango con información
  Dado que el backend informa fecha_minima_con_datos = F_min y fecha_maxima_con_datos = F_max
  Cuando el usuario abre el selector de fecha
  Entonces el selector no permite elegir fechas anteriores a F_min ni posteriores a F_max

Escenario: Continente sin noticias evaluadas en la fecha elegida
  Dado que para un continente el backend responde humor_promedio = null y cantidad_noticias_evaluadas = 0
  Cuando el usuario abre el dashboard "Mapa de humor"
  Entonces el marcador de ese continente muestra el texto "Sin datos"
  Y la vista no muestra ningún mensaje de error

Escenario: Clasificación visual por signo del humor
  Dado un continente con humor_promedio = +3.4, otro con -4.1 y otro con 0.0
  Cuando el usuario abre el dashboard "Mapa de humor"
  Entonces el primero se representa como positivo, el segundo como negativo y el tercero como neutro
  Y la vista incluye una leyenda que explica las 4 representaciones (positivo, neutro, negativo, sin datos)

Escenario: Gráfico de evolución temporal del humor global
  Dado que GET /api/v1/sentiment con desde = F_min y hasta = F_max devuelve una serie_temporal con N fechas
  Cuando el usuario abre el dashboard "Mapa de humor"
  Entonces la vista muestra un gráfico de líneas con exactamente N puntos, 1 por cada fecha de la serie
  Y el eje vertical del gráfico usa la escala fija de -10 a +10

Escenario: Fecha sin noticias evaluadas dentro de la serie temporal
  Dado que una fecha de la serie_temporal tiene humor_promedio = null
  Cuando la vista dibuja el gráfico de evolución temporal
  Entonces esa fecha no se representa con el valor 0
  Y la línea del gráfico se interrumpe en esa fecha

Escenario: El backend no responde o responde con error
  Dado que GET /api/v1/dashboards/map responde con código HTTP 500 o no responde dentro del timeout configurado
  Cuando el usuario abre el dashboard "Mapa de humor"
  Entonces la vista muestra un mensaje de error legible para el usuario
  Y no queda la pantalla en blanco ni un indicador de carga indefinido
```

**Nota de grounding (lista de noticias en el dashboard de humor):** el PDF (sección 4.3.2) pide además que el dashboard de humor ofrezca "una lista de las noticias que más han influido en el cálculo del humor". Ese requisito se cubre con HU-DASH-002; el equipo debe confirmar si basta con que la lista esté en una vista propia accesible desde el menú (como en la maqueta) o si debe mostrarse dentro de la misma vista del mapa.

**Nota de grounding (escala):** la escala de -10 a +10 que muestra la leyenda proviene del PDF (sección 10.4) y de la sección 11 de las instrucciones del proyecto.

### Definition of Done
(Bloque general DoD, sección 14 de las instrucciones del proyecto — código revisado por al menos 1 integrante vía Pull Request, pruebas unitarias con dependencias externas aisladas mediante mocks, cobertura ≥ 80% verificada en GitHub Actions, SonarQube sin issues críticos, build y despliegue con `needs: [test, sonarqube]`.) Adicionalmente:
- La vista consume `GET /api/v1/dashboards/map` y `GET /api/v1/sentiment` reales; no quedan datos de ejemplo en el camino de producción.
- Pruebas unitarias con la llamada a la API simulada mediante mock, cubriendo al menos los 9 escenarios Gherkin anteriores. Nunca pruebas unitarias con llamadas reales al backend ni al servidor de teselas del mapa.
- Validado visualmente en al menos una resolución de pantalla, registrada en el Pull Request.
- `ADR-05-stack-frontend-dashboards.md` en estado Aceptado.
- `contrato-dashboards.openapi.yaml` aprobado por el equipo y endpoint de mapa implementado en el backend.
- Puntos pendientes 1 a 4 de esta historia resueltos y reflejados en el contrato.

---

## HU-DASH-001-v2 — Dashboard mapa mundial de humor (DEPRECADA)

> **Estado: Deprecada (2026-10-05).** Reemplazada por **HU-DASH-001-v3**. Se conserva sin cambios para trazabilidad. Motivo: dependía de una llamada a `/sentiment` por continente y no incluía el gráfico de evolución temporal.

**Reemplaza a:** HU-DASH-001 (Deprecada). **Qué cambió:** la lista de continentes pasa de 6 a los 5 ya confirmados por el equipo en HU-RSS-009; se actualizan el punto pendiente 1 y los dos escenarios Gherkin que usaban la cifra. **Por qué:** HU-DASH-001 contradecía una decisión vigente de EPIC-RSS (hallazgo H-1 de `Revision-consistencia-EPIC-DASH-2026-10-05.md`). El resto de la historia no cambia.

**Tipo:** Historia de Usuario
**Como** analista de medios o usuario interesado en la evolución del sentimiento global *(PDF, sección 4.1)*,
**quiero** ver en un mapa del mundo el humor de cada continente en una fecha que yo elija dentro del rango con información disponible,
**para** identificar de un vistazo qué regiones están de mejor o peor humor y cómo cambia ese humor de un día a otro.

**Prioridad:** Alta *(es la vista principal del proyecto: PDF, sección 4.3.2)*
**Estimación (Planning Poker P3):** 5 puntos *(ya estimado formalmente en el Planning Poker de la Práctica P3 — ver `Anexo-I-Planificacion-entregado-P3.md`; no es un valor definitivo: el detalle de esta historia se escribió después de estimar, por lo que el equipo debe revalidar si 5 puntos sigue siendo representativo)*
**Depende de contrato de API:** Sí — `GET /api/v1/sentiment` con parámetros de query `continente`, `desde` y `hasta` (HU-SENT-004) — ver `contrato-sentimiento-diccionario.openapi.yaml`, tag `sentiment`, esquema `SentimientoAgregado` (`humor_promedio`, `cantidad_noticias_evaluadas`, `serie_temporal`).
**Valor de humor que consume:** `humor_promedio` (promedio de `valor_humor` de las noticias que cumplen el filtro), calculado por el backend. No aplica ninguna variante propia del algoritmo.

**Puntos pendientes de decisión del equipo** (no resueltos por este documento):
1. **Lista de continentes: resuelta; `enum` pendiente.** La lista es la confirmada por el equipo el 2026-09-28 en HU-RSS-009 (`HU-RSS-captura.md`; `contrato-canales-fuentes-rss.openapi.yaml` v1.6.0): los 5 continentes habitados — América, Europa, Asia, África y Oceanía. La maqueta, que asumía seis (América del Norte y América del Sur por separado), debe ajustarse a estos cinco. Sigue pendiente: los contratos definen `continente` como `string` libre; se recomienda convertirlo en un `enum` con esos cinco valores en ambos contratos, para que backend y frontend usen exactamente los mismos literales.
2. **Cómo obtiene el mapa los datos de todos los continentes.** El contrato actual devuelve un único `SentimientoAgregado` por llamada. El mapa necesita uno por continente, lo que hoy implica una llamada por continente. El PDF (sección 10.2) prevé además un recurso `/dashboards` con `GET (nube-palabras, mapa)`. El equipo debe decidir entre N llamadas a `/sentiment` o un endpoint de mapa que devuelva todos los continentes en una sola respuesta.
3. **Rango de fechas con información.** El PDF (sección 4.3.2) pide que el usuario elija la fecha "en el rango de fechas para el que se dispone información". El contrato no expone ese rango (fecha mínima y máxima con datos). Debe definirse de dónde lo obtiene el frontend.
4. **Rangos de color.** La maqueta clasifica solo por signo (mayor que 0 positivo, menor que 0 negativo, igual a 0 neutro). El equipo no ha definido umbrales oficiales para "positivo", "neutro" o "negativo".

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Visualización del humor por continente en la fecha elegida
  Dado que el backend dispone de humor agregado para la fecha 2026-10-02 en los 5 continentes (América, Europa, Asia, África, Oceanía)
  Cuando el usuario abre el dashboard "Mapa de humor" con esa fecha seleccionada
  Entonces el mapa muestra exactamente 1 marcador por cada uno de los 5 continentes
  Y cada marcador muestra el humor_promedio de su continente con 1 decimal y signo explícito cuando es positivo

Escenario: Humor global de la fecha elegida
  Dado que el backend dispone de humor agregado global para la fecha seleccionada
  Cuando el usuario abre el dashboard "Mapa de humor"
  Entonces la vista muestra el humor_promedio global con 1 decimal
  Y muestra la cantidad_noticias_evaluadas que sustenta ese valor

Escenario: Cambio de fecha dentro del rango con información
  Dado que el dashboard está mostrando la fecha 2026-10-02
  Cuando el usuario selecciona la fecha 2026-09-28, que pertenece al rango con información
  Entonces los valores de todos los marcadores y del humor global pasan a ser los de 2026-09-28
  Y la página no se recarga

Escenario: Selector de fecha limitado al rango con información
  Dado que el rango con información va de la fecha F_min a la fecha F_max
  Cuando el usuario abre el selector de fecha
  Entonces el selector no permite elegir fechas anteriores a F_min ni posteriores a F_max

Escenario: Continente sin noticias evaluadas en la fecha elegida
  Dado que para un continente el backend responde humor_promedio = null y cantidad_noticias_evaluadas = 0
  Cuando el usuario abre el dashboard "Mapa de humor"
  Entonces el marcador de ese continente muestra el texto "Sin datos"
  Y la vista no muestra ningún mensaje de error

Escenario: Clasificación visual por signo del humor
  Dado un continente con humor_promedio = +3.4, otro con -4.1 y otro con 0.0
  Cuando el usuario abre el dashboard "Mapa de humor"
  Entonces el primero se representa como positivo, el segundo como negativo y el tercero como neutro
  Y la vista incluye una leyenda que explica las 4 representaciones (positivo, neutro, negativo, sin datos)

Escenario: El backend no responde o responde con error
  Dado que GET /api/v1/sentiment responde con código HTTP 500 o no responde dentro del timeout configurado
  Cuando el usuario abre el dashboard "Mapa de humor"
  Entonces la vista muestra un mensaje de error legible para el usuario
  Y no queda la pantalla en blanco ni un indicador de carga indefinido
```

**Nota de grounding (lista de noticias en el dashboard de humor):** el PDF (sección 4.3.2) pide además que el dashboard de humor ofrezca "una lista de las noticias que más han influido en el cálculo del humor". Ese requisito se cubre con HU-DASH-002; el equipo debe confirmar si basta con que la lista esté en una vista propia accesible desde el menú (como en la maqueta) o si debe mostrarse dentro de la misma vista del mapa.

**Nota de grounding (escala):** la escala de -10 a +10 que muestra la leyenda proviene del PDF (sección 10.4) y de la sección 11 de las instrucciones del proyecto.

### Definition of Done
(Bloque general DoD, sección 14 de las instrucciones del proyecto — código revisado por al menos 1 integrante vía Pull Request, pruebas unitarias con dependencias externas aisladas mediante mocks, cobertura ≥ 80% verificada en GitHub Actions, SonarQube sin issues críticos, build y despliegue con `needs: [test, sonarqube]`.) Adicionalmente:
- La vista consume `GET /api/v1/sentiment` real; no quedan datos de ejemplo en el camino de producción.
- Pruebas unitarias con la llamada a la API simulada mediante mock, cubriendo al menos los 7 escenarios Gherkin anteriores. Nunca pruebas unitarias con llamadas reales al backend ni al servidor de teselas del mapa.
- Validado visualmente en al menos una resolución de pantalla, registrada en el Pull Request.
- `ADR-05-stack-frontend-dashboards.md` en estado Aceptado.
- Puntos pendientes 1 a 4 de esta historia resueltos y reflejados en el contrato.

---

## HU-DASH-001 — Dashboard mapa mundial de humor (DEPRECADA)

> **Estado: Deprecada (2026-10-05).** Reemplazada por **HU-DASH-001-v2**. Se conserva sin cambios para trazabilidad. Motivo: asumía 6 continentes y daba la lista por no definida, en contradicción con la decisión del equipo en HU-RSS-009 (5 continentes).

**Tipo:** Historia de Usuario
**Como** analista de medios o usuario interesado en la evolución del sentimiento global *(PDF, sección 4.1)*,
**quiero** ver en un mapa del mundo el humor de cada continente en una fecha que yo elija dentro del rango con información disponible,
**para** identificar de un vistazo qué regiones están de mejor o peor humor y cómo cambia ese humor de un día a otro.

**Prioridad:** Alta *(es la vista principal del proyecto: PDF, sección 4.3.2)*
**Estimación (Planning Poker P3):** 5 puntos *(ya estimado formalmente en el Planning Poker de la Práctica P3 — ver `Anexo-I-Planificacion-entregado-P3.md`; no es un valor definitivo: el detalle de esta historia se escribió después de estimar, por lo que el equipo debe revalidar si 5 puntos sigue siendo representativo)*
**Depende de contrato de API:** Sí — `GET /api/v1/sentiment` con parámetros de query `continente`, `desde` y `hasta` (HU-SENT-004) — ver `contrato-sentimiento-diccionario.openapi.yaml`, tag `sentiment`, esquema `SentimientoAgregado` (`humor_promedio`, `cantidad_noticias_evaluadas`, `serie_temporal`).
**Valor de humor que consume:** `humor_promedio` (promedio de `valor_humor` de las noticias que cumplen el filtro), calculado por el backend. No aplica ninguna variante propia del algoritmo.

**Puntos pendientes de decisión del equipo** (no resueltos por este documento):
1. **Lista cerrada de continentes.** El contrato define `continente` como `string` libre y la carga inicial de fuentes por continente (HU-RSS-009) aún no fija la lista definitiva. La maqueta asume seis: América del Norte, América del Sur, Europa, África, Asia y Oceanía. Se recomienda convertir el parámetro en un `enum` en el contrato para que backend y frontend usen exactamente los mismos valores.
2. **Cómo obtiene el mapa los datos de todos los continentes.** El contrato actual devuelve un único `SentimientoAgregado` por llamada. El mapa necesita uno por continente, lo que hoy implica una llamada por continente. El PDF (sección 10.2) prevé además un recurso `/dashboards` con `GET (nube-palabras, mapa)`. El equipo debe decidir entre N llamadas a `/sentiment` o un endpoint de mapa que devuelva todos los continentes en una sola respuesta.
3. **Rango de fechas con información.** El PDF (sección 4.3.2) pide que el usuario elija la fecha "en el rango de fechas para el que se dispone información". El contrato no expone ese rango (fecha mínima y máxima con datos). Debe definirse de dónde lo obtiene el frontend.
4. **Rangos de color.** La maqueta clasifica solo por signo (mayor que 0 positivo, menor que 0 negativo, igual a 0 neutro). El equipo no ha definido umbrales oficiales para "positivo", "neutro" o "negativo".

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Visualización del humor por continente en la fecha elegida
  Dado que el backend dispone de humor agregado para la fecha 2026-10-02 en 6 continentes
  Cuando el usuario abre el dashboard "Mapa de humor" con esa fecha seleccionada
  Entonces el mapa muestra exactamente 1 marcador por cada uno de los 6 continentes
  Y cada marcador muestra el humor_promedio de su continente con 1 decimal y signo explícito cuando es positivo

Escenario: Humor global de la fecha elegida
  Dado que el backend dispone de humor agregado global para la fecha seleccionada
  Cuando el usuario abre el dashboard "Mapa de humor"
  Entonces la vista muestra el humor_promedio global con 1 decimal
  Y muestra la cantidad_noticias_evaluadas que sustenta ese valor

Escenario: Cambio de fecha dentro del rango con información
  Dado que el dashboard está mostrando la fecha 2026-10-02
  Cuando el usuario selecciona la fecha 2026-09-28, que pertenece al rango con información
  Entonces los valores de todos los marcadores y del humor global pasan a ser los de 2026-09-28
  Y la página no se recarga

Escenario: Selector de fecha limitado al rango con información
  Dado que el rango con información va de la fecha F_min a la fecha F_max
  Cuando el usuario abre el selector de fecha
  Entonces el selector no permite elegir fechas anteriores a F_min ni posteriores a F_max

Escenario: Continente sin noticias evaluadas en la fecha elegida
  Dado que para un continente el backend responde humor_promedio = null y cantidad_noticias_evaluadas = 0
  Cuando el usuario abre el dashboard "Mapa de humor"
  Entonces el marcador de ese continente muestra el texto "Sin datos"
  Y la vista no muestra ningún mensaje de error

Escenario: Clasificación visual por signo del humor
  Dado un continente con humor_promedio = +3.4, otro con -4.1 y otro con 0.0
  Cuando el usuario abre el dashboard "Mapa de humor"
  Entonces el primero se representa como positivo, el segundo como negativo y el tercero como neutro
  Y la vista incluye una leyenda que explica las 4 representaciones (positivo, neutro, negativo, sin datos)

Escenario: El backend no responde o responde con error
  Dado que GET /api/v1/sentiment responde con código HTTP 500 o no responde dentro del timeout configurado
  Cuando el usuario abre el dashboard "Mapa de humor"
  Entonces la vista muestra un mensaje de error legible para el usuario
  Y no queda la pantalla en blanco ni un indicador de carga indefinido
```

**Nota de grounding (lista de noticias en el dashboard de humor):** el PDF (sección 4.3.2) pide además que el dashboard de humor ofrezca "una lista de las noticias que más han influido en el cálculo del humor". Ese requisito se cubre con HU-DASH-002; el equipo debe confirmar si basta con que la lista esté en una vista propia accesible desde el menú (como en la maqueta) o si debe mostrarse dentro de la misma vista del mapa.

**Nota de grounding (escala):** la escala de -10 a +10 que muestra la leyenda proviene del PDF (sección 10.4) y de la sección 11 de las instrucciones del proyecto.

### Definition of Done
(Bloque general DoD, sección 14 de las instrucciones del proyecto — código revisado por al menos 1 integrante vía Pull Request, pruebas unitarias con dependencias externas aisladas mediante mocks, cobertura ≥ 80% verificada en GitHub Actions, SonarQube sin issues críticos, build y despliegue con `needs: [test, sonarqube]`.) Adicionalmente:
- La vista consume `GET /api/v1/sentiment` real; no quedan datos de ejemplo en el camino de producción.
- Pruebas unitarias con la llamada a la API simulada mediante mock, cubriendo al menos los 7 escenarios Gherkin anteriores. Nunca pruebas unitarias con llamadas reales al backend ni al servidor de teselas del mapa.
- Validado visualmente en al menos una resolución de pantalla, registrada en el Pull Request.
- `ADR-05-stack-frontend-dashboards.md` en estado Aceptado.
- Puntos pendientes 1 a 4 de esta historia resueltos y reflejados en el contrato.

---

## HU-DASH-002-v2 — Listado de noticias más influyentes

**Reemplaza a:** HU-DASH-002 (Deprecada). **Qué cambió:** se resuelven los 4 puntos pendientes y la historia pasa a depender de `contrato-noticias.openapi.yaml` (`GET /api/v1/news` y `GET /api/v1/news/{id}`). **Por qué:** propuesta de Valentín García (influencia = valor absoluto de `valor_humor`, paginación de 10 por defecto y 50 como máximo, filtros) con tres ajustes de la PO del 2026-10-18: día de referencia `COALESCE(fecha_publicacion, fecha_registro)`, desempate estable por `id` y parámetro `orden` (`fecha` o `influencia`). Se agregan 4 escenarios Gherkin.

**Tipo:** Historia de Usuario
**Como** analista de medios o usuario interesado en la evolución del sentimiento global,
**quiero** ver el listado de las noticias que más han influido en el humor calculado, con su valor de humor y sus datos de origen, y poder filtrarlo,
**para** entender qué hechos concretos explican el humor que muestra el dashboard.

**Prioridad:** Alta
**Estimación (Planning Poker P3):** 2 puntos *(estimado en P3 sin contrato ni paginación; el alcance creció con los filtros, la paginación y el detalle, por lo que el equipo debe reestimar en Planning Poker. No se propone aquí una cifra nueva)*
**Depende de contrato de API:** Sí — `GET /api/v1/news` y `GET /api/v1/news/{id}` — ver `contrato-noticias.openapi.yaml` (v1.0.0).
**Valor de humor que consume:** `valor_humor` de cada noticia, calculado y persistido por el backend (HU-SENT-002-v3). La influencia (`|valor_humor|`) y el orden los calcula el backend. No aplica ninguna variante propia del algoritmo.

**Decisiones (antes puntos pendientes de HU-DASH-002):**
1. **Influencia** = valor absoluto de `valor_humor`: mientras más lejos de 0, más influyente. Con `orden=influencia`, desempata la fecha de referencia más reciente y después el `id`.
2. **Cantidad:** paginación con la convención de `/channels` y `/sources` (`items`, `pagina`, `tamanio_pagina`, `total`); 10 por página por defecto y 50 como máximo.
3. **Filtros:** `signo` (`todas`, `positivas`, `negativas`), `continente` (enum de 5), `pais` y `fecha` (día de referencia, la misma regla que el mapa). La vista usa signo, continente y país (2026-10-19, mismo selector de país que la nube); fecha queda disponible en la API.
4. **Nombres de campos:** los del modelo (`enlace_original`, `categoria_iptc`). La "fuente" que muestra la vista es el nombre del `CanalNoticias` (campo `canal`), porque `FuenteRSS` solo tiene url (hallazgo H-6). El frontend traduce el código IPTC a su nombre.

**Puntos pendientes de decisión del equipo:**
1. **Ubicación en la interfaz.** Sigue abierta la pregunta de HU-DASH-001-v3: basta con la vista propia del menú, o la lista debe aparecer también dentro del dashboard de humor.

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Listado ordenado por influencia
  Dado que existen noticias con valor_humor +7.5, -7.2, -6.8 y +3.9
  Cuando el usuario abre la vista "Noticias"
  Entonces las noticias aparecen en el orden +7.5, -7.2, -6.8, +3.9
  Y ese orden corresponde al valor absoluto de valor_humor de mayor a menor

Escenario: Datos visibles de cada noticia
  Cuando el usuario abre la vista "Noticias"
  Entonces cada noticia muestra su título, su valor_humor con 1 decimal y signo, su canal, su continente, el nombre de su categoría IPTC y su fecha de referencia
  Y el título es un enlace al enlace_original de la noticia que se abre en una pestaña nueva

Escenario: Filtro de noticias positivas
  Dado que existen noticias con valor_humor positivo, negativo e igual a 0
  Cuando el usuario elige el filtro "Positivas"
  Entonces la lista muestra únicamente noticias con valor_humor mayor que 0

Escenario: Filtro de noticias negativas
  Dado que existen noticias con valor_humor positivo, negativo e igual a 0
  Cuando el usuario elige el filtro "Negativas"
  Entonces la lista muestra únicamente noticias con valor_humor menor que 0

Escenario: Filtro por continente
  Dado que existen noticias de canales de Europa y de Oceanía
  Cuando el usuario elige el continente "Europa"
  Entonces la lista muestra únicamente noticias de canales de Europa

Escenario: Noticias sin humor calculado
  Dado que existen noticias con valor_humor = null
  Cuando el usuario abre la vista "Noticias"
  Entonces esas noticias no aparecen en el listado

Escenario: Paginación estable
  Dado que existen 25 noticias con humor calculado
  Cuando el usuario recorre las páginas 1, 2 y 3 de 10 noticias
  Entonces ve exactamente 25 noticias distintas, sin repetir ni saltar ninguna
  Y la vista indica la página actual y el total de noticias

Escenario: Desempate por fecha y por id
  Dado dos noticias con el mismo |valor_humor|
  Cuando el listado se ordena por influencia
  Entonces aparece primero la de fecha de referencia más reciente y, si coincide, la de id mayor

Escenario: Filtro sin resultados
  Dado que ninguna noticia cumple el filtro elegido
  Cuando el usuario aplica ese filtro
  Entonces la vista muestra el mensaje "No hay noticias para este filtro"
  Y no muestra ningún mensaje de error

Escenario: Detalle de una noticia inexistente
  Cuando se envía GET a /api/v1/news/999 y esa noticia no existe
  Entonces el sistema responde con código HTTP 404 y codigo "NOTICIA_NO_ENCONTRADA"
```

**Nota de grounding (categoría):** la categoría es el primer nivel de IPTC Media Topics (PDF, sección 3, Alcance, punto 3); la noticia la hereda de su fuente (HU-RSS-002).

### Definition of Done
(Bloque general DoD, sección 14 de las instrucciones del proyecto.) Adicionalmente:
- `contrato-noticias.openapi.yaml` aprobado por el equipo.
- La vista consume el endpoint real; el orden por influencia, los filtros y la paginación los aplica el backend.
- Pruebas del backend de los escenarios anteriores (implementadas en `src/tests/test_news.py`).
- Pruebas unitarias del frontend con la llamada a la API simulada mediante mock (herramienta pendiente, `ADR-05-stack-frontend-dashboards.md`).
- Validado visualmente en al menos una resolución de pantalla, registrada en el Pull Request.

---

## HU-DASH-002 — Listado de noticias más influyentes (DEPRECADA)

> **Estado: Deprecada (2026-10-19).** Reemplazada por **HU-DASH-002-v2**. Se conserva sin cambios para trazabilidad. Motivo: tenía 4 puntos pendientes y ningún contrato de API.

**Tipo:** Historia de Usuario
**Como** analista de medios o usuario interesado en la evolución del sentimiento global,
**quiero** ver el listado de las noticias que más han influido en el humor calculado, con su valor de humor y sus datos de origen,
**para** entender qué hechos concretos explican el humor que muestra el dashboard.

**Prioridad:** Alta
**Estimación (Planning Poker P3):** 2 puntos *(ya estimado en P3; valor de partida sujeto a revalidación del equipo, en especial porque el contrato de API que necesita todavía no existe)*
**Depende de contrato de API:** Sí — recurso nuevo, **no existe todavía en ningún contrato**. El PDF (sección 10.2) exige `/news` con `GET (lista, detalle, filtros, influyentes)`. Debe crearse el contrato antes de integrar esta historia.
**Valor de humor que consume:** `valor_humor` de cada noticia, calculado y persistido por el backend (HU-SENT-002-v2 y HU-SENT-003). No aplica ninguna variante propia del algoritmo.

**Puntos pendientes de decisión del equipo:**
1. **Definición de "influyente".** El PDF no la define. La maqueta usa el valor absoluto de `valor_humor` (mientras más lejos de 0, más influyente). Es una definición propuesta, no decidida: el equipo debe ratificarla o reemplazarla, y el orden debe calcularlo el backend, no el frontend.
2. **Cantidad máxima de noticias del listado.** No hay cifra en el PDF. Debe fijarse un límite o una paginación coherente con la convención ya usada en `/channels` y `/sources` (`items`, `pagina`, `tamanio_pagina`, `total`).
3. **Filtros.** El PDF menciona "filtros" sin detallarlos. La maqueta filtra por signo (todas, positivas, negativas). Falta decidir si se filtra también por continente y por fecha, en coherencia con HU-DASH-001-v3.
4. **Nombres de campos.** La maqueta supuso `enlace` y `categoria`; el modelo `Noticia` vigente en `docs/architecture.md` (sección 5) usa `enlace_original` y `categoria_iptc`. El contrato debe seguir el modelo, y los datos de ejemplo deben corregirse a esos nombres.

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Listado ordenado por influencia
  Dado que existen noticias con valor_humor +7.5, -7.2, -6.8 y +3.9
  Cuando el usuario abre la vista "Noticias"
  Entonces las noticias aparecen en el orden +7.5, -7.2, -6.8, +3.9
  Y ese orden corresponde al valor absoluto de valor_humor de mayor a menor

Escenario: Datos visibles de cada noticia
  Cuando el usuario abre la vista "Noticias"
  Entonces cada noticia muestra su título, su valor_humor con 1 decimal y signo, su fuente, su continente, su categoría IPTC y su fecha de publicación
  Y el título es un enlace al enlace_original de la noticia que se abre en una pestaña nueva

Escenario: Filtro de noticias positivas
  Dado que existen noticias con valor_humor positivo, negativo e igual a 0
  Cuando el usuario elige el filtro "Positivas"
  Entonces la lista muestra únicamente noticias con valor_humor mayor que 0

Escenario: Filtro de noticias negativas
  Dado que existen noticias con valor_humor positivo, negativo e igual a 0
  Cuando el usuario elige el filtro "Negativas"
  Entonces la lista muestra únicamente noticias con valor_humor menor que 0

Escenario: Noticias sin humor calculado
  Dado que existen noticias con valor_humor = null (pendientes de cálculo, ver HU-SENT-003)
  Cuando el usuario abre la vista "Noticias"
  Entonces esas noticias no aparecen en el listado

Escenario: Filtro sin resultados
  Dado que ninguna noticia cumple el filtro elegido
  Cuando el usuario aplica ese filtro
  Entonces la vista muestra el mensaje "No hay noticias para este filtro"
  Y no muestra ningún mensaje de error
```

**Nota de grounding (categoría):** la categoría mostrada es el primer nivel de IPTC Media Topics, tal como exige el PDF (sección 3, Alcance, punto 3).

### Definition of Done
(Bloque general DoD, sección 14 de las instrucciones del proyecto.) Adicionalmente:
- Contrato de `/news` creado y aprobado por el equipo, originado en esta historia.
- La vista consume el endpoint real; el orden por influencia y el límite de resultados los aplica el backend.
- Pruebas unitarias con la llamada a la API simulada mediante mock, cubriendo los 6 escenarios Gherkin anteriores.
- Validado visualmente en al menos una resolución de pantalla, registrada en el Pull Request.

---

## HU-DASH-003-v2 — Nube de palabras influyentes con filtros

**Reemplaza a:** HU-DASH-003 (Deprecada). **Qué cambió:** se define el peso de una palabra y el origen de sus datos, y la historia pasa a depender de HU-SENT-008 y de `contrato-dashboards.openapi.yaml`. **Por qué:** HU-DASH-003 dependía de coincidencias término–noticia que ninguna historia persistía, y su ejemplo de peso contradecía HU-SENT-007 (hallazgos H-2 y H-3 de `Revision-consistencia-EPIC-DASH-2026-10-05.md`). Decisiones de equipo de la sesión del 2026-10-05. Los criterios de aceptación no cambian.

**Tipo:** Historia de Usuario
**Como** analista de medios o usuario interesado en la evolución del sentimiento global,
**quiero** ver una nube con las palabras que más influyen en el cálculo del humor, pudiendo filtrarla por continente o por país,
**para** reconocer qué términos dominan el humor de una región sin tener que leer noticia por noticia.

**Prioridad:** Media *(el PDF la exige en la sección 4.3.1, pero depende de más decisiones abiertas que las otras dos vistas)*
**Estimación (Planning Poker P3):** 5 puntos *(ya estimado en P3; valor de partida sujeto a revalidación del equipo: la definición de "influencia" de una palabra y su relación con el camino de ML no estaban resueltas al estimar)*
**Depende de contrato de API:** Sí — `GET /api/v1/dashboards/word-cloud` con parámetros de query `continente`, `pais` y `limite` — ver `contrato-dashboards.openapi.yaml`, esquema `NubePalabras`.
**Valor de humor que consume:** el `valor` de cada término del diccionario (escala -10 a +10, HU-SENT-001) y su `peso`, calculado por el backend como la cantidad de noticias del filtro que contienen el término (HU-SENT-008). No aplica ninguna variante propia del algoritmo.

**Puntos pendientes de decisión del equipo:**
1. **Definición de "influencia" de una palabra: resuelto.** Peso = cantidad de noticias del filtro que contienen el término (decisión de equipo, 2026-10-05). Cada término cuenta una sola vez por noticia, en coherencia con HU-SENT-007 y `ADR-03-eleccion-algoritmo-agregacion-sentimiento.md`; no se cuentan las repeticiones dentro de un mismo texto.
2. **Relación con el camino de ML: resuelto.** La nube se construye siempre a partir de las coincidencias con el diccionario, que HU-SENT-008 registra en una tabla de unión para toda noticia capturada, también cuando su humor lo calcula el modelo de ML.
3. **Filtro por país.** El PDF pide filtro "por continente o país". La maqueta implementa solo continente. Falta definir de dónde sale la lista de países (`CanalNoticias.pais` es opcional en el modelo vigente).
4. **Cantidad máxima de palabras.** No hay cifra en el PDF; debe fijarse un límite para que la nube sea legible. El contrato ya expone el parámetro `limite`, sin valor por defecto ni máximo.
5. **Idioma.** Los términos son únicos por palabra e idioma (HU-SENT-001). Falta decidir si la nube mezcla español e inglés y cómo trata una misma palabra presente en ambos idiomas.

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Tamaño proporcional a la influencia
  Dado un conjunto de palabras con peso 100, 50 y 10
  Cuando el usuario abre la vista "Nube de palabras"
  Entonces la palabra de peso 100 se muestra con el tamaño de letra máximo
  Y cada una de las demás se muestra con un tamaño estrictamente menor que el de cualquier palabra de mayor peso

Escenario: Color según el signo del valor del término
  Dado una palabra con valor +8 y otra con valor -10 en el diccionario
  Cuando el usuario abre la vista "Nube de palabras"
  Entonces la primera se representa como positiva y la segunda como negativa
  Y la vista incluye una leyenda que explica ambas representaciones

Escenario: Filtro por continente
  Dado que la nube está mostrando las palabras de todo el mundo
  Cuando el usuario elige el continente "Asia"
  Entonces la nube muestra únicamente las palabras influyentes de Asia
  Y la página no se recarga

Escenario: Filtro por país
  Dado que existen canales con país informado
  Cuando el usuario elige un país
  Entonces la nube muestra únicamente las palabras influyentes de ese país

Escenario: Consulta del valor de una palabra
  Cuando el usuario sitúa el puntero sobre una palabra de la nube
  Entonces la vista muestra el valor de esa palabra en el diccionario, con signo

Escenario: Filtro sin palabras
  Dado que no hay palabras influyentes para el filtro elegido
  Cuando el usuario aplica ese filtro
  Entonces la vista muestra el mensaje "No hay palabras para este filtro"
  Y no muestra ningún mensaje de error
```

**Nota de grounding (diccionario opcional):** la corrección del 21/08/26 al PDF (sección 4.2.2) indica que el diccionario solo es obligatorio si se usa el método de evaluación de la sección 10.4. El equipo eligió un enfoque híbrido que conserva el diccionario (HU-SENT-007), por lo que la nube de palabras sigue teniendo una fuente de datos válida.

### Definition of Done
(Bloque general DoD, sección 14 de las instrucciones del proyecto.) Adicionalmente:
- `contrato-dashboards.openapi.yaml` aprobado por el equipo.
- HU-SENT-008 implementada y cumpliendo su propia Definition of Done.
- El peso de cada palabra lo calcula el backend; el frontend no implementa ninguna fórmula de influencia.
- Filtro por país implementado, además del filtro por continente.
- Pruebas unitarias con la llamada a la API simulada mediante mock, cubriendo los 6 escenarios Gherkin anteriores.
- Validado visualmente en al menos una resolución de pantalla, registrada en el Pull Request.

---

## HU-DASH-003 — Nube de palabras influyentes con filtros (DEPRECADA)

> **Estado: Deprecada (2026-10-05).** Reemplazada por **HU-DASH-003-v2**. Se conserva sin cambios para trazabilidad. Motivo: no definía el peso de una palabra y dependía de un dato que el backend no persistía.

**Tipo:** Historia de Usuario
**Como** analista de medios o usuario interesado en la evolución del sentimiento global,
**quiero** ver una nube con las palabras que más influyen en el cálculo del humor, pudiendo filtrarla por continente o por país,
**para** reconocer qué términos dominan el humor de una región sin tener que leer noticia por noticia.

**Prioridad:** Media *(el PDF la exige en la sección 4.3.1, pero depende de más decisiones abiertas que las otras dos vistas)*
**Estimación (Planning Poker P3):** 5 puntos *(ya estimado en P3; valor de partida sujeto a revalidación del equipo: la definición de "influencia" de una palabra y su relación con el camino de ML no estaban resueltas al estimar)*
**Depende de contrato de API:** Sí — recurso nuevo, **no existe todavía en ningún contrato**. El PDF (sección 10.2) exige `/dashboards` con `GET (nube-palabras, mapa)`. Debe crearse el contrato antes de integrar esta historia.
**Valor de humor que consume:** el `valor` de cada término del diccionario (escala -10 a +10, HU-SENT-001) y un peso de influencia calculado por el backend. No aplica ninguna variante propia del algoritmo.

**Puntos pendientes de decisión del equipo:**
1. **Definición de "influencia" de una palabra.** El PDF no la define. La maqueta recibe un campo `peso` ya calculado y solo lo usa para el tamaño de la letra. El equipo debe decidir cómo se calcula ese peso en el backend (por ejemplo, frecuencia de aparición o frecuencia ponderada por el valor absoluto del término). Esa decisión es de EPIC-SENT, no de la capa de presentación.
2. **Relación con el camino de ML.** Cuando el humor de una noticia se calcula con el modelo de ML (`ADR-04-arquitectura-modelo-ml-sentimiento.md`: embeddings más regresor), el cálculo no usa términos del diccionario. El equipo debe decidir si la nube se construye siempre a partir de las coincidencias con el diccionario, independientemente del método que calculó el humor.
3. ~~**Filtro por país.**~~ **Resuelto el 2026-10-19:** la lista de países sale del campo `pais` de los canales registrados (`GET /api/v1/channels`, HU-RSS-010), el mismo dato con el que el backend filtra; con un continente elegido solo se ofrecen sus países. Los canales sin país informado solo aparecen en el filtro por continente.
4. **Cantidad máxima de palabras.** No hay cifra en el PDF; debe fijarse un límite para que la nube sea legible.

### Criterios de aceptación (Gherkin)

```gherkin
Escenario: Tamaño proporcional a la influencia
  Dado un conjunto de palabras con peso 100, 50 y 10
  Cuando el usuario abre la vista "Nube de palabras"
  Entonces la palabra de peso 100 se muestra con el tamaño de letra máximo
  Y cada una de las demás se muestra con un tamaño estrictamente menor que el de cualquier palabra de mayor peso

Escenario: Color según el signo del valor del término
  Dado una palabra con valor +8 y otra con valor -10 en el diccionario
  Cuando el usuario abre la vista "Nube de palabras"
  Entonces la primera se representa como positiva y la segunda como negativa
  Y la vista incluye una leyenda que explica ambas representaciones

Escenario: Filtro por continente
  Dado que la nube está mostrando las palabras de todo el mundo
  Cuando el usuario elige el continente "Asia"
  Entonces la nube muestra únicamente las palabras influyentes de Asia
  Y la página no se recarga

Escenario: Filtro por país
  Dado que existen canales con país informado
  Cuando el usuario elige un país
  Entonces la nube muestra únicamente las palabras influyentes de ese país

Escenario: Consulta del valor de una palabra
  Cuando el usuario sitúa el puntero sobre una palabra de la nube
  Entonces la vista muestra el valor de esa palabra en el diccionario, con signo

Escenario: Filtro sin palabras
  Dado que no hay palabras influyentes para el filtro elegido
  Cuando el usuario aplica ese filtro
  Entonces la vista muestra el mensaje "No hay palabras para este filtro"
  Y no muestra ningún mensaje de error
```

**Nota de grounding (diccionario opcional):** la corrección del 21/08/26 al PDF (sección 4.2.2) indica que el diccionario solo es obligatorio si se usa el método de evaluación de la sección 10.4. El equipo eligió un enfoque híbrido que conserva el diccionario (HU-SENT-007), por lo que la nube de palabras sigue teniendo una fuente de datos válida.

### Definition of Done
(Bloque general DoD, sección 14 de las instrucciones del proyecto.) Adicionalmente:
- Contrato de `/dashboards` (nube de palabras) creado y aprobado por el equipo, originado en esta historia.
- El peso de cada palabra lo calcula el backend; el frontend no implementa ninguna fórmula de influencia.
- Filtro por país implementado, además del filtro por continente.
- Pruebas unitarias con la llamada a la API simulada mediante mock, cubriendo los 6 escenarios Gherkin anteriores.
- Validado visualmente en al menos una resolución de pantalla, registrada en el Pull Request.

---

## Resumen de trazabilidad

| ID | Tipo | Prioridad | Puntos (P3) | Endpoint / mecanismo | Referencia PDF |
|---|---|---|---|---|---|
| HU-DASH-001 | Historia de Usuario — **Deprecada**, reemplazada por HU-DASH-001-v2 | — | — | — | — |
| HU-DASH-001-v2 | Historia de Usuario — **Deprecada**, reemplazada por HU-DASH-001-v3 | — | — | — | — |
| HU-DASH-001-v3 | Historia de Usuario | Alta | 5 (por reestimar) | `GET /api/v1/dashboards/map` — ver `contrato-dashboards.openapi.yaml`; `GET /api/v1/sentiment` (serie temporal, HU-SENT-004) | §4.3, §4.3.2, §10.2 |
| HU-DASH-002 | Historia de Usuario — **Deprecada**, reemplazada por HU-DASH-002-v2 | — | — | — | — |
| HU-DASH-002-v2 | Historia de Usuario | Alta | 2 (por reestimar) | `GET /api/v1/news` y `GET /api/v1/news/{id}` — ver `contrato-noticias.openapi.yaml` | §4.3, §4.3.2, §10.2 |
| HU-DASH-003 | Historia de Usuario — **Deprecada**, reemplazada por HU-DASH-003-v2 | — | — | — | — |
| HU-DASH-003-v2 | Historia de Usuario | Media | 5 | `GET /api/v1/dashboards/word-cloud` — ver `contrato-dashboards.openapi.yaml` | §4.3, §4.3.1, §10.2 |

Las estimaciones en puntos provienen del Planning Poker de P3 y son un punto de partida, no un valor definitivo: deben revalidarse con el equipo ahora que el alcance está detallado.

## Dependencias con otras épicas

| Historia | Depende de | Motivo |
|---|---|---|
| HU-DASH-001-v3 | HU-SENT-004, HU-SENT-002-v2, HU-SENT-003 | Sin humor calculado y sin el endpoint de consulta no hay datos reales que mostrar |
| HU-DASH-001-v3 | HU-RSS-009 | Fija la lista de 5 continentes (América, Europa, Asia, África, Oceanía) que el mapa debe mostrar |
| HU-DASH-002-v2 | HU-SENT-002-v3 | Necesita `valor_humor` persistido en cada noticia |
| HU-DASH-003-v2 | HU-SENT-001, HU-SENT-008 | Necesita el diccionario y las coincidencias término–noticia persistidas (`HU-SENT-008-coincidencias-terminos.md`) |

## Tabla de control de versiones

| ID | Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|---|
| HU-DASH-001 a 003 | v1.0 | 2026-10-03 | Primera formalización detallada de las 3 historias de EPIC-DASH, a partir de los títulos ya oficializados en el backlog de P3 y de la estimación del Planning Poker de P3. Se agregan Gherkin, DoD, dependencia de contratos, notas de grounding y los puntos pendientes de decisión del equipo detectados al construir la maqueta de la rama `feature/frontend-dashboards`. |
| HU-DASH-001 a 003 | v1.1 (editorial) | 2026-10-05 | Normalización de nomenclatura al incorporar el documento al Proyecto: referencias a ADRs con tres dígitos (`ADR-03`, `ADR-04`, `ADR-05`) y nombres de archivo reales (`ADR-03-eleccion-algoritmo-agregacion-sentimiento.md`, `ADR-04-arquitectura-modelo-ml-sentimiento.md`, `ADR-05-stack-frontend-dashboards.md`). Sin cambios en alcance, criterios de aceptación, estimaciones ni puntos pendientes. Los hallazgos de fondo de la revisión cruzada están en `Revision-consistencia-EPIC-DASH-2026-10-05.md` y no se aplicaron aquí. |
| HU-DASH-001-v2 | v1.2 | 2026-10-05 | HU-DASH-001 pasa a **Deprecada** y se crea HU-DASH-001-v2: la lista de continentes se alinea a los 5 confirmados por el equipo en HU-RSS-009 (América, Europa, Asia, África, Oceanía), en lugar de los 6 asumidos por la maqueta. Cambian el punto pendiente 1 (queda solo la conversión a `enum`) y dos escenarios Gherkin. La estimación de 5 puntos se mantiene como punto de partida, sujeta a revalidación del equipo. Referencias actualizadas en `ADR-05-stack-frontend-dashboards.md` (v1.2). |
| HU-DASH-001-v3, HU-DASH-003-v2 | v1.3 | 2026-10-05 | Cuatro decisiones de equipo tomadas en sesión. **HU-DASH-001-v3** (deprecada la v2): endpoint único `GET /api/v1/dashboards/map` y nuevo gráfico de evolución temporal con 2 escenarios Gherkin adicionales; la estimación de 5 puntos queda por reestimar. **HU-DASH-003-v2** (deprecada la original): peso = cantidad de noticias que contienen el término; datos provistos por la nueva HU-SENT-008 (tabla de unión, también en el camino de ML). Se crea `contrato-dashboards.openapi.yaml` (v1.0.0). Referencias actualizadas en `ADR-05-stack-frontend-dashboards.md` (v1.3). HU-DASH-002 no cambia: sus puntos pendientes y el contrato de `/news` siguen abiertos. |
| Todas | v1.4 (editorial) | 2026-10-18 | Copia para el repositorio: las referencias a ADR vuelven a la convención de dos dígitos y a los nombres de archivo de `docs/Adr/` (`ADR-03-eleccion-algoritmo-agregacion-sentimiento.md`, `ADR-04-arquitectura-modelo-ml-sentimiento.md`, `ADR-05-stack-frontend-dashboards.md`). Deja sin efecto la normalización a tres dígitos de la v1.1. Sin cambios de contenido. |
| HU-DASH-002-v2 | v1.5 | 2026-10-19 | HU-DASH-002 pasa a **Deprecada** y se crea HU-DASH-002-v2: se resuelven sus 4 puntos pendientes con la propuesta de Valentín García (influencia = `|valor_humor|`, paginación 10/50, filtros) y los ajustes de la PO (día de referencia `COALESCE(fecha_publicacion, fecha_registro)`, desempate por `id`, parámetro `orden`). Se crea `contrato-noticias.openapi.yaml` (v1.0.0) y se agregan 4 escenarios Gherkin. Se actualiza la nota de estado de implementación de las tres vistas. La estimación de 2 puntos queda por reestimar. |
| HU-DASH-002-v2, HU-DASH-003-v2 | v1.6 | 2026-10-19 | Se implementa el filtro por país en la nube de palabras y en el listado de noticias (PDF §4.3.1). Se resuelve el punto pendiente 3 de HU-DASH-003-v2: los países salen de `CanalNoticias.pais` vía `GET /api/v1/channels`. Sin cambios en criterios de aceptación ni contratos. |
