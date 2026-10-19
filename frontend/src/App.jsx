// HumWorld - estructura base del frontend: cabecera con la mascota, menú y pantalla activa.
// Cada pantalla vive en su propio archivo dentro de src/pantallas.
// Origen: HU-DASH-001-v3 a HU-DASH-003-v2 y ADR-05. El mapa usa datos reales del
// backend; la nube y el listado siguen con datos de ejemplo hasta tener sus endpoints.
import { useEffect, useState } from 'react'
import './App.css'
import { obtenerMapa } from './api/cliente.js'
import CerebroHumor from './componentes/CerebroHumor.jsx'
import ListadoNoticias from './pantallas/ListadoNoticias.jsx'
import MapaHumor from './pantallas/MapaHumor.jsx'
import NubePalabras from './pantallas/NubePalabras.jsx'
import { formatoHumor, tipoHumor } from './utilidades/humor.js'

// Lista de pantallas del menú. Para agregar una pantalla nueva, se suma una línea aquí.
const PANTALLAS = [
  { id: 'mapa', nombre: 'Mapa de humor' },
  { id: 'nube', nombre: 'Nube de palabras' },
  { id: 'noticias', nombre: 'Noticias' },
]

export default function App() {
  // Guarda cuál pantalla se está mostrando. Parte en el mapa.
  const [pantallaActiva, setPantallaActiva] = useState('mapa')

  // Fecha elegida. Vive aquí, y no dentro del mapa, porque la usan dos piezas:
  // el mapa y la mascota de la cabecera. null = el último día con datos.
  const [fecha, setFecha] = useState(null)
  const [mapa, setMapa] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  // Pide al backend los datos del mapa cada vez que cambia la fecha.
  useEffect(() => {
    let vigente = true
    obtenerMapa(fecha)
      .then((datos) => {
        if (vigente) {
          setMapa(datos)
          setError(null)
        }
      })
      .catch((causa) => vigente && setError(causa.message))
      .finally(() => vigente && setCargando(false))
    return () => {
      vigente = false
    }
  }, [fecha])

  function cambiarFecha(nuevaFecha) {
    setCargando(true)
    setFecha(nuevaFecha)
  }

  // Humor global de la fecha elegida: decide la cara de la mascota.
  const humorGlobal = mapa?.global?.humor_promedio ?? null

  return (
    <div className="app">
      <header className="cabecera">
        <div className="marca">
          <CerebroHumor humor={humorGlobal} tamano={58} />
          <div>
            <h1 className="marca-nombre">HumWorld</h1>
            <p className="marca-frase">
              Humor del mundo
              <strong className={`texto-${tipoHumor(humorGlobal)}`}>
                {formatoHumor(humorGlobal)}
              </strong>
            </p>
          </div>
        </div>
        <nav className="menu" aria-label="Pantallas">
          {PANTALLAS.map((pantalla) => (
            <button
              key={pantalla.id}
              type="button"
              className={pantalla.id === pantallaActiva ? 'menu-boton activo' : 'menu-boton'}
              aria-current={pantalla.id === pantallaActiva ? 'page' : undefined}
              onClick={() => setPantallaActiva(pantalla.id)}
            >
              {pantalla.nombre}
            </button>
          ))}
        </nav>
      </header>

      <main className="contenido">
        {pantallaActiva === 'mapa' && (
          <MapaHumor mapa={mapa} cargando={cargando} error={error} alCambiarFecha={cambiarFecha} />
        )}
        {pantallaActiva === 'nube' && <NubePalabras />}
        {pantallaActiva === 'noticias' && <ListadoNoticias />}
      </main>
    </div>
  )
}
