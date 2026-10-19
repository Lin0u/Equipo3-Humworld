// HumWorld - selector de país para filtrar la nube y el listado de noticias.
// Origen: PDF §4.3.1 ("podrá filtrarse por continente o país"), HU-DASH-003-v2 y
// HU-DASH-002-v2. Los países salen de los canales registrados (GET /channels):
// si se eligió un continente, solo se ofrecen los países de ese continente.
import { useEffect, useState } from 'react'
import { obtenerPaises } from '../api/cliente.js'

export default function SelectorPais({ continente, valor, onCambio }) {
  // Se guarda el continente junto con la lista: si no coincide con el actual,
  // la lista aún se está cargando.
  const [estado, setEstado] = useState({ continente: null, paises: [], error: false })

  useEffect(() => {
    let vigente = true
    obtenerPaises(continente)
      .then((paises) => vigente && setEstado({ continente, paises, error: false }))
      .catch(() => vigente && setEstado({ continente, paises: [], error: true }))
    return () => {
      vigente = false
    }
  }, [continente])

  const cargando = estado.continente !== continente
  const sinPaises = !cargando && estado.paises.length === 0

  let textoVacio = 'Todos'
  if (cargando) textoVacio = 'Cargando…'
  else if (estado.error) textoVacio = 'No disponible'

  return (
    <label className="campo">
      País
      <select
        value={valor}
        disabled={cargando || sinPaises}
        onChange={(evento) => onCambio(evento.target.value)}
      >
        <option value="">{textoVacio}</option>
        {!cargando &&
          estado.paises.map((pais) => (
            <option key={pais} value={pais}>
              {pais}
            </option>
          ))}
      </select>
    </label>
  )
}
