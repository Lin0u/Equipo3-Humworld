## 1. Contrato y normalización

- [ ] 1.1 Actualizar `CanalNoticiasCrear` para recortar `nombre`, `continente`, `pais` y `descripcion` antes de validar, y verificar con tests que los espacios exteriores se eliminan
- [ ] 1.2 Rechazar `nombre` vacío o compuesto solo por espacios, conservar `continente` como texto libre y verificar respuestas de validación con el schema `Error` (`codigo`, `mensaje`)

## 2. Servicio y persistencia

- [ ] 2.1 Implementar el caso de uso de alta en la capa de servicio y verificar que persiste un canal válido con los valores normalizados
- [ ] 2.2 Implementar la detección de nombres duplicados ignorando mayúsculas/minúsculas y verificar el conflicto con una prueba de nombres equivalentes
- [ ] 2.3 Traducir la violación de unicidad de persistencia a un error de dominio que pueda responder como `409`, y verificar el comportamiento ante una carrera o restricción duplicada

## 3. API HTTP

- [ ] 3.1 Conectar `POST /channels` con el servicio y verificar que una creación válida responde `201` con la representación del canal y su identificador
- [ ] 3.2 Mapear errores de entrada a `400` y conflictos de nombre a `409`, verificando en ambos casos un cuerpo conforme al schema `Error` con `codigo` y `mensaje`
- [ ] 3.3 Verificar que el alta no introduce dependencias de autenticación o autorización y que no se modifican los endpoints de consulta

## 4. Pruebas de integración

- [ ] 4.1 Añadir cobertura para alta válida, campos opcionales, normalización de todos los campos y continente fuera de catálogo, verificando el flujo HTTP completo
- [ ] 4.2 Añadir cobertura para nombre vacío tras recorte, longitudes inválidas y duplicados por capitalización o espacios, verificando estados `400` y `409`

## 5. Migración de base de datos

- [ ] 5.1 **Pendiente:** crear la migración Alembic necesaria para respaldar la tabla de canales y la unicidad case-insensitive, y verificarla aplicando y revirtiendo la migración en un entorno de prueba
- [ ] 5.2 **Pendiente:** ejecutar la migración en el entorno objetivo y verificar que se aplica antes del despliegue de la nueva capacidad