import { useLocation, useNavigate } from 'react-router-dom'
import { logout } from '../api/auth.js'

export default function LogoutControl() {
  const { pathname } = useLocation()
  const navigate = useNavigate()

  if (!localStorage.getItem('jwt') || ['/login', '/register'].includes(pathname)) return null

  return (
    <button type="button" className="nav-link" onClick={() => {
      void logout()
      navigate('/login', { replace: true })
    }}>
      <span>Log out</span>
    </button>
  )
}
