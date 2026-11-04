// HumWorld - pestaña "Fuentes RSS" del panel de administración.
// Origen: HU-RSS-001 (alta de canal), HU-RSS-002 (alta de fuente), HU-RSS-003-v2
// (consulta con filtros), HU-RSS-004 y HU-RSS-005 (desactivar/reactivar: baja
// lógica) y HU-RSS-008 (captura manual). PDF §4.1 punto 4 y §4.2.1.
import { useEffect, useState } from 'react'
import {
  cambiarEstadoFuente,
  capturarFuente,
  capturarFuentes,
  crearCanal,
  crearFuente,
  obtenerCanales,
  obtenerFuentes,
} from '../../api/cliente.js'
import { LISTA_CATEGORIAS_IPTC, nombreCategoria } from '../../utilidades/iptc.js'
import Aviso from './Aviso.jsx'

const POR_PAGINA = 10
const CONTINENTES = ['América', 'Europa', 'Asia', 'África', 'Oceanía']
const ESTADOS_CIRCUITO = { cerrado: 'Cerrado', abierto: 'Abierto', semi_abierto: 'Semiabierto' }
const ESTADOS_CAPTURA = {
  exitosa: 'exitosa',
  fallida_transitoria: 'falló (error transitorio)',
  fallida_circuito_abierto: 'no se intentó (circuito abierto)',
}
const FILTROS_VACIOS = { canalId: '', continente: '', categoriaIptc: '', activo: '' }

// Texto de un resultado de captura (HU-RSS-008): estado, noticias nuevas y mensaje.
function textoResultado(resultado) {
  const estado = ESTADOS_CAPTURA[resultado.estado] ?? resultado.estado
  const detalle = resultado.mensaje ? ` ${resultado.mensaje}` : ''
  return `Fuente ${resultado.fuente_id}: ${estado}, ${resultado.noticias_nuevas} noticias nuevas.${detalle}`
}

function formatoFecha(valor) {
  return valor ? new Date(valor).toLocaleString('es-CL') : 'Nunca'
}

function urlValida(texto) {
  try {
    const url = new URL(texto)
    return url.protocol === 'http:' || url.protocol === 'https:'
  } catch {
    return false
  }
}

export default function FuentesAdmin() {
  const [canales, setCanales] = useState([])
  const [versionCanales, setVersionCanales] = useState(0)
  const [filtros, setFiltros] = useState(FILTROS_VACIOS)
  const [pagina, setPagina] = useState(1)
  const [version, setVersion] = useState(0)
  const [resultado, setResultado] = useState(null)
  const [seleccion, setSeleccion] = useState([])
  const [aviso, setAviso] = useState(null)
  const [capturas, setCapturas] = useState([])
  const [enCurso, setEnCurso] = useState(false)
  const [nuevaFuente, setNuevaFuente] = useState({ canalId: '', url: '', categoriaIptc: '' })
  const [nuevoCanal, setNuevoCanal] = useState({ nombre: '', continente: '', pais: '' })

  useEffect(() => {
    let vigente = true
    obtenerCanales()
      .then((lista) => vigente && setCanales(lista))
      .catch((causa) => vigente && setAviso({ tipo: 'error', texto: causa.message }))
    return () => {
      vigente = false
    }
  }, [versionCanales])

  useEffect(() => {
    let vigente = true
    obtenerFuentes({ ...filtros, pagina, tamanioPagina: POR_PAGINA })
      .then((datos) => vigente && setResultado(datos))
      .catch((causa) => vigente && setAviso({ tipo: 'error', texto: causa.message }))
    return () => {
      vigente = false
    }
  }, [filtros, pagina, version])

  const nombreCanal = (id) => canales.find((canal) => canal.id === id)?.nombre ?? `Canal ${id}`

  function cambiarFiltro(clave, valor) {
    setFiltros({ ...filtros, [clave]: valor })
    setPagina(1)
    setSeleccion([])
  }

  function recargar() {
    setVersion((v) => v + 1)
  }

  async function ejecutar(accion, textoExito) {
    try {
      await accion()
      setAviso({ tipo: 'exito', texto: textoExito })
      return true
    } catch (causa) {
      setAviso({ tipo: 'error', texto: causa.message })
      return false
    }
  }

  async function agregarCanal(evento) {
    evento.preventDefault()
    const nombre = nuevoCanal.nombre.trim()
    const ok = await ejecutar(
      () => crearCanal({ nombre, continente: nuevoCanal.continente, pais: nuevoCanal.pais.trim() }),
      `Canal "${nombre}" creado.`,
    )
    if (ok) {
      setNuevoCanal({ nombre: '', continente: '', pais: '' })
      setVersionCanales((v) => v + 1)
    }
  }

  async function agregarFuente(evento) {
    evento.preventDefault()
    const ok = await ejecutar(() => crearFuente({ ...nuevaFuente, url: nuevaFuente.url.trim() }), 'Fuente creada.')
    if (ok) {
      setNuevaFuente({ canalId: nuevaFuente.canalId, url: '', categoriaIptc: '' })
      recargar()
    }
  }

  async function alternarEstado(fuente) {
    const accion = fuente.activo ? 'desactivada' : 'reactivada'
    if (fuente.activo && !window.confirm(`¿Desactivar la fuente ${fuente.url}? Dejará de capturarse.`)) {
      return
    }
    const ok = await ejecutar(() => cambiarEstadoFuente(fuente.id, !fuente.activo), `Fuente ${accion}.`)
    if (ok) recargar()
  }

  async function capturar(ids) {
    setEnCurso(true)
    setCapturas([])
    try {
      const resultados = ids.length === 1 ? [await capturarFuente(ids[0])] : await capturarFuentes(ids)
      setCapturas(resultados)
      setAviso(null)
      setSeleccion([])
      recargar()
    } catch (causa) {
      setAviso({ tipo: 'error', texto: causa.message })
      // El backend pudo haber capturado igual: se recarga para ver la fecha real.
      recargar()
    } finally {
      setEnCurso(false)
    }
  }

  function alternarSeleccion(id) {
    setSeleccion(seleccion.includes(id) ? seleccion.filter((x) => x !== id) : [...seleccion, id])
  }

  const canalValido = nuevoCanal.nombre.trim() !== '' && nuevoCanal.continente !== ''
  const fuenteValida =
    nuevaFuente.canalId !== '' && nuevaFuente.categoriaIptc !== '' && urlValida(nuevaFuente.url.trim())
  const totalPaginas = resultado ? Math.max(1, Math.ceil(resultado.total / POR_PAGINA)) : 1

  return (
    <div>
      <form className="admin-fila-formulario" onSubmit={agregarCanal} aria-label="Nuevo canal">
        <label className="campo">
          Canal
          <input value={nuevoCanal.nombre} onChange={(e) => setNuevoCanal({ ...nuevoCanal, nombre: e.target.value })} />
        </label>
        <label className="campo">
          Continente
          <select
            value={nuevoCanal.continente}
            onChange={(e) => setNuevoCanal({ ...nuevoCanal, continente: e.target.value })}
          >
            <option value="">Elegir…</option>
            {CONTINENTES.map((nombre) => (
              <option key={nombre} value={nombre}>
                {nombre}
              </option>
            ))}
          </select>
        </label>
        <label className="campo">
          País
          <input value={nuevoCanal.pais} onChange={(e) => setNuevoCanal({ ...nuevoCanal, pais: e.target.value })} />
        </label>
        <button type="submit" className="filtro activo" disabled={!canalValido}>
          Agregar canal
        </button>
      </form>

      <form className="admin-fila-formulario" onSubmit={agregarFuente} aria-label="Nueva fuente">
        <label className="campo">
          Canal de la fuente
          <select
            value={nuevaFuente.canalId}
            onChange={(e) => setNuevaFuente({ ...nuevaFuente, canalId: e.target.value })}
          >
            <option value="">Elegir…</option>
            {canales.map((canal) => (
              <option key={canal.id} value={canal.id}>
                {canal.nombre}
              </option>
            ))}
          </select>
        </label>
        <label className="campo">
          URL
          <input
            type="url"
            value={nuevaFuente.url}
            onChange={(e) => setNuevaFuente({ ...nuevaFuente, url: e.target.value })}
          />
        </label>
        <label className="campo">
          Categoría
          <select
            value={nuevaFuente.categoriaIptc}
            onChange={(e) => setNuevaFuente({ ...nuevaFuente, categoriaIptc: e.target.value })}
          >
            <option value="">Elegir…</option>
            {LISTA_CATEGORIAS_IPTC.map(([codigo, nombre]) => (
              <option key={codigo} value={codigo}>
                {nombre}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" className="filtro activo" disabled={!fuenteValida}>
          Agregar fuente
        </button>
      </form>
      {nuevaFuente.url.trim() !== '' && !urlValida(nuevaFuente.url.trim()) && (
        <p className="admin-ayuda">La URL debe empezar con http:// o https://.</p>
      )}

      <Aviso aviso={aviso} />
      {capturas.length > 0 && (
        <ul className="admin-resultados" aria-label="Resultado de la captura">
          {capturas.map((captura) => (
            <li key={captura.fuente_id}>{textoResultado(captura)}</li>
          ))}
        </ul>
      )}

      <div className="admin-fila-formulario" aria-label="Filtros de fuentes">
        <label className="campo">
          Filtrar por canal
          <select value={filtros.canalId} onChange={(e) => cambiarFiltro('canalId', e.target.value)}>
            <option value="">Todos</option>
            {canales.map((canal) => (
              <option key={canal.id} value={canal.id}>
                {canal.nombre}
              </option>
            ))}
          </select>
        </label>
        <label className="campo">
          Filtrar por continente
          <select value={filtros.continente} onChange={(e) => cambiarFiltro('continente', e.target.value)}>
            <option value="">Todos</option>
            {CONTINENTES.map((nombre) => (
              <option key={nombre} value={nombre}>
                {nombre}
              </option>
            ))}
          </select>
        </label>
        <label className="campo">
          Filtrar por categoría
          <select value={filtros.categoriaIptc} onChange={(e) => cambiarFiltro('categoriaIptc', e.target.value)}>
            <option value="">Todas</option>
            {LISTA_CATEGORIAS_IPTC.map(([codigo, nombre]) => (
              <option key={codigo} value={codigo}>
                {nombre}
              </option>
            ))}
          </select>
        </label>
        <label className="campo">
          Estado
          <select value={filtros.activo} onChange={(e) => cambiarFiltro('activo', e.target.value)}>
            <option value="">Todas</option>
            <option value="true">Activas</option>
            <option value="false">Inactivas</option>
          </select>
        </label>
      </div>

      {!resultado ? (
        <p>Cargando fuentes…</p>
      ) : (
        <>
          <div className="admin-acciones">
            <p className="admin-ayuda">{resultado.total} fuentes encontradas.</p>
            <button
              type="button"
              className="filtro activo"
              disabled={seleccion.length === 0 || enCurso}
              onClick={() => capturar(seleccion)}
            >
              Capturar seleccionadas ({seleccion.length})
            </button>
          </div>
          <div className="admin-tabla-contenedor">
            <table className="admin-tabla">
              <thead>
                <tr>
                  <th aria-label="Seleccionar" />
                  <th>Canal</th>
                  <th>URL</th>
                  <th>Categoría</th>
                  <th>Activa</th>
                  <th>Última captura exitosa</th>
                  <th>Circuito</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {resultado.items.map((fuente) => (
                  <tr key={fuente.id}>
                    <td>
                      <input
                        type="checkbox"
                        aria-label={`Seleccionar ${fuente.url}`}
                        disabled={!fuente.activo}
                        checked={seleccion.includes(fuente.id)}
                        onChange={() => alternarSeleccion(fuente.id)}
                      />
                    </td>
                    <td>{nombreCanal(fuente.canal_id)}</td>
                    <td className="admin-url">{fuente.url}</td>
                    <td>{nombreCategoria(fuente.categoria_iptc)}</td>
                    <td>{fuente.activo ? 'Sí' : 'No'}</td>
                    <td>{formatoFecha(fuente.fecha_ultima_captura_exitosa)}</td>
                    <td>{ESTADOS_CIRCUITO[fuente.estado_circuit_breaker] ?? fuente.estado_circuit_breaker}</td>
                    <td>
                      <div className="admin-acciones admin-acciones-fila">
                        <button
                          type="button"
                          className="filtro"
                          disabled={!fuente.activo || enCurso}
                          onClick={() => capturar([fuente.id])}
                        >
                          Capturar ahora
                        </button>
                        <button type="button" className="filtro" onClick={() => alternarEstado(fuente)}>
                          {fuente.activo ? 'Desactivar' : 'Reactivar'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {resultado.total > POR_PAGINA && (
            <nav className="paginacion" aria-label="Páginas de fuentes">
              <button type="button" className="filtro" disabled={pagina <= 1} onClick={() => setPagina(pagina - 1)}>
                Anterior
              </button>
              <span>
                Página {pagina} de {totalPaginas}
              </span>
              <button
                type="button"
                className="filtro"
                disabled={pagina >= totalPaginas}
                onClick={() => setPagina(pagina + 1)}
              >
                Siguiente
              </button>
            </nav>
          )}
        </>
      )}
    </div>
  )
}
