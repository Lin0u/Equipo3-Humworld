// HumWorld - acceso a la API REST del backend.
// Origen: HU-DASH-001-v3 y contrato docs/Contratos/contrato-dashboards.openapi.yaml.
// La dirección se configura con VITE_API_URL (archivo .env de Vite); por defecto,
// el backend de docker compose. El backend permite este origen por CORS (ADR-005).

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

// Tiempo máximo de espera de cada llamada. Valores propuestos, a ratificar por el equipo.
const TIMEOUT_MS = 10000
// La captura manual (HU-RSS-008) y el entrenamiento (HU-SENT-006) tardan más: una
// captura puede hacer hasta 4 intentos con timeouts de 5 s + 10 s y backoff
// (src/app/core/config.py), más el cálculo del humor; varias fuentes se capturan en
// serie. Con 10 s el navegador abandonaba la espera aunque el backend terminara bien.
export const TIMEOUT_LARGO_MS = 180000

// Error de la API con el código HTTP y el "codigo" de negocio que devuelve el
// backend (por ejemplo, TERMINO_DUPLICADO). El mensaje es el que manda la API,
// para mostrárselo al usuario tal cual (HU-ADMIN-004, decisión de diseño 5).
export class ErrorApi extends Error {
  constructor(mensaje, status, codigo) {
    super(mensaje)
    this.name = 'ErrorApi'
    this.status = status
    this.codigo = codigo
  }
}

async function errorDeRespuesta(respuesta) {
  let cuerpo = null
  try {
    cuerpo = await respuesta.json()
  } catch {
    // Respuesta sin cuerpo JSON: se usa el mensaje genérico.
  }
  const mensaje = cuerpo?.mensaje ?? `El servidor respondió con el código ${respuesta.status}.`
  return new ErrorApi(mensaje, respuesta.status, cuerpo?.codigo)
}

async function solicitar(ruta, { metodo = 'GET', cuerpo, timeoutMs = TIMEOUT_MS } = {}) {
  const control = new AbortController()
  const temporizador = setTimeout(() => control.abort(), timeoutMs)
  const opciones = { method: metodo, signal: control.signal }
  if (cuerpo !== undefined) {
    opciones.headers = { 'Content-Type': 'application/json' }
    opciones.body = JSON.stringify(cuerpo)
  }
  try {
    const respuesta = await fetch(`${API_URL}${ruta}`, opciones)
    if (!respuesta.ok) {
      throw await errorDeRespuesta(respuesta)
    }
    // 204 No Content (por ejemplo, DELETE): no hay cuerpo que leer.
    return respuesta.status === 204 ? null : await respuesta.json()
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

const obtenerJson = (ruta) => solicitar(ruta)

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

// Máximo de elementos por página que aceptan los listados paginados (HU-RSS-010).
const MAXIMO_POR_PAGINA = 50

// Todos los canales registrados (GET /channels, HU-RSS-010), recorriendo todas
// las páginas. Con continente, solo los de ese continente.
export async function obtenerCanales(continente = '') {
  const canales = []
  let pagina = 1
  let total = Infinity
  while ((pagina - 1) * MAXIMO_POR_PAGINA < total) {
    const consulta = agregarFiltros(
      new URLSearchParams({ pagina: String(pagina), tamanio_pagina: String(MAXIMO_POR_PAGINA) }),
      { continente },
    )
    const datos = await obtenerJson(`/channels?${consulta}`)
    canales.push(...datos.items)
    total = datos.total
    pagina += 1
  }
  return canales
}

// Países con canales registrados, para el filtro por país. Salen del campo "pais"
// de los canales: es el mismo dato con el que el backend filtra la nube y las noticias.
export async function obtenerPaises(continente = '') {
  const canales = await obtenerCanales(continente)
  const paises = new Set(canales.map((canal) => canal.pais).filter(Boolean))
  return [...paises].sort((a, b) => a.localeCompare(b, 'es'))
}

// GET /news (HU-DASH-002-v2): noticias más influyentes, paginadas y filtradas.
export function obtenerNoticias({ signo = 'todas', continente = '', pais = '', pagina = 1, tamanioPagina = 10 }) {
  const consulta = new URLSearchParams({
    orden: 'influencia',
    signo,
    pagina: String(pagina),
    tamanio_pagina: String(tamanioPagina),
  })
  agregarFiltros(consulta, { continente, pais })
  return obtenerJson(`/news?${consulta}`)
}

// --- Panel de administración (HU-ADMIN-004) --------------------------------
// Ningún endpoint es nuevo: el panel usa los que ya existen en la API.

// POST /channels (HU-RSS-001).
export function crearCanal({ nombre, continente, pais = '' }) {
  return solicitar('/channels', {
    metodo: 'POST',
    cuerpo: { nombre, continente, pais: pais || null },
  })
}

// GET /sources (HU-RSS-003-v2), paginado y con filtros opcionales.
export function obtenerFuentes({
  canalId = '',
  continente = '',
  categoriaIptc = '',
  activo = '',
  pagina = 1,
  tamanioPagina = 10,
} = {}) {
  const consulta = agregarFiltros(
    new URLSearchParams({ pagina: String(pagina), tamanio_pagina: String(tamanioPagina) }),
    { canal_id: canalId, continente, categoria_iptc: categoriaIptc, activo },
  )
  return obtenerJson(`/sources?${consulta}`)
}

// POST /sources (HU-RSS-002).
export function crearFuente({ canalId, url, categoriaIptc }) {
  return solicitar('/sources', {
    metodo: 'POST',
    cuerpo: { canal_id: Number(canalId), url, categoria_iptc: categoriaIptc },
  })
}

// PATCH /sources/{id} con "activo" (HU-RSS-004). Desactivar es la baja lógica
// de HU-RSS-005: la fuente se conserva y deja de capturarse.
export function cambiarEstadoFuente(id, activo) {
  return solicitar(`/sources/${id}`, { metodo: 'PATCH', cuerpo: { activo } })
}

// POST /sources/{id}/captures (HU-RSS-008): captura manual de una fuente.
export function capturarFuente(id) {
  return solicitar(`/sources/${id}/captures`, { metodo: 'POST', timeoutMs: TIMEOUT_LARGO_MS })
}

// POST /captures (HU-RSS-008): captura manual de varias fuentes.
export function capturarFuentes(ids) {
  return solicitar('/captures', { metodo: 'POST', cuerpo: { fuente_ids: ids }, timeoutMs: TIMEOUT_LARGO_MS })
}

// GET /dictionary (HU-SENT-001-v2), paginado y con búsqueda.
export function obtenerTerminos({ busqueda = '', pagina = 1, tamanioPagina = 25 } = {}) {
  const consulta = agregarFiltros(
    new URLSearchParams({ pagina: String(pagina), tamanio_pagina: String(tamanioPagina) }),
    { busqueda },
  )
  return obtenerJson(`/dictionary?${consulta}`)
}

// POST /dictionary (HU-SENT-001-v2).
export function crearTermino({ palabra, idioma, valor }) {
  return solicitar('/dictionary', { metodo: 'POST', cuerpo: { palabra, idioma, valor } })
}

// PATCH /dictionary/{id} (HU-SENT-001-v2).
export function actualizarTermino(id, cambios) {
  return solicitar(`/dictionary/${id}`, { metodo: 'PATCH', cuerpo: cambios })
}

// DELETE /dictionary/{id} (HU-SENT-001-v2).
export function eliminarTermino(id) {
  return solicitar(`/dictionary/${id}`, { metodo: 'DELETE' })
}

// GET /config (HU-RSS-007, HU-ADMIN-001).
export function obtenerConfiguracion() {
  return obtenerJson('/config')
}

// PUT /config (HU-RSS-007, HU-ADMIN-001).
export function guardarConfiguracion({ periodicidad, caducidad }) {
  return solicitar('/config', {
    metodo: 'PUT',
    cuerpo: { periodicidad_cron_minutos: periodicidad, caducidad_noticias_dias: caducidad },
  })
}

// DELETE /news (HU-ADMIN-003). Sin fecha, aplica la caducidad configurada.
export function purgarNoticias(fecha = '') {
  const consulta = fecha ? `?fecha_anterior_a=${encodeURIComponent(fecha)}` : ''
  return solicitar(`/news${consulta}`, { metodo: 'DELETE' })
}

// POST /trainings (HU-SENT-006).
export function entrenarModelo() {
  return solicitar('/trainings', { metodo: 'POST', timeoutMs: TIMEOUT_LARGO_MS })
}
