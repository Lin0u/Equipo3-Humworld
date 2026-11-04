// HumWorld - mensaje de resultado o de error de una acción del panel de administración.
// Muestra el mensaje que devuelve la API tal cual (HU-ADMIN-004, decisión de diseño 5).
export default function Aviso({ aviso }) {
  if (!aviso) return null
  return (
    <p className={`admin-aviso admin-aviso-${aviso.tipo}`} role={aviso.tipo === 'error' ? 'alert' : 'status'}>
      {aviso.texto}
    </p>
  )
}
