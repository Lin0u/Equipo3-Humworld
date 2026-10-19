// HumWorld - funciones compartidas para mostrar el humor en las pantallas.
// Son solo de presentación (colores y formato de números), no calculan el humor:
// ese cálculo es responsabilidad del backend (HU-SENT-002-v2 y ADR-003).

// Mismos colores que las variables --humor-* de index.css. Se repiten aquí para
// las piezas que necesitan el código del color y no el nombre de la variable.
export const COLORES_HUMOR = {
  positivo: '#2ec4a0',
  negativo: '#ff5a5f',
  neutro: '#ffc93c',
  sinDatos: '#d9d4ea',
}

// Clasifica el humor según su signo. El equipo todavía no define rangos
// oficiales para "positivo", "neutro" o "negativo"; cuando existan, se cambia aquí.
export function tipoHumor(valor) {
  if (valor === null || valor === undefined) return 'sinDatos'
  if (valor > 0) return 'positivo'
  if (valor < 0) return 'negativo'
  return 'neutro'
}

// Muestra el valor con un decimal y con signo + cuando es positivo.
export function formatoHumor(valor) {
  if (valor === null || valor === undefined) return 'Sin datos'
  return valor > 0 ? `+${valor.toFixed(1)}` : valor.toFixed(1)
}

// Busca dentro de la serie temporal de un resultado el dato de una fecha.
export function datoDeLaFecha(agregado, fecha) {
  return agregado.serie_temporal.find((dia) => dia.fecha === fecha) ?? null
}

// Forma de la boca de la carita para cada tipo de humor (trazos de dibujo SVG).
export const BOCAS_CARITA = {
  positivo: 'M12 24 Q20 32 28 24',
  negativo: 'M12 29 Q20 21 28 29',
  neutro: 'M13 26 L27 26',
  sinDatos: 'M15 26 L25 26',
}

// Devuelve la carita como texto HTML. Solo la usa el mapa: Leaflet pide el
// dibujo de sus marcadores como texto. El resto de la página usa el componente
// Carita.jsx, que dibuja lo mismo.
export function caritaComoTexto(tipo, tamano) {
  const tinta = '#2b2350'
  return (
    `<svg class="carita" viewBox="0 0 40 40" width="${tamano}" height="${tamano}" aria-hidden="true">` +
    `<circle cx="20" cy="20" r="17" fill="${COLORES_HUMOR[tipo]}" stroke="${tinta}" stroke-width="2.5"/>` +
    `<circle cx="14" cy="17" r="2.4" fill="${tinta}"/>` +
    `<circle cx="26" cy="17" r="2.4" fill="${tinta}"/>` +
    `<path d="${BOCAS_CARITA[tipo]}" fill="none" stroke="${tinta}" stroke-width="2.5" stroke-linecap="round"/>` +
    '</svg>'
  )
}
