## 1. Modelo y migración

- [ ] 1.0 Verificar que ya existe la migración de HU-SENT-002-v2 que crea `metodo_calculo` y `cantidad_terminos_evaluados` (decisión de equipo del 2026-10-18); no iniciar este cambio antes.
- [ ] 1.1 Extender `src/app/models/noticia.py` con `polarizacion_terminos` nullable de tipo Float; verificar la definición ORM. `metodo_calculo` ya lo agrega HU-SENT-002-v2 y no se redefine.
- [ ] 1.2 Crear migración Alembic solo para `polarizacion_terminos`, con `down_revision` igual a la revisión de HU-SENT-002-v2; verificar `alembic upgrade head --sql`, orden de migración y un downgrade que retire solo esa columna.
- [ ] 1.3 Actualizar `docs/UML/diagrama-clases.md` con los nuevos atributos de `Noticia`; verificar que el diagrama refleja modelo, nullabilidad y tipo persistido.

## 2. Repositorio y persistencia

- [ ] 2.1 Añadir o ajustar métodos en `src/app/repositories/noticias.py` para persistir/leer valor, polarización y método en una transacción; verificar rollback conjunto de los campos con SQLite.
- [ ] 2.2 Verificar persistencia round-trip para `valor_humor=-1.0`, `polarizacion_terminos=7.0` y ambos métodos (`diccionario`, `ml`); comprobar conservación de precisión.
- [ ] 2.3 Verificar el caso sin términos: `valor_humor=NULL`, `polarizacion_terminos=NULL`, `metodo_calculo=diccionario`; distinguirlo del caso neutral con `valor_humor=0.0`.

## 3. Pruebas y calidad

- [ ] 3.1 Añadir pruebas unitarias con SQLite para round-trip, valores float, nulos, neutral evaluado, métodos válidos y rollback ante fallo de persistencia.
- [ ] 3.2 Ejecutar `pytest` y `pytest-cov`; verificar toda la suite y cobertura mínima del 80% sin llamadas HTTP externas.
- [ ] 3.3 Revisar conformidad con `docs/architecture.md`, `openspec/config.yaml` y `.github/copilot-instructions.md`; verificar separación API/Servicios/Repositorios/Persistencia, ausencia de endpoints y que el cambio no implementa HU-SENT-002-v2/004-007 fuera de la persistencia requerida.