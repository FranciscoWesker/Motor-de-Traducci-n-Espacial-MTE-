"""
Estimador de escala basado en densidad de vértices, resolución espacial y área
"""
import geopandas as gpd
import numpy as np
from typing import Optional, Dict, Any
from shapely.geometry import Point, LineString, Polygon


class ScaleEstimator:
    """Estima la escala de captura de datos espaciales"""
    
    # Escalas estándar comunes en topografía y cartografía
    STANDARD_SCALES = [
        100, 200, 500, 1000, 2000, 5000, 10000, 25000, 50000, 100000, 250000, 500000
    ]
    
    # Resolución típica en metros por escala (error de representación)
    SCALE_RESOLUTION = {
        100: 0.05,    # 1:100 -> 5cm
        200: 0.10,    # 1:200 -> 10cm
        500: 0.25,    # 1:500 -> 25cm
        1000: 0.50,   # 1:1000 -> 50cm
        2000: 1.0,    # 1:2000 -> 1m
        5000: 2.5,    # 1:5000 -> 2.5m
        10000: 5.0,   # 1:10000 -> 5m
        25000: 12.5,  # 1:25000 -> 12.5m
        50000: 25.0,  # 1:50000 -> 25m
        100000: 50.0, # 1:100000 -> 50m
    }
    
    def __init__(self, gdf: gpd.GeoDataFrame):
        self.gdf = gdf
        self.bounds = gdf.total_bounds
        
    def estimate_scale(self) -> Dict[str, Any]:
        """Estima la escala más probable del dataset"""
        if len(self.gdf) == 0:
            return {
                'escala_estimada': None,
                'confidence': 0.0,
                'method': 'empty_dataset',
                'explicacion': 'Dataset vacío, no se puede estimar escala'
            }
        
        # Convertir a CRS proyectado si es necesario para cálculos
        gdf_projected = self._ensure_projected()
        
        # Método 1: Análisis de densidad de vértices
        vertex_density_scale = self._estimate_from_vertex_density(gdf_projected)
        
        # Método 2: Análisis de resolución espacial
        spatial_resolution_scale = self._estimate_from_spatial_resolution(gdf_projected)
        
        # Método 3: Análisis de área y extensión
        area_scale = self._estimate_from_area(gdf_projected)
        
        # Combinar resultados
        candidates = []
        if vertex_density_scale['escala_estimada']:
            candidates.append(vertex_density_scale)
        if spatial_resolution_scale['escala_estimada']:
            candidates.append(spatial_resolution_scale)
        if area_scale['escala_estimada']:
            candidates.append(area_scale)
        
        if not candidates:
            return {
                'escala_estimada': None,
                'confidence': 0.0,
                'method': 'no_estimation',
                'explicacion': 'No se pudo estimar la escala con los métodos disponibles'
            }
        
        # Seleccionar la escala más probable (promedio ponderado)
        best_scale = self._select_best_scale(candidates)
        
        return best_scale
    
    def _ensure_projected(self) -> gpd.GeoDataFrame:
        """Convierte a CRS proyectado si es geográfico"""
        if self.gdf.crs is None:
            # Asumir WGS84 si no hay CRS
            gdf_copy = self.gdf.copy()
            gdf_copy.set_crs('EPSG:4326', allow_override=True)
        else:
            gdf_copy = self.gdf.copy()
        
        # Si es geográfico, convertir a proyección local (Bogotá)
        if gdf_copy.crs and gdf_copy.crs.is_geographic:
            try:
                # Intentar convertir a MAGNA-SIRGAS Bogotá
                gdf_copy = gdf_copy.to_crs('EPSG:3116')
            except Exception:
                # Si falla, usar UTM
                try:
                    gdf_copy = gdf_copy.to_crs('EPSG:32618')  # UTM 18N
                except Exception:
                    pass
        
        return gdf_copy
    
    def _estimate_from_vertex_density(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Estima escala basándose en la densidad de vértices"""
        try:
            # Contar vértices totales
            total_vertices = 0
            total_length = 0.0
            
            for geom in gdf.geometry:
                if geom is None:
                    continue
                
                if isinstance(geom, Point):
                    total_vertices += 1
                elif isinstance(geom, LineString):
                    coords = list(geom.coords)
                    total_vertices += len(coords)
                    total_length += geom.length
                elif isinstance(geom, Polygon):
                    coords = list(geom.exterior.coords)
                    total_vertices += len(coords)
                    # Agregar interiores
                    for interior in geom.interiors:
                        total_vertices += len(list(interior.coords))
                    total_length += geom.exterior.length
            
            if total_vertices == 0:
                return {'escala_estimada': None, 'confidence': 0.0}
            
            # Calcular densidad de vértices (vértices por metro)
            if total_length > 0:
                vertex_density = total_vertices / total_length
            else:
                # Si no hay longitud (solo puntos), usar área
                total_area = gdf.geometry.area.sum()
                if total_area > 0:
                    vertex_density = total_vertices / total_area
                else:
                    return {'escala_estimada': None, 'confidence': 0.0}
            
            # Densidades típicas por escala (vértices por metro)
            # Escalas grandes (1:100-1:500): alta densidad (>10 vértices/m)
            # Escalas medianas (1:1000-1:5000): densidad media (1-10 vértices/m)
            # Escalas pequeñas (1:10000+): baja densidad (<1 vértice/m)
            
            if vertex_density > 10:
                estimated_scale = 500  # Escala grande
                confidence = 0.7
            elif vertex_density > 1:
                estimated_scale = 2000  # Escala mediana
                confidence = 0.6
            elif vertex_density > 0.1:
                estimated_scale = 10000  # Escala pequeña
                confidence = 0.5
            else:
                estimated_scale = 50000  # Escala muy pequeña
                confidence = 0.4
            
            # Ajustar a escala estándar más cercana
            estimated_scale = self._round_to_standard_scale(estimated_scale)
            
            return {
                'escala_estimada': estimated_scale,
                'confidence': confidence,
                'method': 'vertex_density',
                'explicacion': f'Densidad de vértices: {vertex_density:.2f} vértices/m sugiere escala 1:{estimated_scale}'
            }
        except Exception as e:
            return {
                'escala_estimada': None,
                'confidence': 0.0,
                'method': 'vertex_density_error',
                'explicacion': f'Error en análisis de densidad: {str(e)}'
            }
    
    def _estimate_from_spatial_resolution(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Estima escala basándose en la resolución espacial (distancia mínima entre vértices)"""
        try:
            min_distance = float('inf')
            
            # Calcular distancia mínima entre vértices
            for geom in gdf.geometry:
                if geom is None:
                    continue
                
                if isinstance(geom, Point):
                    # Para puntos, calcular distancia mínima entre todos los puntos
                    coords = [(geom.x, geom.y)]
                elif isinstance(geom, LineString):
                    coords = list(geom.coords)
                elif isinstance(geom, Polygon):
                    coords = list(geom.exterior.coords)
                else:
                    continue
                
                # Calcular distancias entre vértices consecutivos
                for i in range(len(coords) - 1):
                    p1 = np.array(coords[i])
                    p2 = np.array(coords[i + 1])
                    dist = np.linalg.norm(p2 - p1)
                    if dist > 0 and dist < min_distance:
                        min_distance = dist
            
            if min_distance == float('inf') or min_distance == 0:
                return {'escala_estimada': None, 'confidence': 0.0}
            
            # Mapear resolución a escala
            # Resolución pequeña (<0.5m) -> escala grande (1:500-1:1000)
            # Resolución media (0.5-5m) -> escala mediana (1:2000-1:5000)
            # Resolución grande (>5m) -> escala pequeña (1:10000+)
            
            if min_distance < 0.5:
                estimated_scale = 500
                confidence = 0.8
            elif min_distance < 2.0:
                estimated_scale = 2000
                confidence = 0.7
            elif min_distance < 5.0:
                estimated_scale = 5000
                confidence = 0.6
            elif min_distance < 25.0:
                estimated_scale = 25000
                confidence = 0.5
            else:
                estimated_scale = 100000
                confidence = 0.4
            
            estimated_scale = self._round_to_standard_scale(estimated_scale)
            
            return {
                'escala_estimada': estimated_scale,
                'confidence': confidence,
                'method': 'spatial_resolution',
                'explicacion': f'Resolución espacial mínima: {min_distance:.2f}m sugiere escala 1:{estimated_scale}'
            }
        except Exception as e:
            return {
                'escala_estimada': None,
                'confidence': 0.0,
                'method': 'spatial_resolution_error',
                'explicacion': f'Error en análisis de resolución: {str(e)}'
            }
    
    def _estimate_from_area(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Estima escala basándose en el área y extensión del dataset"""
        try:
            bounds = gdf.total_bounds
            minx, miny, maxx, maxy = bounds
            
            # Calcular extensión en metros
            width = abs(maxx - minx)
            height = abs(maxy - miny)
            max_extent = max(width, height)
            
            # Calcular área total
            total_area = gdf.geometry.area.sum()
            
            if max_extent == 0:
                return {'escala_estimada': None, 'confidence': 0.0}
            
            # Escalas típicas por extensión:
            # < 1km -> escala grande (1:500-1:2000) - parcelas, obras
            # 1-10km -> escala mediana (1:5000-1:25000) - barrios, municipios
            # > 10km -> escala pequeña (1:50000+) - regiones, departamentos
            
            if max_extent < 1000:  # < 1km
                estimated_scale = 1000
                confidence = 0.7
            elif max_extent < 5000:  # 1-5km
                estimated_scale = 5000
                confidence = 0.6
            elif max_extent < 10000:  # 5-10km
                estimated_scale = 25000
                confidence = 0.5
            elif max_extent < 50000:  # 10-50km
                estimated_scale = 50000
                confidence = 0.5
            else:  # > 50km
                estimated_scale = 100000
                confidence = 0.4
            
            estimated_scale = self._round_to_standard_scale(estimated_scale)
            
            return {
                'escala_estimada': estimated_scale,
                'confidence': confidence,
                'method': 'area_extent',
                'explicacion': f'Extensión máxima: {max_extent:.0f}m sugiere escala 1:{estimated_scale}'
            }
        except Exception as e:
            return {
                'escala_estimada': None,
                'confidence': 0.0,
                'method': 'area_extent_error',
                'explicacion': f'Error en análisis de área: {str(e)}'
            }
    
    def _round_to_standard_scale(self, scale: float) -> int:
        """Redondea a la escala estándar más cercana"""
        return min(self.STANDARD_SCALES, key=lambda x: abs(x - scale))
    
    def _select_best_scale(self, candidates: list) -> Dict[str, Any]:
        """Selecciona la mejor escala de entre los candidatos"""
        if not candidates:
            return {
                'escala_estimada': None,
                'confidence': 0.0,
                'method': 'no_candidates',
                'explicacion': 'No hay candidatos válidos'
            }
        
        # Calcular promedio ponderado por confianza
        total_weight = sum(c.get('confidence', 0.0) for c in candidates)
        if total_weight == 0:
            # Si no hay confianza, usar el primer candidato
            best = candidates[0]
            return {
                'escala_estimada': best.get('escala_estimada'),
                'confidence': 0.3,
                'method': 'first_candidate',
                'explicacion': best.get('explicacion', 'Escala estimada')
            }
        
        # Agrupar por escala y calcular promedio ponderado
        scale_scores = {}
        for candidate in candidates:
            scale = candidate.get('escala_estimada')
            if scale is None:
                continue
            confidence = candidate.get('confidence', 0.0)
            if scale not in scale_scores:
                scale_scores[scale] = []
            scale_scores[scale].append(confidence)
        
        # Calcular score promedio por escala
        scale_avg_scores = {
            scale: np.mean(scores) for scale, scores in scale_scores.items()
        }
        
        # Seleccionar escala con mayor score
        best_scale = max(scale_avg_scores.items(), key=lambda x: x[1])
        
        # Combinar explicaciones
        methods = [c.get('method', 'unknown') for c in candidates if c.get('escala_estimada') == best_scale[0]]
        explanations = [c.get('explicacion', '') for c in candidates if c.get('escala_estimada') == best_scale[0]]
        
        return {
            'escala_estimada': best_scale[0],
            'confidence': best_scale[1],
            'method': '+'.join(set(methods)),
            'explicacion': ' | '.join(explanations)
        }

