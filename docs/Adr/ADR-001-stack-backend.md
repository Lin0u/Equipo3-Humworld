# ADR-001: Elección del stack tecnológico de backend

**Estado:** Aceptado — ratificado por el equipo el 2026-08-19, al confirmar el inicio de la implementación de Sprint 1 (captura y gestión de fuentes RSS).

---

## Contexto

El proyecto HumWorld (Equipo 3, asignatura Uso de IA en Ingeniería de Software, Universidad Andrés Bello, curso 2026-27) requiere implementar una API REST completa que exponga operaciones CRUD sobre las entidades principales (fuentes RSS, canales, noticias, diccionario de términos, configuraciones) y funcionalidades especiales (captura manual, purgado, cálculo de sentimiento), documentada mediante Swagger/OpenAPI en `/api/docs` (PDF de especificaciones, sección 10.1, pág. 12).

Restricciones reales del proyecto que condicionan esta decisión:

1. **Plazo académico fijo:** el desarrollo debe completarse dentro del marco temporal del curso, con fecha límite de verificación formal prevista para el 2 de noviembre (P3 ESPEC Y PLANIFICACIÓN.pdf, Paso 3). No hay margen para curvas de aprendizaje extensas sobre un framework desconocido por el equipo.
2. **Motor de base de datos ya fijado:** las instrucciones del proyecto (sección 8) establecen MySQL como motor relacional principal, a diferencia de la sugerencia original del PDF de especificaciones (SQLite para prototipado o MongoDB para escalabilidad, sección 6.2). Esta decisión de MySQL ya adoptada por el equipo condiciona la elección del ORM/driver disponible en cada ecosistema.
3. **Documentación obligatoria vía Swagger/OpenAPI**, generada de forma trazable a partir del propio código o de un contrato OpenSpec (sección 6.2 y 10.1 del PDF; sección 6 de las instrucciones del proyecto).
4. **Requisito de cobertura de pruebas ≥ 80%** verificado en un pipeline de GitHub Actions con dependencias entre jobs (`needs`), de forma que build/despliegue solo ocurran si tests y SonarQube son exitosos (PDF, sección 7 y 4.6.3; instrucciones del proyecto, sección 8 y 14).
5. **Integración con fuentes RSS externas potencialmente inestables** (feeds de medios de comunicación de distintos países, sección 5 del PDF), lo que exige soporte robusto para llamadas HTTP salientes con manejo de timeouts, reintentos acotados y aislamiento de fallos (ver ADR-002).
6. **Herramientas de asistencia de IA ya fijadas:** Visual Studio Code + GitHub Copilot (instrucciones del proyecto, sección 8), lo que favorece frameworks con amplio soporte y ejemplos de entrenamiento (mayor calidad de autocompletado y sugerencias).
7. **Contenerización obligatoria con Docker** (instrucciones del proyecto, sección 8; PDF, sección 4.6.2), por lo que el stack elegido debe empaquetarse limpiamente en una imagen ligera y reproducible.
8. **Perfil del equipo:** estudiantes de últimos años de Ingeniería Civil Informática, con formación previa mixta en lenguajes de backend, sin especialización previa confirmada en un framework específico.
9. **El PDF de especificaciones (sección 6.2) sugiere, sin obligar, dos familias de opciones:** Python (FastAPI, Django) o Node.js (Express). Cualquier elección dentro de este conjunto es coherente con el alcance; el equipo delegó en este agente Product Owner/Arquitecto la elección concreta dentro de dicho conjunto sugerido, quedando pendiente de ratificación formal por el equipo.

## Decisión

Se adopta **Python 3.11+ con el framework FastAPI**, **SQLAlchemy 2.x** como ORM/capa de acceso a datos sobre MySQL, y **Pydantic v2** para la validación de esquemas de entrada/salida.

Componentes concretos de la decisión:

- **Framework web:** FastAPI.
- **ORM:** SQLAlchemy (modo declarativo) + Alembic para migraciones de esquema.
- **Driver MySQL:** `mysqlclient` o `PyMySQL` (a confirmar por el equipo según facilidad de instalación en el entorno Docker elegido).
- **Validación y serialización:** Pydantic v2, integrado nativamente con FastAPI.
- **Documentación API:** generación automática de la especificación OpenAPI 3.x por FastAPI, expuesta en `/api/docs` (Swagger UI) y `/api/redoc`.
- **Cliente HTTP para consumo de feeds RSS:** librería `httpx` (soporta modo asíncrono, necesario para el patrón de resiliencia definido en ADR-002) combinada con `feedparser` para el parseo del formato RSS/Atom.
- **Testing:** `pytest` + `pytest-asyncio` + `pytest-cov` (para el umbral de cobertura ≥80%) + `responses`/`respx` para mockear llamadas HTTP externas (RSS), evitando pruebas unitarias con llamadas reales, conforme a la sección 14 de las instrucciones del proyecto.
- **Empaquetado:** imagen Docker basada en `python:3.11-slim`, con `uvicorn` (ASGI server) como proceso de entrada.

### Justificación técnica

1. **Concurrencia I/O-bound nativa:** el módulo de Captura RSS realiza múltiples llamadas HTTP salientes a feeds externos potencialmente lentos o caídos (PDF, sección 5). FastAPI, construido sobre Starlette/ASGI, ofrece soporte `async`/`await` de primera clase, permitiendo ejecutar la consulta a múltiples fuentes RSS de forma concurrente sin bloquear el hilo principal — una ventaja directa frente a Django (síncrono por defecto, aunque con soporte ASGI parcial) para este caso de uso específico.
2. **Generación automática y trazable de OpenAPI:** FastAPI deriva la especificación OpenAPI directamente de las firmas de las funciones y los modelos Pydantic, reduciendo el riesgo de desincronización entre código y documentación Swagger — requisito explícito de la sección 10.1 del PDF y la sección 6 de las instrucciones del proyecto (contratos OpenSpec).
3. **Validación declarativa con Pydantic:** los criterios de aceptación Gherkin definidos en las historias de usuario (p. ej. HU-RSS-001, HU-RSS-002) exigen validaciones estructurales explícitas (campos obligatorios, formatos de URL, categorías IPTC válidas) que se expresan de forma natural como modelos Pydantic, con generación automática de errores HTTP 400 coherentes con el contrato.
4. **Curva de aprendizaje acotada al plazo académico:** FastAPI tiene una superficie de API reducida comparada con Django (que incluye ORM propio, sistema de administración, sistema de plantillas, etc., de los cuales el proyecto solo necesitaría una fracción). Esto reduce el riesgo de invertir tiempo del curso en funcionalidades del framework no utilizadas.
5. **Ecosistema maduro para testing con mocks**, alineado con el requisito estricto de la sección 14 ("nunca pruebas unitarias con llamadas reales a servicios externos").
6. **Amplio soporte de GitHub Copilot** para Python/FastAPI, dado que es uno de los stacks más representados en los datos de entrenamiento de los asistentes de código, lo que favorece la productividad del equipo al usar Copilot como asistente principal de desarrollo (instrucciones del proyecto, sección 12).

## Alternativas consideradas

### Alternativa A: Python + Django + Django REST Framework (DRF)

**Ventajas:**
- ORM propio maduro, con sistema de migraciones integrado (`makemigrations`/`migrate`).
- Panel de administración autogenerado, útil potencialmente para el "Panel de administración" descrito en la sección 4.3 del PDF.
- DRF genera documentación OpenAPI/Swagger mediante `drf-spectacular` o similar.

**Desventajas (trade-offs concretos frente a la decisión adoptada):**
- Modelo de concurrencia predominantemente síncrono; el soporte async de Django (desde 4.1) es más reciente y menos homogéneo en todo el stack (el ORM de Django solo soporta operaciones async desde versiones recientes y con limitaciones), lo que complica la implementación eficiente del cron de captura concurrente sobre múltiples fuentes RSS (HU-RSS-006).
- Mayor superficie de framework (templates, sistema de administración, middleware de sesiones) que el proyecto no necesita en su mayoría, dado que no se contempla un sistema de autenticación (PDF, sección 3, Limitaciones, punto 3) ni una interfaz basada en templates de servidor (el frontend es SPA, sección 6.2).
- Mayor tiempo de configuración inicial (Sprint 0) para un equipo sin experiencia previa confirmada en Django, en un cronograma con Sprint 0 dedicado a "Configuración del entorno, definición de arquitectura, repositorio, herramientas" (PDF, sección 8.1) ya de por sí ajustado.

**Veredicto:** descartada para este proyecto por la sobrecarga de funcionalidad no utilizada y el soporte async menos maduro, aunque sigue siendo una alternativa técnicamente viable si el equipo tuviera mayor familiaridad previa con Django.

### Alternativa B: Node.js + Express (+ TypeScript)

**Ventajas:**
- Modelo de concurrencia basado en event loop, naturalmente adecuado para I/O concurrente (llamadas RSS), similar en filosofía a la ventaja que ofrece FastAPI con `async`/`await`.
- Ecosistema npm extenso para clientes HTTP (`axios`) y parseo de RSS (`rss-parser`).
- Con TypeScript, aporta tipado estático que reduce errores de contrato entre capas.

**Desventajas (trade-offs concretos frente a la decisión adoptada):**
- Express, a diferencia de FastAPI, no genera documentación OpenAPI de forma nativa: requiere anotación manual o herramientas adicionales (`swagger-jsdoc`, `tsoa`), aumentando el riesgo de desincronización entre código y contrato — riesgo que la sección 6 de las instrucciones del proyecto busca minimizar explícitamente ("mantenlos siempre consistentes entre sí").
- No existe un ORM "por defecto" recomendado junto con Express (a diferencia de SQLAlchemy con FastAPI o el ORM propio de Django); el equipo debería evaluar adicionalmente Sequelize, TypeORM o Prisma para MySQL, añadiendo una decisión de arquitectura más al proyecto.
- Validación de esquemas de entrada/salida requiere una librería adicional (`zod`, `class-validator`, `joi`), sin la integración nativa que ofrece Pydantic + FastAPI.

**Veredicto:** técnicamente viable y con fortalezas de concurrencia comparables a FastAPI, pero requiere más decisiones de arquitectura adicionales (ORM, validación, generación de OpenAPI) para alcanzar el mismo nivel de cohesión "out of the box" que FastAPI ofrece de fábrica, lo cual pesa más en un proyecto con plazo académico fijo.

### Alternativa C: Mantener SQLite/MongoDB como sugiere el PDF (sección 6.2), en lugar de MySQL

No aplica como alternativa dentro de este ADR: las instrucciones del proyecto (sección 8) ya fijan MySQL como motor relacional principal para todo el proyecto, y cualquier motor alternativo requeriría justificación técnica propia y aprobación explícita del equipo, quedando fuera del alcance de esta decisión de stack de backend.

## Consecuencias

**Positivas:**
- Documentación OpenAPI/Swagger generada automáticamente y siempre sincronizada con el código, reduciendo el riesgo de contratos desactualizados frente a los ADRs y contratos OpenSpec ya definidos.
- Soporte async nativo que facilita implementar los patrones de resiliencia (Circuit Breaker, Timeout, Retry acotado) descritos en ADR-002 sin bloquear el servidor durante la consulta a fuentes RSS externas.
- Menor código repetitivo (boilerplate) para CRUD estándar gracias a Pydantic + SQLAlchemy, lo que dejará más tiempo del curso para el algoritmo de análisis de sentimiento y los dashboards.
- Buen soporte de GitHub Copilot, alineado con la sección 12 de las instrucciones del proyecto (el agente da el andamiaje, el equipo desarrolla con Copilot como asistente principal).

**Negativas / riesgos a mitigar:**
- El equipo debe validar que todos sus integrantes tienen o adquieren familiaridad mínima con Python y programación asíncrona (`async`/`await`); si el perfil real del equipo está más orientado a JavaScript/TypeScript, este ADR debería revisarse (ver sección de Gestión de Cambios del proyecto: nueva versión con sufijo `-v2` si se decide pivotar el stack).
- El driver MySQL para Python (`mysqlclient`) puede requerir dependencias de compilación nativas (`libmysqlclient-dev`) en la imagen Docker; se recomienda evaluar `PyMySQL` (puro Python) como alternativa más simple de contenerizar si surgen problemas de build.
- Alembic (migraciones) añade una herramienta adicional a aprender por el equipo de DevOps/Backend, distinta del sistema de migraciones que tendría Django "de fábrica".

**Impacto en otros entregables:**
- Todo el código base/esqueleto generado a partir de este ADR (routers, modelos, esquemas) asumirá FastAPI + SQLAlchemy + Pydantic. Si el equipo revierte esta decisión, deberá regenerarse el scaffolding correspondiente.
- El contrato OpenSpec (YAML) de los endpoints `/channels` y `/sources` es agnóstico de framework y no requiere cambios si el stack se revisa posteriormente.

## Historias de usuario relacionadas

- HU-RSS-001, HU-RSS-002, HU-RSS-003, HU-RSS-004, HU-RSS-005, HU-RSS-010 (CRUD y consulta de canales/fuentes, implementadas como routers FastAPI).
- HU-RSS-006 (cron de captura, se beneficia directamente de la concurrencia async de FastAPI/httpx).
- HU-RSS-007 (configuración, expuesta como router FastAPI adicional).
- HU-RSS-008 (captura manual, reutiliza el mismo cliente HTTP asíncrono que HU-RSS-006).
- HU-RSS-009 (script de seed, implementado como script Python independiente que usa el mismo ORM SQLAlchemy).

---

## Historial de revisión de este ADR

| Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|
| v1 | 2026-08-14 | Creación inicial — decisión delegada por el equipo al agente Product Owner/Arquitecto dentro del conjunto de opciones sugeridas por el PDF (sección 6.2). Pendiente de ratificación formal por el equipo. |
| v1.1 | 2026-08-19 | Estado actualizado de "Propuesto" a "Aceptado" — el equipo confirmó proceder con esta decisión al iniciar el scaffolding de código de Sprint 1 (EPIC-RSS). Sin cambios de contenido técnico. |
| v1.2 | 2026-08-26 | Se agrega HU-RSS-010 (consulta y listado de canales) a la lista de historias relacionadas, tras su formalización en `HU-RSS-captura.md`. Sin cambios en la Decisión ni en las Alternativas. |
