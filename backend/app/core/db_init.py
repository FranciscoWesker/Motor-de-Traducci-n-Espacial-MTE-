"""
Utilidades para inicializar la base de datos
"""
from sqlalchemy import text
from app.core.database import Base, engine
# Importar todos los modelos para que SQLAlchemy los registre en Base.metadata
from app.models import Project, DataFile, SpatialAnalysis, ValidationResult
from app.models.transformation import Transformation
from app.models.export import Export
import logging

logger = logging.getLogger(__name__)

def init_db():
    """
    Inicializa la base de datos creando todas las tablas si no existen
    También habilita la extensión PostGIS si está disponible
    """
    try:
        print("[DB] Inicializando base de datos...")
        
        # Intentar habilitar PostGIS si está disponible
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
                conn.commit()
            print("[DB] Extension PostGIS habilitada (o ya estaba habilitada)")
        except Exception as e:
            # Si PostGIS no está disponible, continuar sin ella
            print(f"[DB] ADVERTENCIA: No se pudo habilitar PostGIS: {str(e)}")
            print("[DB] Continuando sin PostGIS (algunas funcionalidades espaciales pueden no estar disponibles)")
        
        print("[DB] Creando tablas si no existen...")
        
        # Crear todas las tablas definidas en los modelos
        Base.metadata.create_all(bind=engine)
        
        print("[DB] Base de datos inicializada correctamente")
        return True
    except Exception as e:
        print(f"[DB] ERROR al inicializar base de datos: {str(e)}")
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        return False

