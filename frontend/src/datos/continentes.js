// HumWorld - ubicación de cada continente en el mapa (dato fijo del frontend).
// "centro" es [latitud, longitud]: el punto donde se dibuja el círculo.
// "alias" son otras formas de escribir el mismo continente, para que el mapa
// siga funcionando si el backend lo manda en mayúsculas, sin tildes o en inglés.
// Supuesto a validar con el equipo: la lista definitiva de continentes depende
// de la carga inicial de fuentes (HU-RSS-009), que aún no está terminada.
const CONTINENTES = [
  {
    nombre: 'América del Norte',
    centro: [45, -100],
    alias: ['america del norte', 'norteamerica', 'north america'],
  },
  {
    nombre: 'América del Sur',
    centro: [-15, -60],
    alias: ['america del sur', 'sudamerica', 'south america'],
  },
  { nombre: 'Europa', centro: [52, 15], alias: ['europa', 'europe'] },
  { nombre: 'África', centro: [5, 20], alias: ['africa'] },
  { nombre: 'Asia', centro: [40, 90], alias: ['asia'] },
  { nombre: 'Oceanía', centro: [-25, 135], alias: ['oceania'] },
]

// Deja el texto en minúsculas y sin tildes, para comparar sin fijarse en eso.
function normalizar(texto) {
  return texto
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
}

// Recibe el nombre que manda el backend y devuelve el continente con su ubicación.
// Si no lo reconoce devuelve null, y el mapa simplemente no dibuja ese círculo.
export function buscarContinente(nombre) {
  if (!nombre) return null
  const buscado = normalizar(nombre)
  return CONTINENTES.find((continente) => continente.alias.includes(buscado)) ?? null
}
