"""
Schemas para exportación
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ExportRequest(BaseModel):
    analysis_id: int
    formato: str  # geojson, shp, geopackage, kml
    crs_target: Optional[str] = None  # CRS destino opcional


class ExportResponse(BaseModel):
    id: int
    archivo_id: int
    transformacion_id: Optional[int] = None
    formato_salida: str
    ruta_archivo: str
    metadatos_completos: Optional[str] = None
    fecha_exportacion: datetime
    
    class Config:
        from_attributes = True

