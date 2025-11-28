import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getAnalysis, getPreview, AnalysisResponse } from '@/services/api'
import MapViewer from '@/components/map/MapViewer'
import DiagnosticPanel from '@/components/diagnostic/DiagnosticPanel'
import './AnalysisDetailPage.css'

export default function AnalysisDetailPage() {
  const { analysisId } = useParams<{ analysisId: string }>()
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null)
  const [preview, setPreview] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadData = async () => {
      if (!analysisId) return

      try {
        setLoading(true)
        const [analysisData, previewData] = await Promise.all([
          getAnalysis(parseInt(analysisId)),
          getPreview(parseInt(analysisId))
        ])
        setAnalysis(analysisData)
        setPreview(previewData)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Error al cargar el análisis')
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [analysisId])

  if (loading) {
    return (
      <div className="analysis-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Cargando análisis...</p>
        </div>
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="analysis-page">
        <div className="error-container">
          <p>{error || 'Análisis no encontrado'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="analysis-page">
      <div className="analysis-layout">
        <div className="map-section">
          {preview && (
            <MapViewer geojson={preview.geojson} bounds={preview.bounds} />
          )}
        </div>
        <div className="diagnostic-section">
          <DiagnosticPanel analysis={analysis} />
        </div>
      </div>
    </div>
  )
}

