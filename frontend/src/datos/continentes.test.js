import { describe, expect, it } from 'vitest'
import { buscarContinente } from './continentes.js'

describe('buscarContinente', () => {
  it('reconoce el nombre con o sin tildes y en inglés', () => {
    expect(buscarContinente('África').nombre).toBe('África')
    expect(buscarContinente('africa').nombre).toBe('África')
    expect(buscarContinente('Europe').nombre).toBe('Europa')
  })

  it('devuelve null si no lo reconoce o no hay nombre', () => {
    expect(buscarContinente('Antártida')).toBeNull()
    expect(buscarContinente('')).toBeNull()
  })
})
