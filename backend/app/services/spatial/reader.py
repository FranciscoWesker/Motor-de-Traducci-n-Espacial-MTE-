"""
Servicio de lectura de archivos espaciales
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import geopandas as gpd
import pandas as pd
# from osgeo import gdal, ogr  # No se usa actualmente, comentado para evitar dependencias
import json


class SpatialFileReader:
    """Lee archivos espaciales en múltiples formatos"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.format = self._detect_format()

    def _detect_format(self) -> str:
        """Detecta el formato del archivo"""
        ext = self.file_path.suffix.lower()
        
        if ext == ".shp":
            return "shapefile"
        elif ext in [".geojson", ".json"]:
            return "geojson"
        elif ext == ".csv":
            return "csv"
        else:
            raise ValueError(f"Formato no soportado: {ext}")

    def read(self) -> gpd.GeoDataFrame:
        """Lee el archivo y retorna un GeoDataFrame"""
        if self.format == "shapefile":
            return gpd.read_file(self.file_path)
        elif self.format == "geojson":
            return gpd.read_file(self.file_path)
        elif self.format == "csv":
            return self._read_csv()
        else:
            raise ValueError(f"Formato no implementado: {self.format}")

    def _read_csv(self) -> gpd.GeoDataFrame:
        """Lee CSV y convierte a GeoDataFrame"""
        df = pd.read_csv(self.file_path)
        
        # Buscar columnas de coordenadas comunes
        coord_cols = self._find_coordinate_columns(df)
        
        if not coord_cols:
            raise ValueError("No se encontraron columnas de coordenadas en el CSV")
        
        # Crear geometría
        geometry = gpd.points_from_xy(
            df[coord_cols["lon"]], 
            df[coord_cols["lat"]]
        )
        
        return gpd.GeoDataFrame(df, geometry=geometry)

    def _find_coordinate_columns(self, df: pd.DataFrame) -> Optional[Dict[str, str]]:
        """Encuentra columnas de coordenadas en el DataFrame"""
        cols_lower = {col.lower(): col for col in df.columns}
        
        # Buscar patrones comunes
        patterns = {
            "lat": ["lat", "latitude", "y", "coord_y"],
            "lon": ["lon", "lng", "long", "longitude", "x", "coord_x"]
        }
        
        result = {}
        for key, patterns_list in patterns.items():
            for pattern in patterns_list:
                if pattern in cols_lower:
                    result[key] = cols_lower[pattern]
                    break
        
        return result if len(result) == 2 else None

    def get_metadata(self) -> Dict[str, Any]:
        """Obtiene metadatos del archivo"""
        gdf = self.read()
        
        metadata = {
            "format": self.format,
            "crs": str(gdf.crs) if gdf.crs else None,
            "bounds": {
                "minx": float(gdf.total_bounds[0]),
                "miny": float(gdf.total_bounds[1]),
                "maxx": float(gdf.total_bounds[2]),
                "maxy": float(gdf.total_bounds[3]),
            },
            "feature_count": len(gdf),
            "geometry_types": gdf.geometry.type.unique().tolist(),
        }
        
        return metadata

    def to_geojson(self) -> Dict[str, Any]:
        """Convierte el archivo a GeoJSON"""
        gdf = self.read()
        return json.loads(gdf.to_json())

