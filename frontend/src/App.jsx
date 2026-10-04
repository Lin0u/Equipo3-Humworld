// HumWorld - estructura base del frontend: cabecera con la mascota, menú y pantalla activa.
// Cada pantalla vive en su propio archivo dentro de src/pantallas.
// Origen: vistas de dashboard del PDF del proyecto y Sprint 3 de la planificación.
// Historias HU-DASH-001 a 003 y ADR del frontend: pendientes de redactar.
import { useState } from 'react'
import './App.css'
import CerebroHumor from './componentes/CerebroHumor.jsx'
import { humorGlobalEjemplo } from './datos/humorEjemplo.js'
import ListadoNoticias from './pantallas/ListadoNoticias.jsx'
import MapaHumor from './pantallas/MapaHumor.jsx'
import NubePalabras from './pantallas/NubePalabras.jsx'
import { datoDeLaFecha, formatoHumor, tipoHumor } from './utilidades/humor.js'

// Lista de pantallas del menú. Para agregar una pantalla nueva, se suma una línea aquí.
const PANTALLAS = [
  { id: 'mapa', nombre: 'Mapa de humor' },
  { id: 'nube', nombre: 'Nube de palabras' },
  { id: 'noticias', nombre: 'Noticias' },
]

// Rango de fechas con información, tomado de los datos de ejemplo.
const FECHAS = humorGlobalEjemplo.serie_temporal.map((dia) => dia.fecha)
const PRIMERA_FECHA = FECHAS[0]
const ULTIMA_FECHA = FECHAS[FECHAS.length - 1]

export default function App() {
  // Guarda cuál pantalla se está mostrando. Parte en el mapa.
  const [pantallaActiva, setPantallaActiva] = useState('mapa')

  // Guarda la fecha elegida. Vive aquí, y no dentro del mapa, porque la usan
  // dos piezas: el mapa y la mascota de la cabecera.
  const [fecha, setFecha] = useState(ULTIMA_FECHA)

  // Humor global de la fecha elegida: decide la cara de la mascota.
  const diaGlobal = datoDeLaFecha(humorGlobalEjemplo, fecha)
  const humorGlobal = diaGlobal ? diaGlobal.humor_promedio : null

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
          <MapaHumor
            fecha={fecha}
            alCambiarFecha={setFecha}
            primeraFecha={PRIMERA_FECHA}
            ultimaFecha={ULTIMA_FECHA}
          />
        )}
        {pantallaActiva === 'nube' && <NubePalabras />}
        {pantallaActiva === 'noticias' && <ListadoNoticias />}
      </main>
    </div>
  )
}
