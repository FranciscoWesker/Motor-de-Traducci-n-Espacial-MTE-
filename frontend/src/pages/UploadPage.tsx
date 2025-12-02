import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import FileUploader from '@/components/upload/FileUploader'
import { diagnoseFile } from '@/services/api'

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
    <div className="p-8 max-w-6xl mx-auto">
      <div className="card">
        <div className="mb-8">
          <h2 className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-3">
            Cargar y Analizar Archivo Espacial
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Sube un archivo espacial para analizar su sistema de coordenadas, detectar CRS, unidades y evaluar su calidad.
            El sistema detectará automáticamente el sistema de referencia y proporcionará recomendaciones profesionales.
          </p>
        </div>
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-center gap-3">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 18C14.4183 18 18 14.4183 18 10C18 5.58172 14.4183 2 10 2C5.58172 2 2 5.58172 2 10C2 14.4183 5.58172 18 10 18Z" stroke="currentColor" strokeWidth="2"/>
              <path d="M10 6V10M10 14H10.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <span className="font-medium">{error}</span>
          </div>
        )}

        {isAnalyzing ? (
          <div className="flex flex-col items-center gap-4 py-12 text-primary-600">
            <div className="w-12 h-12 border-4 border-gray-200 border-t-primary-500 rounded-full animate-spin"></div>
            <p className="text-lg font-semibold text-gray-700">Analizando archivo espacial...</p>
            <p className="text-sm text-gray-600">Detectando CRS, unidades y validando geometrías</p>
          </div>
        ) : (
          <>
            <FileUploader
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
            />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 pt-8 border-t border-gray-200">
              <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M9 12L11 14L15 10" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M21 12C21 16.971 16.971 21 12 21C7.029 21 3 16.971 3 12C3 7.029 7.029 3 12 3C16.971 3 21 7.029 21 12Z" stroke="#10b981" strokeWidth="2"/>
                  </svg>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-1">Detección Automática</h4>
                  <p className="text-xs text-gray-600">CRS, unidades y origen</p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="#667eea" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M2 17L12 22L22 17" stroke="#667eea" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M2 12L12 17L22 12" stroke="#667eea" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-1">Validación Completa</h4>
                  <p className="text-xs text-gray-600">Geometrías y calidad</p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-1">Recomendaciones</h4>
                  <p className="text-xs text-gray-600">Casos de uso y mejoras</p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
