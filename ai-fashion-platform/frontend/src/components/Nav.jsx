import { NavLink, useNavigate } from 'react-router-dom'
import { getUser, setToken, setUser } from '../api.js'

export default function Nav() {
  const user = getUser()
  const nav = useNavigate()

  function logout() {
    setToken(null); setUser(null); nav('/login', { replace: true })
  }

  const rolePill = {
    admin:    { cls: 'pill pill-pink',   icon: '★' },
    designer: { cls: 'pill pill-violet', icon: '✎' },
    shopper:  { cls: 'pill pill-neon',   icon: '◎' },
  }[user?.role || 'designer']

  return (
    <nav className="nav glass">
      <div className="nav-brand">
        <div className="nav-logo">F</div>
        <div>
          <div>Fashion<span className="text-neon">/AI</span></div>
          <div className="text-xs text-mute" style={{ fontWeight: 400 }}>
            Intelligence · Design
          </div>
        </div>
      </div>

      {user && (
        <div className="nav-links">
          {/* Designer workspace — only visible to designers/admins */}
          {(user.role === 'designer' || user.role === 'admin') && (
            <NavLink to="/designer"
                     className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
              Designer
            </NavLink>
          )}

          {/* Browse — visible to everyone; primary for shoppers */}
          <NavLink to="/browse"
                   className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            Browse
          </NavLink>

          <NavLink to="/history"
                   className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
            History
          </NavLink>

          {user.role === 'admin' && (
            <NavLink to="/admin"
                     className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>
              Admin
            </NavLink>
          )}

          <span className={rolePill.cls + ' hidden-sm'}>
            {rolePill.icon} {user.name}
          </span>
          <button className="btn btn-ghost" onClick={logout}>Sign out</button>
        </div>
      )}
    </nav>
  )
}
