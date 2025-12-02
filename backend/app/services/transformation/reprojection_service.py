"""
Servicio de transformación/reproyección de datos espaciales
"""
import geopandas as gpd
from pyproj import CRS, Transformer
from typing import Dict, Any, Optional
import json


class ReprojectionService:
    """Servicio para transformar datos espaciales entre sistemas de coordenadas"""
    
    def __init__(self):
        pass
    
    def validate_transformation(
        self,
        crs_source: str,
        crs_target: str
    ) -> Dict[str, Any]:
        """Valida si la transformación es posible y segura"""
        try:
            # Validar CRS origen
            try:
                crs_src = CRS.from_string(crs_source)
            except Exception:
                crs_src = CRS(crs_source)
            
            # Validar CRS destino
            try:
                crs_tgt = CRS.from_string(crs_target)
            except Exception:
                crs_tgt = CRS(crs_target)
            
            # Verificar si son iguales
            if crs_src == crs_tgt:
                return {
                    'valid': True,
                    'warning': 'CRS origen y destino son iguales, no se requiere transformación',
                    'method': 'no_transformation_needed'
                }
            
            # Intentar crear transformer para validar
            try:
                transformer = Transformer.from_crs(crs_src, crs_tgt, always_xy=True)
                # Probar con un punto de prueba
                test_point = (0.0, 0.0)
                try:
                    transformed = transformer.transform(test_point[0], test_point[1])
                    if transformed[0] is None or transformed[1] is None:
                        return {
                            'valid': False,
                            'error': 'La transformación falló con punto de prueba',
                            'method': 'validation_failed'
                        }
                except Exception as e:
                    return {
                        'valid': False,
                        'error': f'Error al probar transformación: {str(e)}',
                        'method': 'test_failed'
                    }
            except Exception as e:
                return {
                    'valid': False,
                    'error': f'No se puede crear transformer: {str(e)}',
                    'method': 'transformer_creation_failed'
                }
            
            # Determinar método de transformación
            method = self._determine_transformation_method(crs_src, crs_tgt)
            
            return {
                'valid': True,
                'method': method,
                'crs_source': str(crs_src),
                'crs_target': str(crs_tgt),
                'warning': None
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error en validación: {str(e)}',
                'method': 'validation_error'
            }
    
    def transform(
        self,
        gdf: gpd.GeoDataFrame,
        crs_target: str,
        crs_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transforma GeoDataFrame a CRS destino"""
        try:
            # Si no se especifica CRS origen, usar el del GDF
            if crs_source is None:
                if gdf.crs is None:
                    raise ValueError("No se puede transformar: GDF no tiene CRS y no se especificó CRS origen")
                crs_source = str(gdf.crs)
            
            # Validar transformación
            validation = self.validate_transformation(crs_source, crs_target)
            if not validation['valid']:
                raise ValueError(f"Transformación no válida: {validation.get('error', 'Unknown error')}")
            
            # Aplicar transformación
            gdf_transformed = gdf.to_crs(crs_target)
            
            # Calcular estadísticas de transformación
            stats = self._calculate_transformation_stats(gdf, gdf_transformed)
            
            return {
                'success': True,
                'gdf_transformed': gdf_transformed,
                'crs_source': crs_source,
                'crs_target': crs_target,
                'method': validation['method'],
                'statistics': stats
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'gdf_transformed': None
            }
    
    def _determine_transformation_method(self, crs_source: CRS, crs_target: CRS) -> str:
        """Determina el método de transformación utilizado"""
        # Si ambos son geográficos o ambos son proyectados
        if crs_source.is_geographic == crs_target.is_geographic:
            if crs_source.is_geographic:
                return 'geographic_to_geographic'
            else:
                return 'projected_to_projected'
        
        # Si uno es geográfico y otro proyectado
        if crs_source.is_geographic and not crs_target.is_geographic:
            return 'geographic_to_projected'
        else:
            return 'projected_to_geographic'
    
    def _calculate_transformation_stats(
        self,
        gdf_original: gpd.GeoDataFrame,
        gdf_transformed: gpd.GeoDataFrame
    ) -> Dict[str, Any]:
        """Calcula estadísticas de la transformación"""
        try:
            # Comparar bounds
            bounds_orig = gdf_original.total_bounds
            bounds_trans = gdf_transformed.total_bounds
            
            # Calcular cambio en extensión
            extent_orig = max(
                abs(bounds_orig[2] - bounds_orig[0]),
                abs(bounds_orig[3] - bounds_orig[1])
            )
            extent_trans = max(
                abs(bounds_trans[2] - bounds_trans[0]),
                abs(bounds_trans[3] - bounds_trans[1])
            )
            
            return {
                'bounds_original': bounds_orig.tolist(),
                'bounds_transformed': bounds_trans.tolist(),
                'extent_original': float(extent_orig),
                'extent_transformed': float(extent_trans),
                'extent_change_percentage': float(((extent_trans - extent_orig) / extent_orig) * 100) if extent_orig > 0 else 0.0
            }
        except Exception as e:
            return {
                'error': f'Error calculando estadísticas: {str(e)}'
            }

