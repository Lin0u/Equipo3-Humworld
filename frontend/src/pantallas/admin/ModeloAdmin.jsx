// HumWorld - pestaña "Modelo ML" del panel de administración (opcional en HU-ADMIN-004).
// Origen: HU-SENT-006 y ADR-004. POST /api/v1/trainings. Muestra la versión creada o
// el mensaje de la API (409 datos insuficientes, 502 servicio caído, 503 sin clave).
import { useState } from 'react'
import { entrenarModelo } from '../../api/cliente.js'
import Aviso from './Aviso.jsx'

export default function ModeloAdmin() {
  const [aviso, setAviso] = useState(null)
  const [enCurso, setEnCurso] = useState(false)

  async function entrenar() {
    setEnCurso(true)
    setAviso({ tipo: 'info', texto: 'Entrenando el modelo… puede tardar hasta 3 minutos.' })
    try {
      const modelo = await entrenarModelo()
      setAviso({
        tipo: 'exito',
        texto: `Versión ${modelo.version} activa (MAE contra diccionario: ${modelo.mae_evaluacion.toFixed(2)}).`,
      })
    } catch (causa) {
      setAviso({ tipo: 'error', texto: causa.message })
    } finally {
      setEnCurso(false)
    }
  }

  return (
    <div className="admin-formulario">
      <p>
        Entrena una nueva versión del modelo con las noticias ya evaluadas por diccionario. Requiere la
        clave de Gemini configurada en el servidor.
      </p>
      <button type="button" className="filtro activo" disabled={enCurso} onClick={entrenar}>
        Entrenar modelo
      </button>
      <Aviso aviso={aviso} />
    </div>
  )
}
