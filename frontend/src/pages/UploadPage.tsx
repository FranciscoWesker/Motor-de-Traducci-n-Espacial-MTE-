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
        <h2>Cargar y Analizar Archivo Espacial</h2>
        <p className="upload-description">
          Sube un archivo espacial (SHP, GeoJSON o CSV) para analizar su sistema de coordenadas,
          detectar CRS, unidades y evaluar su calidad.
        </p>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {isAnalyzing ? (
          <div className="analyzing-message">
            <div className="spinner"></div>
            <p>Analizando archivo...</p>
          </div>
        ) : (
          <FileUploader
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        )}
      </div>
    </div>
  )
}

