"""
Endpoints para exportación de datos espaciales
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.data_file import DataFile
from app.models.spatial_analysis import SpatialAnalysis
from app.models.export import Export
from app.models.transformation import Transformation
from app.schemas.export import ExportRequest, ExportResponse
from app.services.spatial.file_loader import FileLoader
from app.services.export.export_service import ExportService
from pathlib import Path
import os

router = APIRouter()

@router.post("/export", response_model=ExportResponse)
async def export_data(
    request: ExportRequest,
    db: Session = Depends(get_db)
):
    """Exporta datos analizados a formato especificado"""
    
    # Obtener análisis
    analysis = db.query(SpatialAnalysis).filter(SpatialAnalysis.id == request.analysis_id).first()
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
        
        # Aplicar CRS detectado si existe
        if analysis.crs_detectado:
            try:
                gdf.set_crs(analysis.crs_detectado, allow_override=True)
            except Exception:
                pass
        
        # Obtener transformación si existe
        transformation = None
        if request.crs_target:
            # Buscar transformación existente o crear nueva
            transformation = db.query(Transformation).filter(
                Transformation.analisis_id == analysis.id,
                Transformation.crs_destino == request.crs_target
            ).first()
        
        # Crear servicio de exportación
        upload_dir = settings.get_upload_dir()
        export_dir = os.path.join(upload_dir, "exports")
        os.makedirs(export_dir, exist_ok=True)
        export_service = ExportService(output_dir=export_dir)
        
        # Crear metadatos
        metadata = export_service.create_metadata(analysis, file, transformation)
        
        # Generar nombre de archivo
        base_name = os.path.splitext(file.nombre_archivo)[0]
        filename = f"{base_name}_export_{analysis.id}"
        
        # Exportar
        export_result = export_service.export(
            gdf=gdf,
            format=request.formato,
            filename=filename,
            metadata=metadata,
            crs_target=request.crs_target
        )
        
        # Guardar registro de exportación
        export_record = Export(
            archivo_id=file.id,
            transformacion_id=transformation.id if transformation else None,
            formato_salida=export_result['formato_salida'],
            ruta_archivo=export_result['ruta_archivo'],
            metadatos_completos=export_result['metadatos_completos']
        )
        db.add(export_record)
        db.commit()
        db.refresh(export_record)
        
        return ExportResponse(
            id=export_record.id,
            archivo_id=export_record.archivo_id,
            transformacion_id=export_record.transformacion_id,
            formato_salida=export_record.formato_salida,
            ruta_archivo=export_record.ruta_archivo,
            metadatos_completos=export_record.metadatos_completos,
            fecha_exportacion=export_record.fecha_exportacion
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en exportación: {str(e)}")

@router.get("/export/{export_id}", response_model=ExportResponse)
async def get_export(
    export_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene información de una exportación"""
    export = db.query(Export).filter(Export.id == export_id).first()
    if not export:
        raise HTTPException(status_code=404, detail="Exportación no encontrada")
    
    return ExportResponse(
        id=export.id,
        archivo_id=export.archivo_id,
        transformacion_id=export.transformacion_id,
        formato_salida=export.formato_salida,
        ruta_archivo=export.ruta_archivo,
        metadatos_completos=export.metadatos_completos,
        fecha_exportacion=export.fecha_exportacion
    )

@router.get("/export/{export_id}/download")
async def download_export(
    export_id: int,
    db: Session = Depends(get_db)
):
    """Descarga archivo exportado"""
    from fastapi.responses import FileResponse
    
    export = db.query(Export).filter(Export.id == export_id).first()
    if not export:
        raise HTTPException(status_code=404, detail="Exportación no encontrada")
    
    file_path = Path(export.ruta_archivo)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo de exportación no encontrado")
    
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type='application/octet-stream'
    )

