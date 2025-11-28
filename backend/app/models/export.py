"""
Modelo de Exportación (Post-MVP)
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Export(Base):
    __tablename__ = "exports"

    id = Column(Integer, primary_key=True, index=True)
    archivo_id = Column(Integer, ForeignKey("data_files.id"), nullable=False)
    transformacion_id = Column(Integer, ForeignKey("transformations.id"), nullable=True)
    
    formato_salida = Column(String(50), nullable=False)  # geojson, shp, geopackage, etc.
    ruta_archivo = Column(String(500), nullable=False)
    metadatos_completos = Column(Text, nullable=True)  # JSON string
    
    fecha_exportacion = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    transformation = relationship("Transformation", back_populates="exports")

