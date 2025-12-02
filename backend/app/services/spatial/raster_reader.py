"""
Lector de archivos raster (GeoTIFF, DEM)
"""
import rasterio
from rasterio.features import shapes
import geopandas as gpd
import numpy as np
from typing import Optional, Dict, Any
from pathlib import Path


class RasterReader:
    """Lee archivos raster y extrae información espacial"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        
    def read_metadata(self) -> Dict[str, Any]:
        """Lee metadatos del archivo raster"""
        with rasterio.open(self.file_path) as src:
            return {
                'crs': str(src.crs) if src.crs else None,
                'bounds': list(src.bounds),
                'width': src.width,
                'height': src.height,
                'count': src.count,
                'dtype': str(src.dtypes[0]),
                'transform': list(src.transform),
                'resolution': (abs(src.transform[0]), abs(src.transform[4])),
                'nodata': src.nodata,
                'driver': src.driver
            }
    
    def to_vector(self, band: int = 1, mask_nodata: bool = True) -> Optional[gpd.GeoDataFrame]:
        """Convierte raster a vector (polígonos)"""
        try:
            with rasterio.open(self.file_path) as src:
                # Leer banda
                data = src.read(band)
                
                # Crear máscara si hay nodata
                if mask_nodata and src.nodata is not None:
                    mask = data != src.nodata
                else:
                    mask = None
                
                # Extraer formas (shapes)
                shapes_gen = shapes(data, mask=mask, transform=src.transform)
                
                # Convertir a GeoDataFrame
                features = []
                for geom, value in shapes_gen:
                    features.append({
                        'geometry': geom,
                        'value': value
                    })
                
                if not features:
                    return None
                
                gdf = gpd.GeoDataFrame(features, crs=src.crs)
                return gdf
        except Exception as e:
            raise ValueError(f"Error al convertir raster a vector: {str(e)}")
    
    def get_bounds_gdf(self) -> gpd.GeoDataFrame:
        """Crea un GeoDataFrame con el bounding box del raster"""
        metadata = self.read_metadata()
        bounds = metadata['bounds']
        
        from shapely.geometry import box
        bbox = box(bounds[0], bounds[1], bounds[2], bounds[3])
        
        gdf = gpd.GeoDataFrame([{'geometry': bbox}], crs=metadata['crs'])
        return gdf
    
    def estimate_scale_from_resolution(self) -> Optional[float]:
        """Estima escala basándose en la resolución espacial"""
        metadata = self.read_metadata()
        resolution = metadata['resolution']
        
        # Resolución promedio en metros
        avg_resolution = (resolution[0] + resolution[1]) / 2
        
        # Mapear resolución a escala
        # Resolución pequeña (<0.5m) -> escala grande (1:500-1:1000)
        # Resolución media (0.5-5m) -> escala mediana (1:2000-1:5000)
        # Resolución grande (>5m) -> escala pequeña (1:10000+)
        
        if avg_resolution < 0.5:
            return 500
        elif avg_resolution < 2.0:
            return 2000
        elif avg_resolution < 5.0:
            return 5000
        elif avg_resolution < 25.0:
            return 25000
        else:
            return 100000

