import geopandas as gpd
from typing import Optional, Dict, Any
import numpy as np

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
        
        # Inferencia estadística
        stats_inference = self._statistical_inference(gdf_wgs84)
        
        # Combinar resultados
        if bbox_match['match']:
            results['crs_detectado'] = bbox_match['crs']
            results['confidence'] = bbox_match['confidence']
            results['method'] = 'bounding_box_match'
            results['explicacion'] = bbox_match['explicacion']
        elif stats_inference['confidence'] > 0.7:
            results['crs_detectado'] = stats_inference['crs']
            results['confidence'] = stats_inference['confidence']
            results['method'] = 'statistical_inference'
            results['explicacion'] = stats_inference['explicacion']
        else:
            # CRS por defecto basado en análisis de coordenadas
            if coord_analysis['is_geographic']:
                results['crs_detectado'] = 'EPSG:4326'
                results['confidence'] = 0.6
                results['method'] = 'coordinate_analysis'
                results['explicacion'] = 'Coordenadas geográficas detectadas, usando WGS84 como referencia'
            else:
                results['crs_detectado'] = None
                results['confidence'] = 0.3
                results['method'] = 'insufficient_data'
                results['explicacion'] = 'No se pudo determinar el CRS con suficiente confianza'
        
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


