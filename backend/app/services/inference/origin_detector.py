import geopandas as gpd
from typing import Dict, Any, Optional

class OriginDetector:
    """Detecta si el origen es local o sistema oficial (MAGNA-SIRGAS)"""
    
    MAGNA_SIRGAS_CRS = ['EPSG:4686', 'EPSG:3116', 'EPSG:3115']
    
    def __init__(self, gdf: gpd.GeoDataFrame, crs_detectado: Optional[str] = None):
        self.gdf = gdf
        self.crs_detectado = crs_detectado
        
    def detect_origin(self) -> Dict[str, Any]:
        """Detecta si el origen es local o sistema oficial"""
        # Si el CRS detectado es MAGNA-SIRGAS, es oficial
        if self.crs_detectado and any(crs in str(self.crs_detectado) for crs in self.MAGNA_SIRGAS_CRS):
            return {
                'origen': 'MAGNA-SIRGAS',
                'tipo': 'oficial',
                'confidence': 0.9,
                'explicacion': f'CRS detectado ({self.crs_detectado}) corresponde a sistema oficial MAGNA-SIRGAS'
            }
        
        # Si no tiene CRS o es desconocido, probablemente es local
        if self.crs_detectado is None or '4326' in str(self.crs_detectado):
            # Verificar si hay desplazamientos sistemáticos
            displacement = self._check_systematic_displacement()
            
            if displacement['has_displacement']:
                return {
                    'origen': 'local',
                    'tipo': 'local',
                    'confidence': 0.7,
                    'explicacion': 'Se detectaron desplazamientos sistemáticos, probablemente sistema local'
                }
            else:
                return {
                    'origen': 'WGS84',
                    'tipo': 'internacional',
                    'confidence': 0.6,
                    'explicacion': 'Sistema de referencia internacional WGS84'
                }
        
        return {
            'origen': 'desconocido',
            'tipo': 'indeterminado',
            'confidence': 0.4,
            'explicacion': 'No se pudo determinar el origen del sistema de coordenadas'
        }
    
    def _check_systematic_displacement(self) -> Dict[str, Any]:
        """Verifica si hay desplazamientos sistemáticos que indiquen sistema local"""
        # Esta es una implementación básica
        # En producción, se compararía con puntos de control conocidos
        return {
            'has_displacement': False,
            'displacement_magnitude': 0.0
        }
