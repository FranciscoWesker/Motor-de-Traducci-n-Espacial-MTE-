import { AnalysisResponse } from '@/services/api'
import ConfidenceIndicator from './ConfidenceIndicator'
import './DiagnosticPanel.css'

interface DiagnosticPanelProps {
  analysis: AnalysisResponse
}

export default function DiagnosticPanel({ analysis }: DiagnosticPanelProps) {
  const isHighConfidence = analysis.confiabilidad.toLowerCase() === 'verde'
  const hasCompleteData = analysis.crs_detectado && analysis.unidades_detectadas && analysis.escala_estimada

  return (
    <div className="diagnostic-panel">
      {isHighConfidence && (
        <div className="success-banner">
          <div className="success-banner-content">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            <div>
              <h3>Datos de Alta Calidad</h3>
              <p>Este análisis cumple con los estándares de calidad espacial y está listo para uso profesional</p>
            </div>
          </div>
        </div>
      )}
      
      <div className="panel-header">
        <h2>Diagnóstico Espacial</h2>
        <ConfidenceIndicator level={analysis.confiabilidad} size="large" />
      </div>

      {isHighConfidence && hasCompleteData && (
        <div className="quality-metrics">
          <div className="quality-metric-card">
            <div className="metric-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2L2 7L12 12L22 7L12 2Z"></path>
                <path d="M2 17L12 22L22 17"></path>
                <path d="M2 12L12 17L22 12"></path>
              </svg>
            </div>
            <div className="metric-content">
              <span className="metric-label">CRS Verificado</span>
              <span className="metric-value">{analysis.crs_detectado}</span>
            </div>
          </div>
          {analysis.escala_estimada && (
            <div className="quality-metric-card">
              <div className="metric-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
              </div>
              <div className="metric-content">
                <span className="metric-label">Escala Detectada</span>
                <span className="metric-value">1:{Math.round(analysis.escala_estimada).toLocaleString()}</span>
              </div>
            </div>
          )}
          {analysis.unidades_detectadas && (
            <div className="quality-metric-card">
              <div className="metric-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="9" y1="3" x2="9" y2="21"></line>
                </svg>
              </div>
              <div className="metric-content">
                <span className="metric-label">Unidades</span>
                <span className="metric-value">{analysis.unidades_detectadas}</span>
              </div>
            </div>
          )}
        </div>
      )}

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
