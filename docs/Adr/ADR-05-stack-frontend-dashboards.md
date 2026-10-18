# ADR-05: Stack tecnológico y arquitectura de la capa de presentación (frontend de dashboards)

## Estado

**Propuesto** — pendiente de revisión y ratificación del equipo, análogo al proceso seguido con ADR-02, ADR-03 y ADR-04.

Antecedentes de aprobación informal, que este ADR formaliza pero no sustituye: la líder del equipo dio el visto bueno por chat al uso de React, Leaflet y Chart.js (2026-10-02), y el responsable de DevOps aceptó la carpeta `frontend/` en la raíz del repositorio (2026-10-03). Ninguna de las dos conversaciones constituye una ratificación formal de este documento.

---

## Contexto

### 1. Origen y por qué este ADR existe

El PDF de especificaciones exige una "interfaz web" (sección 3, Alcance, punto 4) y define una **capa de presentación** separada de la lógica de negocio y de los datos (sección 6.1: "Interfaz web para la visualización de Dashboards y gestión de configuraciones"). La sección 4.3 enumera las vistas: Panel de administración, Dashboard de humor, Nube de palabras y Listado de noticias. El Sprint 3 de la planificación del equipo (`Anexo-I-Planificacion-entregado-P3.md`) está dedicado a las tres vistas de visualización (HU-DASH-001-v3, HU-DASH-002 y HU-DASH-003-v2).

Hasta ahora ningún ADR decide la tecnología de esa capa. `docs/architecture.md` (sección 2) solo anota, como referencia y fuera del alcance del backend, que la SPA de frontend usará "React 19.2.8 o superior", y la sección 7 declara que "el frontend de HumWorld es una SPA separada". Esa mención no evalúa alternativas ni cubre las demás piezas necesarias (herramienta de construcción, mapas, gráficos, estilos, acceso a datos, pruebas).

Este ADR existe además por una regla del propio proyecto: `openspec/config.yaml` prohíbe "añadir nuevas tecnologías o dependencias sin aprobación humana" y "proponer tecnologías que no estén aprobadas en el contexto". Sin este ADR, cualquier cambio de OpenSpec que toque el frontend estaría incorporando tecnologías no aprobadas.

### 2. Restricciones reales del proyecto

- **El PDF sugiere, sin obligar** (sección 6.2): "Frontend: React.js, Angular o Vue.js para los dashboards interactivos" y "Gráficos / mapas interactivos: Chart.js, D3.js, mapas: Leaflet, Mapbox". La sección 4.3 pide "un diseño limpio, con gráficos interactivos (Chart.js, D3.js) y mapas (Leaflet, Mapbox)". El equipo debe justificar cualquier decisión tecnológica como parte de la documentación (sección 3, Limitaciones, punto 2).
- **Plazo académico fijo:** verificación formal del sistema el 2 de noviembre de 2026. El Sprint 3 termina el 4 de octubre de 2026 y el backend de sentimiento del que dependen los dashboards (Sprint 2) no está terminado a la fecha de este documento.
- **Capacidad del equipo:** hay un único integrante con rol de Frontend, con experiencia básica de programación y sin experiencia previa en frameworks de frontend. La tecnología elegida debe poder aprenderse y mantenerse en ese contexto.
- **Asistentes de programación:** Visual Studio Code con GitHub Copilot como herramienta principal (instrucciones del proyecto, sección 8), además de Claude Code (PDF, sección 6.2). Conviene un stack con documentación y ejemplos abundantes, donde la asistencia por IA sea fiable.
- **Backend ya decidido:** API REST en FastAPI bajo `/api/v1`, con JSON como formato de intercambio (ADR-01; PDF, sección 10.3). El frontend consume esa API; no accede a MySQL.
- **Calidad exigida:** cobertura de pruebas ≥ 80% y SonarQube sin issues críticos (PDF, sección 7; instrucciones del proyecto, sección 14). El PDF pide además pruebas de integración "Frontend ↔ API".
- **Infraestructura existente:** el pipeline de GitHub Actions (`.github/workflows/ci.yml`) y `docker-compose.yml` cubren hoy solo el backend en Python y MySQL. No existe ningún job ni contenedor para un proyecto de frontend.
- **Estado actual:** existe una maqueta navegable de las tres vistas en la rama `feature/frontend-dashboards`, construida con el stack que este ADR propone y con datos de ejemplo. Se construyó antes de ratificar este ADR para tener una validación visual temprana; el equipo puede rechazar la decisión y la maqueta se descartaría.

---

## Decisión

Se adopta, para toda la capa de presentación de HumWorld (dashboards de EPIC-DASH y, más adelante, el panel de administración de EPIC-ADMIN), el siguiente stack y la siguiente organización.

### 1. Framework de interfaz: React 19, en JavaScript

Aplicación de página única (SPA) con React (`react` y `react-dom` 19.2 o superior), escrita en JavaScript con JSX, sin TypeScript. Coincide con la tecnología ya anotada en `docs/architecture.md`, sección 2.

### 2. Herramienta de construcción y servidor de desarrollo: Vite

Proyecto generado con la plantilla oficial de React de Vite (`vite` 8, `@vitejs/plugin-react`). Vite provee el servidor de desarrollo con recarga en caliente y el empaquetado de producción (`npm run build`, que genera archivos estáticos).

### 3. Ubicación en el repositorio: carpeta `frontend/`

El frontend vive en `frontend/`, en la raíz del repositorio, separado de `src/` (backend). Tiene su propio `package.json` y su propio ciclo de instalación, análisis y construcción. Mantiene la separación de capas que exige el PDF (sección 4.6.2) y la declaración de `docs/architecture.md` de que el frontend es una SPA separada del backend.

### 4. Mapas: Leaflet con react-leaflet, sobre teselas de OpenStreetMap

`leaflet` 1.9 y su adaptador `react-leaflet` 5 para el mapa mundial de HU-DASH-001-v3. La cartografía de fondo se obtiene del servidor público de teselas de OpenStreetMap, con la atribución que su licencia exige.

### 5. Gráficos: Chart.js con react-chartjs-2

`chart.js` 4 y su adaptador `react-chartjs-2` 5 para los gráficos de los dashboards, en particular la serie temporal de humor (`serie_temporal` del esquema `SentimientoAgregado`). Su uso queda respaldado por HU-DASH-001-v3, que incorpora el gráfico de evolución temporal del humor global (decisión de equipo, 2026-10-05). A la fecha de la maqueta ambas dependencias están instaladas pero todavía no se usan.

### 6. Nube de palabras: implementación propia, sin librería adicional

La nube de HU-DASH-003-v2 se dibuja con HTML y CSS (tamaño de letra proporcional al peso que entrega el backend). No se incorpora ninguna librería de nubes de palabras, para no sumar una dependencia más a un requisito que se resuelve con pocas líneas.

### 7. Estilos: CSS plano con variables, sin framework de estilos

Hojas de estilo CSS por pantalla, con los colores, bordes y tipografías definidos una sola vez como variables CSS en `index.css`. No se adopta ningún framework de estilos ni librería de componentes.

### 8. Navegación y estado: mecanismos nativos de React

La navegación entre las tres vistas se resuelve con estado local (`useState`), sin librería de enrutamiento ni de gestión de estado global. Esta parte de la decisión debe revisarse cuando se incorpore el panel de administración (HU-ADMIN-004), que agrega más vistas.

### 9. Organización interna y regla de responsabilidad

Estructura de `frontend/src/`: `pantallas/` (una vista por archivo), `componentes/` (piezas reutilizables), `datos/` (acceso a datos) y `utilidades/` (funciones de formato y presentación).

Regla obligatoria, análoga a la regla de `docs/architecture.md` que prohíbe lógica de negocio en los routers: **el frontend no calcula humor ni influencia**. Solo muestra valores ya calculados por el backend (`valor_humor`, `humor_promedio`, peso de las palabras). Cualquier agregación, orden por influencia o fórmula pertenece al backend.

### 10. Acceso a datos: `fetch` nativo contra `/api/v1`

Las vistas obtienen sus datos de la API REST mediante la función `fetch` del navegador, sin librería HTTP adicional. En la maqueta, la carpeta `datos/` contiene datos de ejemplo con la misma forma que los esquemas del contrato (`SentimientoAgregado`), de modo que la integración consista en sustituir el origen de los datos sin rehacer las vistas.

### 11. Calidad de código y pruebas

Análisis estático con ESLint, con la configuración que genera la plantilla de Vite (`npm run lint`).

**Queda explícitamente sin decidir en este ADR** la herramienta de pruebas unitarias del frontend. Es una dependencia nueva y requiere su propia aprobación. Se propone evaluar Vitest con React Testing Library por su integración directa con Vite, pero el equipo debe ratificarlo antes de incorporarlo.

### 12. Patrones de resiliencia (sección 13 de las instrucciones del proyecto)

El frontend depende de tres servicios que pueden fallar o demorarse: la API propia de HumWorld, el servidor público de teselas de OpenStreetMap y el servicio de tipografías de Google Fonts. Los dos últimos son servicios externos de terceros, sin acuerdo de nivel de servicio con el equipo. Evaluación de los cuatro patrones:

- **Timeout explícito — se adopta** para toda llamada a la API propia, como salvaguarda mínima. Sin timeout, una API que no responde dejaría la vista en estado de carga indefinido, lo que contradice el escenario Gherkin de error de HU-DASH-001-v3. El valor concreto del timeout no se fija aquí: debe proponerse y validarse con mediciones reales una vez integrado el backend.
- **Retry con backoff exponencial y límite — se adopta solo para peticiones `GET`**, que son idempotentes, y con un número máximo de reintentos acotado. Nunca reintento infinito y nunca sobre `POST`. El número máximo de reintentos queda pendiente de validación del equipo.
- **Circuit Breaker — no se adopta en el frontend.** El patrón protege a un proceso de larga vida que hace muchas llamadas concurrentes a un servicio caído. Una sesión de navegador hace pocas llamadas y ya está protegida por el timeout y el límite de reintentos. El backend ya aplica Circuit Breaker donde sí corresponde (fuentes RSS, `docs/architecture.md`, sección 8; proveedor de embeddings, ADR-04).
- **Bulkhead — no se adopta.** El aislamiento de recursos entre servicios lo provee el propio navegador, que limita las conexiones por origen. No hay un recurso compartido del frontend que un servicio caído pueda agotar.
- **Degradación controlada ante los servicios externos:** si las teselas de OpenStreetMap no cargan, los marcadores y las tarjetas de continentes siguen mostrando los datos de humor, porque no dependen de la imagen de fondo. Si Google Fonts no responde, la página usa las tipografías del sistema declaradas como alternativa en CSS. Ninguno de los dos fallos bloquea la consulta de datos.

---

## Alternativas consideradas

### Alternativa A — Angular

Framework completo, sugerido por el PDF. Incluye enrutamiento, formularios, cliente HTTP y herramientas de pruebas integradas, lo que reduce el número de decisiones posteriores.
**Motivo de descarte:** exige TypeScript y un conjunto de conceptos propio (módulos o componentes independientes, inyección de dependencias, RxJS) cuya curva de aprendizaje es alta para un único responsable sin experiencia previa en frontend y con un plazo de pocas semanas. Sus ventajas pesan más en aplicaciones grandes con varios equipos, que no es el caso de tres dashboards y un panel de administración.

### Alternativa B — Vue.js

Framework progresivo, sugerido por el PDF, con una curva de aprendizaje comparable o menor que la de React y un ecosistema suficiente para este proyecto (existen adaptadores para Leaflet y Chart.js).
**Motivo de descarte:** técnicamente es una alternativa válida y el descarte no se debe a una carencia del framework. Se prefiere React porque ya figura como tecnología prevista en `docs/architecture.md`, por lo que elegir Vue obligaría a contradecir un documento vigente, y porque el equipo no identificó ninguna ventaja de Vue que compense ese cambio.

### Alternativa C — Sin SPA: páginas renderizadas por el backend (plantillas de FastAPI)

Servir HTML desde el propio backend con plantillas, sin proyecto de frontend separado. Elimina el segundo ecosistema (Node.js) y simplifica Docker y CI.
**Motivo de descarte:** mezcla la capa de presentación con el backend, contra la separación de capas del PDF (secciones 4.6.2 y 6.1) y contra `docs/architecture.md`, sección 7 ("No hay app/static/ ni app/templates/"). Además, la interactividad que pide el PDF (mapa interactivo, selector de fecha, filtros sin recarga) exigiría igualmente JavaScript en el cliente, sin la estructura que aporta un framework.

### Alternativa D — Mapbox en lugar de Leaflet

Sugerido por el PDF. Ofrece mapas vectoriales con mejor rendimiento y más opciones de estilo.
**Motivo de descarte:** requiere crear una cuenta y gestionar un token de acceso, que pasaría a ser un secreto más que administrar en el repositorio, en CI y en Docker, y su uso está sujeto a un modelo de cobro por consumo. Leaflet es de código abierto y no exige cuenta ni credenciales. Para un mapa con un marcador por continente, las ventajas de Mapbox no se aprovechan.

### Alternativa E — D3.js en lugar de Chart.js

Sugerido por el PDF. Permite cualquier visualización a medida, incluido el coloreado de los contornos de los continentes y nubes de palabras con colocación automática.
**Motivo de descarte:** D3 es una librería de bajo nivel: cada gráfico se construye a mano, con mayor esfuerzo de desarrollo y de pruebas. Chart.js entrega los tipos de gráfico estándar (líneas, barras) con configuración declarativa, suficiente para la serie temporal de humor. Si más adelante el equipo decide pintar los contornos reales de los continentes como mapa de calor (PDF, sección 4.1), esta alternativa debe reevaluarse en un ADR nuevo.

### Alternativa F — Otra herramienta de construcción (Create React App o Next.js)

Create React App fue durante años la forma estándar de iniciar un proyecto React; Next.js es un framework sobre React con renderizado en servidor.
**Motivo de descarte:** Create React App fue declarado obsoleto por el equipo de React y ya no se recomienda para proyectos nuevos. Next.js agrega un servidor Node.js en ejecución y un modelo de renderizado en servidor que este proyecto no necesita: el frontend solo consume una API REST y puede servirse como archivos estáticos.

### Alternativa G — TypeScript en lugar de JavaScript

Agrega verificación de tipos en tiempo de desarrollo y detecta antes los errores de forma de datos entre el contrato y las vistas.
**Motivo de descarte:** aumenta la carga de aprendizaje para el responsable de Frontend en el plazo disponible. Es la alternativa con mejor argumento técnico a favor, y su descarte se registra como deuda aceptada (ver Consecuencias).

### Alternativa H — Framework de estilos o librería de componentes

Usar un framework de estilos utilitario o una librería de componentes prefabricados para acelerar la maquetación.
**Motivo de descarte:** suma una dependencia y una convención más que aprender, y el diseño elegido (mascota propia, pocas vistas) no se beneficia de componentes genéricos. CSS plano con variables cubre el alcance actual.

---

## Consecuencias

### Positivas

- La decisión es coherente con las sugerencias del PDF (sección 6.2) y con lo ya anotado en `docs/architecture.md`, por lo que no contradice ningún documento vigente.
- La capa de presentación queda físicamente separada del backend (`frontend/` frente a `src/`), cumpliendo la separación de capas del PDF y permitiendo que frontend y backend avancen en ramas distintas sin conflictos de archivos.
- El frontend puede desarrollarse con datos de ejemplo que respetan la forma del contrato, sin esperar a que el backend esté terminado. Esto ya permitió tener una maqueta de las tres vistas mientras el Sprint 2 sigue abierto.
- El resultado de `npm run build` son archivos estáticos, lo que simplifica el despliegue: basta un servidor web o un contenedor mínimo, sin proceso Node.js en producción.
- Todas las dependencias son de código abierto y no requieren cuentas, tokens ni credenciales, por lo que no agregan secretos que gestionar.
- La regla de que el frontend no calcula humor mantiene una única fuente de verdad para el algoritmo (backend, ADR-03 y ADR-04) y evita que una misma fórmula exista en dos lenguajes.

### Negativas / riesgos a mitigar

- **Segundo ecosistema en el repositorio.** Se incorpora Node.js y npm junto a Python. El pipeline de GitHub Actions necesita jobs nuevos para el frontend (instalación, lint, pruebas, construcción), integrados en la cadena `needs` para que el build y el despliegue sigan ocurriendo solo si las pruebas y SonarQube son exitosos. Hoy esos jobs no existen.
- **Docker.** `docker-compose.yml` define solo `db` y `api`. Hace falta un servicio adicional para servir el frontend, o una decisión explícita de servirlo de otro modo. Queda a cargo del responsable de DevOps.
- **SonarQube.** `sonar-project.properties` debe ampliarse para incluir `frontend/src` en el análisis; de lo contrario, el código del frontend quedaría fuera de las métricas de calidad exigidas.
- **CORS.** El backend no tiene configurado CORS. En desarrollo, el frontend corre en un origen distinto al de la API (puerto del servidor de Vite frente al puerto 8000), y el navegador bloqueará las llamadas hasta que el backend lo permita o se configure un proxy de desarrollo en Vite. Requiere un cambio coordinado con el backend antes de integrar HU-DASH-001-v3.
- **Pruebas del frontend sin herramienta definida.** Mientras no se ratifique la herramienta de pruebas (sección 11 de la Decisión), ninguna historia de EPIC-DASH puede cumplir la Definition of Done (cobertura ≥ 80%).
- **Dependencia de servicios externos sin acuerdo de servicio.** El servidor público de teselas de OpenStreetMap tiene una política de uso pensada para tráfico bajo y no garantiza disponibilidad; es adecuado para un prototipo académico, no para un uso intensivo. Google Fonts es una dependencia externa adicional que puede eliminarse alojando las tipografías en el propio proyecto.
- **Riesgo de divergencia entre datos de ejemplo y contrato.** Dos de las tres vistas (HU-DASH-002 y HU-DASH-003-v2) se maquetaron sin contrato de API, suponiendo la forma de los datos. Cuando se creen los contratos de `/news` y `/dashboards`, esas vistas pueden requerir ajustes.
- **Deuda técnica aceptada**, entendida como esfuerzo estimado de refactorización y no como conteo de defectos: (a) ausencia de tipos estáticos por usar JavaScript, que traslada a las pruebas la detección de errores de forma de datos; (b) navegación sin librería de enrutamiento, que deberá refactorizarse si el número de vistas crece con EPIC-ADMIN; (c) el dibujo de la carita de humor existe en dos formas (componente React y texto HTML para los marcadores de Leaflet), duplicación pequeña impuesta por la forma en que Leaflet recibe sus iconos.

### Sincronización requerida si este ADR se acepta

- `docs/architecture.md`: mover el frontend de "fuera del alcance" a tecnología aprobada (sección 2) y describir la organización de `frontend/` (sección 7).
- `openspec/config.yaml`: agregar a "Tecnologías aprobadas" las de este ADR, para que los cambios de OpenSpec del frontend no violen la regla de no incorporar tecnologías nuevas.
- `.github/workflows/ci.yml`, `docker-compose.yml` y `sonar-project.properties`: incorporar el frontend, según lo descrito en las consecuencias negativas.
- Contratos: `contrato-dashboards.openapi.yaml` (v1.0.0, Propuesto) cubre el mapa de HU-DASH-001-v3 y la nube de HU-DASH-003-v2. Sigue por crear el de `/news` (HU-DASH-002).

---

## Historias de usuario relacionadas

HU-DASH-001-v3, HU-DASH-002, HU-DASH-003-v2 *(ver `HU-DASH-dashboards.md`)*; HU-SENT-004 *(endpoint que consume el mapa)*; HU-SENT-001 y HU-SENT-008 *(diccionario y coincidencias término–noticia persistidas, origen de la nube de palabras)*; HU-RSS-009 *(carga inicial de fuentes, que fija la lista de continentes)*; HU-ADMIN-004 *(panel de administración unificado, que reutilizará este stack en el Sprint 4)*.

---

## Historial de revisión de este ADR

| Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|
| v1.0 | 2026-10-03 | Creación inicial. Formaliza el stack de la capa de presentación (React 19 con Vite, Leaflet, Chart.js, CSS plano, `fetch` nativo) ya usado en la maqueta de la rama `feature/frontend-dashboards`, evalúa ocho alternativas y los cuatro patrones de resiliencia de la sección 13 de las instrucciones del proyecto, y deja explícitamente sin decidir la herramienta de pruebas del frontend. |
| v1.1 (editorial) | 2026-10-05 | Renumerado de ADR-05 a ADR-05 y normalización de las referencias a ADR-01 a ADR-04 con tres dígitos, según la convención del Proyecto. Sin cambios en la Decisión, las Alternativas ni las Consecuencias. Hallazgos de la revisión cruzada en `Revision-consistencia-EPIC-DASH-2026-10-05.md`, no aplicados aquí. |
| v1.2 | 2026-10-05 | Actualización de referencias: HU-DASH-001 fue deprecada y reemplazada por HU-DASH-001-v2 (lista de 5 continentes, según HU-RSS-009). Sin cambios en la Decisión, las Alternativas ni las Consecuencias. |
| v1.3 | 2026-10-05 | Chart.js queda respaldado por una historia (gráfico de evolución temporal de HU-DASH-001-v3). Referencias actualizadas a HU-DASH-001-v3, HU-DASH-003-v2 y HU-SENT-008, y al nuevo `contrato-dashboards.openapi.yaml`. Sin cambios en el stack decidido ni en las Alternativas. |
| v1.4 (editorial) | 2026-10-18 | Copia para el repositorio: se mantiene el número ADR-05 y las referencias de dos dígitos de `docs/Adr/`, dejando sin efecto la renumeración a tres dígitos de la v1.1. Sin cambios en la Decisión, las Alternativas ni las Consecuencias. |
