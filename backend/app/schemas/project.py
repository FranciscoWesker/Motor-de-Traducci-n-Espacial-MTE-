"""
Schemas para proyectos
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProjectCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    fecha_creacion: datetime
    estado: str

    class Config:
        from_attributes = True

