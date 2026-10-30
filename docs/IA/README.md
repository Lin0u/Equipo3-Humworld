# Ficheros de contexto de IA — HumWorld

Este directorio reúne los ficheros de contexto y prompts de las herramientas de IA que el equipo usó en el proyecto, como exige la especificación (§4.7 punto 5: "Ficheros de contexto y prompts principales utilizados como herramientas de IA (OpenSpec, Copilot, Claude)").

El objetivo de HumWorld es, además de construir la aplicación, hacer un desarrollo asistido por IA que sea **explicable y reproducible** (§2, objetivo específico 5). Por eso se conserva el contexto con el que se configuró cada herramienta.

## Qué herramienta se usó para qué

| Herramienta | Para qué se usó | Contexto / prompt |
|---|---|---|
| **Claude (Proyecto "PO y Arquitecto")** | Generar y mantener los entregables de producto y diseño: historias de usuario, ADRs, contratos de API y scaffolding inicial, consistentes con la especificación. | [`claude-project-instructions.md`](./claude-project-instructions.md) |
| **Gemini (Gem "Mentor HumWorld")** | Resolver dudas teóricas de la asignatura (conceptos, metodología, UML). No genera entregables del proyecto. | [`gem-mentor-humworld.md`](./gem-mentor-humworld.md) |
| **GitHub Copilot** | Asistente principal de desarrollo de código dentro de VS Code, siguiendo las reglas de arquitectura del proyecto. | [`../../.github/copilot-instructions.md`](../../.github/copilot-instructions.md) |
| **OpenSpec** | Metodología de desarrollo dirigido por especificación (SDD): contratos y especificaciones de cada cambio. | [`../../openspec/`](../../openspec/) (y sus instrucciones en [`../../openspec/copilot-instructions.md`](../../openspec/copilot-instructions.md)) |

## Separación de responsabilidades entre los agentes

- **Claude** produce entregables (historias, ADRs, contratos, scaffolding). No resuelve dudas teóricas.
- **El Gem** resuelve dudas teóricas de la asignatura. No produce entregables del proyecto.
- **Copilot** genera código dentro del IDE, apoyándose en los contratos y las reglas de arquitectura ya definidas.
- **OpenSpec** estructura cada cambio en `proposal.md`, `spec.md`, `design.md` y `tasks.md` antes de implementar.

## Ubicación de los contextos ya existentes en el repositorio

Las instrucciones de Copilot y OpenSpec ya viven en sus ubicaciones propias dentro del repositorio y no se duplican aquí:

- Copilot: `.github/copilot-instructions.md`
- OpenSpec: `openspec/` (configuración en `openspec/config.yaml`, instrucciones en `openspec/copilot-instructions.md`, cambios en `openspec/changes/`).

Este directorio (`docs/IA/`) añade los contextos que no estaban versionados en el repositorio: los prompts de configuración de Claude y del Gem, exportados desde sus plataformas respectivas (claude.ai y Google Gemini).

---

## Tabla de control de versiones

| Versión | Fecha | Motivo del cambio |
|---|---|---|
| v1.0 | 2026-10-29 | Creación. Se incorporan los prompts de configuración de Claude (PO/Arquitecto, v1.1) y del Gem "Mentor HumWorld", y un README que explica qué herramienta de IA se usó para qué, con enlaces a los contextos de Copilot y OpenSpec ya presentes en el repositorio. Entregable de §4.7 punto 5. |
