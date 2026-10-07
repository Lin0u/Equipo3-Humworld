# Guía de ejecución — Práctica P5 OpenSpec (Specification-Driven Development) aplicada a HumWorld

**Proyecto:** HumWorld — Equipo 3
**Práctica de referencia:** `P5 - OPENSPEC / Specification-Driven Development` (continuación de P4 — La Fábrica de Software)
**Historia de usuario elegida como caso piloto:** HU-RSS-001 — Alta de Canal de Noticias
**Fecha/sesión:** 2026-08-21
**Objetivo de este documento:** traducir paso a paso las instrucciones genéricas de la práctica P5 (que usa el proyecto de ejemplo "AGENDA" y la historia "HU-01 Registrar persona") al contexto real de HumWorld, para que el equipo pueda ejecutarla directamente en su repositorio.

> **Importante — qué es y qué no es este documento.** Esta práctica requiere trabajo en el entorno local del equipo: instalar Node.js/OpenSpec, ejecutar comandos en la terminal de VS Code y conversar con GitHub Copilot Chat dentro del repositorio real de HumWorld. Eso solo se puede ejecutar en las máquinas del equipo. Este documento no reemplaza esos pasos — les da el prompt exacto, los nombres de comando y los criterios de revisión ya adaptados a HumWorld, para que no tengan que traducir "AGENDA / HU-01 Registrar persona" a HumWorld mientras están en clase.

---

## 0. Por qué HU-RSS-001 es el caso piloto correcto

Según `PLANIFICACION-AGIL-HUMWORLD-ENTREGADO-P3.md`, el Sprint 1 ("Captura de noticias") va del **24-ago-26 al 06-sep-26** e incluye exactamente HU-RSS-001 a HU-RSS-005. Hoy es 21-ago-26: el Sprint 1 arranca en tres días. HU-RSS-001 es además la primera historia de esa lista y ya tiene criterios de aceptación Gherkin completos y aprobados en `HU-RSS-captura.md`, por lo que es el equivalente natural de "HU-01 Registrar persona" del documento de la práctica: una historia acotada, ya revisada, ideal para la primera pasada completa por el flujo Historia → Especificación → Diseño → Tareas → Implementación.

---

## 1. Preparar el entorno (idéntico al documento, sección 4)

Estos pasos son los mismos que en el documento P5, ejecutados sobre el repositorio real de HumWorld en lugar de "AGENDA":

1. Abrir el repositorio de HumWorld en VS Code y confirmar que se está en `main` (o en la rama de trabajo que use el equipo):
   ```
   git status
   ```
2. Comprobar si Node.js y npm ya están instalados:
   ```
   node --version
   npm --version
   ```
   Si dan error, instalar la versión **LTS** desde https://nodejs.org/es/download, asegurándose de habilitar la incorporación al PATH, y reabrir VS Code.
3. Instalar OpenSpec y comprobar la instalación:
   ```
   openspec --version
   ```

## 2. Inicializar OpenSpec en el repositorio HumWorld (sección 4.4 del documento)

1. Confirmar que se está en la raíz del repositorio de HumWorld (no en una subcarpeta del backend):
   ```
   git status
   ```
2. Ejecutar:
   ```
   openspec init
   ```
3. En el asistente interactivo, **seleccionar solo GitHub Copilot** como asistente de IA a instalar (igual que indica el documento).
4. Antes de generar nada más, inspeccionar qué creó OpenSpec:
   ```
   git status
   ```
   Identificar en el explorador de VS Code: qué carpetas creó OpenSpec, qué ficheros de configuración aparecen, cuáles están relacionados con Copilot, y cuáles deben quedar versionados en Git (todo lo que no sea configuración local/sensible debe ir a Git, siguiendo el mismo criterio que en P4).

No generar código todavía en este punto.

## 3. Analizar HU-RSS-001 con GitHub Copilot Chat

Localizar en GitHub la Issue **HU-RSS-001 — Alta de Canal de Noticias** (o crearla si el equipo aún no la ha subido desde `HU-RSS-captura.md`) y abrir GitHub Copilot Chat en VS Code.

Igual que indica el documento, en esta fase la IA se usa para **analizar y afinar la especificación, no para generar código todavía**. Evitar prompts como "programa el CRUD de canales" o "crea el endpoint de canales".

### Prompt sugerido para Copilot Chat (adaptado a HumWorld)

Copiar y pegar tal cual en el chat:

```
Estamos desarrollando la aplicación HumWorld, un sistema que analiza noticias
en tiempo real capturadas vía RSS para calcular el "estado de ánimo" del
mundo mediante análisis de sentimiento.

Queremos implementar la historia de usuario HU-RSS-001 — Alta de Canal de
Noticias:

Como administrador del sistema, quiero dar de alta un canal de noticias
(medio de comunicación), para poder agrupar bajo él las fuentes RSS que se
van a capturar.

Depende del contrato de API POST /api/v1/channels.

Criterios de aceptación ya acordados por el equipo:
- Alta exitosa: si "nombre" y "continente" son válidos y no vacíos, el
  sistema responde 201, crea exactamente 1 registro y devuelve el
  identificador único generado.
- Rechazo por datos obligatorios faltantes: si "nombre" está vacío o
  ausente, el sistema responde 400 y no crea ningún registro.
- Rechazo por nombre de canal duplicado: si ya existe un canal con el mismo
  "nombre", el sistema responde 409.

Contexto adicional del modelo de datos (ya decidido en ADR-002, relación de
composición CanalNoticias -> FuenteRSS): un canal tiene id, nombre,
continente, pais (opcional) y descripcion (opcional). El motor de
persistencia es MySQL.

Quiero utilizar OpenSpec y trabajar siguiendo Specification-Driven
Development.

Analiza la funcionalidad.
Identifica ambigüedades, restricciones y decisiones que deberíamos resolver
en la especificación.
No escribas todavía código.
```

### Ambigüedades esperables a discutir en equipo

Antes de correr el prompt, o al contrastar la respuesta de Copilot, el equipo debería tener claro que **al menos estos puntos siguen abiertos** en la documentación actual del proyecto (no están inventados aquí; son vacíos reales de `HU-RSS-captura.md` y `ADR-002`):

1. **Formato y validación de "nombre" y "continente".** ¿Longitud máxima de "nombre"? ¿"continente" es una lista cerrada (enum de continentes) o texto libre? El ADR-002 no lo fija.
2. **Campos opcionales del modelo (`pais`, `descripcion`).** Están en el modelo de datos de ADR-002 pero no aparecen en los criterios de aceptación de HU-RSS-001: ¿deben poder enviarse en el `POST /api/v1/channels` desde ya, o quedan para una historia posterior?
3. **Criterio exacto de duplicado.** ¿La comparación de "nombre" es exacta, insensible a mayúsculas/minúsculas, o normalizada (espacios, tildes)? No está especificado.
4. **Eliminación/edición de canal.** El backlog actual (HU-RSS-001 a 009) no incluye una historia de modificación o baja de `CanalNoticias` (sí existe para `FuenteRSS`, en HU-RSS-004 y HU-RSS-005). Confirmar si es un vacío intencional para Sprint 1 o si falta agregarla al backlog.

Para cada ambigüedad: identificar el aspecto no definido → revisar la propuesta de Copilot → decidir en equipo → si la decisión cambia el comportamiento esperado, actualizar los criterios Gherkin de la Issue HU-RSS-001 (y avisar para reflejarlo también en `HU-RSS-captura.md`); si es un detalle técnico, se incorpora directamente en la especificación de OpenSpec.

## 4. Crear el primer cambio con OpenSpec

En el chat de Copilot, generar la instrucción OpenSpec:

```
/opsx:propose alta-canal-noticias
```

Seguida del detalle del cambio (siguiendo la convención de nombres del documento — sustantivo, sin verbos, kebab-case, coherente con el recurso `/api/v1/channels`):

```
Implementar la historia de usuario HU-RSS-001 de HumWorld.

Como administrador del sistema quiero dar de alta un canal de noticias
(nombre, continente, y opcionalmente pais y descripcion) para poder agrupar
bajo él las fuentes RSS que se van a capturar.

Criterios acordados:
- nombre y continente son obligatorios;
- pais y descripcion son opcionales;
- el nombre del canal debe ser único (rechazo con 409 en caso de
  duplicado);
- cada canal tendrá un identificador único generado por el sistema.

No implementar todavía código. Preparar únicamente la especificación, el
diseño y las tareas necesarias.
```

Esto debería generar la estructura:
```
openspec/
└── changes/
    └── alta-canal-noticias/
        ├── proposal.md
        ├── specs/
        │   └── ...
        │       └── spec.md
        ├── design.md
        └── tasks.md
```

## 5. Revisar la propuesta antes de programar (no saltarse este paso)

El flujo correcto es **ESPECIFICAR → REVISAR → IMPLEMENTAR**, nunca "prompt → código" directo. Revisar especialmente:

| Artefacto | Qué comprobar en el caso de HU-RSS-001 |
|---|---|
| `proposal.md` | Que el "por qué" del cambio referencie HU-RSS-001 y el endpoint `POST /api/v1/channels`. |
| `spec.md` | Que los escenarios cubran, como mínimo, los tres ya acordados (alta exitosa, datos obligatorios faltantes, nombre duplicado) — incorporar al menos dos casos adicionales, cubriendo por ejemplo los campos opcionales (`pais`, `descripcion`) y el criterio de duplicado que se haya decidido en el paso 3. |
| `design.md` | Que sea coherente con el modelo de datos ya decidido en ADR-002 (entidad `CanalNoticias`, MySQL, capa de servicio separada del router FastAPI) y no contradiga la relación de composición `CanalNoticias → FuenteRSS`. |
| `tasks.md` | Que las tareas respeten la separación de capas de ADR-002 (presentación/API, lógica de negocio, datos) y que no incluyan la implementación de HU-RSS-002 en adelante (alcance limitado a HU-RSS-001). |

Si algo en `design.md` o `spec.md` se aparta de lo ya decidido en `ADR-002-arquitectura-captura-rss.md` o de los criterios ya aprobados en `HU-RSS-captura.md`, es una señal de alucinación de la IA o de un vacío real de especificación — no aceptar automáticamente, discutir en equipo (ver Anexo 8.2 del documento original: "Aceptar automáticamente la especificación propuesta por la IA" está listado explícitamente como error frecuente a evitar).

## 6. Trazabilidad con GitHub

Volver a la Issue **HU-RSS-001** y añadir un comentario:

```
Esta historia está siendo desarrollada mediante SDD utilizando OpenSpec.

Cambio OpenSpec: alta-canal-noticias
```

Cadena de trazabilidad resultante:
```
Issue GitHub (HU-RSS-001)
        ↓
Historia de Usuario (HU-RSS-captura.md)
        ↓
Cambio OpenSpec (alta-canal-noticias)
        ↓
Especificación (spec.md)
        ↓
Tareas (tasks.md)
        ↓
Código
```

## 7. Acciones de finalización

1. Confirmar los cambios en Git:
   ```
   git status
   git diff
   git add .
   git commit -m "configura HumWorld con OpenSpec para desarrollo SDD (HU-RSS-001)"
   git push
   ```
2. Verificar en GitHub que los nuevos artefactos (`openspec/`, `changes/alta-canal-noticias/...`) aparecen en el repositorio.
3. En GitHub → Actions, comprobar:
   - Ejecución correcta del pipeline `CI.yml` ya existente (de P4).
   - Ejecución correcta de cualquier pipeline adicional generado por OpenSpec.

## 8. Errores frecuentes a evitar (Anexo 8.2 del documento original)

- Instalar OpenSpec y no inicializarlo dentro del repositorio de HumWorld.
- Ejecutar `openspec init` fuera de la raíz del repositorio.
- Pedirle directamente a Copilot que genere el CRUD de canales sin pasar por `spec.md`.
- Aceptar automáticamente la especificación propuesta por la IA sin discutirla en equipo.
- Confundir la historia de usuario (`HU-RSS-captura.md`) con la especificación (`spec.md` de OpenSpec) — son artefactos distintos y complementarios.
- Crear una especificación sin escenarios verificables (sin cifras/umbrales concretos).
- Modificar la especificación pero no dejarla versionada en Git.
- Generar código antes de que el equipo haya revisado la especificación.

## 9. Pregunta de cierre del documento original (para reflexión de equipo, no respondida aquí)

> "¿Qué enfoque proporciona mayor control al equipo y por qué?" — comparando el flujo directo Prompt → Código frente al flujo Especificar → Revisar → Implementar con OpenSpec.

Esta es una pregunta de reflexión pedida explícitamente por el documento de la práctica para que la responda el equipo tras ejecutar el flujo, no una decisión de arquitectura que corresponda fijar aquí de antemano.

---

## Próximo paso sugerido

Una vez el equipo ejecute `/opsx:propose alta-canal-noticias` y revise los artefactos generados, puedo ayudarles a: (a) contrastar `spec.md`/`design.md` generados contra `ADR-002` y `HU-RSS-captura.md` para detectar inconsistencias, y (b) si el equipo lo pide explícitamente, generar el scaffolding inicial del endpoint (`POST /api/v1/channels`) sin lógica de negocio, según la sección 12 de las instrucciones del proyecto.
