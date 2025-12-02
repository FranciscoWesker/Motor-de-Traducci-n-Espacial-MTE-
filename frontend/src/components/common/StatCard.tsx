import './StatCard.css'

interface StatCardProps {
  title: string
  value: string | number
  icon?: React.ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  subtitle?: string
  color?: 'blue' | 'green' | 'purple' | 'orange'
}

export default function StatCard({ 
  title, 
  value, 
  icon, 
  trend, 
  subtitle,
  color = 'blue' 
}: StatCardProps) {
  return (
    <div className={`stat-card stat-card-${color}`}>
      <div className="stat-card-header">
        <h3 className="stat-card-title">{title}</h3>
        {icon && <div className="stat-card-icon">{icon}</div>}
      </div>
      <div className="stat-card-body">
        <div className="stat-card-value">{value}</div>
        {subtitle && <div className="stat-card-subtitle">{subtitle}</div>}
        {trend && (
          <div className={`stat-card-trend ${trend.isPositive ? 'positive' : 'negative'}`}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              {trend.isPositive ? (
                <path d="M8 4L12 8H9V12H7V8H4L8 4Z" fill="currentColor"/>
              ) : (
                <path d="M8 12L4 8H7V4H9V8H12L8 12Z" fill="currentColor"/>
              )}
            </svg>
            <span>{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>
    </div>
  )
}

