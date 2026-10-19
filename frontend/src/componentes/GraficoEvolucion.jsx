// HumWorld - gráfico de evolución temporal del humor global.
// Origen: HU-DASH-001-v3 (gráfico temporal) y ADR-005 (Chart.js). Consume
// serie_temporal de GET /api/v1/sentiment (HU-SENT-004); no calcula humor.
import {
  CategoryScale,
  Chart as ChartJS,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from 'chart.js'
import { useEffect, useState } from 'react'
import { Line } from 'react-chartjs-2'
import { obtenerSerieGlobal } from '../api/cliente.js'
import { COLORES_HUMOR, formatoHumor, tipoHumor } from '../utilidades/humor.js'

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Tooltip)

// Días que muestra el gráfico, hacia atrás desde el último día con datos.
// Valor propuesto, a ratificar por el equipo.
const DIAS_GRAFICO = 30

// Resta días a una fecha "AAAA-MM-DD" sin pasar por la zona horaria local.
function restarDias(fecha, dias) {
  const [anio, mes, dia] = fecha.split('-').map(Number)
  const resultado = new Date(Date.UTC(anio, mes - 1, dia - dias))
  return resultado.toISOString().slice(0, 10)
}

function rangoDelGrafico(primeraFecha, ultimaFecha) {
  if (!ultimaFecha) return null
  const desde = restarDias(ultimaFecha, DIAS_GRAFICO - 1)
  return { desde: primeraFecha && primeraFecha > desde ? primeraFecha : desde, hasta: ultimaFecha }
}

export default function GraficoEvolucion({ primeraFecha, ultimaFecha, fechaElegida }) {
  const [serie, setSerie] = useState(null)
  const [error, setError] = useState(null)
  const rango = rangoDelGrafico(primeraFecha, ultimaFecha)
  const desde = rango?.desde
  const hasta = rango?.hasta

  useEffect(() => {
    if (!desde || !hasta) return undefined
    let vigente = true
    obtenerSerieGlobal(desde, hasta)
      .then((datos) => {
        if (vigente) {
          setSerie(datos.serie_temporal ?? [])
          setError(null)
        }
      })
      .catch((causa) => vigente && setError(causa.message))
    return () => {
      vigente = false
    }
  }, [desde, hasta])

  if (!rango) return null
  if (error) {
    return (
      <p className="mapa-aviso mapa-error" role="alert">
        No se pudo cargar la evolución del humor. {error}
      </p>
    )
  }
  if (!serie) return <p className="mapa-aviso">Cargando evolución…</p>

  const datos = {
    labels: serie.map((dia) => dia.fecha),
    datasets: [
      {
        label: 'Humor global',
        data: serie.map((dia) => dia.humor_promedio),
        borderColor: '#2b2350',
        borderWidth: 2,
        spanGaps: true,
        pointRadius: serie.map((dia) => (dia.fecha === fechaElegida ? 7 : 4)),
        pointBackgroundColor: serie.map((dia) => COLORES_HUMOR[tipoHumor(dia.humor_promedio)]),
        pointBorderColor: '#2b2350',
      },
    ],
  }

  const opciones = {
    responsive: true,
    maintainAspectRatio: false,
    scales: { y: { suggestedMin: -3, suggestedMax: 3, title: { display: true, text: 'Humor' } } },
    plugins: {
      tooltip: {
        callbacks: {
          label: (contexto) => {
            const dia = serie[contexto.dataIndex]
            return `${formatoHumor(dia.humor_promedio)} (${dia.cantidad_noticias_evaluadas} noticias)`
          },
        },
      },
    },
  }

  return (
    <div className="grafico-evolucion">
      <h3>Evolución del humor global</h3>
      <p>
        {serie.length === 1 ? 'Último día' : `Últimos ${serie.length} días`} con su promedio
        diario. Los días sin noticias evaluadas quedan sin punto.
      </p>
      <div className="grafico-lienzo">
        <Line data={datos} options={opciones} aria-label="Gráfico de evolución del humor global" />
      </div>
    </div>
  )
}
