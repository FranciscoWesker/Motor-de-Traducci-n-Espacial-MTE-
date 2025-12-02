import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface FileUploadResponse {
  id: number
  nombre_archivo: string
  formato: string
  tamaño: number
  fecha_carga: string
}

export interface AnalysisResponse {
  id: number
  archivo_id: number
  crs_detectado: string | null
  crs_original: string | null
  unidades_detectadas: string | null
  origen_detectado: string | null
  escala_estimada: number | null
  error_planimetrico: number | null
  error_altimetrico: number | null
  confiabilidad: string
  fecha_analisis: string
  recomendaciones: string[]
  explicacion_tecnica: string | null
}

export interface AnalysisPreview {
  geojson: any
  crs_aplicado: string
  bounds: number[]
}

export interface DashboardStats {
  total_analyses: number
  successful_analyses: number
  success_rate: number
  average_confidence: number
  total_files: number
  recent_analyses: Array<{
    id: number
    archivo_nombre: string
    crs_detectado: string
    confiabilidad: string
    fecha_analisis: string | null
    escala_estimada: number | null
  }>
  quality_stats: {
    alta_confianza: { count: number; percentage: number }
    media_confianza: { count: number; percentage: number }
    baja_confianza: { count: number; percentage: number }
  }
}

export const uploadFile = async (file: File): Promise<FileUploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post<FileUploadResponse>('/files/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  return response.data
}

export const diagnoseFile = async (fileId: number): Promise<AnalysisResponse> => {
  const response = await api.post<AnalysisResponse>(`/analysis/${fileId}/diagnose`)
  return response.data
}

export const getAnalysis = async (analysisId: number): Promise<AnalysisResponse> => {
  const response = await api.get<AnalysisResponse>(`/analysis/${analysisId}`)
  return response.data
}

export const getPreview = async (analysisId: number): Promise<AnalysisPreview> => {
  const response = await api.get<AnalysisPreview>(`/analysis/${analysisId}/preview`)
  return response.data
}

export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await api.get<DashboardStats>('/stats/dashboard')
  return response.data
}

export default api
