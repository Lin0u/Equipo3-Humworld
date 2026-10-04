// HumWorld - pantalla "Mapa de humor" (maqueta con datos de ejemplo).
// Origen: PDF del proyecto, "Dashboard de humor" (mapa del mundo con el humor de
// cada continente en una fecha que el usuario elige) y HU-SENT-004 (consulta del
// análisis). Historia HU-DASH y ADR del frontend: pendientes de redactar.
import { useState } from 'react'
import { CircleMarker, MapContainer, TileLayer, Tooltip } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { humorGlobalEjemplo, humorPorContinenteEjemplo } from '../datos/humorEjemplo.js'
import { buscarContinente } from '../datos/continentes.js'
import './MapaHumor.css'

// Mismos colores que las variables --humor-* de index.css. Se repiten aquí
// porque el mapa necesita el código del color, no el nombre de la variable.
const COLORES = {
  positivo: '#2a9d8f',
  negativo: '#d1495b',
  neutro: '#e3b23c',
  sinDatos: '#9aa7b2',
}

// Esquinas del mapa al abrir: [abajo-izquierda, arriba-derecha] en [latitud, longitud].
const LIMITES_MUNDO = [
  [-55, -150],
  [72, 170],
]

// Clasifica el humor según su signo. Es solo presentación: el equipo todavía
// no define rangos oficiales para "positivo", "neutro" o "negativo".
function tipoHumor(valor) {
  if (valor === null || valor === undefined) return 'sinDatos'
  if (valor > 0) return 'positivo'
  if (valor < 0) return 'negativo'
  return 'neutro'
}

// Muestra el valor con un decimal y con signo + cuando es positivo.
function formatoHumor(valor) {
  if (valor === null || valor === undefined) return 'Sin datos'
  return valor > 0 ? `+${valor.toFixed(1)}` : valor.toFixed(1)
}

// Mientras más lejos de 0 está el humor, más intenso se pinta el círculo.
// La escala del proyecto va de -10 a +10.
function intensidad(valor) {
  if (valor === null || valor === undefined) return 0.35
  return 0.4 + 0.5 * (Math.min(Math.abs(valor), 10) / 10)
}

// Busca dentro de la serie temporal el dato de la fecha elegida.
function datoDeLaFecha(agregado, fecha) {
  return agregado.serie_temporal.find((dia) => dia.fecha === fecha) ?? null
}

export default function MapaHumor() {
  // Rango de fechas con información, tomado de los datos.
  const fechas = humorGlobalEjemplo.serie_temporal.map((dia) => dia.fecha)
  const primeraFecha = fechas[0]
  const ultimaFecha = fechas[fechas.length - 1]

  // Guarda la fecha elegida. Parte en la más reciente.
  const [fecha, setFecha] = useState(ultimaFecha)

  const global = datoDeLaFecha(humorGlobalEjemplo, fecha)

  // Arma, para cada continente, lo que se necesita dibujar en la fecha elegida.
  const continentes = humorPorContinenteEjemplo.map((agregado) => {
    const dia = datoDeLaFecha(agregado, fecha)
    return {
      nombre: agregado.continente,
      ubicacion: buscarContinente(agregado.continente),
      humor: dia ? dia.humor_promedio : null,
      noticias: dia ? dia.cantidad_noticias_evaluadas : 0,
    }
  })

  return (
    <section className="pantalla">
      <div className="mapa-encabezado">
        <div>
          <h2>Mapa de humor</h2>
          <p>Humor promedio de cada continente en la fecha elegida. Datos de ejemplo.</p>
        </div>
        <label className="mapa-fecha">
          Fecha
          <input
            type="date"
            value={fecha}
            min={primeraFecha}
            max={ultimaFecha}
            onChange={(evento) => setFecha(evento.target.value)}
          />
        </label>
      </div>

      <p className="mapa-global">
        {global ? (
          <>
            Humor global:{' '}
            <strong className={`texto-${tipoHumor(global.humor_promedio)}`}>
              {formatoHumor(global.humor_promedio)}
            </strong>{' '}
            con {global.cantidad_noticias_evaluadas} noticias evaluadas
          </>
        ) : (
          `No hay datos para esa fecha. Elige una entre ${primeraFecha} y ${ultimaFecha}.`
        )}
      </p>

      <div className="mapa-contenedor">
        <MapContainer
          bounds={LIMITES_MUNDO}
          zoomSnap={0.25}
          minZoom={1}
          maxZoom={5}
          scrollWheelZoom={false}
          worldCopyJump
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          />
          {continentes
            .filter((continente) => continente.ubicacion)
            .map((continente) => (
              <CircleMarker
                key={continente.nombre}
                center={continente.ubicacion.centro}
                radius={30}
                pathOptions={{
                  color: COLORES[tipoHumor(continente.humor)],
                  fillColor: COLORES[tipoHumor(continente.humor)],
                  fillOpacity: intensidad(continente.humor),
                  weight: 2,
                }}
              >
                <Tooltip permanent direction="center" className="mapa-etiqueta">
                  {formatoHumor(continente.humor)}
                </Tooltip>
              </CircleMarker>
            ))}
        </MapContainer>
      </div>

      <ul className="mapa-leyenda" aria-label="Significado de los colores">
        <li><span className="punto fondo-negativo" /> Negativo</li>
        <li><span className="punto fondo-neutro" /> Neutro</li>
        <li><span className="punto fondo-positivo" /> Positivo</li>
        <li><span className="punto fondo-sinDatos" /> Sin datos</li>
        <li className="mapa-escala">Escala de -10 a +10</li>
      </ul>

      <ul className="continentes">
        {continentes.map((continente) => (
          <li key={continente.nombre} className="continente">
            <span className="continente-nombre">{continente.nombre}</span>
            <strong className={`continente-humor texto-${tipoHumor(continente.humor)}`}>
              {formatoHumor(continente.humor)}
            </strong>
            <span className="continente-noticias">
              {continente.noticias} noticias evaluadas
            </span>
          </li>
        ))}
      </ul>
    </section>
  )
}
