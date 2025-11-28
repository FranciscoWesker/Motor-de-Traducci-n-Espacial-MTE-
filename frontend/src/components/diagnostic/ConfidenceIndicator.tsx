import './ConfidenceIndicator.css'

interface ConfidenceIndicatorProps {
  level: string
}

export default function ConfidenceIndicator({ level }: ConfidenceIndicatorProps) {
  const getColor = () => {
    switch (level.toLowerCase()) {
      case 'verde':
        return '#27ae60'
      case 'amarillo':
        return '#f39c12'
      case 'rojo':
        return '#e74c3c'
      default:
        return '#95a5a6'
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

  return (
    <div className="confidence-indicator" style={{ '--color': getColor() } as React.CSSProperties}>
      <div className="confidence-dot"></div>
      <span className="confidence-label">{getLabel()}</span>
    </div>
  )
}
