import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { obtenerMapa } from './api/cliente.js'
import App from './App.jsx'

// El mapa (Leaflet) y las otras pantallas tienen sus propias pruebas o necesitan
// un navegador real; aquí se reemplazan por piezas simples.
vi.mock('./api/cliente.js', () => ({ obtenerMapa: vi.fn() }))
vi.mock('./pantallas/MapaHumor.jsx', () => ({
  default: ({ cargando, error, alCambiarFecha }) => (
    <div>
      <p>{cargando ? 'mapa cargando' : `mapa listo ${error ?? ''}`}</p>
      <button type="button" onClick={() => alCambiarFecha('2026-10-01')}>
        elegir fecha
      </button>
    </div>
  ),
}))
vi.mock('./pantallas/NubePalabras.jsx', () => ({ default: () => <p>pantalla nube</p> }))
vi.mock('./pantallas/ListadoNoticias.jsx', () => ({ default: () => <p>pantalla noticias</p> }))

beforeEach(() => {
  obtenerMapa.mockReset().mockResolvedValue({ global: { humor_promedio: 1.25 } })
})

describe('App', () => {
  it('muestra el humor global en la cabecera y cambia de pantalla', async () => {
    render(<App />)

    expect(await screen.findByText('+1.3')).toHaveClass('texto-positivo')
    expect(screen.getByText(/mapa listo/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Mapa de humor' })).toHaveAttribute('aria-current', 'page')

    await userEvent.click(screen.getByRole('button', { name: 'Nube de palabras' }))
    expect(screen.getByText('pantalla nube')).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Noticias' }))
    expect(screen.getByText('pantalla noticias')).toBeInTheDocument()
  })

  it('vuelve a pedir el mapa al cambiar la fecha', async () => {
    render(<App />)
    await screen.findByText(/mapa listo/)

    await userEvent.click(screen.getByRole('button', { name: 'elegir fecha' }))

    expect(obtenerMapa).toHaveBeenLastCalledWith('2026-10-01')
  })

  it('pasa el error de la API al mapa', async () => {
    obtenerMapa.mockRejectedValue(new Error('sin conexión'))
    render(<App />)
    expect(await screen.findByText('mapa listo sin conexión')).toBeInTheDocument()
    expect(screen.getByText('Sin datos')).toBeInTheDocument()
  })
})
