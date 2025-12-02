import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import StatCard from '@/components/common/StatCard'
import { getDashboardStats, DashboardStats } from '@/services/api'
import './DashboardPage.css'

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
    // Actualizar cada 30 segundos
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-loading">
          <div className="spinner"></div>
          <p>Cargando estadísticas...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-error">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
            <path d="M12 8V12M12 16H12.01M21 12C21 16.971 16.971 21 12 21C7.029 21 3 16.971 3 12C3 7.029 7.029 3 12 3C16.971 3 21 7.029 21 12Z" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
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
      case 'verde': return '#10b981'
      case 'amarillo': return '#f59e0b'
      case 'rojo': return '#ef4444'
      default: return '#6b7280'
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
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Vista general del sistema de análisis espacial</p>
      </div>

      <div className="dashboard-stats">
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

      <div className="dashboard-content">
        <div className="dashboard-section">
          <h2>Análisis Recientes</h2>
          <div className="recent-analyses">
            {stats.recent_analyses.length === 0 ? (
              <div className="empty-state">
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                  <path d="M32 8L8 20V44L32 56L56 44V20L32 8Z" stroke="#9ca3af" strokeWidth="2"/>
                  <path d="M32 24L20 30V38L32 44L44 38V30L32 24Z" stroke="#9ca3af" strokeWidth="2"/>
                </svg>
                <p>No hay análisis recientes</p>
                <p className="empty-state-subtitle">Sube un archivo para comenzar</p>
              </div>
            ) : (
              <div className="recent-analyses-list">
                {stats.recent_analyses.map((analysis) => (
                  <div 
                    key={analysis.id} 
                    className="recent-analysis-item"
                    onClick={() => navigate(`/analysis/${analysis.id}`)}
                  >
                    <div className="analysis-item-header">
                      <h4>{analysis.archivo_nombre}</h4>
                      <span 
                        className="confidence-badge"
                        style={{ 
                          backgroundColor: getConfidenceColor(analysis.confiabilidad) + '20',
                          color: getConfidenceColor(analysis.confiabilidad)
                        }}
                      >
                        {getConfidenceLabel(analysis.confiabilidad)}
                      </span>
                    </div>
                    <div className="analysis-item-details">
                      <span className="detail-item">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2"/>
                        </svg>
                        {analysis.crs_detectado}
                      </span>
                      {analysis.escala_estimada && (
                        <span className="detail-item">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" strokeWidth="2"/>
                          </svg>
                          1:{analysis.escala_estimada.toLocaleString()}
                        </span>
                      )}
                    </div>
                    {analysis.fecha_analisis && (
                      <div className="analysis-item-date">
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

        <div className="dashboard-section">
          <h2>Estadísticas de Calidad</h2>
          <div className="quality-stats">
            <div className="quality-bar">
              <div className="quality-bar-label">
                <span>Alta Confianza</span>
                <span>{stats.quality_stats.alta_confianza.percentage}%</span>
              </div>
              <div className="quality-bar-track">
                <div 
                  className="quality-bar-fill quality-bar-green" 
                  style={{ width: `${stats.quality_stats.alta_confianza.percentage}%` }}
                ></div>
              </div>
              <div className="quality-bar-count">
                {stats.quality_stats.alta_confianza.count} análisis
              </div>
            </div>
            <div className="quality-bar">
              <div className="quality-bar-label">
                <span>Confianza Media</span>
                <span>{stats.quality_stats.media_confianza.percentage}%</span>
              </div>
              <div className="quality-bar-track">
                <div 
                  className="quality-bar-fill quality-bar-yellow" 
                  style={{ width: `${stats.quality_stats.media_confianza.percentage}%` }}
                ></div>
              </div>
              <div className="quality-bar-count">
                {stats.quality_stats.media_confianza.count} análisis
              </div>
            </div>
            <div className="quality-bar">
              <div className="quality-bar-label">
                <span>Baja Confianza</span>
                <span>{stats.quality_stats.baja_confianza.percentage}%</span>
              </div>
              <div className="quality-bar-track">
                <div 
                  className="quality-bar-fill quality-bar-red" 
                  style={{ width: `${stats.quality_stats.baja_confianza.percentage}%` }}
                ></div>
              </div>
              <div className="quality-bar-count">
                {stats.quality_stats.baja_confianza.count} análisis
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

