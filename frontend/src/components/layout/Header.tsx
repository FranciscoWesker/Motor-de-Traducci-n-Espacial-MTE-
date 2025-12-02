import './Header.css'

interface HeaderProps {
  title?: string
  subtitle?: string
}

export default function Header({ title, subtitle }: HeaderProps) {
  return (
    <header className="main-header">
      <div className="header-content">
        {title && <h1 className="header-title">{title}</h1>}
        {subtitle && <p className="header-subtitle">{subtitle}</p>}
      </div>
      <div className="header-actions">
        <button className="header-btn">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 2V18M2 10H18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
        <button className="header-btn">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M15 17.5C15 16.672 15.672 16 16.5 16C17.328 16 18 16.672 18 17.5C18 18.328 17.328 19 16.5 19C15.672 19 15 18.328 15 17.5Z" fill="currentColor"/>
            <path d="M10 17.5C10 16.672 10.672 16 11.5 16C12.328 16 13 16.672 13 17.5C13 18.328 12.328 19 11.5 19C10.672 19 10 18.328 10 17.5Z" fill="currentColor"/>
            <path d="M5 17.5C5 16.672 5.672 16 6.5 16C7.328 16 8 16.672 8 17.5C8 18.328 7.328 19 6.5 19C5.672 19 5 18.328 5 17.5Z" fill="currentColor"/>
          </svg>
        </button>
      </div>
    </header>
  )
}

