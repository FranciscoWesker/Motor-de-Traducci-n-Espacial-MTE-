"""
Cliente para interactuar con GeoServer
"""
import requests
from typing import Dict, Any, Optional
import base64
import json


class GeoServerClient:
    """Cliente para publicar y gestionar capas en GeoServer"""
    
    def __init__(
        self,
        base_url: str = "http://geoserver:8080/geoserver",
        username: str = "admin",
        password: str = "geoserver"
    ):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.auth_header = self._create_auth_header()
    
    def _create_auth_header(self) -> Dict[str, str]:
        """Crea header de autenticación básica"""
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}
    
    def create_workspace(self, workspace: str) -> bool:
        """Crea un workspace en GeoServer"""
        try:
            url = f"{self.base_url}/rest/workspaces"
            data = {"workspace": {"name": workspace}}
            response = requests.post(
                url,
                json=data,
                headers={**self.auth_header, "Content-Type": "application/json"}
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error creando workspace: {str(e)}")
            return False
    
    def publish_postgis_layer(
        self,
        workspace: str,
        store_name: str,
        layer_name: str,
        table_name: str,
        db_config: Dict[str, str]
    ) -> bool:
        """Publica una capa desde PostGIS"""
        try:
            # Crear datastore
            store_url = f"{self.base_url}/rest/workspaces/{workspace}/datastores"
            store_data = {
                "dataStore": {
                    "name": store_name,
                    "type": "PostGIS",
                    "connectionParameters": {
                        "entry": [
                            {"@key": "host", "$": db_config.get("host", "postgres")},
                            {"@key": "port", "$": str(db_config.get("port", 5432))},
                            {"@key": "database", "$": db_config.get("database", "mte_db")},
                            {"@key": "user", "$": db_config.get("user", "postgres")},
                            {"@key": "passwd", "$": db_config.get("password", "postgres")},
                            {"@key": "dbtype", "$": "postgis"},
                            {"@key": "schema", "$": db_config.get("schema", "public")}
                        ]
                    }
                }
            }
            
            response = requests.post(
                store_url,
                json=store_data,
                headers={**self.auth_header, "Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                print(f"Error creando datastore: {response.text}")
                return False
            
            # Publicar capa
            layer_url = f"{self.base_url}/rest/workspaces/{workspace}/datastores/{store_name}/featuretypes"
            layer_data = {
                "featureType": {
                    "name": layer_name,
                    "nativeName": table_name,
                    "srs": "EPSG:4326"
                }
            }
            
            response = requests.post(
                layer_url,
                json=layer_data,
                headers={**self.auth_header, "Content-Type": "application/json"}
            )
            
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error publicando capa: {str(e)}")
            return False
    
    def get_layer_info(self, workspace: str, layer_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de una capa"""
        try:
            url = f"{self.base_url}/rest/workspaces/{workspace}/layers/{layer_name}"
            response = requests.get(
                url,
                headers=self.auth_header
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error obteniendo información de capa: {str(e)}")
            return None
    
    def get_wms_url(self, workspace: str, layer_name: str) -> str:
        """Genera URL WMS para una capa"""
        return f"{self.base_url}/{workspace}/wms?service=WMS&version=1.1.0&request=GetMap&layers={workspace}:{layer_name}&styles=&bbox={{bbox}}&width={{width}}&height={{height}}&srs={{srs}}&format=image/png"
    
    def get_wfs_url(self, workspace: str, layer_name: str) -> str:
        """Genera URL WFS para una capa"""
        return f"{self.base_url}/{workspace}/wfs?service=WFS&version=1.1.0&request=GetFeature&typeName={workspace}:{layer_name}&outputFormat=application/json"

