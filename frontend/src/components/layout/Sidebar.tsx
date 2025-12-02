import { Link, useLocation } from 'react-router-dom'

export default function Sidebar() {
  const location = useLocation()

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(path)
  }

  return (
    <aside className="w-64 h-screen bg-gradient-to-b from-slate-800 to-slate-900 text-white flex flex-col fixed left-0 top-0 z-50 shadow-xl">
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center gap-3 text-xl font-bold text-white">
          <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
            <svg width="20" height="20" viewBox="0 0 32 32" fill="none">
              <path
                d="M16 2L4 8V16C4 22.627 9.373 28 16 28C22.627 28 28 22.627 28 16V8L16 2Z"
                fill="currentColor"
              />
              <path
                d="M16 6L8 10V16C8 20.418 11.582 24 16 24C20.418 24 24 20.418 24 16V10L16 6Z"
                fill="white"
              />
            </svg>
          </div>
          <span>MTE</span>
        </div>
      </div>
      
      <nav className="flex-1 py-4 overflow-y-auto">
        <Link 
          to="/" 
          className={`flex items-center gap-3 px-6 py-3 text-gray-300 hover:text-white hover:bg-slate-700/50 transition-all border-l-3 border-transparent ${
            isActive('/') ? 'bg-primary-500/20 text-white border-primary-500' : ''
          }`}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 2L2 7V18H8V12H12V18H18V7L10 2Z" fill="currentColor"/>
          </svg>
          <span className="font-medium">Inicio</span>
        </Link>
        
        <Link 
          to="/upload" 
          className={`flex items-center gap-3 px-6 py-3 text-gray-300 hover:text-white hover:bg-slate-700/50 transition-all border-l-3 border-transparent ${
            isActive('/upload') ? 'bg-primary-500/20 text-white border-primary-500' : ''
          }`}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 2V12M10 2L6 6M10 2L14 6M2 14V16C2 17.105 2.895 18 4 18H16C17.105 18 18 17.105 18 16V14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span className="font-medium">Subir Archivo</span>
        </Link>
        
        <Link 
          to="/analyses" 
          className={`flex items-center gap-3 px-6 py-3 text-gray-300 hover:text-white hover:bg-slate-700/50 transition-all border-l-3 border-transparent ${
            isActive('/analyses') ? 'bg-primary-500/20 text-white border-primary-500' : ''
          }`}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M3 3H17V17H3V3Z" stroke="currentColor" strokeWidth="2"/>
            <path d="M7 7H13M7 11H13M7 15H11" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <span className="font-medium">Análisis</span>
        </Link>
        
        <Link 
          to="/dashboard" 
          className={`flex items-center gap-3 px-6 py-3 text-gray-300 hover:text-white hover:bg-slate-700/50 transition-all border-l-3 border-transparent ${
            isActive('/dashboard') ? 'bg-primary-500/20 text-white border-primary-500' : ''
          }`}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M3 3H9V9H3V3Z" stroke="currentColor" strokeWidth="2"/>
            <path d="M11 3H17V9H11V3Z" stroke="currentColor" strokeWidth="2"/>
            <path d="M3 11H9V17H3V11Z" stroke="currentColor" strokeWidth="2"/>
            <path d="M11 11H17V17H11V11Z" stroke="currentColor" strokeWidth="2"/>
          </svg>
          <span className="font-medium">Dashboard</span>
        </Link>
      </nav>
      
      <div className="p-6 border-t border-slate-700">
        <div className="flex flex-col gap-2">
          <p className="text-xs text-gray-400">v1.0.0</p>
          <div className="flex items-center gap-2 text-sm text-gray-300">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span>Sistema Activo</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
