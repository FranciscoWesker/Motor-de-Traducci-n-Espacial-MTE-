"""
Calculador de errores planimétricos y altimétricos
"""
import geopandas as gpd
import numpy as np
from typing import Optional, Dict, Any, List
from shapely.geometry import Point, LineString, Polygon


class ErrorCalculator:
    """Calcula errores planimétricos y altimétricos de datos espaciales"""
    
    def __init__(self, gdf: gpd.GeoDataFrame):
        self.gdf = gdf
        
    def calculate_errors(self, crs_detectado: Optional[str] = None, escala_estimada: Optional[float] = None) -> Dict[str, Any]:
        """Calcula errores planimétricos y altimétricos"""
        results = {
            'error_planimetrico': None,
            'error_altimetrico': None,
            'method_planimetrico': None,
            'method_altimetrico': None,
            'explicacion': None
        }
        
        # Convertir a CRS proyectado si es necesario
        gdf_projected = self._ensure_projected()
        
        # Calcular error planimétrico
        planimetric_error = self._calculate_planimetric_error(gdf_projected, escala_estimada)
        results['error_planimetrico'] = planimetric_error.get('error')
        results['method_planimetrico'] = planimetric_error.get('method')
        
        # Calcular error altimétrico (solo si hay datos Z)
        altimetric_error = self._calculate_altimetric_error(gdf_projected)
        results['error_altimetrico'] = altimetric_error.get('error')
        results['method_altimetrico'] = altimetric_error.get('method')
        
        # Generar explicación
        explanations = []
        if results['error_planimetrico'] is not None:
            explanations.append(f"Error planimétrico: {results['error_planimetrico']:.2f}m ({planimetric_error.get('explicacion', '')})")
        if results['error_altimetrico'] is not None:
            explanations.append(f"Error altimétrico: {results['error_altimetrico']:.2f}m ({altimetric_error.get('explicacion', '')})")
        
        results['explicacion'] = ' | '.join(explanations) if explanations else 'No se pudieron calcular errores'
        
        return results
    
    def _ensure_projected(self) -> gpd.GeoDataFrame:
        """Convierte a CRS proyectado si es geográfico"""
        if self.gdf.crs is None:
            gdf_copy = self.gdf.copy()
            gdf_copy.set_crs('EPSG:4326', allow_override=True)
        else:
            gdf_copy = self.gdf.copy()
        
        if gdf_copy.crs and gdf_copy.crs.is_geographic:
            try:
                gdf_copy = gdf_copy.to_crs('EPSG:3116')  # MAGNA-SIRGAS Bogotá
            except:
                try:
                    gdf_copy = gdf_copy.to_crs('EPSG:32618')  # UTM 18N
                except Exception:
                    pass
        
        return gdf_copy
    
    def _calculate_planimetric_error(self, gdf: gpd.GeoDataFrame, escala_estimada: Optional[float] = None) -> Dict[str, Any]:
        """Calcula error planimétrico usando desviación estándar y análisis de precisión"""
        try:
            if len(gdf) == 0:
                return {'error': None, 'method': 'empty_dataset'}
            
            # Método 1: Desviación estándar de coordenadas (precisión interna)
            std_error = self._calculate_std_error(gdf)
            
            # Método 2: Error basado en escala (si está disponible)
            scale_error = None
            if escala_estimada:
                scale_error = self._calculate_scale_based_error(escala_estimada)
            
            # Método 3: Análisis de consistencia geométrica
            consistency_error = self._calculate_consistency_error(gdf)
            
            # Combinar métodos (usar el más conservador o promedio)
            errors = []
            if std_error is not None:
                errors.append(std_error)
            if scale_error is not None:
                errors.append(scale_error)
            if consistency_error is not None:
                errors.append(consistency_error)
            
            if not errors:
                return {'error': None, 'method': 'no_method_available'}
            
            # Usar el máximo (más conservador) o promedio
            final_error = max(errors)  # Más conservador
            
            method = 'std_deviation'
            if scale_error is not None:
                method = 'scale_based'
            if consistency_error is not None and consistency_error > final_error * 0.8:
                method = 'consistency_analysis'
            
            return {
                'error': final_error,
                'method': method,
                'explicacion': f'Error calculado mediante {method}'
            }
        except Exception as e:
            return {
                'error': None,
                'method': 'error',
                'explicacion': f'Error en cálculo: {str(e)}'
            }
    
    def _calculate_std_error(self, gdf: gpd.GeoDataFrame) -> Optional[float]:
        """Calcula error basado en desviación estándar de coordenadas"""
        try:
            coords = []
            for geom in gdf.geometry:
                if geom is None:
                    continue
                if isinstance(geom, Point):
                    coords.append([geom.x, geom.y])
                elif isinstance(geom, LineString):
                    coords.extend(list(geom.coords))
                elif isinstance(geom, Polygon):
                    coords.extend(list(geom.exterior.coords))
            
            if len(coords) < 2:
                return None
            
            coords_array = np.array(coords)
            
            # Calcular desviación estándar en X e Y
            std_x = np.std(coords_array[:, 0])
            std_y = np.std(coords_array[:, 1])
            
            # Error planimétrico como raíz cuadrada de la suma de varianzas
            # (aproximación del error circular)
            error = np.sqrt(std_x**2 + std_y**2)
            
            # Normalizar: si el error es muy grande comparado con la extensión, 
            # puede ser que los datos estén en diferentes zonas
            bounds = gdf.total_bounds
            extent = max(abs(bounds[2] - bounds[0]), abs(bounds[3] - bounds[1]))
            
            if error > extent * 0.1:  # Si el error es >10% de la extensión, es sospechoso
                # Usar un error más conservador basado en la extensión
                error = extent * 0.01  # 1% de la extensión
            
            return float(error)
        except Exception:
            return None
    
    def _calculate_scale_based_error(self, escala: float) -> Optional[float]:
        """Calcula error esperado basado en la escala"""
        # Error típico en metros = escala / 2000 (regla general)
        # Ejemplo: escala 1:1000 -> error ~0.5m
        error = escala / 2000.0
        return float(error)
    
    def _calculate_consistency_error(self, gdf: gpd.GeoDataFrame) -> Optional[float]:
        """Calcula error basado en consistencia geométrica (duplicados, solapamientos)"""
        try:
            if len(gdf) < 2:
                return None
            
            # Analizar distancias mínimas entre geometrías
            min_distances = []
            
            for i in range(min(100, len(gdf))):  # Limitar a 100 para rendimiento
                geom1 = gdf.iloc[i].geometry
                if geom1 is None:
                    continue
                
                for j in range(i + 1, min(i + 10, len(gdf))):  # Comparar con siguientes 10
                    geom2 = gdf.iloc[j].geometry
                    if geom2 is None:
                        continue
                    
                    try:
                        dist = geom1.distance(geom2)
                        if dist > 0:
                            min_distances.append(dist)
                    except Exception:
                        continue
            
            if not min_distances:
                return None
            
            # Si hay muchas distancias muy pequeñas, puede indicar duplicados o baja precisión
            min_dist = min(min_distances)
            median_dist = np.median(min_distances)
            
            # Si la distancia mínima es muy pequeña (< 0.1m), puede indicar error de precisión
            if min_dist < 0.1:
                return float(min_dist * 10)  # Estimación conservadora
            elif median_dist < 1.0:
                return float(median_dist * 0.5)
            else:
                return None
        except Exception:
            return None
    
    def _calculate_altimetric_error(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Calcula error altimétrico si hay datos Z"""
        try:
            # Extraer coordenadas Z
            z_values = []
            
            for geom in gdf.geometry:
                if geom is None:
                    continue
                
                if isinstance(geom, Point):
                    if hasattr(geom, 'z') and geom.z is not None:
                        z_values.append(geom.z)
                elif isinstance(geom, LineString):
                    coords = list(geom.coords)
                    for coord in coords:
                        if len(coord) > 2 and coord[2] is not None:
                            z_values.append(coord[2])
                elif isinstance(geom, Polygon):
                    coords = list(geom.exterior.coords)
                    for coord in coords:
                        if len(coord) > 2 and coord[2] is not None:
                            z_values.append(coord[2])
            
            if len(z_values) < 2:
                return {
                    'error': None,
                    'method': 'no_z_data',
                    'explicacion': 'No hay datos altimétricos (Z) disponibles'
                }
            
            z_array = np.array(z_values)
            
            # Calcular desviación estándar de Z
            std_z = np.std(z_array)
            
            # Error altimétrico como desviación estándar
            # Si hay mucha variación, puede ser terreno natural o error
            # Usar un umbral: si std_z es muy grande, puede ser variación natural del terreno
            range_z = np.max(z_array) - np.min(z_array)
            
            if range_z > 100:  # Si el rango es >100m, probablemente es variación natural
                # Error relativo al rango
                error = range_z * 0.01  # 1% del rango
            else:
                # Error como desviación estándar
                error = std_z * 0.5  # Mitad de la desviación estándar
            
            return {
                'error': float(error),
                'method': 'std_deviation_z',
                'explicacion': f'Error calculado a partir de {len(z_values)} puntos con coordenada Z'
            }
        except Exception as e:
            return {
                'error': None,
                'method': 'error',
                'explicacion': f'Error en cálculo altimétrico: {str(e)}'
            }

