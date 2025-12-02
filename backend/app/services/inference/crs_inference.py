import geopandas as gpd
from typing import Optional, Dict, Any
import numpy as np
from app.services.inference.boundary_matcher import BoundaryMatcher

class CRSInferenceEngine:
    """Motor de inferencia de CRS basado en reglas geodésicas y heurísticas"""
    
    # Bounding boxes por país/región
    BOUNDING_BOXES = {
        'colombia': {
            'lat_min': 4.0,
            'lat_max': 12.0,
            'lon_min': -79.0,
            'lon_max': -67.0
        }
    }
    
    # Sistemas de referencia conocidos para Colombia
    KNOWN_CRS = {
        'EPSG:4686': 'MAGNA-SIRGAS (Geográfico)',
        'EPSG:3116': 'MAGNA-SIRGAS / Bogotá',
        'EPSG:3115': 'MAGNA-SIRGAS / Origen Nacional',
        'EPSG:4326': 'WGS84',
    }
    
    def __init__(self, gdf: gpd.GeoDataFrame):
        self.gdf = gdf
        self.bounds = gdf.total_bounds
        
    def infer_crs(self) -> Dict[str, Any]:
        """Infiere el CRS más probable del GeoDataFrame"""
        results = {
            'crs_detectado': None,
            'confidence': 0.0,
            'method': None,
            'explicacion': None
        }
        
        # Si ya tiene CRS, verificar si es válido
        if self.gdf.crs is not None:
            results['crs_detectado'] = str(self.gdf.crs)
            results['confidence'] = 0.9
            results['method'] = 'metadata_existente'
            results['explicacion'] = f'CRS encontrado en metadatos: {self.gdf.crs}'
            return results
        
        # Convertir a WGS84 para análisis
        if self.gdf.crs is None:
            # Asumir que está en coordenadas geográficas sin CRS
            gdf_wgs84 = self.gdf.copy()
            gdf_wgs84.set_crs('EPSG:4326', allow_override=True)
        else:
            gdf_wgs84 = self.gdf.to_crs('EPSG:4326')
        
        # Análisis de rangos de coordenadas
        coord_analysis = self._analyze_coordinates(gdf_wgs84)
        
        # Matching con bounding boxes conocidos
        bbox_match = self._match_bounding_box(gdf_wgs84)
        
        # Matching con límites administrativos (mejora)
        boundary_matcher = BoundaryMatcher()
        boundary_match = boundary_matcher.match_boundaries(gdf_wgs84)
        
        # Inferencia estadística
        stats_inference = self._statistical_inference(gdf_wgs84)
        
        # Combinar resultados con boost de boundary matching
        base_confidence = 0.0
        suggested_crs = None
        method = None
        explicacion = None
        
        if bbox_match['match']:
            base_confidence = bbox_match['confidence']
            suggested_crs = bbox_match['crs']
            method = 'bounding_box_match'
            explicacion = bbox_match['explicacion']
        elif stats_inference['confidence'] > 0.7:
            base_confidence = stats_inference['confidence']
            suggested_crs = stats_inference['crs']
            method = 'statistical_inference'
            explicacion = stats_inference['explicacion']
        else:
            # CRS por defecto basado en análisis de coordenadas
            if coord_analysis['is_geographic']:
                base_confidence = 0.6
                suggested_crs = 'EPSG:4326'
                method = 'coordinate_analysis'
                explicacion = 'Coordenadas geográficas detectadas, usando WGS84 como referencia'
            else:
                base_confidence = 0.3
                suggested_crs = None
                method = 'insufficient_data'
                explicacion = 'No se pudo determinar el CRS con suficiente confianza'
        
        # Aplicar boost de boundary matching
        if boundary_match['matched']:
            base_confidence += boundary_match['confidence_boost']
            # Si boundary matching sugiere un CRS específico, usarlo
            if boundary_match['suggested_crs'] and base_confidence < 0.8:
                suggested_crs = boundary_match['suggested_crs']
                method = f"{method}+boundary_match"
                explicacion = f"{explicacion}. {boundary_match['explicacion']}"
        
        # Limitar confianza a 1.0
        base_confidence = min(1.0, base_confidence)
        
        results['crs_detectado'] = suggested_crs
        results['confidence'] = base_confidence
        results['method'] = method
        results['explicacion'] = explicacion
        
        return results
    
    def _analyze_coordinates(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Analiza las coordenadas para determinar si son geográficas o proyectadas"""
        bounds = gdf.total_bounds
        minx, miny, maxx, maxy = bounds
        
        # Si las coordenadas están en rangos típicos de lat/lon
        is_geographic = (
            -180 <= minx <= 180 and
            -180 <= maxx <= 180 and
            -90 <= miny <= 90 and
            -90 <= maxy <= 90
        )
        
        return {
            'is_geographic': is_geographic,
            'bounds': bounds
        }
    
    def _match_bounding_box(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Compara con bounding boxes conocidos"""
        bounds = gdf.total_bounds
        minx, miny, maxx, maxy = bounds
        
        colombia_bbox = self.BOUNDING_BOXES['colombia']
        
        # Verificar si los datos están dentro del bounding box de Colombia
        match = (
            colombia_bbox['lon_min'] <= minx <= colombia_bbox['lon_max'] and
            colombia_bbox['lon_min'] <= maxx <= colombia_bbox['lon_max'] and
            colombia_bbox['lat_min'] <= miny <= colombia_bbox['lat_max'] and
            colombia_bbox['lat_min'] <= maxy <= colombia_bbox['lat_max']
        )
        
        if match:
            # Si está en Colombia, probablemente es MAGNA-SIRGAS
            return {
                'match': True,
                'crs': 'EPSG:4686',
                'confidence': 0.8,
                'explicacion': 'Los datos están dentro del bounding box de Colombia. Se sugiere MAGNA-SIRGAS (EPSG:4686)'
            }
        
        return {
            'match': False,
            'crs': None,
            'confidence': 0.0,
            'explicacion': None
        }
    
    def _statistical_inference(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Inferencia estadística de patrones espaciales"""
        # Extraer coordenadas
        coords = np.array([[geom.x, geom.y] for geom in gdf.geometry if geom is not None])
        
        if len(coords) == 0:
            return {
                'crs': None,
                'confidence': 0.0,
                'explicacion': 'No hay geometrías válidas para análisis'
            }
        
        # Análisis de distribución
        lon_mean = np.mean(coords[:, 0])
        lat_mean = np.mean(coords[:, 1])
        lon_std = np.std(coords[:, 0])
        lat_std = np.std(coords[:, 1])
        
        # Si la distribución es razonable para Colombia
        colombia_bbox = self.BOUNDING_BOXES['colombia']
        if (colombia_bbox['lon_min'] <= lon_mean <= colombia_bbox['lon_max'] and
            colombia_bbox['lat_min'] <= lat_mean <= colombia_bbox['lat_max']):
            return {
                'crs': 'EPSG:4686',
                'confidence': 0.75,
                'explicacion': f'Análisis estadístico sugiere MAGNA-SIRGAS. Centro: ({lon_mean:.4f}, {lat_mean:.4f})'
            }
        
        return {
            'crs': None,
            'confidence': 0.5,
            'explicacion': 'Análisis estadístico no concluyente'
        }


