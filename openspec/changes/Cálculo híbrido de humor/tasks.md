## 1. Servicio de cálculo por diccionario

- [x] 1.1 Reutilizar el servicio determinista de HU-SENT-007 para calcular humor durante el flujo de captura; verificar promedio de términos únicos, cero coincidencias y tratamiento de idioma desconocido con mocks/fixtures deterministas.
- [x] 1.2 Añadir un servicio de orquestación independiente de FastAPI que seleccione diccionario mientras HU-SENT-006 no provea modelo activo, registre `metodo_calculo` y aisle fallos del análisis; verificar que el fallo no revierte la `Noticia` capturada.
- [x] 1.3 Definir el punto de extensión/adaptador ML con timeout configurable y fallback; verificar con mocks éxito, error y timeout, sin proveedor real ni catálogo/versionado de HU-SENT-006.

## 2. Persistencia y repositorios

- [x] 2.1 Añadir a `Noticia` los campos mínimos `metodo_calculo` y `cantidad_terminos_evaluados`; verificar round-trip SQLite y conservar `valor_humor=NULL` para cero coincidencias.
- [x] 2.2 Crear migración Alembic para los campos permitidos por HU-SENT-002-v2, excluyendo `polarizacion_terminos` y tabla de modelos; verificar SQL MySQL offline y orden de migraciones.
- [x] 2.3 Añadir/reutilizar consultas de Repositorio para persistir resultado y leer noticias pendientes; verificar consultas y que no haya SQL en Servicios ni routers.

## 3. Integración de captura y barrido

- [x] 3.1 Invocar cálculo síncrono después de persistir cada noticia en `captura_service.py`; verificar captura exitosa con método registrado y que fallo de sentimiento no deshace la noticia RSS.
- [x] 3.2 Registrar el job de reparación en APScheduler con periodicidad configurable (propuesta 30 minutos, aún no ratificada); verificar registro, ejecución sobre noticias `valor_humor IS NULL` y aislamiento de fallos por noticia.
- [x] 3.3 Añadir settings configurables para timeout propuesto de 3 segundos y periodicidad del barrido, evitando tratar los valores propuestos como decisiones definitivas; verificar overrides de configuración.

## 4. Pruebas y calidad

- [x] 4.1 Añadir pruebas unitarias con servicio ML mockeado para ausencia de modelo, éxito futuro, error y timeout; verificar fallback a diccionario, método/versión solo cuando el contrato ML exista y ausencia de llamadas reales a Google.
- [x] 4.2 Añadir pruebas de integración captura→cálculo→persistencia y barrido con SQLite; verificar idioma es/en, idioma desconocido consulta ambos, `metodo_calculo`, cantidad evaluada y preservación de noticias ante fallos.
- [x] 4.3 Ejecutar `pytest` y `pytest-cov`; verificar suite completa y cobertura mínima del 80% sin dependencias externas reales ni carga de modelo.
- [ ] 4.4 Revisar conformidad con `docs/architecture.md`, `openspec/config.yaml`, `.github/copilot-instructions.md`, ADR-003 y ADR-004; verificar separación de capas, ausencia de endpoints/colas y que no se implementan HU-SENT-003/006/007 fuera de las dependencias autorizadas.

## Notas de implementación (2026-10-18)

- Marca de pendiente del barrido: `metodo_calculo IS NULL`, no `valor_humor IS NULL`, para no reprocesar en cada barrido las noticias con 0 coincidencias (riesgo ya señalado en design.md). Decisión de equipo del 2026-10-18; spec.md actualizado.
- Recálculo tras cambios del diccionario: cada alta, modificación o baja de un término marca como pendientes las noticias calculadas con diccionario (no las de ML) y el barrido las recalcula. Decisión de equipo del 2026-10-18; spec.md actualizado. Cierra el punto pendiente 2 de HU-SENT-008.
- Coincidencia de términos (decisión de equipo del 2026-10-18; HU-SENT-007 no la fijaba): palabra o frase completa; sin distinguir mayúsculas ni tildes, conservando la ñ; sin lematización (singular y plural se cargan como términos distintos); se quita el HTML del resumen. spec.md actualizado.
- El barrido corre 1 minuto después de arrancar la API y luego cada `SENTIMIENTO_BARRIDO_MINUTOS` (propuesto: 30).
- La 4.4 (revisión de conformidad) queda para la revisión del PR.
