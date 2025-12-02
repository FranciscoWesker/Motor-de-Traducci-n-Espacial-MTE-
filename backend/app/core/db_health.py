"""
Utilidades para verificar la salud de la conexión a la base de datos
"""
from sqlalchemy import text
from app.core.database import engine
import time

def check_db_connection(max_retries: int = 5, retry_delay: int = 2) -> bool:
    """
    Verifica la conexión a la base de datos con reintentos
    """
    import os
    
    # Verificar si DATABASE_URL está configurada
    env_db_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or os.getenv("PGDATABASE_URL")
    if not env_db_url:
        print("[DB] ADVERTENCIA: DATABASE_URL no está configurada")
        print("[DB] La aplicación puede no funcionar correctamente sin conexión a base de datos")
        # Verificar si estamos en Railway
        is_railway = bool(os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_SERVICE_NAME") or os.getenv("RAILWAY_PROJECT_ID"))
        if is_railway:
            print("[DB] SOLUCION: En Railway Dashboard, conecta el servicio PostgreSQL al servicio backend")
        return False
    
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            print("[DB] Conexion a base de datos exitosa")
            return True
        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                print(f"[DB] Intento {attempt + 1}/{max_retries} fallo. Reintentando en {retry_delay}s...")
                # Mostrar solo el mensaje de error principal, no el traceback completo
                if "password authentication failed" in error_msg:
                    print(f"[DB] Error: Autenticación fallida - verifica las credenciales en DATABASE_URL")
                elif "Connection refused" in error_msg or "could not connect" in error_msg.lower():
                    print(f"[DB] Error: No se puede conectar al servidor - verifica que la BD esté corriendo")
                else:
                    print(f"[DB] Error: {error_msg[:100]}...")
                time.sleep(retry_delay)
            else:
                print(f"[DB] ERROR: No se pudo conectar a la base de datos despues de {max_retries} intentos")
                if "password authentication failed" in error_msg:
                    print("[DB] SOLUCION: Verifica que DATABASE_URL tenga las credenciales correctas")
                    print("[DB] En Railway: Asegúrate de que el servicio PostgreSQL esté conectado al servicio backend")
                elif "Connection refused" in error_msg or "could not connect" in error_msg.lower():
                    print("[DB] SOLUCION: Verifica que el servicio de base de datos esté corriendo y accesible")
                else:
                    print(f"[DB] Error final: {error_msg[:200]}...")
                return False
    return False

