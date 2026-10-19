// HumWorld - carita de humor: un círculo de color con la expresión del humor.
// Se usa en el mapa (una por continente), en las leyendas y en la lista de noticias.
// "tipo" puede ser: positivo, negativo, neutro o sinDatos (ver utilidades/humor.js).
import { BOCAS_CARITA, COLORES_HUMOR } from '../utilidades/humor.js'

const TINTA = '#2b2350'

export default function Carita({ tipo = 'neutro', tamano = 32 }) {
  return (
    <svg className="carita" viewBox="0 0 40 40" width={tamano} height={tamano} aria-hidden="true">
      <circle cx="20" cy="20" r="17" fill={COLORES_HUMOR[tipo]} stroke={TINTA} strokeWidth="2.5" />
      <circle cx="14" cy="17" r="2.4" fill={TINTA} />
      <circle cx="26" cy="17" r="2.4" fill={TINTA} />
      <path d={BOCAS_CARITA[tipo]} fill="none" stroke={TINTA} strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  )
}
