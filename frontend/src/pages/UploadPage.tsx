import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import FileUploader from '@/components/upload/FileUploader'
import { diagnoseFile } from '@/services/api'
import './UploadPage.css'

export default function UploadPage() {
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleUploadSuccess = async (fileId: number) => {
    setError(null)
    setIsAnalyzing(true)
    
    try {
      const analysis = await diagnoseFile(fileId)
      navigate(`/analysis/${analysis.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al analizar el archivo')
      setIsAnalyzing(false)
    }
  }

  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage)
  }

  return (
    <div className="upload-page">
      <div className="upload-container">
        <div className="upload-header">
          <h2>Cargar y Analizar Archivo Espacial</h2>
          <p className="upload-description">
            Sube un archivo espacial para analizar su sistema de coordenadas, detectar CRS, unidades y evaluar su calidad.
            El sistema detectará automáticamente el sistema de referencia y proporcionará recomendaciones profesionales.
          </p>
        </div>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {isAnalyzing ? (
          <div className="analyzing-message">
            <div className="spinner"></div>
            <p>Analizando archivo espacial...</p>
            <p className="analyzing-subtitle">Detectando CRS, unidades y validando geometrías</p>
          </div>
        ) : (
          <>
            <FileUploader
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
            />
            <div className="upload-features">
              <div className="feature-item">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M9 12L11 14L15 10" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M21 12C21 16.971 16.971 21 12 21C7.029 21 3 16.971 3 12C3 7.029 7.029 3 12 3C16.971 3 21 7.029 21 12Z" stroke="#10b981" strokeWidth="2"/>
                </svg>
                <div>
                  <h4>Detección Automática</h4>
                  <p>CRS, unidades y origen</p>
                </div>
              </div>
              <div className="feature-item">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="#667eea" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 17L12 22L22 17" stroke="#667eea" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M2 12L12 17L22 12" stroke="#667eea" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <div>
                  <h4>Validación Completa</h4>
                  <p>Geometrías y calidad</p>
                </div>
              </div>
              <div className="feature-item">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <div>
                  <h4>Recomendaciones</h4>
                  <p>Casos de uso y mejoras</p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

