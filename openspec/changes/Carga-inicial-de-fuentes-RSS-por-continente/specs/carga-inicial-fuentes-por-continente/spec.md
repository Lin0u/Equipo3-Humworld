## Purpose

Definir un procedimiento interno repetible para inicializar `CanalNoticias` y `FuenteRSS` con cobertura de los cinco continentes y sin duplicar entidades ya registradas.

## ADDED Requirements

### Requirement: Cobertura continental del conjunto semilla

El conjunto de datos autorizado para la carga inicial SHALL incluir al menos un `CanalNoticias` y una `FuenteRSS` asociada por cada uno de estos cinco continentes: América, Europa, Asia, África y Oceanía. Cada `FuenteRSS` SHALL referenciar un `CanalNoticias` incluido o ya existente. Solo se incluirán URLs de feeds RSS verificadas y aprobadas por el equipo; mientras falten esos datos, el seed SHALL permanecer sin dataset ejecutable y no SHALL insertar registros inventados.

#### Scenario: Conjunto semilla completo
- **Dado** que el equipo proporcionó datos verificados y aprobados para los cinco continentes
- **Cuando** se valida el conjunto semilla antes de ejecutarlo
- **Entonces** existe al menos un `CanalNoticias` y una `FuenteRSS` asociada para América, Europa, Asia, África y Oceanía
- **Y** cada URL incluida fue validada y aprobada por el equipo

#### Scenario: Datos verificados incompletos
- **Dado** que falta un feed verificado para uno o más de los cinco continentes
- **Cuando** se prepara el conjunto semilla
- **Entonces** el seed no se considera listo para una ejecución de aceptación
- **Y** no se sustituyen los datos faltantes por URLs inventadas o ejemplos no aprobados

### Requirement: Ejecución idempotente de la carga

El procedimiento SHALL crear los `CanalNoticias` y `FuenteRSS` definidos en el conjunto autorizado cuando no existan. SHALL tratar como existentes los canales con el mismo `nombre` y las fuentes con la misma `url`. Las fuentes SHALL quedar asociadas a un canal válido. Una ejecución repetida SHALL NOT crear duplicados y SHALL informar cero registros nuevos cuando no haya datos pendientes.

#### Scenario: Carga inicial en una base vacía
- **Dado** que la persistencia no contiene los canales ni las fuentes del conjunto semilla completo y aprobado
- **Cuando** se ejecuta el procedimiento de carga inicial
- **Entonces** se crea al menos un `CanalNoticias` y una `FuenteRSS` asociada para cada uno de los cinco continentes
- **Y** cada `FuenteRSS` queda asociada a un `CanalNoticias` válido
- **Y** el resultado informa las cantidades de canales y fuentes creados

#### Scenario: Ejecución repetida sin duplicados
- **Dado** que los registros del conjunto semilla ya existen en la persistencia
- **Cuando** se vuelve a ejecutar el procedimiento
- **Entonces** no se crean registros duplicados por nombre de `CanalNoticias` ni por URL de `FuenteRSS`
- **Y** el resultado informa cero canales y cero fuentes nuevos creados

#### Scenario: Reutilización de canal existente
- **Dado** que ya existe un `CanalNoticias` con el nombre semilla, pero aún no existe una de sus `FuenteRSS`
- **Cuando** se ejecuta el procedimiento de carga inicial
- **Entonces** se reutiliza el `CanalNoticias` existente
- **Y** se crea la `FuenteRSS` faltante asociada a ese canal