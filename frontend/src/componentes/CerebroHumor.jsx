// HumWorld - mascota del proyecto: un cerebro que pone la cara del humor que recibe.
// Es un dibujo hecho con código (SVG), original del proyecto.
// Uso: <CerebroHumor humor={0.4} tamano={56} />
import { tipoHumor } from '../utilidades/humor.js'

const DESCRIPCION = {
  positivo: 'Cerebro contento: el humor es positivo',
  negativo: 'Cerebro triste: el humor es negativo',
  neutro: 'Cerebro tranquilo: el humor es neutro',
  sinDatos: 'Cerebro tranquilo: no hay datos de humor',
}

const TINTA = '#2b2350'

export default function CerebroHumor({ humor, tamano = 64, animado = true }) {
  const tipo = tipoHumor(humor)

  return (
    <svg
      className={animado ? 'cerebro cerebro-animado' : 'cerebro'}
      viewBox="0 0 120 110"
      width={tamano}
      height={(tamano * 110) / 120}
      role="img"
      aria-label={DESCRIPCION[tipo]}
    >
      {/* Contorno: los mismos círculos un poco más grandes, en color tinta. */}
      <g fill={TINTA}>
        <circle cx="38" cy="48" r="27" />
        <circle cx="60" cy="38" r="29" />
        <circle cx="84" cy="48" r="25" />
        <circle cx="46" cy="70" r="25" />
        <circle cx="76" cy="72" r="27" />
      </g>
      {/* Cuerpo rosado. */}
      <g fill="#ff8fb1">
        <circle cx="38" cy="48" r="24" />
        <circle cx="60" cy="38" r="26" />
        <circle cx="84" cy="48" r="22" />
        <circle cx="46" cy="70" r="22" />
        <circle cx="76" cy="72" r="24" />
      </g>
      {/* Pliegues del cerebro. */}
      <g fill="none" stroke="#f06a96" strokeWidth="3" strokeLinecap="round">
        <path d="M60 14 C55 22 65 30 60 38" />
        <path d="M26 40 C32 34 38 40 34 46" />
        <path d="M88 34 C94 38 92 46 86 46" />
        <path d="M30 76 C36 82 44 80 44 74" />
        <path d="M82 90 C90 88 94 80 90 74" />
      </g>
      {/* Ojos. */}
      <circle cx="48" cy="54" r="5.5" fill={TINTA} />
      <circle cx="74" cy="54" r="5.5" fill={TINTA} />
      <circle cx="49.8" cy="52.2" r="1.8" fill="#ffffff" />
      <circle cx="75.8" cy="52.2" r="1.8" fill="#ffffff" />

      {/* Expresión según el humor. */}
      {tipo === 'positivo' && (
        <>
          <ellipse cx="38" cy="64" rx="6" ry="3.5" fill="#ff5a8a" opacity="0.55" />
          <ellipse cx="84" cy="64" rx="6" ry="3.5" fill="#ff5a8a" opacity="0.55" />
          <path
            d="M49 66 Q61 82 73 66 Z"
            fill={TINTA}
            stroke={TINTA}
            strokeWidth="3"
            strokeLinejoin="round"
          />
        </>
      )}
      {(tipo === 'neutro' || tipo === 'sinDatos') && (
        <path d="M52 70 L70 70" fill="none" stroke={TINTA} strokeWidth="4" strokeLinecap="round" />
      )}
      {tipo === 'negativo' && (
        <>
          <path d="M41 43 L53 47" stroke={TINTA} strokeWidth="3.5" strokeLinecap="round" />
          <path d="M81 43 L69 47" stroke={TINTA} strokeWidth="3.5" strokeLinecap="round" />
          <path
            d="M50 76 Q61 64 72 76"
            fill="none"
            stroke={TINTA}
            strokeWidth="4"
            strokeLinecap="round"
          />
          <path
            d="M82 60 q4 8 0 11 q-4 -3 0 -11 Z"
            fill="#7fd0ff"
            stroke={TINTA}
            strokeWidth="1.5"
          />
        </>
      )}
    </svg>
  )
}
