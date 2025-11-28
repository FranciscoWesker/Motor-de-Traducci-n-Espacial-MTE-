import os
from typing import Optional

class FormatDetector:
    """Detecta el formato de archivos espaciales"""
    
    FORMATS = {
        '.shp': 'SHP',
        '.geojson': 'GeoJSON',
        '.json': 'GeoJSON',
        '.csv': 'CSV',
        '.dwg': 'DWG',
        '.dxf': 'DXF',
        '.tif': 'GeoTIFF',
        '.tiff': 'GeoTIFF',
        '.dem': 'DEM',
    }
    
    @classmethod
    def detect(cls, filename: str) -> Optional[str]:
        """Detecta el formato basado en la extensión del archivo"""
        ext = os.path.splitext(filename)[1].lower()
        return cls.FORMATS.get(ext)
    
    @classmethod
    def is_supported(cls, filename: str) -> bool:
        """Verifica si el formato está soportado"""
        return cls.detect(filename) is not None


