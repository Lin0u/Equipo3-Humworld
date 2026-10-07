## 1. Contrato y persistencia

- [ ] 1.1 Confirmar el esquema actual y añadir el modelo de configuración y la migración Alembic necesarios para `periodicidad_cron_minutos`; verificar con una prueba de persistencia SQLite/MySQL.
- [ ] 1.2 Implementar el repositorio para consultar, insertar y actualizar la configuración con transacciones atómicas; verificar que la actualización inválida deja el valor previo intacto.
- [ ] 1.3 Ampliar `docs/Contratos/contrato-canales-fuentes-rss.openapi.yaml` con `GET /api/v1/config` y `PUT /api/v1/config`, schemas de solicitud y respuesta, y códigos `200`, `400` y `500`; validar el documento OpenAPI.

## 2. API y servicio

- [ ] 2.1 Crear el schema Pydantic v2 para la respuesta de configuración y para el cuerpo de actualización, requiriendo un entero positivo; verificar que `0`, negativos y tipos no enteros producen `400`.
- [ ] 2.2 Añadir el router FastAPI de configuración con `GET /api/v1/config` y `PUT /api/v1/config`; verificar respuesta HTTP `200` y el cuerpo con `periodicidad_cron_minutos`.
- [ ] 2.3 Implementar el servicio de lectura y actualización y verificar que la operación persiste el valor antes de reprogramar el scheduler.

## 3. Scheduler y ciclo de vida

- [ ] 3.1 Implementar `reprogramar_periodicidad(minutos)` en `src/app/jobs/scheduler.py`, manteniendo una sola instancia de APScheduler, `max_instances=1` y `coalesce=True`.
- [ ] 3.2 Conectar la actualización válida con la reprogramación del scheduler y verificar que la siguiente ejecución use el nuevo valor sin captura inmediata.
- [ ] 3.3 Añadir pruebas de scheduler que simulen la actualización y permitan comprobar el intervalo_next_run o el funcionamiento del job con un mock de APScheduler.

## 4. Pruebas automatizadas

- [ ] 4.1 Añadir pruebas del endpoint `GET /api/v1/config` para responder el valor actual con HTTP `200`.
- [ ] 4.2 Añadir pruebas del endpoint `PUT /api/v1/config` para una actualización válida y para `0` y valores negativos con HTTP `400` y valor previo conservado.
- [ ] 4.3 Añadir pruebas del servicio y repositorio para persistencia, transacción y error de actualización.
- [ ] 4.4 Añadir pruebas que verifiquen la reprogramación y que no semartes una nueva dependencia o una llamada real a RSS.
- [ ] 4.5 Ejecutar `pytest` con cobertura mínima del 80% y comprobar que no se exponen trazas internas.

## 5. Conformidad final

- [ ] 5.1 Revisar que los routers no contienen SQL ni lógica de negocio y que los servicios no dependen de FastAPI.
- [ ] 5.2 Revisar que toda operación de datos reste en repositorios y que las tecnologías sean las aprobadas en `docs/architecture.md` y los ADR vigentes.
- [ ] 5.3 Ejecitar `pytest`, confirmar cobertura ≥80%, y documentar cualquier caso de prueba bloqueado o dependiente de infraestructura.
- [ ] 5.4 Comprobar la conformidad final con `docs/architecture.md`, `openspec/config.yaml` y el contrato OpenAPI de la configuración.
