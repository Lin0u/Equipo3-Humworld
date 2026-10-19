// HumWorld - acceso a la API REST del backend.
// Origen: HU-DASH-001-v3 y contrato docs/Contratos/contrato-dashboards.openapi.yaml.
// La dirección se configura con VITE_API_URL (archivo .env de Vite); por defecto,
// el backend de docker compose. El backend permite este origen por CORS (ADR-05).

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

// Tiempo máximo de espera de cada llamada. Valor propuesto, a ratificar por el equipo.
const TIMEOUT_MS = 10000

async function obtenerJson(ruta) {
  const control = new AbortController()
  const temporizador = setTimeout(() => control.abort(), TIMEOUT_MS)
  try {
    const respuesta = await fetch(`${API_URL}${ruta}`, { signal: control.signal })
    if (!respuesta.ok) {
      throw new Error(`El servidor respondió con el código ${respuesta.status}.`)
    }
    return await respuesta.json()
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('El servidor no respondió a tiempo.', { cause: error })
    }
    if (error instanceof TypeError) {
      throw new Error('No se pudo conectar con el servidor.', { cause: error })
    }
    throw error
  } finally {
    clearTimeout(temporizador)
  }
}

// GET /dashboards/map. Sin fecha, el backend devuelve el último día con datos.
export function obtenerMapa(fecha) {
  const consulta = fecha ? `?fecha=${encodeURIComponent(fecha)}` : ''
  return obtenerJson(`/dashboards/map${consulta}`)
}

// GET /sentiment con rango: humor global día por día (HU-SENT-004).
export function obtenerSerieGlobal(desde, hasta) {
  const consulta = new URLSearchParams({ desde, hasta })
  return obtenerJson(`/sentiment?${consulta}`)
}
