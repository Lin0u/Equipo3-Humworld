import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // Pruebas del frontend (Vitest + Testing Library, decisión de la PO del
  // 2026-10-19). jsdom simula el navegador; la API se reemplaza por mocks, sin
  // llamadas reales al backend (DoD, sección 14).
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    coverage: {
      provider: 'v8',
      include: ['src/**/*.{js,jsx}'],
      // Fuera de la medición: arranque, datos de ejemplo de la maqueta y las
      // piezas que dibujan con Leaflet o Chart.js (requieren un navegador real).
      exclude: [
        'src/main.jsx',
        'src/test/**',
        'src/**/*.test.{js,jsx}',
        'src/datos/*Ejemplo.js',
        'src/pantallas/MapaHumor.jsx',
        'src/componentes/GraficoEvolucion.jsx',
      ],
      reporter: ['text', 'lcov'],
      // DoD: cobertura del módulo >= 80%.
      thresholds: { lines: 80, statements: 80, functions: 80, branches: 80 },
    },
  },
})
