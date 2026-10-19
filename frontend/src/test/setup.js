// Configuración común de las pruebas: matchers de jest-dom (toBeInTheDocument,
// toBeDisabled, etc.) y limpieza del DOM después de cada prueba.
import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

afterEach(() => {
  cleanup()
})
