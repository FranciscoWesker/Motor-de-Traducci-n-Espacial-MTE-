import { useState, useCallback } from 'react'
import { uploadFile } from '@/services/api'

interface FileUploaderProps {
  onUploadSuccess: (fileId: number) => void
  onUploadError: (error: string) => void
}

export default function FileUploader({ onUploadSuccess, onUploadError }: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)

  const handleFile = useCallback(async (file: File) => {
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
      className={`relative border-2 border-dashed rounded-2xl p-16 text-center cursor-pointer transition-all ${
        isDragging 
          ? 'border-primary-500 bg-primary-50 scale-[1.01] shadow-lg' 
          : 'border-gray-300 bg-gradient-to-br from-gray-50 to-white hover:border-primary-400 hover:bg-primary-50/50'
      } ${isUploading ? 'border-primary-500 bg-primary-50 cursor-wait' : ''}`}
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
        className="hidden"
      />
      <label htmlFor="file-input" className="block cursor-pointer">
        {isUploading ? (
          <div className="flex flex-col items-center gap-4 text-primary-600">
            <div className="w-12 h-12 border-4 border-gray-200 border-t-primary-500 rounded-full animate-spin"></div>
            <p className="text-base font-semibold text-gray-700">Cargando archivo...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-6">
            <div className="w-20 h-20 text-primary-500 drop-shadow-md animate-bounce">
              <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Arrastra un archivo aquí o haz clic para seleccionar
              </h3>
              <p className="text-sm text-gray-600 mb-4">Tamaño máximo: 50 MB</p>
            </div>
            <div className="flex justify-center gap-2 flex-wrap">
              <span className="px-3 py-1.5 bg-primary-100 text-primary-700 rounded-md text-xs font-semibold uppercase tracking-wide">
                SHP
              </span>
              <span className="px-3 py-1.5 bg-primary-100 text-primary-700 rounded-md text-xs font-semibold uppercase tracking-wide">
                GeoJSON
              </span>
              <span className="px-3 py-1.5 bg-primary-100 text-primary-700 rounded-md text-xs font-semibold uppercase tracking-wide">
                CSV
              </span>
            </div>
          </div>
        )}
      </label>
    </div>
  )
}
