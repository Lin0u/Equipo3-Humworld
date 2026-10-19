import { describe, expect, it } from 'vitest'
import { nombreCategoria } from './iptc.js'

describe('nombreCategoria', () => {
  it('traduce el código IPTC de primer nivel', () => {
    expect(nombreCategoria('11000000')).toBe('Política')
  })

  it('devuelve el código si no lo conoce y null si no hay código', () => {
    expect(nombreCategoria('99000000')).toBe('99000000')
    expect(nombreCategoria(null)).toBeNull()
  })
})
