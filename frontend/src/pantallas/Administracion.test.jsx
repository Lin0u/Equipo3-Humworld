// Pruebas del panel de administración (HU-ADMIN-004). La API se reemplaza por mocks.
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import * as api from '../api/cliente.js'
import Administracion from './Administracion.jsx'

vi.mock('../api/cliente.js', () => ({
  obtenerCanales: vi.fn(),
  obtenerFuentes: vi.fn(),
  crearCanal: vi.fn(),
  crearFuente: vi.fn(),
  cambiarEstadoFuente: vi.fn(),
  capturarFuente: vi.fn(),
  capturarFuentes: vi.fn(),
  obtenerTerminos: vi.fn(),
  crearTermino: vi.fn(),
  actualizarTermino: vi.fn(),
  eliminarTermino: vi.fn(),
  obtenerConfiguracion: vi.fn(),
  guardarConfiguracion: vi.fn(),
  purgarNoticias: vi.fn(),
  entrenarModelo: vi.fn(),
}))

function fuente(id, extra = {}) {
  return {
    id,
    canal_id: 1,
    url: `https://medio.test/rss/${id}`,
    categoria_iptc: '11000000',
    activo: true,
    fecha_ultima_captura_exitosa: null,
    estado_circuit_breaker: 'cerrado',
    ...extra,
  }
}

let confirmar

beforeEach(() => {
  vi.resetAllMocks()
  api.obtenerCanales.mockResolvedValue([{ id: 1, nombre: 'BBC Mundo', continente: 'Europa', pais: 'Reino Unido' }])
  api.obtenerFuentes.mockResolvedValue({
    items: [fuente(1), fuente(2, { activo: false, estado_circuit_breaker: 'abierto' })],
    pagina: 1,
    tamanio_pagina: 10,
    total: 2,
  })
  api.obtenerTerminos.mockResolvedValue({
    items: [{ id: 5, palabra: 'guerra', idioma: 'es', valor: -8 }],
    pagina: 1,
    tamanio_pagina: 25,
    total: 1,
  })
  api.obtenerConfiguracion.mockResolvedValue({ periodicidad_cron_minutos: 60, caducidad_noticias_dias: 90 })
  confirmar = vi.spyOn(window, 'confirm').mockReturnValue(true)
})

afterEach(() => {
  confirmar.mockRestore()
})

async function abrir(pestana) {
  const usuario = userEvent.setup()
  render(<Administracion />)
  if (pestana) await usuario.click(screen.getByRole('tab', { name: pestana }))
  return usuario
}

describe('pestañas', () => {
  it('parte en Fuentes RSS y cambia de pestaña', async () => {
    const usuario = await abrir()
    expect(screen.getByRole('tab', { name: 'Fuentes RSS' })).toHaveAttribute('aria-selected', 'true')
    await usuario.click(screen.getByRole('tab', { name: 'Modelo ML' }))
    expect(screen.getByRole('tab', { name: 'Modelo ML' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByRole('button', { name: 'Entrenar modelo' })).toBeInTheDocument()
  })
})

describe('Fuentes RSS', () => {
  it('muestra las fuentes con el nombre del canal y su estado', async () => {
    await abrir()
    const fila = (await screen.findByText('https://medio.test/rss/2')).closest('tr')
    expect(within(fila).getByText('BBC Mundo')).toBeInTheDocument()
    expect(within(fila).getByText('Política')).toBeInTheDocument()
    expect(within(fila).getByText('Abierto')).toBeInTheDocument()
    expect(within(fila).getByRole('button', { name: 'Reactivar' })).toBeInTheDocument()
    expect(within(fila).getByRole('button', { name: 'Capturar ahora' })).toBeDisabled()
  })

  it('filtra y vuelve a la primera página', async () => {
    const usuario = await abrir()
    await screen.findByText('https://medio.test/rss/1')
    await usuario.selectOptions(screen.getByLabelText('Estado'), 'false')
    await waitFor(() =>
      expect(api.obtenerFuentes).toHaveBeenLastCalledWith(
        expect.objectContaining({ activo: 'false', pagina: 1, tamanioPagina: 10 }),
      ),
    )
  })

  it('pagina de 10 en 10', async () => {
    api.obtenerFuentes.mockResolvedValue({ items: [fuente(1)], pagina: 1, tamanio_pagina: 10, total: 15 })
    const usuario = await abrir()
    await usuario.click(await screen.findByRole('button', { name: 'Siguiente' }))
    await waitFor(() => expect(api.obtenerFuentes).toHaveBeenLastCalledWith(expect.objectContaining({ pagina: 2 })))
    expect(screen.getByText('Página 2 de 2')).toBeInTheDocument()
    await usuario.click(screen.getByRole('button', { name: 'Anterior' }))
    expect(screen.getByText('Página 1 de 2')).toBeInTheDocument()
  })

  it('crea un canal y recarga la lista de canales', async () => {
    api.crearCanal.mockResolvedValue({ id: 2 })
    const usuario = await abrir()
    const formulario = screen.getByRole('form', { name: 'Nuevo canal' })
    const boton = within(formulario).getByRole('button', { name: 'Agregar canal' })
    expect(boton).toBeDisabled()
    await usuario.type(within(formulario).getByLabelText('Canal'), 'El País')
    await usuario.selectOptions(within(formulario).getByLabelText('Continente'), 'Europa')
    await usuario.type(within(formulario).getByLabelText('País'), 'España')
    await usuario.click(boton)
    expect(api.crearCanal).toHaveBeenCalledWith({ nombre: 'El País', continente: 'Europa', pais: 'España' })
    expect(await screen.findByText('Canal "El País" creado.')).toBeInTheDocument()
    expect(api.obtenerCanales).toHaveBeenCalledTimes(2)
  })

  it('valida la URL y crea la fuente', async () => {
    api.crearFuente.mockResolvedValue({ id: 3 })
    const usuario = await abrir()
    const formulario = screen.getByRole('form', { name: 'Nueva fuente' })
    await screen.findByText('https://medio.test/rss/1')
    await usuario.selectOptions(within(formulario).getByLabelText('Canal de la fuente'), '1')
    await usuario.selectOptions(within(formulario).getByLabelText('Categoría'), '15000000')
    await usuario.type(within(formulario).getByLabelText('URL'), 'medio.test')
    expect(screen.getByText('La URL debe empezar con http:// o https://.')).toBeInTheDocument()
    const boton = within(formulario).getByRole('button', { name: 'Agregar fuente' })
    expect(boton).toBeDisabled()
    await usuario.clear(within(formulario).getByLabelText('URL'))
    await usuario.type(within(formulario).getByLabelText('URL'), 'https://medio.test/deportes')
    await usuario.click(boton)
    expect(api.crearFuente).toHaveBeenCalledWith({
      canalId: '1',
      url: 'https://medio.test/deportes',
      categoriaIptc: '15000000',
    })
    expect(await screen.findByText('Fuente creada.')).toBeInTheDocument()
  })

  it('muestra el mensaje de error de la API', async () => {
    api.crearCanal.mockRejectedValue(new Error('Los datos enviados no son válidos.'))
    const usuario = await abrir()
    const formulario = screen.getByRole('form', { name: 'Nuevo canal' })
    await usuario.type(within(formulario).getByLabelText('Canal'), 'X')
    await usuario.selectOptions(within(formulario).getByLabelText('Continente'), 'Asia')
    await usuario.click(within(formulario).getByRole('button', { name: 'Agregar canal' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Los datos enviados no son válidos.')
  })

  it('desactiva solo si se confirma', async () => {
    api.cambiarEstadoFuente.mockResolvedValue({})
    const usuario = await abrir()
    const fila = (await screen.findByText('https://medio.test/rss/1')).closest('tr')
    confirmar.mockReturnValueOnce(false)
    await usuario.click(within(fila).getByRole('button', { name: 'Desactivar' }))
    expect(api.cambiarEstadoFuente).not.toHaveBeenCalled()
    await usuario.click(within(fila).getByRole('button', { name: 'Desactivar' }))
    expect(api.cambiarEstadoFuente).toHaveBeenCalledWith(1, false)
    expect(await screen.findByText('Fuente desactivada.')).toBeInTheDocument()
  })

  it('reactiva sin pedir confirmación', async () => {
    api.cambiarEstadoFuente.mockResolvedValue({})
    const usuario = await abrir()
    const fila = (await screen.findByText('https://medio.test/rss/2')).closest('tr')
    await usuario.click(within(fila).getByRole('button', { name: 'Reactivar' }))
    expect(confirmar).not.toHaveBeenCalled()
    expect(api.cambiarEstadoFuente).toHaveBeenCalledWith(2, true)
  })

  it('captura una fuente y muestra el resultado', async () => {
    api.capturarFuente.mockResolvedValue({ fuente_id: 1, estado: 'exitosa', noticias_nuevas: 4, mensaje: null })
    const usuario = await abrir()
    const fila = (await screen.findByText('https://medio.test/rss/1')).closest('tr')
    await usuario.click(within(fila).getByRole('button', { name: 'Capturar ahora' }))
    expect(api.capturarFuente).toHaveBeenCalledWith(1)
    expect(await screen.findByText('Fuente 1: exitosa, 4 noticias nuevas.')).toBeInTheDocument()
  })

  it('captura varias fuentes seleccionadas', async () => {
    api.obtenerFuentes.mockResolvedValue({ items: [fuente(1), fuente(3)], pagina: 1, tamanio_pagina: 10, total: 2 })
    api.capturarFuentes.mockResolvedValue([
      { fuente_id: 1, estado: 'fallida_transitoria', noticias_nuevas: 0, mensaje: 'Tiempo agotado.' },
      { fuente_id: 3, estado: 'fallida_circuito_abierto', noticias_nuevas: 0, mensaje: null },
    ])
    const usuario = await abrir()
    await usuario.click(await screen.findByLabelText('Seleccionar https://medio.test/rss/1'))
    await usuario.click(screen.getByLabelText('Seleccionar https://medio.test/rss/3'))
    await usuario.click(screen.getByLabelText('Seleccionar https://medio.test/rss/3'))
    await usuario.click(screen.getByLabelText('Seleccionar https://medio.test/rss/3'))
    await usuario.click(screen.getByRole('button', { name: 'Capturar seleccionadas (2)' }))
    expect(api.capturarFuentes).toHaveBeenCalledWith([1, 3])
    expect(
      await screen.findByText('Fuente 1: falló (error transitorio), 0 noticias nuevas. Tiempo agotado.'),
    ).toBeInTheDocument()
    expect(screen.getByText('Fuente 3: no se intentó (circuito abierto), 0 noticias nuevas.')).toBeInTheDocument()
  })

  it('informa un error de captura', async () => {
    api.capturarFuente.mockRejectedValue(new Error('La fuente está inactiva.'))
    const usuario = await abrir()
    const fila = (await screen.findByText('https://medio.test/rss/1')).closest('tr')
    await usuario.click(within(fila).getByRole('button', { name: 'Capturar ahora' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('La fuente está inactiva.')
  })

  it('informa si no puede cargar canales ni fuentes', async () => {
    api.obtenerCanales.mockRejectedValue(new Error('No se pudo conectar con el servidor.'))
    api.obtenerFuentes.mockRejectedValue(new Error('No se pudo conectar con el servidor.'))
    await abrir()
    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo conectar con el servidor.')
  })
})

describe('Diccionario', () => {
  it('crea un término validando la escala -10..+10', async () => {
    api.crearTermino.mockResolvedValue({ id: 6 })
    const usuario = await abrir('Diccionario')
    const formulario = screen.getByRole('form', { name: 'Nuevo término' })
    await usuario.type(within(formulario).getByLabelText('Palabra'), 'paz')
    await usuario.type(within(formulario).getByLabelText('Valor'), '11')
    expect(screen.getByText('El valor debe ser un entero entre -10 y +10.')).toBeInTheDocument()
    expect(within(formulario).getByRole('button', { name: 'Agregar' })).toBeDisabled()
    await usuario.clear(within(formulario).getByLabelText('Valor'))
    await usuario.type(within(formulario).getByLabelText('Valor'), '7')
    await usuario.selectOptions(within(formulario).getByLabelText('Idioma'), 'en')
    await usuario.click(within(formulario).getByRole('button', { name: 'Agregar' }))
    expect(api.crearTermino).toHaveBeenCalledWith({ palabra: 'paz', idioma: 'en', valor: 7 })
    expect(await screen.findByRole('status')).toHaveTextContent(
      'Término "paz" creado. El humor de las noticias se recalculará en el próximo barrido.',
    )
  })

  it('muestra el error de término duplicado', async () => {
    api.crearTermino.mockRejectedValue(new Error('El término ya existe en ese idioma.'))
    const usuario = await abrir('Diccionario')
    const formulario = screen.getByRole('form', { name: 'Nuevo término' })
    await usuario.type(within(formulario).getByLabelText('Palabra'), 'guerra')
    await usuario.type(within(formulario).getByLabelText('Valor'), '-8')
    await usuario.click(within(formulario).getByRole('button', { name: 'Agregar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('El término ya existe en ese idioma.')
  })

  it('busca desde la primera página', async () => {
    const usuario = await abrir('Diccionario')
    await screen.findByText('guerra')
    await usuario.type(screen.getByLabelText('Buscar'), 'g')
    await waitFor(() =>
      expect(api.obtenerTerminos).toHaveBeenLastCalledWith({ busqueda: 'g', pagina: 1, tamanioPagina: 25 }),
    )
  })

  it('edita el valor y permite cancelar', async () => {
    api.actualizarTermino.mockResolvedValue({})
    const usuario = await abrir('Diccionario')
    await usuario.click(await screen.findByRole('button', { name: 'Editar' }))
    await usuario.click(screen.getByRole('button', { name: 'Cancelar' }))
    expect(screen.queryByLabelText('Nuevo valor de guerra')).not.toBeInTheDocument()
    await usuario.click(screen.getByRole('button', { name: 'Editar' }))
    const campo = screen.getByLabelText('Nuevo valor de guerra')
    await usuario.clear(campo)
    await usuario.type(campo, '-9')
    await usuario.click(screen.getByRole('button', { name: 'Guardar' }))
    expect(api.actualizarTermino).toHaveBeenCalledWith(5, { valor: -9 })
    expect(await screen.findByRole('status')).toHaveTextContent('Valor actualizado.')
  })

  it('elimina solo si se confirma', async () => {
    api.eliminarTermino.mockResolvedValue(null)
    const usuario = await abrir('Diccionario')
    await screen.findByText('guerra')
    confirmar.mockReturnValueOnce(false)
    await usuario.click(screen.getByRole('button', { name: 'Eliminar' }))
    expect(api.eliminarTermino).not.toHaveBeenCalled()
    await usuario.click(screen.getByRole('button', { name: 'Eliminar' }))
    expect(api.eliminarTermino).toHaveBeenCalledWith(5)
  })

  it('pagina de 25 en 25', async () => {
    api.obtenerTerminos.mockResolvedValue({ items: [], pagina: 1, tamanio_pagina: 25, total: 60 })
    const usuario = await abrir('Diccionario')
    await usuario.click(await screen.findByRole('button', { name: 'Siguiente' }))
    expect(screen.getByText('Página 2 de 3')).toBeInTheDocument()
    await usuario.click(screen.getByRole('button', { name: 'Anterior' }))
    expect(screen.getByText('Página 1 de 3')).toBeInTheDocument()
  })

  it('informa si no puede cargar el diccionario', async () => {
    api.obtenerTerminos.mockRejectedValue(new Error('El servidor no respondió a tiempo.'))
    await abrir('Diccionario')
    expect(await screen.findByRole('alert')).toHaveTextContent('El servidor no respondió a tiempo.')
  })
})

describe('Parámetros', () => {
  it('carga, valida y guarda los parámetros', async () => {
    api.guardarConfiguracion.mockResolvedValue({ periodicidad_cron_minutos: 30, caducidad_noticias_dias: 90 })
    const usuario = await abrir('Parámetros')
    const periodicidad = await screen.findByLabelText('Periodicidad del cron (minutos)')
    expect(periodicidad).toHaveValue(60)
    expect(screen.getByLabelText('Caducidad de las noticias (días)')).toHaveValue(90)
    await usuario.clear(periodicidad)
    await usuario.type(periodicidad, '0')
    expect(screen.getByText('Los dos valores deben ser enteros mayores o iguales a 1.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Guardar' })).toBeDisabled()
    await usuario.clear(periodicidad)
    await usuario.type(periodicidad, '30')
    await usuario.click(screen.getByRole('button', { name: 'Guardar' }))
    expect(api.guardarConfiguracion).toHaveBeenCalledWith({ periodicidad: 30, caducidad: 90 })
    expect(await screen.findByRole('status')).toHaveTextContent('Parámetros guardados.')
  })

  it('muestra el error al guardar', async () => {
    api.guardarConfiguracion.mockRejectedValue(new Error('Los datos enviados no son válidos.'))
    const usuario = await abrir('Parámetros')
    await screen.findByLabelText('Periodicidad del cron (minutos)')
    await usuario.click(screen.getByRole('button', { name: 'Guardar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Los datos enviados no son válidos.')
  })

  it('muestra el error si no puede cargar', async () => {
    api.obtenerConfiguracion.mockRejectedValue(new Error('No se pudo conectar con el servidor.'))
    await abrir('Parámetros')
    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo conectar con el servidor.')
  })
})

describe('Purgado', () => {
  it('no purga si se cancela la confirmación', async () => {
    const usuario = await abrir('Purgado')
    confirmar.mockReturnValueOnce(false)
    await usuario.click(screen.getByRole('button', { name: 'Purgar según caducidad' }))
    expect(api.purgarNoticias).not.toHaveBeenCalled()
  })

  it('purga según la caducidad configurada', async () => {
    api.purgarNoticias.mockResolvedValue({ noticias_eliminadas: 12 })
    const usuario = await abrir('Purgado')
    await usuario.click(screen.getByRole('button', { name: 'Purgar según caducidad' }))
    expect(api.purgarNoticias).toHaveBeenCalledWith('')
    expect(await screen.findByRole('status')).toHaveTextContent('Se eliminaron 12 noticias.')
  })

  it('purga antes de una fecha', async () => {
    api.purgarNoticias.mockResolvedValue({ noticias_eliminadas: 3 })
    const usuario = await abrir('Purgado')
    expect(screen.getByRole('button', { name: 'Purgar' })).toBeDisabled()
    await usuario.type(screen.getByLabelText('Eliminar las registradas antes del'), '2026-01-15')
    await usuario.click(screen.getByRole('button', { name: 'Purgar' }))
    expect(confirmar).toHaveBeenCalledWith(expect.stringContaining('antes del 2026-01-15'))
    expect(api.purgarNoticias).toHaveBeenCalledWith('2026-01-15')
    expect(await screen.findByText('Se eliminaron 3 noticias.')).toBeInTheDocument()
  })

  it('muestra el error de la API', async () => {
    api.purgarNoticias.mockRejectedValue(new Error('La fecha no puede ser futura.'))
    const usuario = await abrir('Purgado')
    await usuario.click(screen.getByRole('button', { name: 'Purgar según caducidad' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('La fecha no puede ser futura.')
  })
})

describe('Modelo ML', () => {
  it('entrena y muestra la versión activa', async () => {
    api.entrenarModelo.mockResolvedValue({ version: 2, mae_evaluacion: 1.234 })
    const usuario = await abrir('Modelo ML')
    await usuario.click(screen.getByRole('button', { name: 'Entrenar modelo' }))
    expect(await screen.findByRole('status')).toHaveTextContent(
      'Versión 2 activa (MAE contra diccionario: 1.23).',
    )
  })

  it('muestra el error de datos insuficientes', async () => {
    api.entrenarModelo.mockRejectedValue(new Error('No hay suficientes noticias para entrenar.'))
    const usuario = await abrir('Modelo ML')
    await usuario.click(screen.getByRole('button', { name: 'Entrenar modelo' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('No hay suficientes noticias para entrenar.')
  })
})
