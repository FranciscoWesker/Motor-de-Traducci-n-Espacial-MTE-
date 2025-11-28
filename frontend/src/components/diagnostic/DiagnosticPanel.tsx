import { AnalysisResponse } from '@/services/api'
import ConfidenceIndicator from './ConfidenceIndicator'
import './DiagnosticPanel.css'

interface DiagnosticPanelProps {
  analysis: AnalysisResponse
}

export default function DiagnosticPanel({ analysis }: DiagnosticPanelProps) {
  return (
    <div className="diagnostic-panel">
      <div className="panel-header">
        <h2>Diagnóstico Espacial</h2>
        <ConfidenceIndicator level={analysis.confiabilidad} />
      </div>

      <div className="panel-content">
        <section className="diagnostic-section">
          <h3>Sistema de Referencia (CRS)</h3>
          <div className="info-grid">
            <div className="info-item">
              <label>CRS Detectado:</label>
              <span className={analysis.crs_detectado ? 'value' : 'value-missing'}>
                {analysis.crs_detectado || 'No detectado'}
              </span>
            </div>
            <div className="info-item">
              <label>CRS Original:</label>
              <span>{analysis.crs_original || 'No especificado'}</span>
            </div>
            <div className="info-item">
              <label>Origen:</label>
              <span>{analysis.origen_detectado || 'No determinado'}</span>
            </div>
          </div>
        </section>

        <section className="diagnostic-section">
          <h3>Unidades y Escala</h3>
          <div className="info-grid">
            <div className="info-item">
              <label>Unidades Detectadas:</label>
              <span>{analysis.unidades_detectadas || 'No detectadas'}</span>
            </div>
            <div className="info-item">
              <label>Escala Estimada:</label>
              <span>{analysis.escala_estimada ? `1:${analysis.escala_estimada.toLocaleString()}` : 'No estimada'}</span>
            </div>
          </div>
        </section>

        {analysis.explicacion_tecnica && (
          <section className="diagnostic-section">
            <h3>Explicación Técnica</h3>
            <div className="explanation-box">
              <pre>{analysis.explicacion_tecnica}</pre>
            </div>
          </section>
        )}

        {analysis.recomendaciones && analysis.recomendaciones.length > 0 && (
          <section className="diagnostic-section">
            <h3>Recomendaciones</h3>
            <ul className="recommendations-list">
              {analysis.recomendaciones.map((rec, idx) => (
                <li key={idx}>{rec}</li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  )
}
