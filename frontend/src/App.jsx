// HumWorld - estructura base del frontend: cabecera, menú y pantalla activa.
// Cada pantalla vive en su propio archivo dentro de src/pantallas.
// Origen: vistas de dashboard del PDF del proyecto y Sprint 3 de la planificación.
// Historias HU-DASH-001 a 003 y ADR del frontend: pendientes de redactar.
import { useState } from 'react'
import './App.css'
import ListadoNoticias from './pantallas/ListadoNoticias.jsx'
import MapaHumor from './pantallas/MapaHumor.jsx'
import NubePalabras from './pantallas/NubePalabras.jsx'

// Lista de pantallas del menú. Para agregar una pantalla nueva, se suma una línea aquí.
const PANTALLAS = [
  { id: 'mapa', nombre: 'Mapa de humor' },
  { id: 'nube', nombre: 'Nube de palabras' },
  { id: 'noticias', nombre: 'Noticias' },
]

export default function App() {
  // Guarda cuál pantalla se está mostrando. Parte en el mapa.
  const [pantallaActiva, setPantallaActiva] = useState('mapa')

  return (
    <div className="app">
      <header className="cabecera">
        <h1 className="marca">HumWorld</h1>
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
        {pantallaActiva === 'mapa' && <MapaHumor />}
        {pantallaActiva === 'nube' && <NubePalabras />}
        {pantallaActiva === 'noticias' && <ListadoNoticias />}
      </main>
    </div>
  )
}
