"""
Matching de límites administrativos para mejorar detección CRS
"""
import geopandas as gpd
from typing import Dict, Any, Optional, List
import numpy as np


class BoundaryMatcher:
    """Matching espacial con límites administrativos conocidos"""
    
    # Bounding boxes aproximados de departamentos de Colombia (en WGS84)
    # Estos pueden ser reemplazados por datos reales de límites administrativos
    COLOMBIA_BOUNDARIES = {
        'antioquia': {
            'bounds': [-77.5, 5.5, -74.0, 8.5],
            'crs_typical': 'EPSG:3116'  # MAGNA-SIRGAS Bogotá (zona central)
        },
        'cundinamarca': {
            'bounds': [-75.0, 3.5, -73.0, 5.5],
            'crs_typical': 'EPSG:3116'  # MAGNA-SIRGAS Bogotá
        },
        'valle_del_cauca': {
            'bounds': [-77.5, 3.0, -75.5, 5.0],
            'crs_typical': 'EPSG:3116'
        },
        'atlantico': {
            'bounds': [-75.5, 10.0, -74.5, 11.5],
            'crs_typical': 'EPSG:3116'
        },
        'santander': {
            'bounds': [-74.5, 5.5, -72.5, 7.5],
            'crs_typical': 'EPSG:3116'
        }
    }
    
    # Bounding box general de Colombia
    COLOMBIA_BBOX = {
        'lat_min': 4.0,
        'lat_max': 12.0,
        'lon_min': -79.0,
        'lon_max': -67.0
    }
    
    def __init__(self):
        pass
    
    def match_boundaries(
        self,
        gdf: gpd.GeoDataFrame,
        confidence_boost: float = 0.1
    ) -> Dict[str, Any]:
        """Hace matching con límites administrativos conocidos"""
        try:
            # Convertir a WGS84 para comparación
            if gdf.crs is None:
                gdf_wgs84 = gdf.copy()
                gdf_wgs84.set_crs('EPSG:4326', allow_override=True)
            elif gdf.crs.is_geographic:
                gdf_wgs84 = gdf.copy()
            else:
                gdf_wgs84 = gdf.to_crs('EPSG:4326')
            
            bounds = gdf_wgs84.total_bounds
            minx, miny, maxx, maxy = bounds
            
            # Verificar si está dentro del bounding box de Colombia
            in_colombia = (
                self.COLOMBIA_BBOX['lon_min'] <= minx <= self.COLOMBIA_BBOX['lon_max'] and
                self.COLOMBIA_BBOX['lat_min'] <= miny <= self.COLOMBIA_BBOX['lat_max'] and
                self.COLOMBIA_BBOX['lon_min'] <= maxx <= self.COLOMBIA_BBOX['lon_max'] and
                self.COLOMBIA_BBOX['lat_min'] <= maxy <= self.COLOMBIA_BBOX['lat_max']
            )
            
            if not in_colombia:
                return {
                    'matched': False,
                    'confidence_boost': 0.0,
                    'region': None,
                    'suggested_crs': None,
                    'explicacion': 'Los datos no están dentro del bounding box de Colombia'
                }
            
            # Buscar matching con regiones específicas
            best_match = None
            best_overlap = 0.0
            
            for region_name, region_data in self.COLOMBIA_BOUNDARIES.items():
                region_bounds = region_data['bounds']
                
                # Calcular overlap
                overlap = self._calculate_overlap(
                    bounds,
                    region_bounds
                )
                
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_match = {
                        'region': region_name,
                        'overlap': overlap,
                        'suggested_crs': region_data['crs_typical']
                    }
            
            if best_match and best_match['overlap'] > 0.5:  # 50% de overlap mínimo
                return {
                    'matched': True,
                    'confidence_boost': confidence_boost,
                    'region': best_match['region'],
                    'suggested_crs': best_match['suggested_crs'],
                    'overlap': best_match['overlap'],
                    'explicacion': f'Datos coinciden con región {best_match["region"]} ({best_match["overlap"]:.1%} overlap)'
                }
            else:
                return {
                    'matched': True,
                    'confidence_boost': confidence_boost * 0.5,  # Boost menor si solo está en Colombia
                    'region': 'colombia_general',
                    'suggested_crs': 'EPSG:4686',  # MAGNA-SIRGAS geográfico
                    'overlap': 1.0,
                    'explicacion': 'Datos dentro de Colombia pero sin matching específico de región'
                }
        except Exception as e:
            return {
                'matched': False,
                'confidence_boost': 0.0,
                'region': None,
                'suggested_crs': None,
                'explicacion': f'Error en matching: {str(e)}'
            }
    
    def _calculate_overlap(
        self,
        bounds1: np.ndarray,
        bounds2: List[float]
    ) -> float:
        """Calcula el porcentaje de overlap entre dos bounding boxes"""
        minx1, miny1, maxx1, maxy1 = bounds1
        minx2, miny2, maxx2, maxy2 = bounds2
        
        # Calcular intersección
        inter_minx = max(minx1, minx2)
        inter_miny = max(miny1, miny2)
        inter_maxx = min(maxx1, maxx2)
        inter_maxy = min(maxy1, maxy2)
        
        if inter_minx >= inter_maxx or inter_miny >= inter_maxy:
            return 0.0
        
        # Área de intersección
        inter_area = (inter_maxx - inter_minx) * (inter_maxy - inter_miny)
        
        # Área de bounds1
        area1 = (maxx1 - minx1) * (maxy1 - miny1)
        
        if area1 == 0:
            return 0.0
        
        # Porcentaje de overlap (qué porcentaje de bounds1 está dentro de bounds2)
        overlap = inter_area / area1
        
        return float(overlap)

