// HumWorld - pantalla "Nube de palabras".
// Origen: HU-DASH-003-v2 (PDF, sección 4.3.1) y ADR-05. Muestra los datos de
// GET /api/v1/dashboards/word-cloud: términos del diccionario con más noticias
// que los contienen (HU-SENT-008). El peso lo calcula el backend; aquí solo
// define el tamaño de la letra.
// Pendiente: el filtro por país, cuando el equipo defina de dónde salen los países.
import { useEffect, useState } from 'react'
import { obtenerNubePalabras } from '../api/cliente.js'
import Carita from '../componentes/Carita.jsx'
import { tipoHumor } from '../utilidades/humor.js'
import './NubePalabras.css'

// Tamaño de letra de la palabra menos influyente y de la más influyente.
const TAMANO_MINIMO = 16
const TAMANO_MAXIMO = 50

// Los 5 continentes del enum Continente del contrato (HU-RSS-009-v2).
const CONTINENTES = ['América', 'Europa', 'Asia', 'África', 'Oceanía']

const IDIOMAS = { es: 'español', en: 'inglés' }

// Ordena alfabéticamente para que la nube no quede como una lista por tamaño.
function ordenAlfabetico(a, b) {
  return a.palabra.localeCompare(b.palabra, 'es')
}

export default function NubePalabras() {
  // Continente elegido. La cadena vacía significa "todos".
  const [continente, setContinente] = useState('')
  const [palabras, setPalabras] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let vigente = true
    obtenerNubePalabras(continente)
      .then((datos) => {
        if (vigente) {
          setPalabras([...datos.items].sort(ordenAlfabetico))
          setError(null)
        }
      })
      .catch((causa) => vigente && setError(causa.message))
    return () => {
      vigente = false
    }
  }, [continente])

  function cambiarContinente(nuevo) {
    setPalabras(null)
    setContinente(nuevo)
  }

  // La palabra con más peso define el tamaño máximo; las demás se escalan.
  const lista = palabras ?? []
  const pesoMaximo = Math.max(...lista.map((p) => p.peso), 1)
  const tamano = (peso) =>
    TAMANO_MINIMO + (TAMANO_MAXIMO - TAMANO_MINIMO) * (peso / pesoMaximo)

  let contenido
  if (error) {
    contenido = (
      <p className="nube-vacia" role="alert">
        No se pudieron cargar las palabras. {error}
      </p>
    )
  } else if (palabras === null) {
    contenido = <p className="nube-vacia">Cargando palabras…</p>
  } else if (lista.length === 0) {
    contenido = <p className="nube-vacia">No hay palabras para este filtro.</p>
  } else {
    contenido = (
      // La "key" cambia con el continente para que la animación se repita al filtrar.
      <ul className="nube" key={continente}>
        {lista.map((item, posicion) => (
          <li
            key={item.termino_id}
            className={`palabra texto-${tipoHumor(item.valor)}`}
            style={{ fontSize: `${tamano(item.peso)}px`, animationDelay: `${posicion * 20}ms` }}
            title={`Valor ${item.valor > 0 ? '+' : ''}${item.valor} · aparece en ${item.peso} noticias · ${IDIOMAS[item.idioma] ?? item.idioma}`}
          >
            {item.palabra}
          </li>
        ))}
      </ul>
    )
  }

  return (
    <section className="pantalla">
      <div className="nube-encabezado">
        <div>
          <h2>Nube de palabras</h2>
          <p>Mientras más grande la palabra, en más noticias apareció.</p>
        </div>
        <label className="campo">
          Continente
          <select value={continente} onChange={(evento) => cambiarContinente(evento.target.value)}>
            <option value="">Todos</option>
            {CONTINENTES.map((nombre) => (
              <option key={nombre} value={nombre}>
                {nombre}
              </option>
            ))}
          </select>
        </label>
      </div>

      {contenido}

      <ul className="leyenda" aria-label="Significado de los colores">
        <li><Carita tipo="negativo" tamano={20} /> Palabra negativa</li>
        <li><Carita tipo="positivo" tamano={20} /> Palabra positiva</li>
        <li className="leyenda-nota">Pasa el mouse sobre una palabra para ver su valor</li>
      </ul>
    </section>
  )
}
