## 1. Repositorios y estado de FuenteRSS

- [x] 1.1 Añadir o reutilizar operaciones de repositorio para distinguir `FuenteRSS` inexistente, activa e inactiva; verificar los tres resultados con SQLite.
- [x] 1.2 Confirmar que las operaciones de persistencia de noticias y deduplicación reutilizadas por HU-RSS-006 cubren captura manual sin migración; verificar que una noticia duplicada no genera una segunda fila.

## 2. Servicio de captura manual

- [x] 2.1 Implementar la precondición de captura individual y diferenciar inexistente/inactiva antes de acceder al feed; verificar error de dominio para cada caso.
- [x] 2.2 Implementar la orquestación manual individual reutilizando el procesamiento común de HU-RSS-006; verificar resultado y cantidad de noticias nuevas con feed mockeado.
- [x] 2.3 Implementar la captura por lote con un resultado por id y aislamiento de excepciones por FuenteRSS; verificar con una fuente fallida y otra exitosa que se intenta todo el lote.

## 3. API y contrato

- [x] 3.1 Sustituir los stubs en `src/app/routers/captures.py` para delegar en Servicios y mapear respuestas 201, 404 y 409; verificar los códigos y cuerpos con `TestClient`.
- [x] 3.2 Mantener validación de `fuente_ids` no vacío y error HTTP 400; verificar body ausente, vacío e inválido.
- [x] 3.3 Sincronizar las descripciones obsoletas de los endpoints de captura en `docs/Contratos/contrato-canales-fuentes-rss.openapi.yaml`; verificar que OpenAPI muestra rutas, cuerpos y respuestas acordados.

## 4. Pruebas automatizadas y calidad

- [x] 4.1 Añadir pruebas de API/servicio con SQLite y mocks `respx` para captura individual exitosa, inexistente y fuente inactiva; comprobar que una inactiva no causa llamada HTTP.
- [x] 4.2 Añadir prueba de lote parcialmente fallido con respuestas RSS mockeadas; comprobar que todas las fuentes se intentan y que la fuente exitosa persiste noticias.
- [x] 4.3 Añadir prueba de deduplicación compartida entre captura manual y procesamiento común; comprobar cantidad de noticias nuevas y unicidad persistida.
- [x] 4.4 Ejecutar `pytest` y `pytest-cov`; verificar que toda la suite pasa y que la cobertura del módulo alcanza al menos 80%, sin llamadas RSS reales.
- [x] 4.5 Revisar conformidad final con `docs/architecture.md`, `openspec/config.yaml` y los ADR vigentes; verificar separación API/Servicios/Repositorios/Persistencia y ausencia de cambios fuera de HU-RSS-008.