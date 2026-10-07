## 1. Servicio de cálculo por diccionario

- [ ] 1.1 Reutilizar el servicio determinista de HU-SENT-007 para calcular humor durante el flujo de captura; verificar promedio de términos únicos, cero coincidencias y tratamiento de idioma desconocido con mocks/fixtures deterministas.
- [ ] 1.2 Añadir un servicio de orquestación independiente de FastAPI que seleccione diccionario mientras HU-SENT-006 no provea modelo activo, registre `metodo_calculo` y aisle fallos del análisis; verificar que el fallo no revierte la `Noticia` capturada.
- [ ] 1.3 Definir el punto de extensión/adaptador ML con timeout configurable y fallback; verificar con mocks éxito, error y timeout, sin proveedor real ni catálogo/versionado de HU-SENT-006.

## 2. Persistencia y repositorios

- [ ] 2.1 Añadir a `Noticia` los campos mínimos `metodo_calculo` y `cantidad_terminos_evaluados`; verificar round-trip SQLite y conservar `valor_humor=NULL` para cero coincidencias.
- [ ] 2.2 Crear migración Alembic para los campos permitidos por HU-SENT-002-v2, excluyendo `polarizacion_terminos` y tabla de modelos; verificar SQL MySQL offline y orden de migraciones.
- [ ] 2.3 Añadir/reutilizar consultas de Repositorio para persistir resultado y leer noticias pendientes; verificar consultas y que no haya SQL en Servicios ni routers.

## 3. Integración de captura y barrido

- [ ] 3.1 Invocar cálculo síncrono después de persistir cada noticia en `captura_service.py`; verificar captura exitosa con método registrado y que fallo de sentimiento no deshace la noticia RSS.
- [ ] 3.2 Registrar el job de reparación en APScheduler con periodicidad configurable (propuesta 30 minutos, aún no ratificada); verificar registro, ejecución sobre noticias `valor_humor IS NULL` y aislamiento de fallos por noticia.
- [ ] 3.3 Añadir settings configurables para timeout propuesto de 3 segundos y periodicidad del barrido, evitando tratar los valores propuestos como decisiones definitivas; verificar overrides de configuración.

## 4. Pruebas y calidad

- [ ] 4.1 Añadir pruebas unitarias con servicio ML mockeado para ausencia de modelo, éxito futuro, error y timeout; verificar fallback a diccionario, método/versión solo cuando el contrato ML exista y ausencia de llamadas reales a Google.
- [ ] 4.2 Añadir pruebas de integración captura→cálculo→persistencia y barrido con SQLite; verificar idioma es/en, idioma desconocido consulta ambos, `metodo_calculo`, cantidad evaluada y preservación de noticias ante fallos.
- [ ] 4.3 Ejecutar `pytest` y `pytest-cov`; verificar suite completa y cobertura mínima del 80% sin dependencias externas reales ni carga de modelo.
- [ ] 4.4 Revisar conformidad con `docs/architecture.md`, `openspec/config.yaml`, `.github/copilot-instructions.md`, ADR-03 y ADR-04; verificar separación de capas, ausencia de endpoints/colas y que no se implementan HU-SENT-003/006/007 fuera de las dependencias autorizadas.