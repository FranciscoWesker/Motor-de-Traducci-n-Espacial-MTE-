from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class ValidationResult(Base):
    __tablename__ = "validation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    analisis_id = Column(Integer, ForeignKey("spatial_analyses.id"), nullable=False)
    tipo_validacion = Column(String(100), nullable=False)
    resultado = Column(String(50), nullable=False)
    mensajes = Column(Text)
    advertencias = Column(Text)
    idoneidad_catastro = Column(Boolean, default=False)
    idoneidad_topografia = Column(Boolean, default=False)
    idoneidad_analisis_territorial = Column(Boolean, default=False)
    idoneidad_modelado_ambiental = Column(Boolean, default=False)
    
    # Relationships
    analisis = relationship("SpatialAnalysis", back_populates="validaciones")
