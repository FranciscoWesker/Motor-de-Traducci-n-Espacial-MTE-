"""
Extractor de features para modelos de Machine Learning
"""
import geopandas as gpd
import numpy as np
from typing import Dict, Any, List, Optional
from shapely.geometry import Point, LineString, Polygon


class FeatureExtractor:
    """Extrae features de datos espaciales para modelos ML"""
    
    def extract_features(self, gdf: gpd.GeoDataFrame, analysis_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extrae features para modelos ML"""
        features = {}
        
        # Features geométricas
        features.update(self._extract_geometric_features(gdf))
        
        # Features de coordenadas
        features.update(self._extract_coordinate_features(gdf))
        
        # Features de análisis (si están disponibles)
        if analysis_data:
            features.update(self._extract_analysis_features(analysis_data))
        
        return features
    
    def _extract_geometric_features(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Extrae features geométricas"""
        features = {}
        
        if len(gdf) == 0:
            return features
        
        # Número de features
        features['num_features'] = len(gdf)
        
        # Tipos de geometría
        geom_types = gdf.geometry.type.value_counts().to_dict()
        features['num_points'] = geom_types.get('Point', 0)
        features['num_linestrings'] = geom_types.get('LineString', 0)
        features['num_polygons'] = geom_types.get('Polygon', 0)
        features['num_multipoints'] = geom_types.get('MultiPoint', 0)
        features['num_multilinestrings'] = geom_types.get('MultiLineString', 0)
        features['num_multipolygons'] = geom_types.get('MultiPolygon', 0)
        
        # Estadísticas de área (si aplica)
        try:
            if gdf.crs and not gdf.crs.is_geographic:
                areas = gdf.geometry.area
                features['total_area'] = float(areas.sum())
                features['mean_area'] = float(areas.mean()) if len(areas) > 0 else 0.0
                features['std_area'] = float(areas.std()) if len(areas) > 0 else 0.0
            else:
                # Convertir a proyectado para calcular área
                gdf_proj = gdf.to_crs('EPSG:3116')
                areas = gdf_proj.geometry.area
                features['total_area'] = float(areas.sum())
                features['mean_area'] = float(areas.mean()) if len(areas) > 0 else 0.0
                features['std_area'] = float(areas.std()) if len(areas) > 0 else 0.0
        except Exception:
            features['total_area'] = 0.0
            features['mean_area'] = 0.0
            features['std_area'] = 0.0
        
        # Estadísticas de longitud (si aplica)
        try:
            lengths = []
            for geom in gdf.geometry:
                if isinstance(geom, (LineString, Polygon)):
                    if isinstance(geom, Polygon):
                        lengths.append(geom.exterior.length)
                    else:
                        lengths.append(geom.length)
            
            if lengths:
                features['mean_length'] = float(np.mean(lengths))
                features['std_length'] = float(np.std(lengths))
            else:
                features['mean_length'] = 0.0
                features['std_length'] = 0.0
        except Exception:
            features['mean_length'] = 0.0
            features['std_length'] = 0.0
        
        # Densidad de vértices
        total_vertices = 0
        for geom in gdf.geometry:
            if geom is not None:
                if isinstance(geom, Point):
                    total_vertices += 1
                elif isinstance(geom, LineString):
                    total_vertices += len(list(geom.coords))
                elif isinstance(geom, Polygon):
                    total_vertices += len(list(geom.exterior.coords))
        
        features['total_vertices'] = total_vertices
        features['vertices_per_feature'] = total_vertices / len(gdf) if len(gdf) > 0 else 0.0
        
        return features
    
    def _extract_coordinate_features(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Extrae features de coordenadas"""
        features = {}
        
        if len(gdf) == 0:
            return features
        
        bounds = gdf.total_bounds
        minx, miny, maxx, maxy = bounds
        
        features['min_x'] = float(minx)
        features['min_y'] = float(miny)
        features['max_x'] = float(maxx)
        features['max_y'] = float(maxy)
        features['width'] = float(maxx - minx)
        features['height'] = float(maxy - miny)
        features['center_x'] = float((minx + maxx) / 2)
        features['center_y'] = float((miny + maxy) / 2)
        
        # Extraer coordenadas para análisis estadístico
        coords = []
        for geom in gdf.geometry:
            if geom is not None:
                if isinstance(geom, Point):
                    coords.append([geom.x, geom.y])
                elif isinstance(geom, LineString):
                    coords.extend(list(geom.coords))
                elif isinstance(geom, Polygon):
                    coords.extend(list(geom.exterior.coords))
        
        if coords:
            coords_array = np.array(coords)
            features['mean_x'] = float(np.mean(coords_array[:, 0]))
            features['mean_y'] = float(np.mean(coords_array[:, 1]))
            features['std_x'] = float(np.std(coords_array[:, 0]))
            features['std_y'] = float(np.std(coords_array[:, 1]))
        else:
            features['mean_x'] = 0.0
            features['mean_y'] = 0.0
            features['std_x'] = 0.0
            features['std_y'] = 0.0
        
        return features
    
    def _extract_analysis_features(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae features del análisis"""
        features = {}
        
        # CRS detectado (codificado)
        crs = analysis_data.get('crs_detectado', '')
        features['has_crs'] = 1 if crs else 0
        features['crs_is_magna_sirgas'] = 1 if 'MAGNA-SIRGAS' in str(crs) or '4686' in str(crs) or '3116' in str(crs) or '3115' in str(crs) else 0
        features['crs_is_wgs84'] = 1 if '4326' in str(crs) else 0
        
        # Escala
        escala = analysis_data.get('escala_estimada')
        features['escala_estimada'] = float(escala) if escala else 0.0
        features['has_escala'] = 1 if escala else 0
        
        # Errores
        error_plan = analysis_data.get('error_planimetrico')
        features['error_planimetrico'] = float(error_plan) if error_plan is not None else 0.0
        features['has_error_planimetrico'] = 1 if error_plan is not None else 0
        
        error_alt = analysis_data.get('error_altimetrico')
        features['error_altimetrico'] = float(error_alt) if error_alt is not None else 0.0
        features['has_error_altimetrico'] = 1 if error_alt is not None else 0
        
        # Confianza
        confidence = analysis_data.get('crs_confidence', 0.0)
        features['crs_confidence'] = float(confidence)
        
        # Validación
        validation = analysis_data.get('validation', {})
        features['num_validation_errors'] = len(validation.get('errors', []))
        features['num_outliers'] = len(validation.get('outliers', []))
        features['is_valid'] = 1 if validation.get('is_valid', False) else 0
        
        return features
    
    def features_to_array(self, features: Dict[str, Any], feature_order: Optional[List[str]] = None) -> np.ndarray:
        """Convierte features a array numpy para modelos ML"""
        if feature_order is None:
            feature_order = sorted(features.keys())
        
        return np.array([features.get(key, 0.0) for key in feature_order])

