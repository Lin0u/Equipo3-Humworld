# Dataset propuesto para la carga inicial del diccionario de términos

**Proyecto:** HumWorld — Equipo 3
**Origen:** PDF de especificaciones, sección 4.2.2 ("Deberá existir un diccionario de términos con palabras y su valor para el cálculo del humor"); HU-SENT-001 (gestión del diccionario); HU-SENT-007-v2 (regla de comparación).
**Estado:** **Propuesto — pendiente de aprobación del equipo.** La traducción al español fue generada con IA y debe revisarla una persona del equipo antes de usarse como dato definitivo.
**Versión:** v1.0. **Fecha:** 2026-10-19.
**Archivo:** `src/scripts/data/diccionario_seed.csv` (columnas `palabra`, `idioma`, `valor`, `origen`). Carga: `python -m scripts.seed_diccionario`.

---

## 1. Fuente

**AFINN-en-165** (Finn Årup Nielsen, Technical University of Denmark): 3.382 palabras y expresiones en inglés puntuadas a mano con enteros de -5 a +5. Es el léxico de sentimiento con intensidad más usado en enseñanza y prototipos, y viene incluido en paquetes como `afinn` (Python) y `textdata` (R).

- Repositorio: https://github.com/fnielsen/afinn
- Cita: F. Å. Nielsen, "A new ANEW: Evaluation of a word list for sentiment analysis in microblogs", *Proceedings of the ESWC2011 Workshop on Making Sense of Microposts*, CEUR-WS vol. 718, pp. 93–98, 2011.

**Licencia de los datos: Open Database License (ODbL) v1.0.** El código del repositorio es Apache 2.0, pero la carpeta de datos trae su propia licencia ODbL (`afinn/data/LICENSE`, copiada en `src/scripts/data/AFINN-LICENSE.txt`). Consecuencias para el proyecto:

- Se puede usar, adaptar y traducir.
- Hay que mantener la atribución a AFINN.
- El CSV derivado (incluida la traducción) debe distribuirse bajo la misma ODbL. El código del proyecto no queda afectado: la ODbL aplica a la base de datos, no al software que la usa.

## 2. Cómo se construyó

**Inglés (3.380 términos):** AFINN-en-165 completo, con cada valor multiplicado por 2 para pasar de -5..+5 a la escala -10..+10 del proyecto (sección 11 de las instrucciones; PDF §10.4). Se excluyen los 2 términos con valor 0 ("kind of" y "some kind"), que solo agregarían un 0 al promedio y diluirían el resultado.

**Español (418 términos):** traducción de 148 términos de AFINN elegidos por ser frecuentes en noticias (conflicto, economía, salud, política, deporte). Cada término en inglés se tradujo a sus formas en español (singular, plural, femenino y algunas conjugaciones), y cada forma hereda el valor de AFINN × 2. Se excluyeron formas ambiguas en titulares, por ejemplo:

- "fuerte" (de *strong*, +4): en noticias suele acompañar hechos negativos ("fuerte terremoto", "fuerte caída").
- "fallo" (de *failure*, -4): también significa sentencia judicial.
- "avance" (de *breakthrough*, +6): también se usa para avances de tropas o de incendios.
- "aprueba"/"aprobó" (de *approval*, +4): "el Congreso aprueba la ley" es neutro.
- "seguro"/"seguridad" (de *safe*/*safety*): también significan seguro médico y fuerzas de seguridad.

Se quitaron también las formas que, al ignorar tildes (HU-SENT-007-v2), quedaban iguales a otra ya incluida ("fracasó" = "fracaso").

## 3. Verificaciones automáticas (`src/tests/test_seed_diccionario.py`)

- Sin pares (palabra, idioma) repetidos; solo `es` y `en`; todos los valores enteros, pares, entre -10 y +10 y distintos de 0.
- Al menos 3.000 términos en inglés y 400 en español.
- La carga es idempotente, no sobrescribe términos ya existentes y se revierte completa si una fila es inválida.

## 4. Limitaciones que el equipo debe conocer

- **AFINN se diseñó para Twitter**, no para noticias: incluye jerga y groserías (poco frecuentes en titulares, no afectan) y le faltan palabras habituales en prensa, como *inflation*, *flood* o *drought*. Se pueden agregar después por `POST /api/v1/dictionary`.
- **Valores moderados:** la mayoría de los términos vale entre -6 y +6; solo 21 llegan a ±10. El humor de una noticia rara vez será extremo.
- **El español es más chico (418 frente a 3.380)** y sin validación humana todavía. Con 4 de las 20 fuentes en español, es el punto que más conviene revisar.
- **Sin lematización:** solo se cuentan las formas listadas (HU-SENT-007-v2).
- **Sin contexto:** el método cuenta palabras, no entiende frases. Caso real del 2026-10-19: "Banco Santander se alía con Nvidia para impulsar el despliegue de la IA en la entidad" obtuvo -8.0 porque su resumen menciona "fraude" (la IA se usa para detectarlo) y fue el único término encontrado. Es la limitación conocida del método de diccionario (ADR-003); la polarización (HU-SENT-003) y la cantidad de términos evaluados ayudan a leer estos casos, y el modelo de ML (HU-SENT-006) debería mejorarlos.

## 5. Cómo revisar la traducción

La tabla muestra cada término fuente, su valor en AFINN, el valor en HumWorld y las formas en español. Para corregir, se edita `diccionario_seed.csv` (o el término por API, si ya está cargado).

| AFINN (inglés) | AFINN | HumWorld | Formas en español |
|---|---|---|---|
| abuse | -3 | -6 | abuso, abusos |
| accident | -2 | -4 | accidente, accidentes |
| accuse | -2 | -4 | acusa, acusan, acusación, acusaciones |
| accused | -2 | -4 | acusado, acusada, acusados, acusadas |
| alarm | -2 | -4 | alarma, alarmas |
| anger | -3 | -6 | ira, rabia, furia |
| angry | -3 | -6 | enojado, enojada, enojados, furioso, furiosa, furiosos |
| anxiety | -2 | -4 | ansiedad, angustia |
| approval | 2 | +4 | aprobación |
| arrest | -2 | -4 | detención, detenciones, arresto, arrestos |
| arrested | -3 | -6 | detenido, detenida, detenidos, detenidas, arrestado, arrestada, arrestados |
| assassination | -3 | -6 | magnicidio |
| attack | -1 | -2 | ataque, ataques, atentado, atentados |
| bankruptcy | -3 | -6 | quiebra, quiebras, bancarrota |
| benefit | 2 | +4 | beneficio, beneficios, beneficia |
| best | 3 | +6 | mejor, mejores |
| betrayed | -3 | -6 | traicionado, traicionada, traición |
| blame | -2 | -4 | culpa, culpan, culpó |
| brave | 2 | +4 | valiente, valientes |
| breakthrough | 3 | +6 | hito, hitos |
| bribe | -3 | -6 | soborno, sobornos, coima, coimas |
| brutal | -3 | -6 | brutal, brutales |
| calm | 2 | +4 | calma, tranquilidad |
| catastrophe | -3 | -6 | catástrofe, catástrofes |
| catastrophic | -4 | -8 | catastrófico, catastrófica, catastróficos, catastróficas |
| celebrate | 3 | +6 | celebra, celebran, celebró, celebraron |
| celebration | 3 | +6 | celebración, celebraciones, festejo, festejos |
| chaos | -2 | -4 | caos, caótico, caótica |
| cheated | -3 | -6 | estafado, estafados, estafa, estafas |
| collapse | -2 | -4 | colapso, colapsa, derrumbe |
| condemn | -2 | -4 | condena, condenan, condenó |
| conflict | -2 | -4 | conflicto, conflictos |
| corrupt | -3 | -6 | corrupto, corrupta, corruptos, corruptas |
| corruption | -3 | -6 | corrupción |
| crash | -2 | -4 | choque, choques, desplome |
| crime | -3 | -6 | crimen, crímenes, delito, delitos |
| crisis | -3 | -6 | crisis |
| cruel | -3 | -6 | cruel, crueles, crueldad |
| damage | -3 | -6 | daño, daños, dañado, dañada |
| danger | -2 | -4 | peligro, peligros |
| dangerous | -2 | -4 | peligroso, peligrosa, peligrosos, peligrosas |
| dead | -3 | -6 | muerto, muerta, muertos, muertas |
| deadly | -3 | -6 | mortal, mortales, letal, letales |
| death | -2 | -4 | muerte, muertes |
| debt | -2 | -4 | deuda, deudas |
| defeat | -2 | -4 | derrota, derrotas |
| defeated | -2 | -4 | derrotado, derrotada, derrotados |
| deficit | -2 | -4 | déficit |
| destroy | -3 | -6 | destruye, destruir |
| destroyed | -3 | -6 | destruido, destruida, destruidos, destruidas |
| destruction | -3 | -6 | destrucción |
| devastating | -2 | -4 | devastador, devastadora, devastadores, devastación |
| died | -3 | -6 | murió, murieron, falleció, fallecieron, fallecido, fallecida, fallecidos |
| disappointed | -2 | -4 | decepcionado, decepcionada, decepción |
| disaster | -2 | -4 | desastre, desastres |
| disease | -1 | -2 | enfermedad, enfermedades |
| dispute | -2 | -4 | disputa, disputas, pugna |
| emergency | -2 | -4 | emergencia, emergencias |
| enemy | -2 | -4 | enemigo, enemiga, enemigos |
| evil | -3 | -6 | maldad, malvado |
| excellent | 3 | +6 | excelente, excelentes |
| failed | -2 | -4 | fracasaron, fallido, fallida, fallidos |
| failure | -2 | -4 | fracaso, fracasos |
| famine | -2 | -4 | hambruna, hambrunas |
| fatal | -3 | -6 | fatal, fatales |
| fear | -2 | -4 | miedo, miedos, temor, temores |
| fighting | -2 | -4 | combate, combates, enfrentamiento, enfrentamientos |
| fire | -2 | -4 | incendio, incendios |
| fired | -2 | -4 | despedido, despedida, despedidos, despidos |
| fraud | -4 | -8 | fraude, fraudes |
| freedom | 2 | +4 | libertad, libertades |
| friendly | 2 | +4 | amistoso, amistosa, cordial |
| glad | 3 | +6 | contento, contenta, contentos |
| good | 3 | +6 | bueno, buena, buenos, buenas |
| grief | -2 | -4 | duelo, luto, dolor |
| growth | 2 | +4 | crecimiento |
| guilty | -3 | -6 | culpable, culpables |
| happy | 3 | +6 | feliz, felices, alegre, alegres |
| harm | -2 | -4 | perjuicio, perjuicios |
| hate | -3 | -6 | odio |
| healthy | 2 | +4 | saludable, saludables, sano, sana |
| help | 2 | +4 | ayuda, ayudas |
| hero | 2 | +4 | héroe, héroes, heroína |
| honor | 2 | +4 | honor, homenaje |
| hope | 2 | +4 | esperanza, esperanzas |
| hopeful | 2 | +4 | esperanzado, esperanzada, esperanzador, esperanzadora |
| hunger | -2 | -4 | hambre |
| illegal | -3 | -6 | ilegal, ilegales |
| improve | 2 | +4 | mejora, mejoran, mejoró, mejoras |
| injured | -2 | -4 | herido, herida, heridos, heridas, lesionado, lesionados |
| injury | -2 | -4 | lesión, lesiones |
| invasion | -1 | -2 | invasión, invasiones |
| joy | 3 | +6 | alegría, júbilo |
| justice | 2 | +4 | justicia |
| kidnapping | -2 | -4 | secuestro, secuestros, secuestrado, secuestrados |
| kill | -3 | -6 | matar, mata, mató, mataron |
| loss | -3 | -6 | pérdida, pérdidas |
| lost | -3 | -6 | perdió, perdieron |
| love | 3 | +6 | amor |
| lucky | 3 | +6 | afortunado, afortunada, afortunados |
| murder | -2 | -4 | asesinato, asesinatos, asesinado, asesinada, asesinados, homicidio, homicidios |
| optimism | 2 | +4 | optimismo |
| optimistic | 2 | +4 | optimista, optimistas |
| pain | -2 | -4 | sufrimiento |
| panic | -3 | -6 | pánico |
| peace | 2 | +4 | paz |
| peaceful | 2 | +4 | pacífico, pacífica, pacíficos, pacíficas |
| pollution | -2 | -4 | contaminación |
| poor | -2 | -4 | pobre, pobres |
| poverty | -1 | -2 | pobreza |
| praise | 3 | +6 | elogio, elogios, elogia |
| prison | -2 | -4 | cárcel, cárceles, prisión |
| prisoner | -2 | -4 | preso, presos, prisionero, prisioneros, rehén, rehenes |
| progress | 2 | +4 | progreso, progresos |
| prosperity | 3 | +6 | prosperidad |
| protest | -2 | -4 | protesta, protestas |
| racism | -3 | -6 | racismo, racista, racistas |
| rape | -4 | -8 | violación, violaciones |
| recession | -2 | -4 | recesión |
| rescue | 2 | +4 | rescate, rescates |
| rescued | 2 | +4 | rescatado, rescatada, rescatados |
| riot | -2 | -4 | disturbio, disturbios |
| risk | -2 | -4 | riesgo, riesgos |
| scandal | -3 | -6 | escándalo, escándalos |
| sick | -2 | -4 | enfermo, enferma, enfermos |
| strike | -1 | -2 | huelga, huelgas, paro, paros |
| succeed | 3 | +6 | logra, logró, lograron |
| success | 2 | +4 | éxito, éxitos, exitoso, exitosa |
| suffer | -2 | -4 | sufre, sufren, sufrió |
| suicide | -2 | -4 | suicidio, suicidios |
| support | 2 | +4 | apoyo, apoya, respaldo |
| suspect | -1 | -2 | sospechoso, sospechosa, sospechosos |
| terrible | -3 | -6 | terrible, terribles |
| terror | -3 | -6 | terror, terrorismo |
| terrorist | -2 | -4 | terrorista, terroristas |
| threat | -2 | -4 | amenaza, amenazas |
| threaten | -2 | -4 | amenazó, amenazan |
| torture | -4 | -8 | tortura, torturas, torturado |
| tragedy | -2 | -4 | tragedia, tragedias |
| tragic | -2 | -4 | trágico, trágica, trágicos |
| trauma | -3 | -6 | trauma, traumático |
| triumph | 4 | +8 | triunfo, triunfos, triunfa |
| unemployment | -2 | -4 | desempleo, cesantía |
| victim | -3 | -6 | víctima, víctimas |
| victory | 3 | +6 | victoria, victorias |
| violence | -3 | -6 | violencia |
| violent | -3 | -6 | violento, violenta, violentos, violentas |
| vulnerable | -2 | -4 | vulnerable, vulnerables |
| war | -2 | -4 | guerra, guerras |
| win | 4 | +8 | gana, ganan, ganó, ganaron |
| winner | 4 | +8 | ganador, ganadora, ganadores |
| wonderful | 4 | +8 | maravilloso, maravillosa, maravillosos |
| worried | -3 | -6 | preocupado, preocupada, preocupados, preocupación |
| worse | -3 | -6 | peor, peores, empeora, empeoró |

## 6. Uso recomendado

1. El equipo revisa la sección 5 y aprueba el dataset en el PR.
2. Con la API levantada: `docker compose exec api python -m scripts.seed_diccionario`.
3. El barrido de humor recalcula las noticias en su próxima ejecución (hasta 30 min; o reiniciar la API).

## Tabla de control de versiones

| Documento | Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|---|
| Dataset diccionario inicial | v1.0 | 2026-10-19 | Creación. Inglés: AFINN-en-165 completo (× 2, sin valores 0). Español: traducción generada con IA de 148 términos orientados a noticias (418 formas). Licencia ODbL heredada de AFINN. Pendiente de aprobación del equipo y de revisión humana del español. |
| Dataset diccionario inicial | v1.1 | 2026-10-19 | Se agrega a las limitaciones un caso real de falta de contexto ("fraude" en una noticia positiva sobre IA), detectado al probar el listado de noticias. |
