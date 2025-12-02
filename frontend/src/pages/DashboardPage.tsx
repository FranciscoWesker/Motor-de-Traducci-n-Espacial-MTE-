import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import StatCard from '@/components/common/StatCard'
import { getDashboardStats, DashboardStats } from '@/services/api'

export default function DashboardPage() {
  const navigate = useNavigate()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await getDashboardStats()
        setStats(data)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Error al cargar estadísticas')
        console.error('Error loading dashboard stats:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
          <div className="w-12 h-12 border-4 border-gray-200 border-t-primary-500 rounded-full animate-spin"></div>
          <p className="text-gray-600">Cargando estadísticas...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
          <div className="w-12 h-12 text-red-500">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
              <path d="M12 8V12M12 16H12.01M21 12C21 16.971 16.971 21 12 21C7.029 21 3 16.971 3 12C3 7.029 7.029 3 12 3C16.971 3 21 7.029 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <p className="text-gray-700 font-medium">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="btn-primary"
          >
            Reintentar
          </button>
        </div>
      </div>
    )
  }

  if (!stats) {
    return null
  }

  const getConfidenceColor = (confiabilidad: string) => {
    switch (confiabilidad) {
      case 'verde': return 'bg-green-500'
      case 'amarillo': return 'bg-yellow-500'
      case 'rojo': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getConfidenceLabel = (confiabilidad: string) => {
    switch (confiabilidad) {
      case 'verde': return 'Alta'
      case 'amarillo': return 'Media'
      case 'rojo': return 'Baja'
      default: return 'Desconocida'
    }
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Vista general del sistema de análisis espacial</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total de Análisis"
          value={stats.total_analyses}
          subtitle="Análisis completados"
          color="blue"
          icon={
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M9 11L12 14L22 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M21 12V19C21 20.105 20.105 21 19 21H5C3.895 21 3 20.105 3 19V5C3 3.895 3.895 3 5 3H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          }
        />
        
        <StatCard
          title="Análisis Exitosos"
          value={stats.successful_analyses}
          subtitle={`${stats.success_rate}% de éxito`}
          color="green"
          icon={
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          }
        />
        
        <StatCard
          title="Confianza Promedio"
          value={`${stats.average_confidence}%`}
          subtitle="Nivel de confianza"
          color="purple"
          icon={
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          }
        />
        
        <StatCard
          title="Archivos Procesados"
          value={stats.total_files}
          subtitle="Total de archivos"
          color="orange"
          icon={
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          }
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Análisis Recientes</h2>
          <div className="min-h-[200px]">
            {stats.recent_analyses.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none" className="opacity-50 mb-4">
                  <path d="M32 8L8 20V44L32 56L56 44V20L32 8Z" stroke="#9ca3af" strokeWidth="2"/>
                  <path d="M32 24L20 30V38L32 44L44 38V30L32 24Z" stroke="#9ca3af" strokeWidth="2"/>
                </svg>
                <p className="text-gray-600 font-medium">No hay análisis recientes</p>
                <p className="text-sm text-gray-500 mt-1">Sube un archivo para comenzar</p>
              </div>
            ) : (
              <div className="space-y-3">
                {stats.recent_analyses.map((analysis) => (
                  <div 
                    key={analysis.id} 
                    className="p-4 border border-gray-200 rounded-lg bg-white hover:border-primary-400 hover:shadow-md transition-all cursor-pointer"
                    onClick={() => navigate(`/analysis/${analysis.id}`)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="text-sm font-semibold text-gray-900 truncate flex-1">
                        {analysis.archivo_nombre}
                      </h4>
                      <span 
                        className={`px-2 py-1 rounded-md text-xs font-semibold uppercase ml-2 ${
                          analysis.confiabilidad === 'verde' 
                            ? 'bg-green-100 text-green-700' 
                            : analysis.confiabilidad === 'amarillo'
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-red-100 text-red-700'
                        }`}
                      >
                        {getConfidenceLabel(analysis.confiabilidad)}
                      </span>
                    </div>
                    <div className="flex gap-4 flex-wrap text-xs text-gray-600">
                      <span className="flex items-center gap-1">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2"/>
                        </svg>
                        {analysis.crs_detectado}
                      </span>
                      {analysis.escala_estimada && (
                        <span className="flex items-center gap-1">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" strokeWidth="2"/>
                          </svg>
                          1:{analysis.escala_estimada.toLocaleString()}
                        </span>
                      )}
                    </div>
                    {analysis.fecha_analisis && (
                      <div className="text-xs text-gray-500 mt-2">
                        {new Date(analysis.fecha_analisis).toLocaleDateString('es-ES', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Estadísticas de Calidad</h2>
          <div className="space-y-6">
            <div>
              <div className="flex justify-between text-sm font-semibold text-gray-700 mb-2">
                <span>Alta Confianza</span>
                <span>{stats.quality_stats.alta_confianza.percentage}%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all duration-500"
                  style={{ width: `${stats.quality_stats.alta_confianza.percentage}%` }}
                ></div>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {stats.quality_stats.alta_confianza.count} análisis
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm font-semibold text-gray-700 mb-2">
                <span>Confianza Media</span>
                <span>{stats.quality_stats.media_confianza.percentage}%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-yellow-500 to-yellow-600 transition-all duration-500"
                  style={{ width: `${stats.quality_stats.media_confianza.percentage}%` }}
                ></div>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {stats.quality_stats.media_confianza.count} análisis
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm font-semibold text-gray-700 mb-2">
                <span>Baja Confianza</span>
                <span>{stats.quality_stats.baja_confianza.percentage}%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-red-500 to-red-600 transition-all duration-500"
                  style={{ width: `${stats.quality_stats.baja_confianza.percentage}%` }}
                ></div>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {stats.quality_stats.baja_confianza.count} análisis
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
