## Purpose

Persistir con cada `Noticia` el valor de humor calculado, la polarización de los términos y el método de cálculo utilizado, para que los resultados sobrevivan a la ejecución y puedan consumirse posteriormente sin recálculo.

## ADDED Requirements

### Requirement: Persistencia del resultado de sentimiento

El sistema SHALL almacenar en el registro existente de `Noticia` el `valor_humor` recibido del cálculo, el indicador `polarizacion_terminos` y `metodo_calculo` (`diccionario` o `ml`). La polarización SHALL ser un valor numérico de punto flotante nullable, expresado como desviación estándar poblacional según ADR-03. La escritura SHALL ser transaccional y mantener los valores calculados sin pérdida de precisión dentro del tipo persistido.

#### Scenario: Persistencia exitosa del resultado
- **Dado** que el cálculo produjo `valor_humor=-1.0`, `polarizacion_terminos=7.0` y `metodo_calculo=diccionario` para una `Noticia` existente
- **Cuando** el sistema persiste el resultado
- **Entonces** almacena los tres valores en la misma `Noticia`
- **Y** una lectura posterior devuelve los mismos valores

#### Scenario: Persistencia de resultado calculado por ML
- **Dado** que el cálculo produjo valor de humor, polarización y `metodo_calculo=ml`
- **Cuando** el sistema persiste el resultado
- **Entonces** almacena `metodo_calculo=ml` junto a los valores calculados

### Requirement: Noticia sin términos evaluables

Cuando el método de diccionario no encuentre términos evaluables, el sistema SHALL persistir `valor_humor=NULL` y `polarizacion_terminos=NULL`, sin sustituirlos por cero. SHALL persistir el método utilizado como `diccionario`, permitiendo distinguir ausencia de evaluación de un resultado neutral evaluado.

#### Scenario: Persistencia sin coincidencias en el diccionario
- **Dado** que una `Noticia` no contiene términos evaluables del diccionario
- **Cuando** el sistema persiste el resultado del cálculo determinista
- **Entonces** `valor_humor` queda `NULL`
- **Y** `polarizacion_terminos` queda `NULL`
- **Y** `metodo_calculo` queda `diccionario`

#### Scenario: Resultado neutral con evaluación
- **Dado** que el cálculo evaluó uno o más términos y obtuvo humor `0.0`
- **Cuando** el sistema persiste el resultado
- **Entonces** `valor_humor` queda `0.0`, no `NULL`
- **Y** el método de cálculo queda registrado