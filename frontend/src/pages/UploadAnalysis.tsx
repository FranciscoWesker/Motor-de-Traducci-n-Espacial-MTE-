import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import FileUploader from '../components/upload/FileUploader'
import { uploadFile, diagnoseFile } from '../services/api'
import './UploadAnalysis.css'

const UploadAnalysis = () => {
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const handleFileSelect = async (file: File) => {
    setError(null)
    setUploading(true)

    try {
      // Subir archivo
      const fileResponse = await uploadFile(file)
      
      setUploading(false)
      setAnalyzing(true)

      // Ejecutar análisis
      const analysis = await diagnoseFile(fileResponse.id)
      
      setAnalyzing(false)
      
      // Navegar a la página de resultados
      navigate(`/analysis/${analysis.id}`)
    } catch (err: any) {
      setUploading(false)
      setAnalyzing(false)
      setError(err.response?.data?.detail || err.message || 'Error al procesar el archivo')
    }
  }

  return (
    <div className="upload-analysis-page">
      <div className="upload-container">
        <h2>Análisis de Datos Espaciales</h2>
        <p className="page-description">
          Sube un archivo espacial (SHP, GeoJSON o CSV) para analizar su sistema de coordenadas,
          detectar el CRS, unidades y evaluar la calidad de los datos.
        </p>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {!uploading && !analyzing && (
          <FileUploader onFileSelect={handleFileSelect} />
        )}

        {uploading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Subiendo archivo...</p>
          </div>
        )}

        {analyzing && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Analizando datos espaciales...</p>
            <p className="loading-subtitle">Detectando CRS, unidades y validando geometrías...</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default UploadAnalysis

