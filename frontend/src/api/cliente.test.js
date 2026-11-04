// Pruebas del cliente de la API: se reemplaza fetch por un mock, sin backend real.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  ErrorApi,
  TIMEOUT_LARGO_MS,
  actualizarTermino,
  cambiarEstadoFuente,
  capturarFuente,
  capturarFuentes,
  crearCanal,
  crearFuente,
  crearTermino,
  eliminarTermino,
  entrenarModelo,
  guardarConfiguracion,
  obtenerConfiguracion,
  obtenerFuentes,
  obtenerTerminos,
  purgarNoticias,
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

describe('panel de administración (HU-ADMIN-004)', () => {
  const llamada = (n = 0) => fetchMock.mock.calls[n][1]
  const cuerpo = (n = 0) => JSON.parse(llamada(n).body)

  it('crea canales y fuentes con POST y cuerpo JSON', async () => {
    await crearCanal({ nombre: 'BBC', continente: 'Europa' })
    await crearFuente({ canalId: '3', url: 'https://x.test/rss', categoriaIptc: '11000000' })
    expect(rutaLlamada(0)).toBe('/channels')
    expect(llamada(0).method).toBe('POST')
    expect(llamada(0).headers).toEqual({ 'Content-Type': 'application/json' })
    expect(cuerpo(0)).toEqual({ nombre: 'BBC', continente: 'Europa', pais: null })
    expect(cuerpo(1)).toEqual({ canal_id: 3, url: 'https://x.test/rss', categoria_iptc: '11000000' })
  })

  it('lista fuentes con solo los filtros con valor', async () => {
    await obtenerFuentes({ continente: 'Asia', activo: 'false', pagina: 2 })
    await obtenerFuentes()
    expect(rutaLlamada(0)).toBe('/sources?pagina=2&tamanio_pagina=10&continente=Asia&activo=false')
    expect(rutaLlamada(1)).toBe('/sources?pagina=1&tamanio_pagina=10')
  })

  it('desactiva y captura fuentes', async () => {
    await cambiarEstadoFuente(7, false)
    await capturarFuente(7)
    await capturarFuentes([7, 8])
    expect(llamada(0).method).toBe('PATCH')
    expect(cuerpo(0)).toEqual({ activo: false })
    expect(rutaLlamada(1)).toBe('/sources/7/captures')
    expect(llamada(1).body).toBeUndefined()
    expect(rutaLlamada(2)).toBe('/captures')
    expect(cuerpo(2)).toEqual({ fuente_ids: [7, 8] })
  })

  it('opera sobre el diccionario', async () => {
    await obtenerTerminos({ busqueda: 'guerra' })
    await crearTermino({ palabra: 'paz', idioma: 'es', valor: 7 })
    await actualizarTermino(4, { valor: 3 })
    fetchMock.mockReturnValueOnce(Promise.resolve({ ok: true, status: 204 }))
    const borrado = await eliminarTermino(4)
    expect(rutaLlamada(0)).toBe('/dictionary?pagina=1&tamanio_pagina=25&busqueda=guerra')
    expect(cuerpo(1)).toEqual({ palabra: 'paz', idioma: 'es', valor: 7 })
    expect(llamada(2).method).toBe('PATCH')
    expect(llamada(3).method).toBe('DELETE')
    expect(borrado).toBeNull()
  })

  it('lee y guarda la configuración, purga y entrena', async () => {
    await obtenerConfiguracion()
    await guardarConfiguracion({ periodicidad: 30, caducidad: 90 })
    await purgarNoticias('2026-01-01')
    await purgarNoticias()
    await entrenarModelo()
    expect(rutaLlamada(0)).toBe('/config')
    expect(llamada(1).method).toBe('PUT')
    expect(cuerpo(1)).toEqual({ periodicidad_cron_minutos: 30, caducidad_noticias_dias: 90 })
    expect(rutaLlamada(2)).toBe('/news?fecha_anterior_a=2026-01-01')
    expect(rutaLlamada(3)).toBe('/news')
    expect(rutaLlamada(4)).toBe('/trainings')
  })

  it('espera más tiempo en la captura y el entrenamiento', async () => {
    const espera = vi.spyOn(globalThis, 'setTimeout')
    await obtenerConfiguracion()
    await capturarFuente(1)
    await entrenarModelo()
    expect(espera.mock.calls.map((llamada) => llamada[1])).toEqual([10000, TIMEOUT_LARGO_MS, TIMEOUT_LARGO_MS])
    espera.mockRestore()
  })

  it('usa el mensaje y el código de negocio que devuelve la API', async () => {
    fetchMock.mockReturnValueOnce(respuesta({ codigo: 'TERMINO_DUPLICADO', mensaje: 'Ya existe.' }, 409))
    const error = await crearTermino({ palabra: 'paz', idioma: 'es', valor: 7 }).catch((e) => e)
    expect(error).toBeInstanceOf(ErrorApi)
    expect(error.message).toBe('Ya existe.')
    expect(error.status).toBe(409)
    expect(error.codigo).toBe('TERMINO_DUPLICADO')
  })

  it('usa el mensaje genérico si el error no trae cuerpo JSON', async () => {
    fetchMock.mockReturnValueOnce(
      Promise.resolve({ ok: false, status: 502, json: () => Promise.reject(new SyntaxError('x')) }),
    )
    await expect(obtenerConfiguracion()).rejects.toThrow('El servidor respondió con el código 502.')
  })
})
