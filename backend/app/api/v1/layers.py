"""
Endpoints para gestión de capas en GeoServer
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.spatial_analysis import SpatialAnalysis
from app.services.gis.geoserver_client import GeoServerClient
import os

router = APIRouter()

@router.post("/layers/{analysis_id}/publish")
async def publish_layer(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Publica una capa analizada en GeoServer"""
    
    analysis = db.query(SpatialAnalysis).filter(SpatialAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    
    try:
        # Configurar cliente GeoServer
        geoserver_url = os.getenv("GEOSERVER_URL", "http://geoserver:8080/geoserver")
        geoserver_user = os.getenv("GEOSERVER_USER", "admin")
        geoserver_pass = os.getenv("GEOSERVER_PASSWORD", "geoserver")
        
        client = GeoServerClient(
            base_url=geoserver_url,
            username=geoserver_user,
            password=geoserver_pass
        )
        
        # Crear workspace si no existe
        workspace = "mte"
        client.create_workspace(workspace)
        
        # Configurar conexión a PostGIS
        db_url = settings.DATABASE_URL
        # Parsear DATABASE_URL (formato: postgresql://user:pass@host:port/dbname)
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        
        db_config = {
            "host": parsed.hostname or "postgres",
            "port": parsed.port or 5432,
            "database": parsed.path.lstrip('/') or "mte_db",
            "user": parsed.username or "postgres",
            "password": parsed.password or "postgres",
            "schema": "public"
        }
        
        # Nombre de la capa
        layer_name = f"analysis_{analysis_id}"
        store_name = f"mte_postgis"
        table_name = "spatial_analyses"  # Asumiendo que hay una vista o tabla con geometrías
        
        # Publicar capa
        success = client.publish_postgis_layer(
            workspace=workspace,
            store_name=store_name,
            layer_name=layer_name,
            table_name=table_name,
            db_config=db_config
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Error al publicar capa en GeoServer")
        
        # Obtener URLs
        wms_url = client.get_wms_url(workspace, layer_name)
        wfs_url = client.get_wfs_url(workspace, layer_name)
        
        return {
            "success": True,
            "workspace": workspace,
            "layer_name": layer_name,
            "wms_url": wms_url,
            "wfs_url": wfs_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publicando capa: {str(e)}")

@router.get("/layers/{analysis_id}")
async def get_layer_info(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene información de una capa publicada"""
    
    analysis = db.query(SpatialAnalysis).filter(SpatialAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    
    try:
        geoserver_url = os.getenv("GEOSERVER_URL", "http://geoserver:8080/geoserver")
        geoserver_user = os.getenv("GEOSERVER_USER", "admin")
        geoserver_pass = os.getenv("GEOSERVER_PASSWORD", "geoserver")
        
        client = GeoServerClient(
            base_url=geoserver_url,
            username=geoserver_user,
            password=geoserver_pass
        )
        
        workspace = "mte"
        layer_name = f"analysis_{analysis_id}"
        
        layer_info = client.get_layer_info(workspace, layer_name)
        
        if not layer_info:
            raise HTTPException(status_code=404, detail="Capa no encontrada en GeoServer")
        
        return {
            "layer_info": layer_info,
            "wms_url": client.get_wms_url(workspace, layer_name),
            "wfs_url": client.get_wfs_url(workspace, layer_name)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo información de capa: {str(e)}")

