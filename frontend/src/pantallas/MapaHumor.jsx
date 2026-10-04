// HumWorld - pantalla "Mapa de humor" (maqueta con datos de ejemplo).
// Origen: PDF del proyecto, "Dashboard de humor" (mapa del mundo con el humor de
// cada continente en una fecha que el usuario elige) y HU-SENT-004 (consulta del
// análisis). Historia HU-DASH y ADR del frontend: pendientes de redactar.
import L from 'leaflet'
import { MapContainer, Marker, TileLayer, Tooltip } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import Carita from '../componentes/Carita.jsx'
import CerebroHumor from '../componentes/CerebroHumor.jsx'
import { buscarContinente } from '../datos/continentes.js'
import { humorGlobalEjemplo, humorPorContinenteEjemplo } from '../datos/humorEjemplo.js'
import { caritaComoTexto, datoDeLaFecha, formatoHumor, tipoHumor } from '../utilidades/humor.js'
import './MapaHumor.css'

// Esquinas del mapa al abrir: [abajo-izquierda, arriba-derecha] en [latitud, longitud].
const VISTA_INICIAL = [
  [-55, -150],
  [72, 170],
]

// Hasta dónde se puede mover el mapa: una sola copia del mundo.
const LIMITES_MUNDO = [
  [-85, -180],
  [85, 180],
]

// Arma el dibujo que marca un continente: una carita con el valor debajo.
// Leaflet necesita el dibujo de sus marcadores como texto HTML.
function marcadorContinente(humor) {
  return L.divIcon({
    className: 'marcador-humor',
    html:
      caritaComoTexto(tipoHumor(humor), 46) +
      `<span class="marcador-valor">${formatoHumor(humor)}</span>`,
    iconSize: [70, 72],
    iconAnchor: [35, 30],
  })
}

export default function MapaHumor({ fecha, alCambiarFecha, primeraFecha, ultimaFecha }) {
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
        <label className="campo">
          Fecha
          <input
            type="date"
            value={fecha}
            min={primeraFecha}
            max={ultimaFecha}
            onChange={(evento) => alCambiarFecha(evento.target.value)}
          />
        </label>
      </div>

      <div className="mapa-global">
        <CerebroHumor humor={global ? global.humor_promedio : null} tamano={84} />
        {global ? (
          <p>
            <span className="mapa-global-titulo">Humor global</span>
            <strong className={`mapa-global-valor texto-${tipoHumor(global.humor_promedio)}`}>
              {formatoHumor(global.humor_promedio)}
            </strong>
            <span>con {global.cantidad_noticias_evaluadas} noticias evaluadas</span>
          </p>
        ) : (
          <p>
            No hay datos para esa fecha. Elige una entre {primeraFecha} y {ultimaFecha}.
          </p>
        )}
      </div>

      <div className="mapa-contenedor">
        <MapContainer
          bounds={VISTA_INICIAL}
          maxBounds={LIMITES_MUNDO}
          maxBoundsViscosity={1}
          zoomSnap={0.25}
          minZoom={1}
          maxZoom={5}
          scrollWheelZoom={false}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            noWrap
          />
          {continentes
            .filter((continente) => continente.ubicacion)
            .map((continente) => (
              <Marker
                key={continente.nombre}
                position={continente.ubicacion.centro}
                icon={marcadorContinente(continente.humor)}
                keyboard={false}
              >
                <Tooltip direction="top" offset={[0, -26]}>
                  {continente.nombre}: {continente.noticias} noticias evaluadas
                </Tooltip>
              </Marker>
            ))}
        </MapContainer>
      </div>

      <ul className="leyenda" aria-label="Significado de las caritas">
        <li><Carita tipo="negativo" tamano={20} /> Negativo</li>
        <li><Carita tipo="neutro" tamano={20} /> Neutro</li>
        <li><Carita tipo="positivo" tamano={20} /> Positivo</li>
        <li><Carita tipo="sinDatos" tamano={20} /> Sin datos</li>
        <li className="leyenda-nota">Escala de -10 a +10</li>
      </ul>

      <ul className="continentes">
        {continentes.map((continente) => (
          <li key={continente.nombre} className="continente">
            <Carita tipo={tipoHumor(continente.humor)} tamano={40} />
            <div>
              <span className="continente-nombre">{continente.nombre}</span>
              <strong className={`continente-humor texto-${tipoHumor(continente.humor)}`}>
                {formatoHumor(continente.humor)}
              </strong>
              <span className="continente-noticias">{continente.noticias} noticias</span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
