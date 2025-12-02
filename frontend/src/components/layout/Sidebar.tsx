import { Link, useLocation } from 'react-router-dom'
import './Sidebar.css'

export default function Sidebar() {
  const location = useLocation()

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(path)
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <path
              d="M16 2L4 8V16C4 22.627 9.373 28 16 28C22.627 28 28 22.627 28 16V8L16 2Z"
              fill="currentColor"
            />
            <path
              d="M16 6L8 10V16C8 20.418 11.582 24 16 24C20.418 24 24 20.418 24 16V10L16 6Z"
              fill="white"
            />
          </svg>
          <span>MTE</span>
        </div>
      </div>
      
      <nav className="sidebar-nav">
        <Link 
          to="/" 
          className={`nav-item ${isActive('/') ? 'active' : ''}`}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 2L2 7V18H8V12H12V18H18V7L10 2Z" fill="currentColor"/>
          </svg>
          <span>Inicio</span>
        </Link>
        
        <Link 
          to="/upload" 
          className={`nav-item ${isActive('/upload') ? 'active' : ''}`}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 2V12M10 2L6 6M10 2L14 6M2 14V16C2 17.105 2.895 18 4 18H16C17.105 18 18 17.105 18 16V14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span>Subir Archivo</span>
        </Link>
        
        <Link 
          to="/analyses" 
          className={`nav-item ${isActive('/analyses') ? 'active' : ''}`}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M3 3H17V17H3V3Z" stroke="currentColor" strokeWidth="2"/>
            <path d="M7 7H13M7 11H13M7 15H11" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <span>Análisis</span>
        </Link>
        
        <Link 
          to="/dashboard" 
          className={`nav-item ${isActive('/dashboard') ? 'active' : ''}`}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M3 3H9V9H3V3Z" stroke="currentColor" strokeWidth="2"/>
            <path d="M11 3H17V9H11V3Z" stroke="currentColor" strokeWidth="2"/>
            <path d="M3 11H9V17H3V11Z" stroke="currentColor" strokeWidth="2"/>
            <path d="M11 11H17V17H11V11Z" stroke="currentColor" strokeWidth="2"/>
          </svg>
          <span>Dashboard</span>
        </Link>
      </nav>
      
      <div className="sidebar-footer">
        <div className="sidebar-info">
          <p className="version">v1.0.0</p>
          <p className="status">
            <span className="status-dot"></span>
            Sistema Activo
          </p>
        </div>
      </div>
    </aside>
  )
}

