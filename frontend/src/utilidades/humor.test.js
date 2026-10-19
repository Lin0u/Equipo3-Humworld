import { describe, expect, it } from 'vitest'
import { caritaComoTexto, datoDeLaFecha, formatoHumor, tipoHumor } from './humor.js'

describe('tipoHumor', () => {
  it('clasifica por signo y distingue la ausencia de datos', () => {
    expect(tipoHumor(2.5)).toBe('positivo')
    expect(tipoHumor(-0.1)).toBe('negativo')
    expect(tipoHumor(0)).toBe('neutro')
    expect(tipoHumor(null)).toBe('sinDatos')
    expect(tipoHumor(undefined)).toBe('sinDatos')
  })
})

describe('formatoHumor', () => {
  it('muestra un decimal y el signo + en los positivos', () => {
    expect(formatoHumor(1.26)).toBe('+1.3')
    expect(formatoHumor(-3)).toBe('-3.0')
    expect(formatoHumor(0)).toBe('0.0')
    expect(formatoHumor(null)).toBe('Sin datos')
  })
})

describe('datoDeLaFecha', () => {
  const agregado = { serie_temporal: [{ fecha: '2026-10-01', humor_promedio: 1 }] }

  it('devuelve el día pedido o null', () => {
    expect(datoDeLaFecha(agregado, '2026-10-01')).toEqual(agregado.serie_temporal[0])
    expect(datoDeLaFecha(agregado, '2026-10-02')).toBeNull()
  })
})

describe('caritaComoTexto', () => {
  it('dibuja el SVG con el color del tipo de humor', () => {
    const svg = caritaComoTexto('positivo', 30)
    expect(svg).toContain('width="30"')
    expect(svg).toContain('#2ec4a0')
  })
})
