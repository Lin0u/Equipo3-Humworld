import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { obtenerPaises } from '../api/cliente.js'
import SelectorPais from './SelectorPais.jsx'

vi.mock('../api/cliente.js', () => ({ obtenerPaises: vi.fn() }))

beforeEach(() => {
  obtenerPaises.mockReset()
})

describe('SelectorPais', () => {
  it('ofrece los países del continente elegido y avisa el cambio', async () => {
    obtenerPaises.mockResolvedValue(['Argentina', 'Chile'])
    const onCambio = vi.fn()
    render(<SelectorPais continente="América" valor="" onCambio={onCambio} />)

    const selector = screen.getByLabelText('País')
    expect(selector).toBeDisabled()
    expect(await screen.findByRole('option', { name: 'Chile' })).toBeInTheDocument()
    expect(obtenerPaises).toHaveBeenCalledWith('América')

    await userEvent.selectOptions(selector, 'Chile')
    expect(onCambio).toHaveBeenCalledWith('Chile')
  })

  it('queda deshabilitado si no hay países', async () => {
    obtenerPaises.mockResolvedValue([])
    render(<SelectorPais continente="Oceanía" valor="" onCambio={vi.fn()} />)

    expect(await screen.findByRole('option', { name: 'Todos' })).toBeInTheDocument()
    expect(screen.getByLabelText('País')).toBeDisabled()
  })

  it('indica que no está disponible si la API falla', async () => {
    obtenerPaises.mockRejectedValue(new Error('caída'))
    render(<SelectorPais continente="" valor="" onCambio={vi.fn()} />)

    expect(await screen.findByRole('option', { name: 'No disponible' })).toBeInTheDocument()
  })
})
