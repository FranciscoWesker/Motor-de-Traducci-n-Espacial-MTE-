from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.data_file import DataFile
from app.models.spatial_analysis import SpatialAnalysis
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisPreview
from app.services.spatial.file_loader import FileLoader
from app.services.inference.crs_inference import CRSInferenceEngine
from app.services.inference.unit_detector import UnitDetector
from app.services.inference.origin_detector import OriginDetector
from app.services.validation.geometric_validator import GeometricValidator
from app.services.validation.quality_assessor import QualityAssessor
import json

router = APIRouter()

@router.post("/analysis/{file_id}/diagnose", response_model=AnalysisResponse)
async def diagnose_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    """Ejecuta análisis de detección CRS y diagnóstico básico"""
    
    # Obtener archivo
    file = db.query(DataFile).filter(DataFile.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    try:
        # Cargar archivo
        loader = FileLoader(file.ruta_almacenamiento)
        gdf = loader.load()
        
        # Detectar CRS
        crs_engine = CRSInferenceEngine(gdf)
        crs_results = crs_engine.infer_crs()
        
        # Detectar unidades
        unit_detector = UnitDetector(gdf.total_bounds, crs_results['crs_detectado'])
        unit_results = unit_detector.detect_units()
        
        # Detectar origen
        origin_detector = OriginDetector(gdf, crs_results['crs_detectado'])
        origin_results = origin_detector.detect_origin()
        
        # Validación geométrica
        validator = GeometricValidator(gdf)
        validation_results = validator.validate()
        
        # Evaluar calidad
        analysis_data = {
            'crs_detectado': crs_results['crs_detectado'],
            'crs_confidence': crs_results['confidence'],
            'unidades_detectadas': unit_results['unidades'],
            'origen_detectado': origin_results['origen'],
            'validation': validation_results
        }
        
        quality_assessor = QualityAssessor()
        quality_results = quality_assessor.assess(analysis_data)
        
        # Guardar análisis en BD
        analysis = SpatialAnalysis(
            archivo_id=file_id,
            crs_detectado=crs_results['crs_detectado'],
            crs_original=str(gdf.crs) if gdf.crs else None,
            unidades_detectadas=unit_results['unidades'],
            origen_detectado=origin_results['origen'],
            escala_estimada=None,  # Se puede calcular después
            confiabilidad=quality_results['confiabilidad']
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Preparar respuesta
        response = AnalysisResponse(
            id=analysis.id,
            archivo_id=analysis.archivo_id,
            crs_detectado=analysis.crs_detectado,
            crs_original=analysis.crs_original,
            unidades_detectadas=analysis.unidades_detectadas,
            origen_detectado=analysis.origen_detectado,
            escala_estimada=analysis.escala_estimada,
            error_planimetrico=analysis.error_planimetrico,
            error_altimetrico=analysis.error_altimetrico,
            confiabilidad=analysis.confiabilidad.value,
            fecha_analisis=analysis.fecha_analisis,
            recomendaciones=quality_results['recomendaciones'],
            explicacion_tecnica=quality_results['explicacion_tecnica']
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")

@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene resultados de análisis"""
    analysis = db.query(SpatialAnalysis).filter(SpatialAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    
    # Obtener recomendaciones (por ahora básicas)
    quality_assessor = QualityAssessor()
    analysis_data = {
        'crs_detectado': analysis.crs_detectado,
        'crs_confidence': 0.8 if analysis.crs_detectado else 0.3,
        'unidades_detectadas': analysis.unidades_detectadas,
        'origen_detectado': analysis.origen_detectado,
        'validation': {}
    }
    quality_results = quality_assessor.assess(analysis_data)
    
    return AnalysisResponse(
        id=analysis.id,
        archivo_id=analysis.archivo_id,
        crs_detectado=analysis.crs_detectado,
        crs_original=analysis.crs_original,
        unidades_detectadas=analysis.unidades_detectadas,
        origen_detectado=analysis.origen_detectado,
        escala_estimada=analysis.escala_estimada,
        error_planimetrico=analysis.error_planimetrico,
        error_altimetrico=analysis.error_altimetrico,
        confiabilidad=analysis.confiabilidad.value,
        fecha_analisis=analysis.fecha_analisis,
        recomendaciones=quality_results['recomendaciones'],
        explicacion_tecnica=quality_results['explicacion_tecnica']
    )

@router.get("/analysis/{analysis_id}/preview", response_model=AnalysisPreview)
async def get_preview(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Vista previa de datos para visualización"""
    analysis = db.query(SpatialAnalysis).filter(SpatialAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    
    file = db.query(DataFile).filter(DataFile.id == analysis.archivo_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    try:
        # Cargar archivo
        loader = FileLoader(file.ruta_almacenamiento)
        gdf = loader.load()
        
        # Aplicar CRS detectado si existe
        if analysis.crs_detectado:
            try:
                gdf.set_crs(analysis.crs_detectado, allow_override=True)
            except:
                pass
        
        # Convertir a GeoJSON
        geojson = json.loads(gdf.to_json())
        
        # Obtener bounds
        bounds = gdf.total_bounds.tolist()
        
        return AnalysisPreview(
            geojson=geojson,
            crs_aplicado=analysis.crs_detectado or str(gdf.crs) or "unknown",
            bounds=bounds
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando preview: {str(e)}")
