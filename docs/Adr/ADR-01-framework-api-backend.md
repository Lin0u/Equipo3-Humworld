# ADR-0001: Framework de la API backend

- Estado: Aceptado
- Fecha: 2026-08-19
- Responsables: Equipo 3 (HumWorld)
- Relacionado con: PDF de especificaciones, sección 6.2 (framework sugerido); instrucciones del proyecto, secciones 6, 7, 8, 12 y 14; HU-RSS-001 a HU-RSS-010

## Problema, elemento de arquitectura sobre el que decidir

El sistema requiere una API REST con documentación OpenAPI/Swagger trazable, cobertura de pruebas ≥80% mockeando llamadas externas, y consumo concurrente de múltiples fuentes RSS externas potencialmente lentas o inestables. El equipo debe elegir el framework web de backend dentro del plazo fijo del curso (verificación formal el 2 de noviembre), usando MySQL como motor relacional ya impuesto por las instrucciones del proyecto. El PDF sugiere, sin obligar, dos familias: Python (FastAPI o Django) o Node.js (Express).

## Opciones consideradas

### Opción A: FastAPI (Python)
Framework ASGI con soporte async/await de primera clase, generación automática de OpenAPI a partir de tipado y modelos Pydantic, y superficie de API reducida.

### Opción B: Django + Django REST Framework
Framework Python maduro, con ORM y sistema de administración propios; soporte async más reciente y menos homogéneo en todo el stack, incluido el ORM.

### Opción C: Node.js + Express (+TypeScript)
Modelo de concurrencia por event loop; no genera OpenAPI de forma nativa y no trae ORM ni validación de esquemas por defecto, requiriendo herramientas adicionales.

## Matriz de decisión

FastAPI y Express ofrecen concurrencia I/O-bound comparable, adecuada para consultar muchas fuentes RSS en paralelo; Django es predominantemente síncrono y complicaría ese patrón. Frente a Express, FastAPI genera OpenAPI de forma nativa y sincronizada con el código (Express lo requiere manualmente), y trae validación de esquemas integrada vía Pydantic (Express necesita una librería aparte). Frente a Django, FastAPI tiene menor superficie de framework, evitando invertir tiempo de curso en funcionalidad no usada (templates, panel de administración), y no complica la concurrencia async requerida por el módulo de captura.

## Decisión

Se adopta FastAPI como framework de la API REST del backend.

## Por qué se elige frente a las demás

FastAPI es la única opción que cubre de forma nativa y cohesionada los tres requisitos más costosos de resolver por separado: concurrencia async para el módulo de captura RSS, generación automática de OpenAPI siempre sincronizada con el código, y validación declarativa de esquemas de entrada/salida. Express exigiría sumar y coordinar herramientas adicionales para lograr lo mismo, y Django introduciría funcionalidad no utilizada además de un soporte async menos maduro. El equipo cuenta además con GitHub Copilot como asistente principal, con buen soporte documentado para Python/FastAPI.

## Consecuencias

### Positivas
Documentación OpenAPI siempre sincronizada con el código; soporte async nativo para los patrones de resiliencia del módulo de captura (ver ADR-0004); menor código repetitivo en los endpoints CRUD.

### Negativas y deuda aceptada
El equipo debe tener o adquirir familiaridad con Python y programación asíncrona; si el perfil real del equipo resultara más orientado a JavaScript/TypeScript, este ADR debería revisarse. La elección de framework determina en cascada herramientas del ecosistema (ORM, validación, cliente HTTP, testing), que no se documentan como decisiones arquitectónicas independientes por ser consecuencia directa de esta elección y no tener alternativas realmente comparadas.

## Trazabilidad y sincronización

docs/architecture.md (estilo del backend); openspec/config.yaml; scaffolding de routers, modelos y esquemas de HU-RSS-001 a HU-RSS-010.
