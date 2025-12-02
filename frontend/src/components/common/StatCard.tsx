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

const colorClasses = {
  blue: 'border-t-primary-500',
  green: 'border-t-green-500',
  purple: 'border-t-purple-500',
  orange: 'border-t-orange-500',
}

const iconBgClasses = {
  blue: 'bg-primary-50 text-primary-600',
  green: 'bg-green-50 text-green-600',
  purple: 'bg-purple-50 text-purple-600',
  orange: 'bg-orange-50 text-orange-600',
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
    <div className={`card border-t-4 ${colorClasses[color]} hover:shadow-md transition-shadow`}>
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">{title}</h3>
        {icon && (
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${iconBgClasses[color]}`}>
            {icon}
          </div>
        )}
      </div>
      <div className="space-y-1">
        <div className="text-3xl font-bold text-gray-900">{value}</div>
        {subtitle && <div className="text-sm text-gray-600">{subtitle}</div>}
        {trend && (
          <div className={`flex items-center gap-1 text-sm font-semibold ${
            trend.isPositive ? 'text-green-600' : 'text-red-600'
          }`}>
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
