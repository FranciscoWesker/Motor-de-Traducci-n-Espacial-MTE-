import { AnalysisResponse, AnalysisPreview } from '@/services/api'
import './ComparisonMetrics.css'

interface ComparisonMetricsProps {
  analysis: AnalysisResponse
  originalPreview: AnalysisPreview
  transformedPreview: AnalysisPreview | null
}

export default function ComparisonMetrics({
  analysis,
  originalPreview,
  transformedPreview
}: ComparisonMetricsProps) {
  return (
    <div className="comparison-metrics">
      <h3>Métricas de Comparación</h3>
      <div className="metrics-grid">
        <div className="metric-card">
          <h4>CRS</h4>
          <div className="metric-value">
            <div className="original-value">
              <span className="label">Original:</span>
              <span>{originalPreview.crs_aplicado || 'No especificado'}</span>
            </div>
            {transformedPreview && (
              <div className="transformed-value">
                <span className="label">Transformado:</span>
                <span>{transformedPreview.crs_aplicado}</span>
              </div>
            )}
          </div>
        </div>

        <div className="metric-card">
          <h4>Escala Estimada</h4>
          <div className="metric-value">
            {analysis.escala_estimada ? (
              <span>1:{analysis.escala_estimada.toLocaleString()}</span>
            ) : (
              <span className="no-data">No estimada</span>
            )}
          </div>
        </div>

        <div className="metric-card">
          <h4>Error Planimétrico</h4>
          <div className="metric-value">
            {analysis.error_planimetrico !== null ? (
              <span>{analysis.error_planimetrico.toFixed(2)} m</span>
            ) : (
              <span className="no-data">No calculado</span>
            )}
          </div>
        </div>

        <div className="metric-card">
          <h4>Error Altimétrico</h4>
          <div className="metric-value">
            {analysis.error_altimetrico !== null ? (
              <span>{analysis.error_altimetrico.toFixed(2)} m</span>
            ) : (
              <span className="no-data">No disponible</span>
            )}
          </div>
        </div>

        <div className="metric-card">
          <h4>Confiabilidad</h4>
          <div className="metric-value">
            <span className={`confidence-badge ${analysis.confiabilidad}`}>
              {analysis.confiabilidad.toUpperCase()}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

