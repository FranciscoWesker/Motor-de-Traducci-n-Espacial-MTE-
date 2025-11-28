"""
Modelo de Transformación (Post-MVP)
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Transformation(Base):
    __tablename__ = "transformations"

    id = Column(Integer, primary_key=True, index=True)
    analisis_id = Column(Integer, ForeignKey("spatial_analyses.id"), nullable=False)
    
    crs_origen = Column(String(50), nullable=False)
    crs_destino = Column(String(50), nullable=False)
    parametros_transformacion = Column(Text, nullable=True)  # JSON string
    
    fecha_aplicacion = Column(DateTime(timezone=True), server_default=func.now())
    usuario_id = Column(Integer, nullable=True)

    # Relaciones
    spatial_analysis = relationship("SpatialAnalysis", back_populates="transformations")
    exports = relationship("Export", back_populates="transformation", cascade="all, delete-orphan")

