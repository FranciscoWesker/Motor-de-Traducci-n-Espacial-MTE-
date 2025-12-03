from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ConfiabilidadEnum(str, enum.Enum):
    VERDE = "verde"
    AMARILLO = "amarillo"
    ROJO = "rojo"


class SpatialAnalysis(Base):
    __tablename__ = "spatial_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    archivo_id = Column(Integer, ForeignKey("data_files.id"), nullable=False)
    # CRS principal detectado (ej. "EPSG:3116" o "EPSG:4326")
    crs_detectado = Column(String(100))
    # Representación original del CRS tal como venía en el archivo (WKT/PROJ/etc.)
    crs_original = Column(String(255))
    # Información robusta de CRS para auditoría y reproyección futura
    crs_epsg = Column(Integer, nullable=True)
    crs_wkt = Column(String(2048), nullable=True)
    crs_authority = Column(String(32), nullable=True)
    crs_confidence = Column(Float, nullable=True)
    
    unidades_detectadas = Column(String(50))
    origen_detectado = Column(String(100))
    escala_estimada = Column(Float)
    error_planimetrico = Column(Float, nullable=True)
    error_altimetrico = Column(Float, nullable=True)
    confiabilidad = Column(Enum(ConfiabilidadEnum), default=ConfiabilidadEnum.ROJO)
    fecha_analisis = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    archivo = relationship("DataFile", back_populates="analisis")
    validaciones = relationship("ValidationResult", back_populates="analisis", cascade="all, delete-orphan")
    transformations = relationship("Transformation", back_populates="spatial_analysis", cascade="all, delete-orphan")

{
  "cells": [],
  "metadata": {
    "language_info": {
      "name": "python"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 2
}