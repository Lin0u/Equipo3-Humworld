// HumWorld - pestaña "Parámetros" del panel de administración.
// Origen: HU-RSS-007 (periodicidad del cron) y HU-ADMIN-001 (caducidad de las noticias).
// GET y PUT /api/v1/config.
import { useEffect, useState } from 'react'
import { guardarConfiguracion, obtenerConfiguracion } from '../../api/cliente.js'
import Aviso from './Aviso.jsx'

// Los dos parámetros son enteros mayores o iguales a 1 (contrato de /config).
function esValido(texto) {
  return /^\d+$/.test(texto) && Number(texto) >= 1
}

export default function ParametrosAdmin() {
  const [valores, setValores] = useState(null)
  const [aviso, setAviso] = useState(null)
  const [guardando, setGuardando] = useState(false)

  useEffect(() => {
    let vigente = true
    obtenerConfiguracion()
      .then((datos) =>
        vigente &&
        setValores({
          periodicidad: String(datos.periodicidad_cron_minutos),
          caducidad: String(datos.caducidad_noticias_dias),
        }),
      )
      .catch((causa) => vigente && setAviso({ tipo: 'error', texto: causa.message }))
    return () => {
      vigente = false
    }
  }, [])

  if (!valores) {
    return aviso ? <Aviso aviso={aviso} /> : <p>Cargando parámetros…</p>
  }

  const validos = esValido(valores.periodicidad) && esValido(valores.caducidad)

  async function guardar(evento) {
    evento.preventDefault()
    setGuardando(true)
    try {
      const datos = await guardarConfiguracion({
        periodicidad: Number(valores.periodicidad),
        caducidad: Number(valores.caducidad),
      })
      setValores({
        periodicidad: String(datos.periodicidad_cron_minutos),
        caducidad: String(datos.caducidad_noticias_dias),
      })
      setAviso({ tipo: 'exito', texto: 'Parámetros guardados.' })
    } catch (causa) {
      setAviso({ tipo: 'error', texto: causa.message })
    } finally {
      setGuardando(false)
    }
  }

  return (
    <form className="admin-formulario" onSubmit={guardar}>
      <label className="campo">
        Periodicidad del cron (minutos)
        <input
          type="number"
          min="1"
          value={valores.periodicidad}
          onChange={(evento) => setValores({ ...valores, periodicidad: evento.target.value })}
        />
      </label>
      <label className="campo">
        Caducidad de las noticias (días)
        <input
          type="number"
          min="1"
          value={valores.caducidad}
          onChange={(evento) => setValores({ ...valores, caducidad: evento.target.value })}
        />
      </label>
      {!validos && <p className="admin-ayuda">Los dos valores deben ser enteros mayores o iguales a 1.</p>}
      <button type="submit" className="filtro activo" disabled={!validos || guardando}>
        Guardar
      </button>
      <Aviso aviso={aviso} />
    </form>
  )
}
