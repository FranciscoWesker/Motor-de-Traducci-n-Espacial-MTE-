"""
Motor de inferencia de CRS
"""
import geopandas as gpd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from pyproj import CRS
import pyproj


class CRSDetector:
    """Detecta el sistema de coordenadas de referencia (CRS)"""

    # Bounding boxes por país/región
    BOUNDING_BOXES = {
        "colombia": {
            "lat_min": 4.0,
            "lat_max": 12.0,
            "lon_min": -79.0,
            "lon_max": -67.0,
        }
    }

    # Sistemas de referencia conocidos para Colombia
    KNOWN_CRS = {
        "EPSG:4686": {  # MAGNA-SIRGAS (geográfico)
            "name": "MAGNA-SIRGAS",
            "type": "geographic",
            "bounds": BOUNDING_BOXES["colombia"],
        },
        "EPSG:3116": {  # MAGNA-SIRGAS / Colombia Bogota zone
            "name": "MAGNA-SIRGAS Bogotá",
            "type": "projected",
            "bounds": {"x_min": 800000, "x_max": 1200000, "y_min": 800000, "y_max": 1200000},
        },
        "EPSG:3115": {  # MAGNA-SIRGAS / Colombia West zone
            "name": "MAGNA-SIRGAS Origen Nacional",
            "type": "projected",
        },
    }

    def detect(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Detecta el CRS más probable"""
        # Si ya tiene CRS, validarlo
        if gdf.crs:
            return self._validate_existing_crs(gdf)

        # Obtener coordenadas
        coords = self._extract_coordinates(gdf)

        # Análisis de rangos
        range_analysis = self._analyze_coordinate_ranges(coords)

        # Matching con sistemas conocidos
        crs_candidates = self._match_known_crs(coords, range_analysis)

        # Inferencia estadística
        best_crs = self._statistical_inference(coords, crs_candidates)

        return {
            "crs_detectado": best_crs["code"],
            "confidence": best_crs["confidence"],
            "method": best_crs["method"],
            "candidates": crs_candidates,
            "range_analysis": range_analysis,
        }

    def _validate_existing_crs(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """Valida un CRS existente"""
        crs_code = str(gdf.crs)
        coords = self._extract_coordinates(gdf)

        # Verificar si las coordenadas están en rangos razonables
        range_analysis = self._analyze_coordinate_ranges(coords)

        confidence = "high" if range_analysis["in_reasonable_range"] else "low"

        return {
            "crs_detectado": crs_code,
            "crs_original": crs_code,
            "confidence": confidence,
            "method": "existing_crs",
            "validated": True,
        }

    def _extract_coordinates(self, gdf: gpd.GeoDataFrame) -> np.ndarray:
        """Extrae coordenadas de todas las geometrías"""
        coords_list = []
        for geom in gdf.geometry:
            if geom.geom_type == "Point":
                coords_list.append([geom.x, geom.y])
            elif geom.geom_type in ["LineString", "MultiLineString"]:
                coords_list.extend([[p[0], p[1]] for p in geom.coords])
            elif geom.geom_type in ["Polygon", "MultiPolygon"]:
                for ring in geom.exterior.coords if hasattr(geom, "exterior") else []:
                    coords_list.extend([[p[0], p[1]] for p in [ring]])
        return np.array(coords_list)

    def _analyze_coordinate_ranges(self, coords: np.ndarray) -> Dict[str, Any]:
        """Analiza los rangos de coordenadas"""
        if len(coords) == 0:
            return {"in_reasonable_range": False}

        min_x, min_y = coords.min(axis=0)
        max_x, max_y = coords.max(axis=0)

        # Verificar si está en rango de Colombia (geográfico)
        colombia_box = self.BOUNDING_BOXES["colombia"]
        in_colombia_range = (
            colombia_box["lat_min"] <= min_y <= max_y <= colombia_box["lat_max"]
            and colombia_box["lon_min"] <= min_x <= max_x <= colombia_box["lon_max"]
        )

        # Determinar si parece geográfico o proyectado
        is_geographic = (
            -180 <= min_x <= max_x <= 180 and -90 <= min_y <= max_y <= 90
        )
        is_projected = (
            abs(min_x) > 1000 or abs(max_x) > 1000 or abs(min_y) > 1000 or abs(max_y) > 1000
        )

        return {
            "min_x": float(min_x),
            "min_y": float(min_y),
            "max_x": float(max_x),
            "max_y": float(max_y),
            "in_colombia_range": in_colombia_range,
            "is_geographic": is_geographic,
            "is_projected": is_projected,
            "in_reasonable_range": in_colombia_range or (is_geographic and not is_projected),
        }

    def _match_known_crs(
        self, coords: np.ndarray, range_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Hace matching con sistemas conocidos"""
        candidates = []

        for crs_code, crs_info in self.KNOWN_CRS.items():
            score = 0.0
            method = ""

            if range_analysis["is_geographic"] and crs_info["type"] == "geographic":
                score += 0.5
                method = "geographic_match"

            if range_analysis["in_colombia_range"]:
                score += 0.3
                method += "_colombia_range"

            if crs_code == "EPSG:4686" and range_analysis["in_colombia_range"]:
                score += 0.2
                method = "magna_sirgas_geographic"

            candidates.append({
                "code": crs_code,
                "name": crs_info["name"],
                "score": score,
                "method": method,
            })

        # Ordenar por score
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates

    def _statistical_inference(
        self, coords: np.ndarray, candidates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Inferencia estadística para determinar el mejor CRS"""
        if not candidates:
            return {
                "code": "EPSG:4686",  # Default a MAGNA-SIRGAS
                "confidence": "low",
                "method": "default",
            }

        best_candidate = candidates[0]

        # Calcular confianza basada en score
        if best_candidate["score"] >= 0.8:
            confidence = "high"
        elif best_candidate["score"] >= 0.5:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "code": best_candidate["code"],
            "confidence": confidence,
            "method": best_candidate["method"],
        }

