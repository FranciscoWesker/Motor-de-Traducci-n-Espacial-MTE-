"""
Schemas para transformación
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class TransformationRequest(BaseModel):
    analysis_id: int
    crs_destino: str
    metodo: Optional[str] = None  # Opcional, se determina automáticamente


class TransformationResponse(BaseModel):
    id: int
    analisis_id: int
    crs_origen: str
    crs_destino: str
    parametros_transformacion: Optional[str] = None
    fecha_aplicacion: datetime
    usuario_id: Optional[int] = None
    
    class Config:
        from_attributes = True

