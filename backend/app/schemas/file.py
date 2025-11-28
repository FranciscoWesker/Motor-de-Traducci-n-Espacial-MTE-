from pydantic import BaseModel
from datetime import datetime

class FileUpload(BaseModel):
    nombre: str
    formato: str
    tamaño: int

class FileResponse(BaseModel):
    id: int
    nombre_archivo: str
    formato: str
    tamaño: int
    fecha_carga: datetime
    
    class Config:
        from_attributes = True
