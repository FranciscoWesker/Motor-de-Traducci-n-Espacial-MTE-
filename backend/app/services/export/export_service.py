"""
Servicio de exportación de datos espaciales a múltiples formatos
"""
import os
import json
import geopandas as gpd
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import zipfile
import tempfile


class ExportService:
    """Exporta datos espaciales a diferentes formatos con metadatos completos"""
    
    SUPPORTED_FORMATS = ['geojson', 'shp', 'geopackage', 'kml']
    
    def __init__(self, output_dir: str = "./exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(
        self,
        gdf: gpd.GeoDataFrame,
        format: str,
        filename: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        crs_target: Optional[str] = None
    ) -> Dict[str, Any]:
        """Exporta GeoDataFrame a formato especificado"""
        
        if format.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Formato no soportado: {format}. Formatos soportados: {self.SUPPORTED_FORMATS}")
        
        # Aplicar CRS objetivo si se especifica
        if crs_target:
            if gdf.crs is None:
                raise ValueError("No se puede transformar: GDF no tiene CRS definido")
            try:
                gdf = gdf.to_crs(crs_target)
            except Exception as e:
                raise ValueError(f"Error al transformar CRS: {str(e)}")
        
        # Generar nombre de archivo si no se proporciona
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}"
        
        # Exportar según formato
        if format.lower() == 'geojson':
            return self._export_geojson(gdf, filename, metadata)
        elif format.lower() == 'shp':
            return self._export_shapefile(gdf, filename, metadata)
        elif format.lower() == 'geopackage':
            return self._export_geopackage(gdf, filename, metadata)
        elif format.lower() == 'kml':
            return self._export_kml(gdf, filename, metadata)
        else:
            raise ValueError(f"Formato no implementado: {format}")
    
    def _export_geojson(
        self,
        gdf: gpd.GeoDataFrame,
        filename: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Exporta a GeoJSON"""
        filepath = self.output_dir / f"{filename}.geojson"
        
        # Guardar GeoJSON
        gdf.to_file(filepath, driver='GeoJSON')
        
        # Agregar metadatos al GeoJSON si se proporcionan
        if metadata:
            with open(filepath, 'r') as f:
                geojson_data = json.load(f)
            
            # Agregar metadatos como propiedad en el FeatureCollection
            if 'metadata' not in geojson_data:
                geojson_data['metadata'] = {}
            
            geojson_data['metadata'].update(metadata)
            geojson_data['metadata']['export_date'] = datetime.now().isoformat()
            geojson_data['metadata']['crs'] = str(gdf.crs) if gdf.crs else None
            
            with open(filepath, 'w') as f:
                json.dump(geojson_data, f, indent=2)
        
        return {
            'ruta_archivo': str(filepath),
            'formato_salida': 'geojson',
            'tamaño': filepath.stat().st_size,
            'metadatos_completos': json.dumps(metadata) if metadata else None
        }
    
    def _export_shapefile(
        self,
        gdf: gpd.GeoDataFrame,
        filename: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Exporta a Shapefile (comprimido en ZIP)"""
        # Shapefile requiere múltiples archivos, crear directorio temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            shp_path = temp_path / filename
            
            # Guardar shapefile
            gdf.to_file(shp_path, driver='ESRI Shapefile')
            
            # Crear ZIP con todos los archivos del shapefile
            zip_path = self.output_dir / f"{filename}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
                    file_path = temp_path / f"{filename}{ext}"
                    if file_path.exists():
                        zipf.write(file_path, file_path.name)
                
                # Agregar archivo de metadatos si existe
                if metadata:
                    metadata_path = temp_path / f"{filename}_metadata.json"
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    zipf.write(metadata_path, metadata_path.name)
        
        return {
            'ruta_archivo': str(zip_path),
            'formato_salida': 'shp',
            'tamaño': zip_path.stat().st_size,
            'metadatos_completos': json.dumps(metadata) if metadata else None
        }
    
    def _export_geopackage(
        self,
        gdf: gpd.GeoDataFrame,
        filename: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Exporta a GeoPackage"""
        filepath = self.output_dir / f"{filename}.gpkg"
        
        # Guardar GeoPackage
        gdf.to_file(filepath, driver='GPKG', layer=filename)
        
        # GeoPackage soporta metadatos en la base de datos
        # Por ahora, guardamos metadatos en archivo JSON separado
        if metadata:
            metadata_path = self.output_dir / f"{filename}_metadata.json"
            metadata['export_date'] = datetime.now().isoformat()
            metadata['crs'] = str(gdf.crs) if gdf.crs else None
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        return {
            'ruta_archivo': str(filepath),
            'formato_salida': 'geopackage',
            'tamaño': filepath.stat().st_size,
            'metadatos_completos': json.dumps(metadata) if metadata else None
        }
    
    def _export_kml(
        self,
        gdf: gpd.GeoDataFrame,
        filename: str,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Exporta a KML"""
        filepath = self.output_dir / f"{filename}.kml"
        
        # Convertir a WGS84 si no está ya en ese CRS (KML requiere WGS84)
        if gdf.crs and not gdf.crs.to_string().startswith('EPSG:4326'):
            gdf_kml = gdf.to_crs('EPSG:4326')
        else:
            gdf_kml = gdf.copy()
            if not gdf_kml.crs:
                gdf_kml.set_crs('EPSG:4326', allow_override=True)
        
        # Guardar KML
        gdf_kml.to_file(filepath, driver='KML')
        
        # Agregar metadatos en comentario XML si es posible
        # Por ahora, guardamos en archivo JSON separado
        if metadata:
            metadata_path = self.output_dir / f"{filename}_metadata.json"
            metadata['export_date'] = datetime.now().isoformat()
            metadata['crs'] = 'EPSG:4326'  # KML siempre usa WGS84
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        return {
            'ruta_archivo': str(filepath),
            'formato_salida': 'kml',
            'tamaño': filepath.stat().st_size,
            'metadatos_completos': json.dumps(metadata) if metadata else None
        }
    
    def create_metadata(
        self,
        analysis: Any,
        file: Any,
        transformation: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Crea metadatos completos para exportación"""
        metadata = {
            'archivo_original': {
                'nombre': file.nombre_archivo,
                'formato': file.formato,
                'fecha_carga': file.fecha_carga.isoformat() if file.fecha_carga else None
            },
            'analisis': {
                'id': analysis.id,
                'crs_detectado': analysis.crs_detectado,
                'crs_original': analysis.crs_original,
                'unidades_detectadas': analysis.unidades_detectadas,
                'origen_detectado': analysis.origen_detectado,
                'escala_estimada': analysis.escala_estimada,
                'error_planimetrico': analysis.error_planimetrico,
                'error_altimetrico': analysis.error_altimetrico,
                'confiabilidad': analysis.confiabilidad.value if hasattr(analysis.confiabilidad, 'value') else str(analysis.confiabilidad),
                'fecha_analisis': analysis.fecha_analisis.isoformat() if analysis.fecha_analisis else None
            }
        }
        
        if transformation:
            metadata['transformacion'] = {
                'id': transformation.id,
                'crs_origen': transformation.crs_origen,
                'crs_destino': transformation.crs_destino,
                'fecha_aplicacion': transformation.fecha_aplicacion.isoformat() if transformation.fecha_aplicacion else None
            }
        
        metadata['sistema'] = {
            'nombre': 'Motor de Traducción Espacial (MTE)',
            'version': '1.0.0',
            'fecha_exportacion': datetime.now().isoformat()
        }
        
        return metadata

