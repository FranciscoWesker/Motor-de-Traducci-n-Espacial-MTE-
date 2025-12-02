import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getAnalysis, getPreview, AnalysisResponse, AnalysisPreview } from '@/services/api'
import SideBySideMap from '@/components/comparison/SideBySideMap'
import ComparisonMetrics from '@/components/comparison/ComparisonMetrics'
import './ComparisonPage.css'

export default function ComparisonPage() {
  const { analysisId, transformationId } = useParams<{ analysisId: string; transformationId?: string }>()
  const navigate = useNavigate()
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null)
  const [originalPreview, setOriginalPreview] = useState<AnalysisPreview | null>(null)
  const [transformedPreview, setTransformedPreview] = useState<AnalysisPreview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      if (!analysisId) return

      try {
        setLoading(true)
        const [analysisData, originalPreviewData] = await Promise.all([
          getAnalysis(parseInt(analysisId)),
          getPreview(parseInt(analysisId))
        ])
        setAnalysis(analysisData)
        setOriginalPreview(originalPreviewData)

        // Si hay transformationId, cargar preview transformado
        if (transformationId) {
          try {
            const response = await fetch(`/api/v1/transformation/${transformationId}/preview`)
            if (response.ok) {
              const transformedData = await response.json()
              setTransformedPreview(transformedData)
            }
          } catch (err) {
            console.warn('No se pudo cargar preview transformado:', err)
          }
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Error al cargar datos para comparación')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [analysisId, transformationId])

  if (loading) {
    return (
      <div className="comparison-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Cargando datos para comparación...</p>
        </div>
      </div>
    )
  }

  if (error || !analysis || !originalPreview) {
    return (
      <div className="comparison-page">
        <div className="error-container">
          <p>{error || 'Datos no encontrados'}</p>
          <button onClick={() => navigate(`/analysis/${analysisId}`)}>
            Volver al análisis
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="comparison-page">
      <div className="comparison-header">
        <h2>Comparación Antes/Después</h2>
        <button onClick={() => navigate(`/analysis/${analysisId}`)}>
          Volver al análisis
        </button>
      </div>

      <div className="comparison-content">
        <ComparisonMetrics
          analysis={analysis}
          originalPreview={originalPreview}
          transformedPreview={transformedPreview}
        />

        <SideBySideMap
          originalData={originalPreview}
          transformedData={transformedPreview}
        />
      </div>
    </div>
  )
}

