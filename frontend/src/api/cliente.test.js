// Pruebas del cliente de la API: se reemplaza fetch por un mock, sin backend real.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  obtenerMapa,
  obtenerNoticias,
  obtenerNubePalabras,
  obtenerPaises,
  obtenerSerieGlobal,
} from './cliente.js'

const BASE = 'http://localhost:8000/api/v1'

function respuesta(cuerpo, status = 200) {
  return Promise.resolve({ ok: status < 400, status, json: () => Promise.resolve(cuerpo) })
}

let fetchMock

beforeEach(() => {
  fetchMock = vi.fn(() => respuesta({}))
  vi.stubGlobal('fetch', fetchMock)
})

afterEach(() => {
  vi.unstubAllGlobals()
})

const rutaLlamada = (n = 0) => fetchMock.mock.calls[n][0].replace(BASE, '')

describe('rutas y filtros', () => {
  it('pide el mapa con o sin fecha', async () => {
    await obtenerMapa()
    await obtenerMapa('2026-10-01')
    expect(rutaLlamada(0)).toBe('/dashboards/map')
    expect(rutaLlamada(1)).toBe('/dashboards/map?fecha=2026-10-01')
  })

  it('pide la serie global con el rango', async () => {
    await obtenerSerieGlobal('2026-09-01', '2026-09-30')
    expect(rutaLlamada()).toBe('/sentiment?desde=2026-09-01&hasta=2026-09-30')
  })

  it('agrega a la nube solo los filtros con valor', async () => {
    await obtenerNubePalabras()
    await obtenerNubePalabras('África', '')
    await obtenerNubePalabras('', 'Chile')
    expect(rutaLlamada(0)).toBe('/dashboards/word-cloud')
    expect(rutaLlamada(1)).toBe('/dashboards/word-cloud?continente=%C3%81frica')
    expect(rutaLlamada(2)).toBe('/dashboards/word-cloud?pais=Chile')
  })

  it('pide las noticias por influencia con signo, país y página', async () => {
    await obtenerNoticias({ signo: 'negativas', pais: 'Chile', pagina: 2 })
    const consulta = new URLSearchParams(rutaLlamada().split('?')[1])
    expect(Object.fromEntries(consulta)).toEqual({
      orden: 'influencia',
      signo: 'negativas',
      pagina: '2',
      tamanio_pagina: '10',
      pais: 'Chile',
    })
  })
})

describe('obtenerPaises', () => {
  it('recorre todas las páginas de canales y devuelve países únicos ordenados', async () => {
    const pagina1 = Array.from({ length: 50 }, (_, i) => ({ pais: i % 2 ? 'Chile' : 'Perú' }))
    fetchMock
      .mockReturnValueOnce(respuesta({ items: pagina1, total: 52 }))
      .mockReturnValueOnce(respuesta({ items: [{ pais: 'Argentina' }, { pais: null }], total: 52 }))

    const paises = await obtenerPaises('América')

    expect(paises).toEqual(['Argentina', 'Chile', 'Perú'])
    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(rutaLlamada(1)).toBe('/channels?pagina=2&tamanio_pagina=50&continente=Am%C3%A9rica')
  })
})

describe('errores', () => {
  it('informa el código cuando el servidor responde con error', async () => {
    fetchMock.mockReturnValueOnce(respuesta({}, 500))
    await expect(obtenerMapa()).rejects.toThrow('El servidor respondió con el código 500.')
  })

  it('informa cuando no hay conexión', async () => {
    fetchMock.mockReturnValueOnce(Promise.reject(new TypeError('Failed to fetch')))
    await expect(obtenerMapa()).rejects.toThrow('No se pudo conectar con el servidor.')
  })

  it('informa cuando el servidor no responde a tiempo', async () => {
    const abortado = Object.assign(new Error('abort'), { name: 'AbortError' })
    fetchMock.mockReturnValueOnce(Promise.reject(abortado))
    await expect(obtenerMapa()).rejects.toThrow('El servidor no respondió a tiempo.')
  })

  it('propaga cualquier otro error sin cambiarlo', async () => {
    fetchMock.mockReturnValueOnce(Promise.reject(new Error('otro')))
    await expect(obtenerMapa()).rejects.toThrow('otro')
  })
})
