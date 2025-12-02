import os
import geopandas as gpd
import pandas as pd
from typing import Optional, Dict, Any
from pathlib import Path
from app.services.spatial.format_detector import FormatDetector
from app.services.spatial.raster_reader import RasterReader

class FileLoader:
    """Carga archivos espaciales en diferentes formatos"""
    
    def __init__(self, file_path: str):
        # Normalizar la ruta: convertir a absoluta si es relativa
        if not os.path.isabs(file_path):
            # Si es relativa, intentar resolverla desde diferentes ubicaciones
            # Primero intentar desde el directorio de trabajo actual
            abs_path = os.path.abspath(file_path)
            if os.path.exists(abs_path):
                self.file_path = abs_path
            else:
                # Si no existe, intentar desde /app/uploads (Docker)
                # Remover ./ si está presente
                clean_path = file_path.lstrip("./")
                docker_path = os.path.join("/app", clean_path)
                if os.path.exists(docker_path):
                    self.file_path = docker_path
                else:
                    # Si tampoco existe, intentar desde /app/uploads directamente
                    filename = os.path.basename(clean_path)
                    docker_uploads_path = os.path.join("/app", "uploads", filename)
                    if os.path.exists(docker_uploads_path):
                        self.file_path = docker_uploads_path
                    else:
                        # Usar la ruta absoluta calculada de todas formas
                        self.file_path = abs_path
        else:
            self.file_path = file_path
        
        # Verificar que el archivo existe
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"Archivo no encontrado: {self.file_path} (ruta original: {file_path}). "
                f"Verifica que el archivo existe en el servidor."
            )
        
        self.format = FormatDetector.detect(self.file_path)
        
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
        elif self.format in ['GeoTIFF', 'DEM']:
            return self._load_raster()
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
    
    def _load_raster(self) -> Optional[gpd.GeoDataFrame]:
        """Carga archivo raster (GeoTIFF/DEM) y convierte a vector"""
        raster_reader = RasterReader(self.file_path)
        
        # Intentar convertir a vector
        try:
            gdf = raster_reader.to_vector()
            if gdf is not None and len(gdf) > 0:
                return gdf
        except Exception:
            pass
        
        # Si no se puede convertir a vector, crear bounding box
        return raster_reader.get_bounds_gdf()


