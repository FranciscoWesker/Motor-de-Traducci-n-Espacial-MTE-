from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class AnalysisRequest(BaseModel):
    file_id: int


class AnalysisResponse(BaseModel):
    id: int
    archivo_id: int
    crs_detectado: Optional[str] = None
    crs_original: Optional[str] = None
    unidades_detectadas: Optional[str] = None
    origen_detectado: Optional[str] = None
    escala_estimada: Optional[float] = None
    error_planimetrico: Optional[float] = None
    error_altimetrico: Optional[float] = None
    confiabilidad: str
    fecha_analisis: datetime
    recomendaciones: List[str] = []
    explicacion_tecnica: Optional[str] = None
    
    class Config:
        from_attributes = True

class AnalysisPreview(BaseModel):
    geojson: Dict[str, Any]
    crs_aplicado: str
    bounds: List[float]
