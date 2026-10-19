import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { obtenerNoticias, obtenerPaises } from '../api/cliente.js'
import ListadoNoticias from './ListadoNoticias.jsx'

vi.mock('../api/cliente.js', () => ({ obtenerNoticias: vi.fn(), obtenerPaises: vi.fn() }))

function noticia(id, valor, extra = {}) {
  return {
    id,
    titulo: `Noticia ${id}`,
    enlace_original: `https://example.test/${id}`,
    canal: 'Canal',
    continente: 'América',
    pais: 'Chile',
    categoria_iptc: '11000000',
    fecha_publicacion: '2026-10-02T09:15:00',
    fecha_registro: '2026-10-02T10:00:00',
    valor_humor: valor,
    ...extra,
  }
}

beforeEach(() => {
  obtenerNoticias.mockReset().mockResolvedValue({
    items: [noticia(1, -4.5), noticia(2, 2, { pais: null, categoria_iptc: null })],
    pagina: 1,
    tamanio_pagina: 10,
    total: 25,
  })
  obtenerPaises.mockReset().mockResolvedValue(['Chile'])
})

describe('ListadoNoticias', () => {
  it('muestra cada noticia con su humor, enlace y datos', async () => {
    render(<ListadoNoticias />)

    const enlace = await screen.findByRole('link', { name: 'Noticia 1' })
    expect(enlace).toHaveAttribute('href', 'https://example.test/1')
    expect(enlace).toHaveAttribute('target', '_blank')

    const primera = enlace.closest('li')
    expect(within(primera).getByText('-4.5')).toHaveClass('texto-negativo')
    expect(within(primera).getByText('Chile, América')).toBeInTheDocument()
    expect(within(primera).getByText('Política')).toBeInTheDocument()

    const segunda = screen.getByRole('link', { name: 'Noticia 2' }).closest('li')
    expect(within(segunda).getByText('América')).toBeInTheDocument()
    expect(within(segunda).getByText('+2.0')).toBeInTheDocument()
  })

  it('pagina y vuelve a la página 1 al cambiar un filtro', async () => {
    render(<ListadoNoticias />)
    expect(await screen.findByText('Página 1 de 3 · 25 noticias')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Anterior' })).toBeDisabled()

    await userEvent.click(screen.getByRole('button', { name: 'Siguiente' }))
    expect(obtenerNoticias).toHaveBeenLastCalledWith(expect.objectContaining({ pagina: 2 }))

    await screen.findByText('Página 2 de 3 · 25 noticias')
    await userEvent.click(screen.getByRole('button', { name: 'Anterior' }))
    expect(obtenerNoticias).toHaveBeenLastCalledWith(expect.objectContaining({ pagina: 1 }))

    await screen.findByText('Página 1 de 3 · 25 noticias')
    await userEvent.click(screen.getByRole('button', { name: 'Negativas' }))
    expect(obtenerNoticias).toHaveBeenLastCalledWith(
      expect.objectContaining({ signo: 'negativas', pagina: 1 }),
    )
    expect(screen.getByRole('button', { name: 'Negativas' })).toHaveAttribute('aria-pressed', 'true')
  })

  it('filtra por continente y país', async () => {
    render(<ListadoNoticias />)
    await screen.findByText('Noticia 1')

    await userEvent.selectOptions(screen.getByLabelText('Continente'), 'América')
    await screen.findByRole('option', { name: 'Chile' })
    await userEvent.selectOptions(screen.getByLabelText('País'), 'Chile')

    expect(obtenerNoticias).toHaveBeenLastCalledWith(
      expect.objectContaining({ continente: 'América', pais: 'Chile', pagina: 1 }),
    )
  })

  it('avisa cuando no hay noticias y oculta la paginación', async () => {
    obtenerNoticias.mockResolvedValue({ items: [], pagina: 1, tamanio_pagina: 10, total: 0 })
    render(<ListadoNoticias />)
    expect(await screen.findByText('No hay noticias para este filtro.')).toBeInTheDocument()
    expect(screen.queryByRole('navigation', { name: 'Páginas' })).not.toBeInTheDocument()
  })

  it('muestra el error de la API', async () => {
    obtenerNoticias.mockRejectedValue(new Error('El servidor respondió con el código 500.'))
    render(<ListadoNoticias />)
    expect(await screen.findByRole('alert')).toHaveTextContent('código 500')
  })
})
