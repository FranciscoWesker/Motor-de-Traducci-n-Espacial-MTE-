import { useEffect, useState } from 'react'
import StatCard from '@/components/common/StatCard'
import './DashboardPage.css'

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalAnalyses: 0,
    successfulAnalyses: 0,
    averageConfidence: 0,
    totalFiles: 0
  })

  useEffect(() => {
    // TODO: Fetch real stats from API
    setStats({
      totalAnalyses: 42,
      successfulAnalyses: 38,
      averageConfidence: 87,
      totalFiles: 56
    })
  }, [])

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Vista general del sistema de análisis espacial</p>
      </div>

      <div className="dashboard-stats">
        <StatCard
          title="Total de Análisis"
          value={stats.totalAnalyses}
          subtitle="Análisis completados"
          color="blue"
          icon={
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M9 11L12 14L22 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M21 12V19C21 20.105 20.105 21 19 21H5C3.895 21 3 20.105 3 19V5C3 3.895 3.895 3 5 3H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          }
          trend={{ value: 12, isPositive: true }}
        />
        
        <StatCard
          title="Análisis Exitosos"
          value={stats.successfulAnalyses}
          subtitle={`${Math.round((stats.successfulAnalyses / stats.totalAnalyses) * 100)}% de éxito`}
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
          value={`${stats.averageConfidence}%`}
          subtitle="Nivel de confianza"
          color="purple"
          icon={
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          }
          trend={{ value: 5, isPositive: true }}
        />
        
        <StatCard
          title="Archivos Procesados"
          value={stats.totalFiles}
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
            <div className="empty-state">
              <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                <path d="M32 8L8 20V44L32 56L56 44V20L32 8Z" stroke="#9ca3af" strokeWidth="2"/>
                <path d="M32 24L20 30V38L32 44L44 38V30L32 24Z" stroke="#9ca3af" strokeWidth="2"/>
              </svg>
              <p>No hay análisis recientes</p>
              <p className="empty-state-subtitle">Sube un archivo para comenzar</p>
            </div>
          </div>
        </div>

        <div className="dashboard-section">
          <h2>Estadísticas de Calidad</h2>
          <div className="quality-stats">
            <div className="quality-bar">
              <div className="quality-bar-label">
                <span>Alta Confianza</span>
                <span>65%</span>
              </div>
              <div className="quality-bar-track">
                <div className="quality-bar-fill quality-bar-green" style={{ width: '65%' }}></div>
              </div>
            </div>
            <div className="quality-bar">
              <div className="quality-bar-label">
                <span>Confianza Media</span>
                <span>25%</span>
              </div>
              <div className="quality-bar-track">
                <div className="quality-bar-fill quality-bar-yellow" style={{ width: '25%' }}></div>
              </div>
            </div>
            <div className="quality-bar">
              <div className="quality-bar-label">
                <span>Baja Confianza</span>
                <span>10%</span>
              </div>
              <div className="quality-bar-track">
                <div className="quality-bar-fill quality-bar-red" style={{ width: '10%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

