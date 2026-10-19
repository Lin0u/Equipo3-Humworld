import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { obtenerNubePalabras, obtenerPaises } from '../api/cliente.js'
import NubePalabras from './NubePalabras.jsx'

vi.mock('../api/cliente.js', () => ({ obtenerNubePalabras: vi.fn(), obtenerPaises: vi.fn() }))

const PALABRAS = {
  items: [
    { termino_id: 1, palabra: 'guerra', idioma: 'es', valor: -8, peso: 10 },
    { termino_id: 2, palabra: 'amor', idioma: 'es', valor: 6, peso: 5 },
  ],
}

beforeEach(() => {
  obtenerNubePalabras.mockReset().mockResolvedValue(PALABRAS)
  obtenerPaises.mockReset().mockResolvedValue(['Chile'])
})

describe('NubePalabras', () => {
  it('muestra las palabras en orden alfabético, con tamaño según su peso', async () => {
    render(<NubePalabras />)

    await screen.findByText('guerra')
    const nube = screen.getAllByRole('listitem').filter((li) => li.classList.contains('palabra'))
    expect(nube.map((li) => li.textContent)).toEqual(['amor', 'guerra'])
    expect(nube[1]).toHaveStyle({ fontSize: '50px' })
    expect(nube[1]).toHaveClass('texto-negativo')
    expect(nube[1]).toHaveAttribute('title', 'Valor -8 · aparece en 10 noticias · español')
  })

  it('filtra por continente y luego por país, y el continente borra el país', async () => {
    render(<NubePalabras />)
    await screen.findByText('guerra')

    await userEvent.selectOptions(screen.getByLabelText('Continente'), 'América')
    expect(obtenerNubePalabras).toHaveBeenLastCalledWith('América', '')

    await screen.findByRole('option', { name: 'Chile' })
    await userEvent.selectOptions(screen.getByLabelText('País'), 'Chile')
    expect(obtenerNubePalabras).toHaveBeenLastCalledWith('América', 'Chile')

    await userEvent.selectOptions(screen.getByLabelText('Continente'), 'Europa')
    expect(obtenerNubePalabras).toHaveBeenLastCalledWith('Europa', '')
  })

  it('avisa cuando no hay palabras', async () => {
    obtenerNubePalabras.mockResolvedValue({ items: [] })
    render(<NubePalabras />)
    expect(await screen.findByText('No hay palabras para este filtro.')).toBeInTheDocument()
  })

  it('muestra el error de la API', async () => {
    obtenerNubePalabras.mockRejectedValue(new Error('No se pudo conectar con el servidor.'))
    render(<NubePalabras />)
    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo conectar con el servidor.')
  })
})
