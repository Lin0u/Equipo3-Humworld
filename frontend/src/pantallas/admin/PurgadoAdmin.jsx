// HumWorld - pestaña "Purgado" del panel de administración.
// Origen: HU-ADMIN-003 (PDF §4.2.5: "función de usuario que permita borrar noticias
// antiguas"). DELETE /api/v1/news. Es irreversible: siempre pide confirmación.
import { useState } from 'react'
import { purgarNoticias } from '../../api/cliente.js'
import Aviso from './Aviso.jsx'

function hoyIso() {
  return new Date().toISOString().slice(0, 10)
}

export default function PurgadoAdmin() {
  const [fecha, setFecha] = useState('')
  const [aviso, setAviso] = useState(null)
  const [enCurso, setEnCurso] = useState(false)

  async function purgar(conFecha) {
    const detalle = conFecha
      ? `las noticias registradas antes del ${fecha}`
      : 'las noticias que superan la caducidad configurada'
    if (!window.confirm(`Se eliminarán ${detalle}. Esta operación no se puede deshacer. ¿Continuar?`)) {
      return
    }
    setEnCurso(true)
    try {
      const resultado = await purgarNoticias(conFecha ? fecha : '')
      setAviso({ tipo: 'exito', texto: `Se eliminaron ${resultado.noticias_eliminadas} noticias.` })
    } catch (causa) {
      setAviso({ tipo: 'error', texto: causa.message })
    } finally {
      setEnCurso(false)
    }
  }

  return (
    <div className="admin-formulario">
      <p>Elimina noticias antiguas junto con sus coincidencias de términos. No se puede deshacer.</p>
      <label className="campo">
        Eliminar las registradas antes del
        <input type="date" max={hoyIso()} value={fecha} onChange={(evento) => setFecha(evento.target.value)} />
      </label>
      <div className="admin-acciones">
        <button
          type="button"
          className="filtro activo"
          disabled={!fecha || fecha > hoyIso() || enCurso}
          onClick={() => purgar(true)}
        >
          Purgar
        </button>
        <button type="button" className="filtro" disabled={enCurso} onClick={() => purgar(false)}>
          Purgar según caducidad
        </button>
      </div>
      <Aviso aviso={aviso} />
    </div>
  )
}
