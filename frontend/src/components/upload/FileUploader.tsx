import { useState, useCallback } from 'react'
import { uploadFile } from '@/services/api'
import './FileUploader.css'

interface FileUploaderProps {
  onUploadSuccess: (fileId: number) => void
  onUploadError: (error: string) => void
}

export default function FileUploader({ onUploadSuccess, onUploadError }: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)

  const handleFile = useCallback(async (file: File) => {
    // Validar formato
    const validExtensions = ['.shp', '.geojson', '.json', '.csv']
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
    
    if (!validExtensions.includes(fileExtension)) {
      onUploadError(`Formato no soportado. Formatos válidos: ${validExtensions.join(', ')}`)
      return
    }

    setIsUploading(true)
    try {
      const response = await uploadFile(file)
      onUploadSuccess(response.id)
    } catch (error: any) {
      onUploadError(error.response?.data?.detail || 'Error al cargar el archivo')
    } finally {
      setIsUploading(false)
    }
  }, [onUploadSuccess, onUploadError])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const file = e.dataTransfer.files[0]
    if (file) {
      handleFile(file)
    }
  }, [handleFile])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFile(file)
    }
  }, [handleFile])

  return (
    <div
      className={`file-uploader ${isDragging ? 'dragging' : ''} ${isUploading ? 'uploading' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <input
        type="file"
        id="file-input"
        accept=".shp,.geojson,.json,.csv"
        onChange={handleFileInput}
        disabled={isUploading}
        style={{ display: 'none' }}
      />
      <label htmlFor="file-input" className="upload-label">
        {isUploading ? (
          <div className="upload-progress">
            <div className="spinner"></div>
            <p>Cargando archivo...</p>
          </div>
        ) : (
          <div className="upload-content">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            <div>
              <h3>Arrastra un archivo aquí o haz clic para seleccionar</h3>
              <p>Tamaño máximo: 50 MB</p>
            </div>
            <div className="format-badges">
              <span className="format-badge">SHP</span>
              <span className="format-badge">GeoJSON</span>
              <span className="format-badge">CSV</span>
            </div>
          </div>
        )}
      </label>
    </div>
  )
}
