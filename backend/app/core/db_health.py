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
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            print("[DB] Conexion a base de datos exitosa")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[DB] Intento {attempt + 1}/{max_retries} fallo. Reintentando en {retry_delay}s...")
                print(f"[DB] Error: {str(e)}")
                time.sleep(retry_delay)
            else:
                print(f"[DB] ERROR: No se pudo conectar a la base de datos despues de {max_retries} intentos")
                print(f"[DB] Error final: {str(e)}")
                return False
    return False

