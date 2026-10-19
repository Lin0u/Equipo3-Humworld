// HumWorld - pantalla "Nube de palabras" (maqueta con datos de ejemplo).
// Origen: PDF del proyecto, "Dashboard de palabras influyentes" (nube con las
// palabras más influyentes para el cálculo del humor, filtrable por continente
// o país). Historia HU-DASH y ADR del frontend: pendientes de redactar.
// Pendiente: el filtro por país, cuando el equipo defina de dónde salen los países.
import { useState } from 'react'
import Carita from '../componentes/Carita.jsx'
import { palabrasEjemplo } from '../datos/palabrasEjemplo.js'
import { tipoHumor } from '../utilidades/humor.js'
import './NubePalabras.css'

// Tamaño de letra de la palabra menos influyente y de la más influyente.
const TAMANO_MINIMO = 16
const TAMANO_MAXIMO = 50

export default function NubePalabras() {
  // Guarda el continente elegido. La cadena vacía significa "todos".
  const [continente, setContinente] = useState('')

  // Nombres de continentes disponibles, sacados de los propios datos.
  const opciones = palabrasEjemplo
    .map((grupo) => grupo.continente)
    .filter((nombre) => nombre !== null)

  // Busca el grupo de palabras del continente elegido (o el global).
  const grupo = palabrasEjemplo.find((g) => (g.continente ?? '') === continente)
  const palabras = grupo ? grupo.palabras : []

  // La palabra con más peso define el tamaño máximo; las demás se escalan.
  const pesoMaximo = Math.max(...palabras.map((p) => p.peso), 1)
  const tamano = (peso) =>
    TAMANO_MINIMO + (TAMANO_MAXIMO - TAMANO_MINIMO) * (peso / pesoMaximo)

  return (
    <section className="pantalla">
      <div className="nube-encabezado">
        <div>
          <h2>Nube de palabras</h2>
          <p>Mientras más grande la palabra, más influyó en el humor. Datos de ejemplo.</p>
        </div>
        <label className="campo">
          Continente
          <select value={continente} onChange={(evento) => setContinente(evento.target.value)}>
            <option value="">Todos</option>
            {opciones.map((nombre) => (
              <option key={nombre} value={nombre}>
                {nombre}
              </option>
            ))}
          </select>
        </label>
      </div>

      {palabras.length === 0 ? (
        <p className="nube-vacia">No hay palabras para este filtro.</p>
      ) : (
        // La "key" cambia con el continente para que la animación se repita al filtrar.
        <ul className="nube" key={continente}>
          {palabras.map((item, posicion) => (
            <li
              key={item.palabra}
              className={`palabra texto-${tipoHumor(item.valor)}`}
              style={{ fontSize: `${tamano(item.peso)}px`, animationDelay: `${posicion * 40}ms` }}
              title={`Valor en el diccionario: ${item.valor > 0 ? '+' : ''}${item.valor}`}
            >
              {item.palabra}
            </li>
          ))}
        </ul>
      )}

      <ul className="leyenda" aria-label="Significado de los colores">
        <li><Carita tipo="negativo" tamano={20} /> Palabra negativa</li>
        <li><Carita tipo="positivo" tamano={20} /> Palabra positiva</li>
        <li className="leyenda-nota">Pasa el mouse sobre una palabra para ver su valor</li>
      </ul>
    </section>
  )
}
