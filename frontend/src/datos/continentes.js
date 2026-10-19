// HumWorld - ubicación de cada continente en el mapa (dato fijo del frontend).
// "centro" es [latitud, longitud]: el punto donde se dibuja la carita.
// Son los 5 continentes de HU-RSS-009-v2 y del enum Continente del contrato
// docs/Contratos/contrato-dashboards.openapi.yaml (HU-DASH-001-v3).
// "alias" son otras formas de escribir el mismo continente (sin tildes, en inglés).
const CONTINENTES = [
  { nombre: 'América', centro: [15, -85], alias: ['america', 'americas'] },
  { nombre: 'Europa', centro: [52, 15], alias: ['europa', 'europe'] },
  { nombre: 'África', centro: [5, 20], alias: ['africa'] },
  { nombre: 'Asia', centro: [40, 90], alias: ['asia'] },
  { nombre: 'Oceanía', centro: [-25, 135], alias: ['oceania'] },
]

// Deja el texto en minúsculas y sin tildes, para comparar sin fijarse en eso.
function normalizar(texto) {
  return texto
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .trim()
}

// Recibe el nombre que manda el backend y devuelve el continente con su ubicación.
// Si no lo reconoce devuelve null, y el mapa simplemente no dibuja esa carita.
export function buscarContinente(nombre) {
  if (!nombre) return null
  const buscado = normalizar(nombre)
  return CONTINENTES.find((continente) => continente.alias.includes(buscado)) ?? null
}
