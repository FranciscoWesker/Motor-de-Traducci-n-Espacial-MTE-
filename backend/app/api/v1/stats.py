"""
Endpoints para estadísticas del dashboard
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.core.database import get_db
from app.models.spatial_analysis import SpatialAnalysis, ConfiabilidadEnum
from app.models.data_file import DataFile
from typing import Dict, Any

router = APIRouter()

@router.get("/stats/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Obtiene estadísticas para el dashboard
    """
    # Total de análisis
    total_analyses = db.query(func.count(SpatialAnalysis.id)).scalar() or 0
    
    # Análisis exitosos (con confiabilidad verde o amarilla)
    successful_analyses = db.query(func.count(SpatialAnalysis.id)).filter(
        SpatialAnalysis.confiabilidad.in_([ConfiabilidadEnum.VERDE, ConfiabilidadEnum.AMARILLO])
    ).scalar() or 0
    
    # Calcular confianza promedio
    confidence_map = {
        'verde': 90,
        'amarillo': 70,
        'rojo': 40
    }
    
    # Obtener distribución de confiabilidad
    verde_count = db.query(func.count(SpatialAnalysis.id)).filter(
        SpatialAnalysis.confiabilidad == ConfiabilidadEnum.VERDE
    ).scalar() or 0
    
    amarillo_count = db.query(func.count(SpatialAnalysis.id)).filter(
        SpatialAnalysis.confiabilidad == ConfiabilidadEnum.AMARILLO
    ).scalar() or 0
    
    rojo_count = db.query(func.count(SpatialAnalysis.id)).filter(
        SpatialAnalysis.confiabilidad == ConfiabilidadEnum.ROJO
    ).scalar() or 0
    
    # Calcular promedio ponderado de confianza
    if total_analyses > 0:
        average_confidence = (
            (verde_count * 90) + 
            (amarillo_count * 70) + 
            (rojo_count * 40)
        ) / total_analyses
    else:
        average_confidence = 0
    
    # Total de archivos procesados
    total_files = db.query(func.count(DataFile.id)).scalar() or 0
    
    # Análisis recientes (últimos 5)
    recent_analyses = db.query(SpatialAnalysis).order_by(
        SpatialAnalysis.fecha_analisis.desc()
    ).limit(5).all()
    
    recent_analyses_data = []
    for analysis in recent_analyses:
        file = db.query(DataFile).filter(DataFile.id == analysis.archivo_id).first()
        recent_analyses_data.append({
            'id': analysis.id,
            'archivo_nombre': file.nombre_archivo if file else 'Desconocido',
            'crs_detectado': analysis.crs_detectado or 'No detectado',
            'confiabilidad': analysis.confiabilidad.value if hasattr(analysis.confiabilidad, 'value') else str(analysis.confiabilidad),
            'fecha_analisis': analysis.fecha_analisis.isoformat() if analysis.fecha_analisis else None,
            'escala_estimada': analysis.escala_estimada
        })
    
    # Estadísticas de calidad
    quality_stats = {
        'alta_confianza': {
            'count': verde_count,
            'percentage': round((verde_count / total_analyses * 100) if total_analyses > 0 else 0, 1)
        },
        'media_confianza': {
            'count': amarillo_count,
            'percentage': round((amarillo_count / total_analyses * 100) if total_analyses > 0 else 0, 1)
        },
        'baja_confianza': {
            'count': rojo_count,
            'percentage': round((rojo_count / total_analyses * 100) if total_analyses > 0 else 0, 1)
        }
    }
    
    # Tasa de éxito
    success_rate = round((successful_analyses / total_analyses * 100) if total_analyses > 0 else 0, 1)
    
    return {
        'total_analyses': total_analyses,
        'successful_analyses': successful_analyses,
        'success_rate': success_rate,
        'average_confidence': round(average_confidence, 1),
        'total_files': total_files,
        'recent_analyses': recent_analyses_data,
        'quality_stats': quality_stats
    }

