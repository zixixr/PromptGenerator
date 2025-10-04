import { Link, useLocation } from 'react-router-dom'
import './Navigation.css'

function Navigation() {
  const location = useLocation()

  const isActive = (path: string) => {
    return location.pathname === path ? 'active' : ''
  }

  return (
    <nav className="navigation">
      <div className="nav-content">
        <Link to="/" className="nav-brand">
          Prompt Optimizer
        </Link>
        <div className="nav-links">
          <Link to="/" className={`nav-link ${isActive('/')}`}>
            Projects
          </Link>
          <Link to="/projects/new" className={`nav-link ${isActive('/projects/new')}`}>
            New Project
          </Link>
          <Link to="/settings" className={`nav-link ${isActive('/settings')}`}>
            Settings
          </Link>
        </div>
      </div>
    </nav>
  )
}

export default Navigation
