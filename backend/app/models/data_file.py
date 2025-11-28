from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class DataFile(Base):
    __tablename__ = "data_files"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_archivo = Column(String(255), nullable=False)
    formato = Column(String(50), nullable=False)
    tamaño = Column(BigInteger)
    proyecto_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    fecha_carga = Column(DateTime(timezone=True), server_default=func.now())
    ruta_almacenamiento = Column(String(500), nullable=False)
    
    # Relationships
    proyecto = relationship("Project", backref="archivos")
    analisis = relationship("SpatialAnalysis", back_populates="archivo", cascade="all, delete-orphan")
