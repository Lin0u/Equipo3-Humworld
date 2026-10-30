# Checklist del entregable `EQUIPO_HUMWORLD.tgz`

**Proyecto:** HumWorld — Equipo 3
**Propósito:** preparar y verificar el contenido del entregable único exigido por §9 de la especificación: un fichero comprimido `EQUIPO_HUMWORLD.tgz` a subir a Canvas. El `.tgz` se genera **al final**, cuando todo esté en `main`; esta checklist y el acceso del profesor pueden prepararse desde ya.

**Cómo usar esta checklist:** cada ítem referencia la ruta real en el repositorio. Marca la casilla cuando esté confirmado. Los ítems marcados "pendiente del equipo" requieren una acción fuera del alcance del rol de Documentación.

---

## 1. Contenido obligatorio del `.tgz` (§9)

### Código fuente completo
- [ ] Backend (FastAPI): `src/` — `app/` (routers, services, repositories, models, schemas, core, jobs), `scripts/`, `tests/`, `requirements.txt`, `requirements.lock`.
- [ ] Migraciones de base de datos: `alembic/` y `alembic.ini`.
- [ ] Frontend (React + Vite): `frontend/` — `src/`, `package.json`, `package-lock.json`, `vite.config.js`.

### Documentación en `/docs`
- [ ] Lista formal de requisitos: `docs/Backlog/Requisitos.md`.
- [ ] Backlog de historias de usuario: `docs/Backlog/` (HU-RSS, HU-SENT, HU-DASH, HU-ADMIN y datasets).
- [ ] Decisiones de arquitectura (ADR): `docs/Adr/ADR-001` a `ADR-005`.
- [ ] Documentación UML: `docs/UML/` (casos de uso, clases, componentes).
- [ ] Documento de arquitectura: `docs/architecture.md`.
- [ ] Planificación y sprints: `docs/Planificación/` (entregables de P3 + `Sprints-ejecutados.md`).
- [ ] Plan de pruebas: `docs/Testing/`.
- [ ] Guías de OpenSpec: `docs/Guias/`.


### Ficheros de contexto de IA (§4.7 punto 5)
- [ ] `docs/IA/README.md` (qué herramienta se usó para qué).
- [ ] `docs/IA/claude-project-instructions.md` (prompt del Proyecto Claude PO/Arquitecto).
- [ ] `docs/IA/gem-mentor-humworld.md` (prompt del Gem "Mentor HumWorld").
- [ ] `.github/copilot-instructions.md` (instrucciones de Copilot).
- [ ] Instrucciones y prompts de OpenSpec: `openspec/copilot-instructions.md`, `.github/prompts/`, `.github/skills/`.

### Documentación OpenSpec (contratos y especificaciones)
- [ ] Contratos OpenAPI: `docs/Contratos/` (canales-fuentes-rss, sentimiento-diccionario, dashboards, noticias).
- [ ] Cambios OpenSpec: `openspec/changes/` (proposals, specs, designs, tasks por cambio).
- [ ] Configuración OpenSpec: `openspec/config.yaml`.

### Ficheros de configuración (Docker, CI/CD)
- [ ] Docker: `Dockerfile`, `docker-compose.yml`.
- [ ] CI/CD: `.github/workflows/ci.yml`.
- [ ] Calidad de código: `sonar-project.properties`, `src/.coveragerc`.
- [ ] Variables de entorno de ejemplo: `src/.env.example`.

### Instrucciones de despliegue
- [ ] README principal con los pasos de puesta en marcha: `README.md`.

---

## 2. Verificaciones previas a generar el `.tgz`

- [ ] Todo el trabajo está integrado en la rama `main`.
- [ ] El pipeline de CI (`.github/workflows/ci.yml`) está en verde en el último commit de `main` (jobs `test`, `test-frontend`, `sonarqube`, `build-and-deploy`).
- [ ] El README principal se puede seguir al pie de la letra en una máquina limpia. **Pendiente del equipo:** validación real en un equipo limpio.
- [ ] No se incluyen secretos reales en el `.tgz` (revisar que no haya `.env` con claves; `src/.env.example` sí debe incluirse, con valores de ejemplo).
- [ ] No se incluyen artefactos locales innecesarios (p. ej. `src/venv/`, `src/.coverage`, `src/.pytest_cache/`, `node_modules/`, `__pycache__/`). Verificar contra `.gitignore`.

---

## 3. Acceso del profesor al repositorio (§9)

- [ ] Dar acceso al profesor al repositorio de GitHub (`Settings → Collaborators`). **Pendiente del equipo** (acción administrativa sobre GitHub, fuera del alcance de Documentación).

---

## 4. Generación del comprimido

- [ ] Generar `EQUIPO_HUMWORLD.tgz` desde la raíz del repositorio con todo en `main`. **Se hace al final.** Sugerencia de comando (a ejecutar por el rol correspondiente, excluyendo artefactos locales):

```bash
tar --exclude='.git' --exclude='**/node_modules' --exclude='**/__pycache__' \
    --exclude='src/venv' --exclude='src/.pytest_cache' --exclude='src/.coverage' \
    -czf EQUIPO_HUMWORLD.tgz .
```

- [ ] Subir `EQUIPO_HUMWORLD.tgz` a la plataforma Canvas de la Universidad.

---

## Notas de alcance (rol Documentación)

- Esta checklist es un documento de verificación; no genera el `.tgz` ni modifica configuración del repositorio.
- Los ítems "pendiente del equipo" (acceso del profesor, validación en máquina limpia, verde final del CI, generación y subida del `.tgz`) corresponden a otros roles (Líder, DevOps, Calidad).

---

## Tabla de control de versiones

| Versión | Fecha | Motivo del cambio |
|---|---|---|
| v1.0 | 2026-10-29 | Creación. Checklist del entregable `EQUIPO_HUMWORLD.tgz` según §9, con ítems referenciando rutas reales del repositorio, verificaciones previas, acceso del profesor y pasos de generación/subida. |
