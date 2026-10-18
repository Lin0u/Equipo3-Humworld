# Dataset propuesto de fuentes RSS para la carga inicial (HU-RSS-009-v2)

**Proyecto:** HumWorld — Equipo 3
**Origen:** HU-RSS-009-v2 (`HU-RSS-captura.md` v1.12) y PDF de especificaciones, sección 4.2.1 ("carga inicial de fuentes RSS por continente").
**Estado:** **Propuesto — pendiente de aprobación del equipo.** No debe copiarse a `src/scripts/seed.py` hasta que el equipo lo apruebe.
**Versión:** v2.0. **Fecha de verificación:** 2026-10-18.

---

## 1. Criterios aplicados

- **Cobertura:** 4 fuentes por cada uno de los 5 continentes confirmados en HU-RSS-009, 20 en total (la referencia del equipo era un mínimo de 20).
- **Solo feeds de sección.** Cada fuente cubre un único tema, para que su `categoria_iptc` describa con exactitud las noticias que hereda (decisión de equipo del 2026-10-18). Se descartaron los feeds generales, que mezclan temas y no tienen un código IPTC de primer nivel que los represente.
- **Variedad de categorías:** 5 categorías IPTC distintas, para que el listado de noticias y la nube de palabras no queden sesgados a un solo tema.
- **Idioma:** solo español o inglés, los dos idiomas que exige el PDF (sección 3, Alcance, punto 2) y que admite el diccionario (HU-SENT-001). Por eso África, Asia y Oceanía quedan con medios en inglés.
- **Verificación:** se descargó cada URL y se comprobó que (a) devuelve un documento RSS con canal y elementos `item`, y (b) su ítem más reciente fue publicado en los últimos 3 días.
- **Continentes:** con tilde ("América", "Europa", "Asia", "África", "Oceanía"), decisión de equipo del 2026-10-18.

## 2. Dataset

| # | Continente | Canal (`nombre`) | País | Idioma | URL del feed | Sección | `categoria_iptc` | Ítem más reciente |
|---|---|---|---|---|---|---|---|---|
| 1 | América | El Tiempo | Colombia | es | `https://www.eltiempo.com/rss/politica.xml` | Política | `11000000` política | 2026-10-18 |
| 2 | América | El Tiempo | Colombia | es | `https://www.eltiempo.com/rss/economia.xml` | Economía | `04000000` economía, negocios y finanzas | 2026-10-17 |
| 3 | América | NPR | Estados Unidos | en | `https://feeds.npr.org/1014/rss.xml` | Politics | `11000000` política | 2026-10-18 |
| 4 | América | NPR | Estados Unidos | en | `https://feeds.npr.org/1128/rss.xml` | Health | `07000000` salud | 2026-10-17 |
| 5 | Europa | El Mundo | España | es | `https://e00-elmundo.uecdn.es/elmundo/rss/economia.xml` | Economía | `04000000` economía, negocios y finanzas | 2026-10-18 |
| 6 | Europa | El Mundo | España | es | `https://e00-elmundo.uecdn.es/elmundo/rss/ciencia.xml` | Ciencia | `13000000` ciencia y tecnología | 2026-10-16 |
| 7 | Europa | Sky News | Reino Unido | en | `https://feeds.skynews.com/feeds/rss/politics.xml` | Politics | `11000000` política | 2026-10-17 |
| 8 | Europa | Sky News | Reino Unido | en | `https://feeds.skynews.com/feeds/rss/technology.xml` | Technology | `13000000` ciencia y tecnología | 2026-10-15 |
| 9 | Asia | Japan Today | Japón | en | `https://japantoday.com/category/politics/feed` | Politics | `11000000` política | 2026-10-17 |
| 10 | Asia | Japan Today | Japón | en | `https://japantoday.com/category/tech/feed` | Tech | `13000000` ciencia y tecnología | 2026-10-18 |
| 11 | Asia | Dawn | Pakistán | en | `https://www.dawn.com/feeds/business` | Business | `04000000` economía, negocios y finanzas | 2026-10-18 |
| 12 | Asia | Dawn | Pakistán | en | `https://www.dawn.com/feeds/sport` | Sport | `15000000` deporte | 2026-10-17 |
| 13 | África | Premium Times | Nigeria | en | `https://www.premiumtimesng.com/category/health/feed` | Health | `07000000` salud | 2026-10-18 |
| 14 | África | Premium Times | Nigeria | en | `https://www.premiumtimesng.com/category/sports/feed` | Sports | `15000000` deporte | 2026-10-18 |
| 15 | África | AllAfrica | — | en | `https://allafrica.com/tools/headlines/rdf/business/headlines.rdf` | Economy, Business and Finance | `04000000` economía, negocios y finanzas | 2026-10-16 |
| 16 | África | TechCentral | Sudáfrica | en | `https://techcentral.co.za/feed/` | Medio especializado en tecnología | `13000000` ciencia y tecnología | 2026-10-16 |
| 17 | Oceanía | ABC News | Australia | en | `https://www.abc.net.au/news/feed/104217372/rss.xml` | Politics | `11000000` política | 2026-10-17 |
| 18 | Oceanía | RNZ | Nueva Zelanda | en | `https://www.rnz.co.nz/rss/political.xml` | Politics | `11000000` política | 2026-10-18 |
| 19 | Oceanía | RNZ | Nueva Zelanda | en | `https://www.rnz.co.nz/rss/business.xml` | Business | `04000000` economía, negocios y finanzas | 2026-10-18 |
| 20 | Oceanía | RNZ | Nueva Zelanda | en | `https://www.rnz.co.nz/rss/sport.xml` | Sport | `15000000` deporte | 2026-10-19 |

**Resumen:** 11 canales y 20 fuentes. Por categoría: política (`11000000`) 6, economía (`04000000`) 5, ciencia y tecnología (`13000000`) 4, deporte (`15000000`) 3 y salud (`07000000`) 2. Por idioma: 4 en español y 16 en inglés.

**País vacío (—):** AllAfrica es un agregador de cobertura continental, sin un único país de origen; se deja con `pais = null`, que el modelo permite (`CanalNoticias.pais` es opcional).

## 3. Observaciones que el equipo debe revisar

- **Respuestas cortadas (fuentes 6 y 11): resuelto.** Los feeds de Ciencia de El Mundo y Business de Dawn llegaron cortados a la herramienta de verificación. El 2026-10-18 se abrieron en un navegador: ambos se muestran como árbol XML completo (el navegador los interpreta sin error) y tienen fecha de publicación del 18 y 19 de octubre. El corte era un límite de la herramienta, no del feed.
- **Atributo `length` vacío (fuentes 1 y 2):** los feeds de El Tiempo traen el atributo `length` vacío en sus `enclosure`. No afecta la lectura de títulos, enlaces y fechas.
- **Poco español:** solo América y Europa tienen fuentes en español (4 de 20). No hay medios en español verificables con feeds de sección en los otros continentes.
- **Se pierde Chile:** La Tercera solo se pudo verificar con su feed general; su feed de política devolvió un documento incompleto. Si el equipo quiere un medio chileno, debe encontrar y verificar un feed de sección.
- **Diversidad de medios:** cada continente usa 2 o 3 medios, con 2 fuentes por medio en casi todos los casos. RNZ aporta 3 de las 4 fuentes de Oceanía.

## 4. Feeds descartados

**No verificables:** la herramienta de verificación tenía bloqueado el acceso a estos sitios. Eso no significa que sus feeds no funcionen; si el equipo los prefiere, debe verificarlos en un navegador.
- BBC News, The Guardian, El País, DW en español, France 24 en español, Clarín, Times of India, The Hindu y The Japan News (Yomiuri).

**Verificados pero descartados:**
- Feeds generales de la versión 1.0 de este documento (La Tercera, El Mundo portada, Euronews, Sky News World, Al Jazeera, Dawn portada, Japan Today portada, Arab News, Premium Times portada, AllAfrica últimas noticias, Daily Maverick, The Citizen, ABC Just In y RNZ Pacific): mezclan temas, decisión 3.1 de la versión 1.0.
- Con su ítem más reciente fuera del rango de 3 días: Premium Times Business (12 oct.), ABC Business (14 oct.), AllAfrica Health (3 sep.), AllAfrica Sport (30 sep.), Arab News Saudi Arabia (14 ago.) y SBS News (ago.).
- Otros: El Tiempo Salud (fechas de los ítems en formato ISO 8601 en vez de RFC 822), BusinessTech (cerca de un tercio de sus ítems no son de negocios), SuperSport (devuelve una página HTML, no un feed), feeds de SCMP encontrados (sin publicaciones desde 2019 y 2026-02) y RNZ World (1 solo ítem).

## 5. Uso recomendado

1. El equipo revisa la tabla y las observaciones de la sección 3 y aprueba el dataset.
2. Se re-verifica la lista la misma semana en que se ejecute el seed: los feeds RSS cambian de dirección sin aviso.
3. Se copia el dataset a `CANALES_SEED` en `src/scripts/seed.py`, agrupando las fuentes por canal (11 canales, 20 fuentes).

## Tabla de control de versiones

| Documento | Versión | Fecha/Sesión | Motivo del cambio |
|---|---|---|---|
| Dataset de fuentes RSS (HU-RSS-009-v2) | v1.0 | 2026-10-18 | Creación. 20 fuentes verificadas en 16 canales, 4 por continente, para cerrar el único punto pendiente de HU-RSS-009 (listado real de fuentes). Deja abiertas la categoría IPTC de los feeds generales y la forma de escribir los continentes. |
| Dataset de fuentes RSS (HU-RSS-009-v2) | v1.1 | 2026-10-18 | Se resuelve el punto de los continentes: con tilde. Sigue pendiente la categoría IPTC de los feeds generales. |
| Dataset de fuentes RSS (HU-RSS-009-v2) | v2.0 | 2026-10-18 | Decisión de equipo: solo feeds de sección. Se reemplazan los 14 feeds generales y 2 de sección para diversificar categorías. Resultado: 20 fuentes en 11 canales, todas con una categoría IPTC exacta, sin cambios en el código ni en HU-RSS-002. No quedan decisiones abiertas; solo la aprobación del equipo y la revisión de las observaciones de la sección 3. |
| Dataset de fuentes RSS (HU-RSS-009-v2) | v2.1 | 2026-10-18 | Se confirman en navegador los feeds 6 (El Mundo Ciencia) y 11 (Dawn Business). Las 20 fuentes quedan verificadas. |
