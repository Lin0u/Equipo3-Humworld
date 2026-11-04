// HumWorld - pestaña "Diccionario" del panel de administración.
// Origen: HU-SENT-001-v2 (CRUD del diccionario; PDF §4.2.2: "operaciones CRUD para
// cada término con endpoints API REST e interface de usuario"). El listado se pagina
// en el backend, de 25 en 25.
import { useEffect, useState } from 'react'
import { actualizarTermino, crearTermino, eliminarTermino, obtenerTerminos } from '../../api/cliente.js'
import Aviso from './Aviso.jsx'

const POR_PAGINA = 25
const IDIOMAS = { es: 'Español', en: 'Inglés' }

// Escala del diccionario: enteros de -10 a +10 (ADR-003, sección 11 de las instrucciones).
function valorValido(texto) {
  return /^-?\d+$/.test(texto) && Number(texto) >= -10 && Number(texto) <= 10
}

const AVISO_RECALCULO = 'El humor de las noticias se recalculará en el próximo barrido.'

export default function DiccionarioAdmin() {
  const [busqueda, setBusqueda] = useState('')
  const [pagina, setPagina] = useState(1)
  const [version, setVersion] = useState(0)
  const [resultado, setResultado] = useState(null)
  const [aviso, setAviso] = useState(null)
  const [nuevo, setNuevo] = useState({ palabra: '', idioma: 'es', valor: '' })
  const [edicion, setEdicion] = useState(null)

  useEffect(() => {
    let vigente = true
    obtenerTerminos({ busqueda, pagina, tamanioPagina: POR_PAGINA })
      .then((datos) => vigente && setResultado(datos))
      .catch((causa) => vigente && setAviso({ tipo: 'error', texto: causa.message }))
    return () => {
      vigente = false
    }
  }, [busqueda, pagina, version])

  function buscar(texto) {
    setBusqueda(texto)
    setPagina(1)
  }

  function recargar() {
    setVersion((v) => v + 1)
  }

  async function ejecutar(accion, textoExito) {
    try {
      await accion()
      setAviso({ tipo: 'exito', texto: `${textoExito} ${AVISO_RECALCULO}` })
      recargar()
      return true
    } catch (causa) {
      setAviso({ tipo: 'error', texto: causa.message })
      return false
    }
  }

  async function crear(evento) {
    evento.preventDefault()
    const ok = await ejecutar(
      () => crearTermino({ palabra: nuevo.palabra.trim(), idioma: nuevo.idioma, valor: Number(nuevo.valor) }),
      `Término "${nuevo.palabra.trim()}" creado.`,
    )
    if (ok) setNuevo({ palabra: '', idioma: nuevo.idioma, valor: '' })
  }

  async function guardarEdicion() {
    const ok = await ejecutar(
      () => actualizarTermino(edicion.id, { valor: Number(edicion.valor) }),
      'Valor actualizado.',
    )
    if (ok) setEdicion(null)
  }

  function eliminar(termino) {
    if (!window.confirm(`¿Eliminar el término "${termino.palabra}" (${termino.idioma})?`)) return
    ejecutar(() => eliminarTermino(termino.id), `Término "${termino.palabra}" eliminado.`)
  }

  const nuevoValido = nuevo.palabra.trim() !== '' && valorValido(nuevo.valor)
  const totalPaginas = resultado ? Math.max(1, Math.ceil(resultado.total / POR_PAGINA)) : 1

  return (
    <div>
      <form className="admin-fila-formulario" onSubmit={crear} aria-label="Nuevo término">
        <label className="campo">
          Palabra
          <input value={nuevo.palabra} onChange={(e) => setNuevo({ ...nuevo, palabra: e.target.value })} />
        </label>
        <label className="campo">
          Idioma
          <select value={nuevo.idioma} onChange={(e) => setNuevo({ ...nuevo, idioma: e.target.value })}>
            {Object.entries(IDIOMAS).map(([codigo, nombre]) => (
              <option key={codigo} value={codigo}>
                {nombre}
              </option>
            ))}
          </select>
        </label>
        <label className="campo">
          Valor
          <input
            type="number"
            min="-10"
            max="10"
            value={nuevo.valor}
            onChange={(e) => setNuevo({ ...nuevo, valor: e.target.value })}
          />
        </label>
        <button type="submit" className="filtro activo" disabled={!nuevoValido}>
          Agregar
        </button>
      </form>
      {nuevo.valor !== '' && !valorValido(nuevo.valor) && (
        <p className="admin-ayuda">El valor debe ser un entero entre -10 y +10.</p>
      )}

      <Aviso aviso={aviso} />

      <label className="campo admin-buscador">
        Buscar
        <input type="search" value={busqueda} onChange={(e) => buscar(e.target.value)} />
      </label>

      {!resultado ? (
        <p>Cargando términos…</p>
      ) : (
        <>
          <p className="admin-ayuda">{resultado.total} términos encontrados.</p>
          <table className="admin-tabla">
            <thead>
              <tr>
                <th>Palabra</th>
                <th>Idioma</th>
                <th>Valor</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {resultado.items.map((termino) => (
                <tr key={termino.id}>
                  <td>{termino.palabra}</td>
                  <td>{IDIOMAS[termino.idioma] ?? termino.idioma}</td>
                  <td>
                    {edicion?.id === termino.id ? (
                      <input
                        type="number"
                        min="-10"
                        max="10"
                        aria-label={`Nuevo valor de ${termino.palabra}`}
                        value={edicion.valor}
                        onChange={(e) => setEdicion({ ...edicion, valor: e.target.value })}
                      />
                    ) : (
                      termino.valor
                    )}
                  </td>
                  <td className="admin-acciones">
                    {edicion?.id === termino.id ? (
                      <>
                        <button
                          type="button"
                          className="filtro activo"
                          disabled={!valorValido(edicion.valor)}
                          onClick={guardarEdicion}
                        >
                          Guardar
                        </button>
                        <button type="button" className="filtro" onClick={() => setEdicion(null)}>
                          Cancelar
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          type="button"
                          className="filtro"
                          onClick={() => setEdicion({ id: termino.id, valor: String(termino.valor) })}
                        >
                          Editar
                        </button>
                        <button type="button" className="filtro" onClick={() => eliminar(termino)}>
                          Eliminar
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {resultado.total > POR_PAGINA && (
            <nav className="paginacion" aria-label="Páginas del diccionario">
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
