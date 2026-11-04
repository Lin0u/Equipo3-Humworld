// HumWorld - pantalla "Administración" (panel de administración unificado).
// Origen: HU-ADMIN-004 (PDF §4.3, vista 1; §4.1 punto 4; §4.2.2; §4.2.3; §4.2.5).
// Cada pestaña usa endpoints que ya existen en la API; ninguno es nuevo.
import { useState } from 'react'
import DiccionarioAdmin from './admin/DiccionarioAdmin.jsx'
import FuentesAdmin from './admin/FuentesAdmin.jsx'
import ModeloAdmin from './admin/ModeloAdmin.jsx'
import ParametrosAdmin from './admin/ParametrosAdmin.jsx'
import PurgadoAdmin from './admin/PurgadoAdmin.jsx'
import './Administracion.css'

const PESTANAS = [
  { id: 'fuentes', nombre: 'Fuentes RSS', Componente: FuentesAdmin },
  { id: 'diccionario', nombre: 'Diccionario', Componente: DiccionarioAdmin },
  { id: 'parametros', nombre: 'Parámetros', Componente: ParametrosAdmin },
  { id: 'purgado', nombre: 'Purgado', Componente: PurgadoAdmin },
  { id: 'modelo', nombre: 'Modelo ML', Componente: ModeloAdmin },
]

export default function Administracion() {
  const [activa, setActiva] = useState('fuentes')
  const { Componente } = PESTANAS.find((pestana) => pestana.id === activa)

  return (
    <section className="pantalla">
      <div className="admin-encabezado">
        <h2>Administración</h2>
        <p>Fuentes RSS, diccionario, parámetros, purgado y modelo de humor.</p>
      </div>
      <div className="admin-pestanas" role="tablist" aria-label="Secciones de administración">
        {PESTANAS.map((pestana) => (
          <button
            key={pestana.id}
            type="button"
            role="tab"
            aria-selected={pestana.id === activa}
            className={pestana.id === activa ? 'filtro activo' : 'filtro'}
            onClick={() => setActiva(pestana.id)}
          >
            {pestana.nombre}
          </button>
        ))}
      </div>
      <div role="tabpanel" className="admin-panel">
        <Componente />
      </div>
    </section>
  )
}
