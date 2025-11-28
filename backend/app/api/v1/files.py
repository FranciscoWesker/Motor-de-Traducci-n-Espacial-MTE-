from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.data_file import DataFile
from app.schemas.file import FileResponse
from app.services.spatial.format_detector import FormatDetector
import os
import shutil
from pathlib import Path

router = APIRouter()

# Crear directorio de uploads si no existe
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@router.post("/files/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Carga un archivo espacial"""
    
    # Validar formato
    if not FormatDetector.is_supported(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado: {file.filename}. Formatos soportados: SHP, GeoJSON, CSV"
        )
    
    # Validar tamaño
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo demasiado grande. Tamaño máximo: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Guardar archivo
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Si es Shapefile, verificar que existan los archivos auxiliares
    if FormatDetector.detect(file.filename) == 'SHP':
        base_name = Path(file_path).stem
        shp_dir = Path(file_path).parent
        required_files = [f"{base_name}.shp", f"{base_name}.shx", f"{base_name}.dbf"]
        if not all((shp_dir / f).exists() for f in required_files):
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail="Shapefile incompleto. Se requieren .shp, .shx y .dbf"
            )
    
    # Guardar en base de datos
    db_file = DataFile(
        nombre_archivo=file.filename,
        formato=FormatDetector.detect(file.filename),
        tamaño=file_size,
        ruta_almacenamiento=file_path
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return FileResponse.from_orm(db_file)
