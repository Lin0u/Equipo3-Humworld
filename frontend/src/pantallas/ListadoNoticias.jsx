// HumWorld - pantalla "Listado de noticias" (maqueta con datos de ejemplo).
// Origen: PDF del proyecto, vista "Listado de noticias" y Dashboard de humor
// ("lista de las noticias que más han influido en el cálculo del humor").
// Historia HU-DASH y ADR del frontend: pendientes de redactar.
import { useState } from 'react'
import Carita from '../componentes/Carita.jsx'
import { noticiasEjemplo } from '../datos/noticiasEjemplo.js'
import { formatoHumor, tipoHumor } from '../utilidades/humor.js'
import './ListadoNoticias.css'

const FILTROS = [
  { id: 'todas', nombre: 'Todas' },
  { id: 'positivas', nombre: 'Positivas' },
  { id: 'negativas', nombre: 'Negativas' },
]

// Convierte la fecha técnica (2026-10-02T09:15:00Z) en una fecha legible.
function formatoFecha(fechaIso) {
  return new Date(fechaIso).toLocaleDateString('es-CL', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export default function ListadoNoticias() {
  // Guarda cuál filtro está elegido. Parte mostrando todas.
  const [filtro, setFiltro] = useState('todas')

  // 1) Deja solo las noticias que calzan con el filtro.
  // 2) Las ordena de la más influyente a la menos influyente:
  //    mientras más lejos de 0 está el humor, más pesó la noticia.
  const noticias = noticiasEjemplo
    .filter((noticia) => {
      if (filtro === 'positivas') return noticia.valor_humor > 0
      if (filtro === 'negativas') return noticia.valor_humor < 0
      return true
    })
    .sort((a, b) => Math.abs(b.valor_humor) - Math.abs(a.valor_humor))

  return (
    <section className="pantalla">
      <div className="noticias-encabezado">
        <div>
          <h2>Noticias</h2>
          <p>Las que más pesaron en el cálculo del humor. Datos de ejemplo.</p>
        </div>
        <div className="filtros" role="group" aria-label="Filtrar noticias">
          {FILTROS.map((opcion) => (
            <button
              key={opcion.id}
              type="button"
              className={opcion.id === filtro ? 'filtro activo' : 'filtro'}
              aria-pressed={opcion.id === filtro}
              onClick={() => setFiltro(opcion.id)}
            >
              {opcion.nombre}
            </button>
          ))}
        </div>
      </div>

      {noticias.length === 0 ? (
        <p className="noticias-vacio">No hay noticias para este filtro.</p>
      ) : (
        // La "key" cambia con el filtro para que la animación se repita al filtrar.
        <ul className="noticias-lista" key={filtro}>
          {noticias.map((noticia, posicion) => (
            <li
              key={noticia.id}
              className="noticia"
              style={{ animationDelay: `${posicion * 50}ms` }}
            >
              <div className="noticia-humor">
                <Carita tipo={tipoHumor(noticia.valor_humor)} tamano={38} />
                <strong className={`texto-${tipoHumor(noticia.valor_humor)}`}>
                  {formatoHumor(noticia.valor_humor)}
                </strong>
              </div>
              <div className="noticia-cuerpo">
                <a
                  className="noticia-titulo"
                  href={noticia.enlace}
                  target="_blank"
                  rel="noreferrer"
                >
                  {noticia.titulo}
                </a>
                <div className="noticia-datos">
                  <span>{noticia.fuente}</span>
                  <span>{noticia.continente}</span>
                  <span>{noticia.categoria}</span>
                  <span>{formatoFecha(noticia.fecha_publicacion)}</span>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
