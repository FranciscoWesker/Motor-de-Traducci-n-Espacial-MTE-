import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
from shapely.validation import make_valid
import numpy as np
from typing import Dict, Any, List

class GeometricValidator:
    """Valida la calidad geométrica de los datos espaciales"""
    
    def __init__(self, gdf: gpd.GeoDataFrame):
        self.gdf = gdf
        
    def validate(self) -> Dict[str, Any]:
        """Ejecuta validación geométrica completa"""
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'outliers': [],
            'statistics': {}
        }
        
        # Validar geometrías individuales
        invalid_geoms = self._check_invalid_geometries()
        if invalid_geoms:
            results['is_valid'] = False
            results['errors'].extend(invalid_geoms)
        
        # Detectar outliers espaciales
        outliers = self._detect_outliers()
        if outliers:
            results['outliers'] = outliers
            results['warnings'].append(f'Se detectaron {len(outliers)} outliers espaciales')
        
        # Estadísticas básicas
        results['statistics'] = self._calculate_statistics()
        
        return results
    
    def _check_invalid_geometries(self) -> List[str]:
        """Verifica geometrías inválidas"""
        errors = []
        
        for idx, geom in enumerate(self.gdf.geometry):
            if geom is None:
                errors.append(f'Geometría nula en índice {idx}')
            elif not geom.is_valid:
                # Obtener razón de invalidez si está disponible
                try:
                    from shapely.validation import explain_validity
                    reason = explain_validity(geom)
                    errors.append(f'Geometría inválida en índice {idx}: {reason}')
                except:
                    errors.append(f'Geometría inválida en índice {idx}')
        
        return errors
    
    def _detect_outliers(self) -> List[Dict[str, Any]]:
        """Detecta outliers espaciales usando IQR"""
        if len(self.gdf) < 4:
            return []
        
        # Extraer coordenadas
        coords = []
        for geom in self.gdf.geometry:
            if geom is not None:
                if isinstance(geom, Point):
                    coords.append([geom.x, geom.y])
                else:
                    # Para otras geometrías, usar el centroide
                    centroid = geom.centroid
                    coords.append([centroid.x, centroid.y])
        
        if len(coords) < 4:
            return []
        
        coords = np.array(coords)
        
        # Calcular IQR para cada dimensión
        outliers = []
        for dim in [0, 1]:  # x, y
            q1 = np.percentile(coords[:, dim], 25)
            q3 = np.percentile(coords[:, dim], 75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outlier_indices = np.where(
                (coords[:, dim] < lower_bound) | (coords[:, dim] > upper_bound)
            )[0]
            
            for idx in outlier_indices:
                outliers.append({
                    'index': int(idx),
                    'dimension': 'x' if dim == 0 else 'y',
                    'value': float(coords[idx, dim]),
                    'bounds': [float(lower_bound), float(upper_bound)]
                })
        
        return outliers
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calcula estadísticas básicas"""
        bounds = self.gdf.total_bounds
        area = None
        
        # Calcular área si es posible
        if len(self.gdf) > 0:
            try:
                # Convertir a CRS proyectado para calcular área
                if self.gdf.crs and not self.gdf.crs.is_geographic:
                    area = self.gdf.geometry.area.sum()
                else:
                    # Si es geográfico, usar una proyección local
                    gdf_projected = self.gdf.to_crs('EPSG:3116')  # Bogotá
                    area = gdf_projected.geometry.area.sum()
            except:
                pass
        
        return {
            'num_features': len(self.gdf),
            'bounds': bounds.tolist(),
            'area_estimated': float(area) if area is not None else None
        }
