"""
Endpoints para transformación/reproyección de datos espaciales
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.data_file import DataFile
from app.models.spatial_analysis import SpatialAnalysis
from app.models.transformation import Transformation
from app.schemas.transformation import TransformationRequest, TransformationResponse
from app.services.spatial.file_loader import FileLoader
from app.services.transformation.reprojection_service import ReprojectionService
import json

router = APIRouter()

@router.post("/transformation/{analysis_id}/reproject", response_model=TransformationResponse)
async def reproject_analysis(
    analysis_id: int,
    request: TransformationRequest,
    db: Session = Depends(get_db)
):
    """Transforma datos analizados a CRS destino"""
    
    # Verificar que el analysis_id coincida
    if request.analysis_id != analysis_id:
        raise HTTPException(status_code=400, detail="analysis_id no coincide")
    
    # Obtener análisis
    analysis = db.query(SpatialAnalysis).filter(SpatialAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    
    # Obtener archivo
    file = db.query(DataFile).filter(DataFile.id == analysis.archivo_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    try:
        # Cargar archivo
        loader = FileLoader(file.ruta_almacenamiento)
        gdf = loader.load()
        
        # Determinar CRS origen
        crs_origen = analysis.crs_detectado or str(gdf.crs) if gdf.crs else None
        if not crs_origen:
            raise HTTPException(status_code=400, detail="No se puede transformar: CRS origen no disponible")
        
        # Aplicar CRS origen si no está establecido
        if not gdf.crs:
            try:
                gdf.set_crs(crs_origen, allow_override=True)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error al establecer CRS origen: {str(e)}")
        
        # Crear servicio de transformación
        reprojection_service = ReprojectionService()
        
        # Transformar
        transform_result = reprojection_service.transform(
            gdf=gdf,
            crs_target=request.crs_destino,
            crs_source=crs_origen
        )
        
        if not transform_result['success']:
            raise HTTPException(status_code=400, detail=f"Error en transformación: {transform_result.get('error', 'Unknown error')}")
        
        # Guardar transformación en BD
        transformation = Transformation(
            analisis_id=analysis_id,
            crs_origen=crs_origen,
            crs_destino=request.crs_destino,
            parametros_transformacion=json.dumps({
                'method': transform_result.get('method'),
                'statistics': transform_result.get('statistics', {})
            })
        )
        db.add(transformation)
        db.commit()
        db.refresh(transformation)
        
        return TransformationResponse(
            id=transformation.id,
            analisis_id=transformation.analisis_id,
            crs_origen=transformation.crs_origen,
            crs_destino=transformation.crs_destino,
            parametros_transformacion=transformation.parametros_transformacion,
            fecha_aplicacion=transformation.fecha_aplicacion,
            usuario_id=transformation.usuario_id
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en transformación: {str(e)}")

@router.get("/transformation/{transformation_id}", response_model=TransformationResponse)
async def get_transformation(
    transformation_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene información de una transformación"""
    transformation = db.query(Transformation).filter(Transformation.id == transformation_id).first()
    if not transformation:
        raise HTTPException(status_code=404, detail="Transformación no encontrada")
    
    return TransformationResponse(
        id=transformation.id,
        analisis_id=transformation.analisis_id,
        crs_origen=transformation.crs_origen,
        crs_destino=transformation.crs_destino,
        parametros_transformacion=transformation.parametros_transformacion,
        fecha_aplicacion=transformation.fecha_aplicacion,
        usuario_id=transformation.usuario_id
    )

@router.get("/transformation/{transformation_id}/preview")
async def get_transformation_preview(
    transformation_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene preview de datos transformados"""
    from app.schemas.analysis import AnalysisPreview
    import json
    
    transformation = db.query(Transformation).filter(Transformation.id == transformation_id).first()
    if not transformation:
        raise HTTPException(status_code=404, detail="Transformación no encontrada")
    
    analysis = db.query(SpatialAnalysis).filter(SpatialAnalysis.id == transformation.analisis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    
    file = db.query(DataFile).filter(DataFile.id == analysis.archivo_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    try:
        # Cargar archivo
        loader = FileLoader(file.ruta_almacenamiento)
        gdf = loader.load()
        
        # Aplicar CRS origen
        if transformation.crs_origen:
            try:
                gdf.set_crs(transformation.crs_origen, allow_override=True)
            except:
                pass
        
        # Transformar a CRS destino
        gdf_transformed = gdf.to_crs(transformation.crs_destino)
        
        # Convertir a GeoJSON
        geojson = json.loads(gdf_transformed.to_json())
        
        # Obtener bounds
        bounds = gdf_transformed.total_bounds.tolist()
        
        return AnalysisPreview(
            geojson=geojson,
            crs_aplicado=transformation.crs_destino,
            bounds=bounds
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando preview: {str(e)}")

