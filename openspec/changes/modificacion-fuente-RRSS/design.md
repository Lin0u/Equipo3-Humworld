## Context

Los endpoints `PUT/PATCH /api/v1/sources/{id}` ya están declarados en el router, pero actualmente son stubs. Los schemas existentes incluyen `canal_id` en los payloads de actualización, aunque la decisión de esta HU lo hace inmutable; deberán ajustarse para exponer solo los campos configurables. Véanse [proposal.md](proposal.md) y [spec.md](specs/modificacion-fuente-rss/spec.md) para el contrato acordado.

La implementación debe reutilizar la validación de HU-02, mantener el SQLAlchemy exclusivamente en repositorios y conservar los campos de sistema de `FuenteRSS`.

## Goals / Non-Goals

**Goals:**

- Implementar PUT completo y PATCH parcial con HTTP 200.
- Mantener `canal_id` y campos de sistema inmutables.
- Aplicar validación y normalización consistente con el alta.
- Traducir fuente inexistente a HTTP 404 y entradas inválidas a HTTP 400.
- Mantener la separación API, Servicios, Repositorios y Persistencia.
- Verificar idempotencia de PUT y preservación de campos en PATCH.

**Non-Goals:**

- No implementar cambio de canal propietario.
- No modificar alta, consulta, listado, eliminación ni captura RSS.
- No cambiar tablas, relaciones, migraciones ni añadir dependencias.
- No permitir modificar fechas de captura ni estado del circuit breaker.
- No añadir autenticación o autorización.

## Decisions

### Schemas

`FuenteRSSActualizar` contendrá exactamente `url`, `categoria_iptc` y `activo`, todos obligatorios. `FuenteRSSActualizarParcial` contendrá esos mismos campos opcionales, pero rechazará un payload sin campos y valores `null`. Los schemas rechazarán campos extra como `canal_id`, porque el canal propietario es inmutable. URL y categoría reutilizarán los validadores de HU-02 para recorte, HTTP/HTTPS e IPTC Media Topics 1.4.

Alternativa descartada: conservar `canal_id` en PUT/PATCH, porque permitirlo cambia la composición de la fuente y no está incluido en la intención de la historia. Alternativa descartada: aceptar PATCH vacío como no-op, porque ocultaría errores administrativos y no produce una modificación verificable.

### API

El router validará payload y ruta, delegará al servicio y mapeará `FuenteRSSNotFoundError` a HTTP 404. Las validaciones Pydantic se convertirán mediante el manejador existente a HTTP 400 con `Error`. Las respuestas OpenAPI declararán 200, 400 y 404 para ambos métodos. El router no contendrá SQL ni actualización directa de atributos ORM.

### Servicio

Se añadirán casos de uso independientes de FastAPI para actualización completa y parcial. PUT asignará siempre los tres campos configurables y PATCH asignará solo los presentes. Ambos preservarán los campos no configurables y delegarán la transacción al repositorio.

### Repositorio

El repositorio buscará la `FuenteRSS` por id, aplicará los cambios recibidos, hará `commit`, `refresh` y rollback ante errores de persistencia. El servicio traducirá una fuente inexistente a error de dominio; no se usará una consulta previa en el router.

### Persistencia

No se requieren migraciones: solo se actualizan columnas existentes. La operación se verificará con SQLite aislado y los modelos ORM actuales; la persistencia de producción continúa siendo MySQL.

### Pruebas

Se añadirán pruebas con SQLite y `TestClient` para PUT completo, PUT incompleto/ inválido, idempotencia, PATCH de un campo, PATCH de varios campos, cuerpo vacío/null, fuente inexistente, normalización y preservación de `canal_id`, fecha y circuit breaker. También se comprobará OpenAPI y cobertura mínima del 80%. No hay llamadas RSS externas en este caso de uso, por lo que no se realizarán llamadas reales.

### Ficheros afectados

- Modificar `src/app/schemas/fuente.py`.
- Modificar `src/app/routers/sources.py`.
- Modificar `src/app/services/fuente_service.py`.
- Modificar `src/app/repositories/fuentes.py`.
- Reutilizar excepciones y schemas comunes existentes.
- Añadir pruebas bajo `src/tests/`.
- No modificar modelos ORM ni infraestructura de migraciones.

## Risks / Trade-offs

- **[Riesgo]** Un PATCH parcial puede sobrescribir accidentalmente campos si se serializa con valores por defecto → **Mitigación:** usar solo campos explícitamente presentes y probar `activo=false`, que es falsy pero válido.
- **[Riesgo]** La validación de actualización podría divergir de la de alta → **Mitigación:** extraer o reutilizar los mismos validadores y catálogo IPTC 1.4.
- **[Riesgo]** Un fallo de persistencia puede dejar una sesión en estado inválido → **Mitigación:** rollback en el repositorio antes de propagar un error controlado.
- **[Riesgo]** Clientes antiguos podrían enviar `canal_id` en PUT → **Mitigación:** documentar su inmutabilidad y rechazar el campo con HTTP 400 para evitar una solicitud silenciosamente ignorada.

## Migration Plan

No hay migración de base de datos. Desplegar la aplicación tras ejecutar la suite SQLite y la validación de cobertura. El rollback consiste en retirar las rutas de actualización y revertir los cambios de servicio/repositorio; no requiere revertir datos, aunque las modificaciones ya realizadas permanecerán en la base de datos y deberán restaurarse por procedimiento operativo si fuera necesario.
