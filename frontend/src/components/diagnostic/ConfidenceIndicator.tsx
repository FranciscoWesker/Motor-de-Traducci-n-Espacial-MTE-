import './ConfidenceIndicator.css'

interface ConfidenceIndicatorProps {
  level: string
  showIcon?: boolean
  size?: 'small' | 'medium' | 'large'
}

export default function ConfidenceIndicator({ level, showIcon = true, size = 'medium' }: ConfidenceIndicatorProps) {
  const isHighConfidence = level.toLowerCase() === 'verde'
  
  const getColor = () => {
    switch (level.toLowerCase()) {
      case 'verde':
        return '#10b981'
      case 'amarillo':
        return '#f59e0b'
      case 'rojo':
        return '#ef4444'
      default:
        return '#6b7280'
    }
  }

  const getLabel = () => {
    switch (level.toLowerCase()) {
      case 'verde':
        return 'Confiabilidad Alta'
      case 'amarillo':
        return 'Confiabilidad Media'
      case 'rojo':
        return 'Confiabilidad Baja'
      default:
        return 'Desconocido'
    }
  }

  const getIcon = () => {
    if (!showIcon) return null
    
    if (isHighConfidence) {
      return (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
      )
    }
    return null
  }

  return (
    <div 
      className={`confidence-indicator ${isHighConfidence ? 'high-confidence' : ''} ${size}`}
      style={{ '--color': getColor() } as React.CSSProperties}
    >
      {getIcon()}
      <div className="confidence-dot"></div>
      <span className="confidence-label">{getLabel()}</span>
    </div>
  )
}
