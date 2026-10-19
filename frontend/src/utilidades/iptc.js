// HumWorld - nombres de las categorías de primer nivel de IPTC Media Topics.
// El backend guarda el código (PDF, sección 3, Alcance, punto 3; HU-RSS-002);
// aquí solo se traduce a un nombre legible.
const CATEGORIAS_IPTC = {
  '01000000': 'Arte, cultura, entretenimiento y medios',
  '02000000': 'Delito, derecho y justicia',
  '03000000': 'Desastres, accidentes y emergencias',
  '04000000': 'Economía, negocios y finanzas',
  '05000000': 'Educación',
  '06000000': 'Medio ambiente',
  '07000000': 'Salud',
  '08000000': 'Interés humano',
  '09000000': 'Trabajo',
  '10000000': 'Estilo de vida y ocio',
  '11000000': 'Política',
  '12000000': 'Religión',
  '13000000': 'Ciencia y tecnología',
  '14000000': 'Sociedad',
  '15000000': 'Deporte',
  '16000000': 'Conflicto, guerra y paz',
  '17000000': 'Clima',
}

export function nombreCategoria(codigo) {
  if (!codigo) return null
  return CATEGORIAS_IPTC[codigo] ?? codigo
}
