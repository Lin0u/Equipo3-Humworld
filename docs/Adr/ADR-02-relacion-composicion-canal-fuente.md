# ADR-0002: Relación de composición entre CanalNoticias y FuenteRSS

- Estado: Aceptado
- Fecha: 2026-08-19
- Responsables: Equipo 3 (HumWorld)
- Relacionado con: PDF de especificaciones, secciones 4.2.1 y 4.3.2; instrucciones del proyecto, sección 8; ADR-0001; HU-RSS-001 a HU-RSS-005, HU-RSS-010

## Problema, elemento de arquitectura sobre el que decidir

El PDF describe dos altas separadas: canales de noticias (medios) y fuentes RSS dentro de cada canal. Debe definirse cómo modelar esa relación en el dominio y en la base de datos MySQL, considerando que las consultas agregadas por continente/país de los futuros dashboards dependen de que esta información esté normalizada, y que las instrucciones del proyecto (sección 8) piden ejemplificar una relación de composición.

## Opciones consideradas

### Opción A: CanalNoticias como entidad independiente, en composición con FuenteRSS
Dos entidades y dos altas separadas; una FuenteRSS no existe sin su CanalNoticias.

### Opción B: "Canal" como atributo de texto libre dentro de FuenteRSS
Una sola alta, sin CRUD propio de canal; nombre y continente/país se repiten como texto en cada fuente.

## Matriz de decisión

La Opción A evita duplicación e inconsistencia del nombre de canal y su continente/país entre distintas fuentes de un mismo medio, y deja normalizada la base para las consultas agregadas por continente/país que necesitarán los dashboards. La Opción B reduce la superficie de endpoints y pruebas a cubrir en el Sprint 1, pero corre el riesgo de que el mismo medio quede registrado de forma inconsistente en distintas fuentes, y no corresponde a lo descrito literalmente en el PDF, que plantea dos altas distintas.

## Decisión

Se adopta la Opción A: CanalNoticias como entidad independiente, en relación de composición con FuenteRSS.

## Por qué se elige frente a las demás

El costo adicional de modelar CanalNoticias como entidad separada es bajo, frente al riesgo de inconsistencia de datos que introduce la alternativa simplificada y que afectaría directamente a los dashboards de agregación por continente/país. Además, corresponde a lo descrito explícitamente en el PDF y usa el mismo par de entidades que las instrucciones del proyecto emplean como ejemplo de composición.

## Consecuencias

### Positivas
Continente/país normalizados una sola vez por canal; base lista para la agregación regional de los dashboards; corresponde al comportamiento CRUD descrito en el PDF.

### Negativas y deuda aceptada
Se expone un recurso adicional (`/channels`) además de `/sources`, con su propio CRUD y pruebas a cubrir para el umbral de cobertura ≥80%. Queda pendiente de definir si al eliminar un canal se eliminan en cascada sus fuentes o se bloquea la eliminación mientras tenga fuentes asociadas.

## Trazabilidad y sincronización

Modelos SQLAlchemy `CanalNoticias`/`FuenteRSS`; contrato OpenAPI de `/channels` y `/sources`; HU-RSS-001 a HU-RSS-005 y HU-RSS-010.
