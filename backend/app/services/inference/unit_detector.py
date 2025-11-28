import numpy as np
from typing import Optional, Dict, Any

class UnitDetector:
    """Detecta las unidades de medida de los datos espaciales"""
    
    # Rangos típicos por unidad (en metros)
    UNIT_RANGES = {
        'metros': (0.1, 1000000),  # 10cm a 1000km
        'centimetros': (0.001, 10000),  # 1mm a 10km
        'pies': (0.03, 300000),  # ~1cm a ~100km
        'pulgadas': (0.0025, 30000),  # ~2.5mm a ~30km
    }
    
    def __init__(self, bounds: tuple, crs: Optional[str] = None):
        self.bounds = bounds
        self.crs = crs
        
    def detect_units(self) -> Dict[str, Any]:
        """Detecta las unidades basándose en los valores de las coordenadas"""
        minx, miny, maxx, maxy = self.bounds
        
        # Calcular el rango de valores
        x_range = abs(maxx - minx)
        y_range = abs(maxy - miny)
        avg_range = (x_range + y_range) / 2
        
        # Si el CRS es geográfico, las unidades son grados
        if self.crs and ('4326' in str(self.crs) or '4686' in str(self.crs)):
            return {
                'unidades': 'grados',
                'confidence': 0.9,
                'explicacion': 'CRS geográfico detectado, unidades en grados'
            }
        
        # Si el CRS es proyectado, analizar los valores
        if self.crs and ('3116' in str(self.crs) or '3115' in str(self.crs)):
            # MAGNA-SIRGAS proyectado típicamente en metros
            if 100 < avg_range < 1000000:  # 100m a 1000km
                return {
                    'unidades': 'metros',
                    'confidence': 0.85,
                    'explicacion': f'Rango de valores ({avg_range:.2f}) sugiere unidades en metros'
                }
        
        # Análisis heurístico basado en rangos
        if 0.1 <= avg_range <= 1000000:
            return {
                'unidades': 'metros',
                'confidence': 0.7,
                'explicacion': f'Rango de valores ({avg_range:.2f}) sugiere unidades en metros'
            }
        elif 0.001 <= avg_range <= 10000:
            return {
                'unidades': 'centimetros',
                'confidence': 0.7,
                'explicacion': f'Rango de valores ({avg_range:.2f}) sugiere unidades en centímetros'
            }
        elif 0.03 <= avg_range <= 300000:
            return {
                'unidades': 'pies',
                'confidence': 0.6,
                'explicacion': f'Rango de valores ({avg_range:.2f}) sugiere unidades en pies'
            }
        else:
            return {
                'unidades': 'desconocidas',
                'confidence': 0.3,
                'explicacion': f'No se pudo determinar las unidades con confianza. Rango: {avg_range:.2f}'
            }
