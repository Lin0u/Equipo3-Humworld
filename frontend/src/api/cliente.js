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

// Agrega a la consulta solo los filtros con valor (vacío = "todos").
function agregarFiltros(consulta, filtros) {
  for (const [clave, valor] of Object.entries(filtros)) {
    if (valor) consulta.set(clave, valor)
  }
  return consulta
}

// GET /dashboards/word-cloud (HU-DASH-003-v2, PDF §4.3.1: filtro por continente o
// país). Sin filtros: todo el mundo.
export function obtenerNubePalabras(continente = '', pais = '') {
  const consulta = agregarFiltros(new URLSearchParams(), { continente, pais }).toString()
  return obtenerJson(`/dashboards/word-cloud${consulta ? `?${consulta}` : ''}`)
}

// Máximo de canales por página que acepta GET /channels (HU-RSS-010).
const CANALES_POR_PAGINA = 50

// Países con canales registrados, para el filtro por país. Salen del campo "pais"
// de los canales (GET /channels, HU-RSS-010): es el mismo dato con el que el
// backend filtra la nube y las noticias. Recorre todas las páginas.
export async function obtenerPaises(continente = '') {
  const paises = new Set()
  let pagina = 1
  let total = Infinity
  while ((pagina - 1) * CANALES_POR_PAGINA < total) {
    const consulta = agregarFiltros(
      new URLSearchParams({ pagina: String(pagina), tamanio_pagina: String(CANALES_POR_PAGINA) }),
      { continente },
    )
    const datos = await obtenerJson(`/channels?${consulta}`)
    datos.items.forEach((canal) => canal.pais && paises.add(canal.pais))
    total = datos.total
    pagina += 1
  }
  return [...paises].sort((a, b) => a.localeCompare(b, 'es'))
}

// GET /news (HU-DASH-002-v2): noticias más influyentes, paginadas y filtradas.
export function obtenerNoticias({
  signo = 'todas',
  continente = '',
  pais = '',
  pagina = 1,
  tamanioPagina = 10,
}) {
  const consulta = new URLSearchParams({
    orden: 'influencia',
    signo,
    pagina: String(pagina),
    tamanio_pagina: String(tamanioPagina),
  })
  agregarFiltros(consulta, { continente, pais })
  return obtenerJson(`/news?${consulta}`)
}
