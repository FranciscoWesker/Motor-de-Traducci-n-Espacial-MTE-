import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { listAnalyses, AnalysisListItem } from '@/services/api'

export default function AnalysesPage() {
  const navigate = useNavigate()
  const [analyses, setAnalyses] = useState<AnalysisListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    const fetchAnalyses = async () => {
      try {
        setLoading(true)
        setError(null)
        const response = await listAnalyses(0, 100, filter === 'all' ? undefined : filter)
        setAnalyses(response.items)
        setTotal(response.total)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Error al cargar análisis')
        console.error('Error loading analyses:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchAnalyses()
  }, [filter])

  const getConfidenceLabel = (confiabilidad: string) => {
    switch (confiabilidad) {
      case 'verde': return 'Alta'
      case 'amarillo': return 'Media'
      case 'rojo': return 'Baja'
      default: return 'Desconocida'
    }
  }

  const getConfidenceColor = (confiabilidad: string) => {
    switch (confiabilidad) {
      case 'verde': return 'bg-green-100 text-green-700 border-green-200'
      case 'amarillo': return 'bg-yellow-100 text-yellow-700 border-yellow-200'
      case 'rojo': return 'bg-red-100 text-red-700 border-red-200'
      default: return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
          <div className="w-12 h-12 border-4 border-gray-200 border-t-primary-500 rounded-full animate-spin"></div>
          <p className="text-gray-600">Cargando análisis...</p>
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

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Análisis</h1>
        <p className="text-gray-600">Lista completa de todos los análisis realizados</p>
      </div>

      {/* Filtros */}
      <div className="mb-6 flex gap-3 flex-wrap">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'all'
              ? 'bg-primary-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Todos ({total})
        </button>
        <button
          onClick={() => setFilter('verde')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'verde'
              ? 'bg-green-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Alta Confianza
        </button>
        <button
          onClick={() => setFilter('amarillo')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'amarillo'
              ? 'bg-yellow-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Media Confianza
        </button>
        <button
          onClick={() => setFilter('rojo')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'rojo'
              ? 'bg-red-500 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Baja Confianza
        </button>
      </div>

      {/* Lista de análisis */}
      <div className="card">
        {analyses.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <svg width="64" height="64" viewBox="0 0 64 64" fill="none" className="opacity-50 mb-4">
              <path d="M32 8L8 20V44L32 56L56 44V20L32 8Z" stroke="#9ca3af" strokeWidth="2"/>
              <path d="M32 24L20 30V38L32 44L44 38V30L32 24Z" stroke="#9ca3af" strokeWidth="2"/>
            </svg>
            <p className="text-gray-600 font-medium text-lg mb-1">No hay análisis disponibles</p>
            <p className="text-sm text-gray-500">Sube un archivo para comenzar a analizar</p>
            <button
              onClick={() => navigate('/upload')}
              className="btn-primary mt-4"
            >
              Subir Archivo
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {analyses.map((analysis) => (
              <div
                key={analysis.id}
                className="p-5 border border-gray-200 rounded-lg bg-white hover:border-primary-400 hover:shadow-md transition-all cursor-pointer"
                onClick={() => navigate(`/analysis/${analysis.id}`)}
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {analysis.archivo_nombre}
                    </h3>
                    <div className="flex gap-4 flex-wrap text-sm text-gray-600">
                      {analysis.crs_detectado && (
                        <span className="flex items-center gap-1">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2"/>
                          </svg>
                          {analysis.crs_detectado}
                        </span>
                      )}
                      {analysis.escala_estimada && (
                        <span className="flex items-center gap-1">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                            <polyline points="12 6 12 12 16 14" stroke="currentColor" strokeWidth="2"/>
                          </svg>
                          Escala: 1:{analysis.escala_estimada.toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2 ml-4">
                    <span
                      className={`px-3 py-1 rounded-md text-xs font-semibold uppercase border ${getConfidenceColor(analysis.confiabilidad)}`}
                    >
                      {getConfidenceLabel(analysis.confiabilidad)}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(analysis.fecha_analisis).toLocaleDateString('es-ES', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-sm text-primary-600 mt-3">
                  <span>Ver detalles</span>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

