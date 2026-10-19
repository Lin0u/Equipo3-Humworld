// HumWorld - datos de EJEMPLO para la maqueta del mapa de humor. Todo es inventado.
// La forma de cada objeto sigue el esquema SentimientoAgregado del contrato
// docs/Contratos/contrato-sentimiento-diccionario.openapi.yaml (GET /api/v1/sentiment):
// continente, pais, desde, hasta, humor_promedio, cantidad_noticias_evaluadas
// y serie_temporal (un valor por fecha). Origen: HU-SENT-004.
// Supuesto a validar con el equipo: el contrato define "continente" como texto
// libre y la carga inicial (HU-RSS-009) aún no fija la lista definitiva. Aquí se
// usan nombres en español como el único ejemplo que hay en el repo ("Europa").

// Un objeto por continente: lo que devolvería el backend al filtrar por continente.
export const humorPorContinenteEjemplo = [
  {
    continente: 'América del Norte',
    pais: null,
    desde: '2026-09-26',
    hasta: '2026-10-02',
    humor_promedio: -0.1,
    cantidad_noticias_evaluadas: 808,
    serie_temporal: [
      { fecha: '2026-09-26', humor_promedio: 0.2, cantidad_noticias_evaluadas: 109 },
      { fecha: '2026-09-27', humor_promedio: 0.5, cantidad_noticias_evaluadas: 106 },
      { fecha: '2026-09-28', humor_promedio: -0.6, cantidad_noticias_evaluadas: 122 },
      { fecha: '2026-09-29', humor_promedio: -0.5, cantidad_noticias_evaluadas: 123 },
      { fecha: '2026-09-30', humor_promedio: -0.6, cantidad_noticias_evaluadas: 121 },
      { fecha: '2026-10-01', humor_promedio: -0.1, cantidad_noticias_evaluadas: 107 },
      { fecha: '2026-10-02', humor_promedio: 0.8, cantidad_noticias_evaluadas: 120 },
    ],
  },
  {
    continente: 'América del Sur',
    pais: null,
    desde: '2026-09-26',
    hasta: '2026-10-02',
    humor_promedio: 2.4,
    cantidad_noticias_evaluadas: 496,
    serie_temporal: [
      { fecha: '2026-09-26', humor_promedio: 2.4, cantidad_noticias_evaluadas: 57 },
      { fecha: '2026-09-27', humor_promedio: 1.8, cantidad_noticias_evaluadas: 72 },
      { fecha: '2026-09-28', humor_promedio: 2.4, cantidad_noticias_evaluadas: 81 },
      { fecha: '2026-09-29', humor_promedio: 2.8, cantidad_noticias_evaluadas: 85 },
      { fecha: '2026-09-30', humor_promedio: 1.7, cantidad_noticias_evaluadas: 75 },
      { fecha: '2026-10-01', humor_promedio: 2.9, cantidad_noticias_evaluadas: 56 },
      { fecha: '2026-10-02', humor_promedio: 2.6, cantidad_noticias_evaluadas: 70 },
    ],
  },
  {
    continente: 'Europa',
    pais: null,
    desde: '2026-09-26',
    hasta: '2026-10-02',
    humor_promedio: 2.7,
    cantidad_noticias_evaluadas: 1039,
    serie_temporal: [
      { fecha: '2026-09-26', humor_promedio: 3.6, cantidad_noticias_evaluadas: 147 },
      { fecha: '2026-09-27', humor_promedio: 2.0, cantidad_noticias_evaluadas: 142 },
      { fecha: '2026-09-28', humor_promedio: 1.9, cantidad_noticias_evaluadas: 162 },
      { fecha: '2026-09-29', humor_promedio: 2.2, cantidad_noticias_evaluadas: 148 },
      { fecha: '2026-09-30', humor_promedio: 2.3, cantidad_noticias_evaluadas: 138 },
      { fecha: '2026-10-01', humor_promedio: 3.6, cantidad_noticias_evaluadas: 152 },
      { fecha: '2026-10-02', humor_promedio: 3.4, cantidad_noticias_evaluadas: 150 },
    ],
  },
  {
    continente: 'África',
    pais: null,
    desde: '2026-09-26',
    hasta: '2026-10-02',
    humor_promedio: -3.2,
    cantidad_noticias_evaluadas: 332,
    serie_temporal: [
      { fecha: '2026-09-26', humor_promedio: -1.9, cantidad_noticias_evaluadas: 40 },
      { fecha: '2026-09-27', humor_promedio: -4.2, cantidad_noticias_evaluadas: 53 },
      { fecha: '2026-09-28', humor_promedio: -2.5, cantidad_noticias_evaluadas: 46 },
      { fecha: '2026-09-29', humor_promedio: -4.2, cantidad_noticias_evaluadas: 57 },
      { fecha: '2026-09-30', humor_promedio: -4.3, cantidad_noticias_evaluadas: 36 },
      { fecha: '2026-10-01', humor_promedio: -2.5, cantidad_noticias_evaluadas: 50 },
      { fecha: '2026-10-02', humor_promedio: -2.9, cantidad_noticias_evaluadas: 50 },
    ],
  },
  {
    continente: 'Asia',
    pais: null,
    desde: '2026-09-26',
    hasta: '2026-10-02',
    humor_promedio: -3.6,
    cantidad_noticias_evaluadas: 752,
    serie_temporal: [
      { fecha: '2026-09-26', humor_promedio: -3.5, cantidad_noticias_evaluadas: 108 },
      { fecha: '2026-09-27', humor_promedio: -3.2, cantidad_noticias_evaluadas: 109 },
      { fecha: '2026-09-28', humor_promedio: -3.8, cantidad_noticias_evaluadas: 109 },
      { fecha: '2026-09-29', humor_promedio: -4.5, cantidad_noticias_evaluadas: 102 },
      { fecha: '2026-09-30', humor_promedio: -3.2, cantidad_noticias_evaluadas: 117 },
      { fecha: '2026-10-01', humor_promedio: -3.2, cantidad_noticias_evaluadas: 97 },
      { fecha: '2026-10-02', humor_promedio: -4.1, cantidad_noticias_evaluadas: 110 },
    ],
  },
  {
    continente: 'Oceanía',
    pais: null,
    desde: '2026-09-26',
    hasta: '2026-10-02',
    humor_promedio: 0.1,
    cantidad_noticias_evaluadas: 250,
    serie_temporal: [
      { fecha: '2026-09-26', humor_promedio: 0.5, cantidad_noticias_evaluadas: 41 },
      { fecha: '2026-09-27', humor_promedio: 0.3, cantidad_noticias_evaluadas: 35 },
      { fecha: '2026-09-28', humor_promedio: 1.0, cantidad_noticias_evaluadas: 34 },
      { fecha: '2026-09-29', humor_promedio: 0.6, cantidad_noticias_evaluadas: 27 },
      { fecha: '2026-09-30', humor_promedio: -0.9, cantidad_noticias_evaluadas: 38 },
      { fecha: '2026-10-01', humor_promedio: -0.8, cantidad_noticias_evaluadas: 35 },
      { fecha: '2026-10-02', humor_promedio: 0.3, cantidad_noticias_evaluadas: 40 },
    ],
  },
]

// Humor global: lo que devolvería el backend sin filtro de continente.
export const humorGlobalEjemplo = {
  continente: null,
  pais: null,
  desde: '2026-09-26',
  hasta: '2026-10-02',
  humor_promedio: 0.1,
  cantidad_noticias_evaluadas: 3677,
  serie_temporal: [
    { fecha: '2026-09-26', humor_promedio: 0.5, cantidad_noticias_evaluadas: 502 },
    { fecha: '2026-09-27', humor_promedio: -0.2, cantidad_noticias_evaluadas: 517 },
    { fecha: '2026-09-28', humor_promedio: -0.1, cantidad_noticias_evaluadas: 554 },
    { fecha: '2026-09-29', humor_promedio: -0.3, cantidad_noticias_evaluadas: 542 },
    { fecha: '2026-09-30', humor_promedio: -0.4, cantidad_noticias_evaluadas: 525 },
    { fecha: '2026-10-01', humor_promedio: 0.5, cantidad_noticias_evaluadas: 497 },
    { fecha: '2026-10-02', humor_promedio: 0.4, cantidad_noticias_evaluadas: 540 },
  ],
}
