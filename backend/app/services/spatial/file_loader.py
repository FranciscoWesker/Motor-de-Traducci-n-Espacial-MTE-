import os
import geopandas as gpd
import pandas as pd
from typing import Optional, Dict, Any
from pathlib import Path
from app.services.spatial.format_detector import FormatDetector

class FileLoader:
    """Carga archivos espaciales en diferentes formatos"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.format = FormatDetector.detect(file_path)
        
    def load(self) -> Optional[gpd.GeoDataFrame]:
        """Carga el archivo según su formato"""
        if not self.format:
            raise ValueError(f"Formato no soportado: {self.file_path}")
        
        if self.format == 'SHP':
            return self._load_shp()
        elif self.format == 'GeoJSON':
            return self._load_geojson()
        elif self.format == 'CSV':
            return self._load_csv()
        else:
            raise ValueError(f"Formato {self.format} no implementado aún")
    
    def _load_shp(self) -> gpd.GeoDataFrame:
        """Carga archivo Shapefile"""
        return gpd.read_file(self.file_path)
    
    def _load_geojson(self) -> gpd.GeoDataFrame:
        """Carga archivo GeoJSON"""
        return gpd.read_file(self.file_path)
    
    def _load_csv(self) -> Optional[gpd.GeoDataFrame]:
        """Carga CSV con coordenadas y crea GeoDataFrame"""
        df = pd.read_csv(self.file_path)
        
        # Buscar columnas de coordenadas comunes
        coord_cols = self._find_coordinate_columns(df)
        if not coord_cols:
            raise ValueError("No se encontraron columnas de coordenadas en el CSV")
        
        lon_col, lat_col = coord_cols
        geometry = gpd.points_from_xy(df[lon_col], df[lat_col])
        gdf = gpd.GeoDataFrame(df, geometry=geometry)
        
        return gdf
    
    def _find_coordinate_columns(self, df: pd.DataFrame) -> Optional[tuple]:
        """Encuentra columnas de coordenadas en el DataFrame"""
        possible_lon = ['lon', 'long', 'longitude', 'x', 'lng', 'longitud']
        possible_lat = ['lat', 'latitude', 'y', 'latitud']
        
        lon_col = None
        lat_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in possible_lon and lon_col is None:
                lon_col = col
            if col_lower in possible_lat and lat_col is None:
                lat_col = col
        
        if lon_col and lat_col:
            return (lon_col, lat_col)
        return None


