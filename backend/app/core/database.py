from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

# Obtener DATABASE_URL de variable de entorno o configuración
# Prioridad: 1. Variable de entorno DATABASE_URL, 2. settings.DATABASE_URL
# Railway y otros servicios cloud proporcionan DATABASE_URL automáticamente
env_db_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or os.getenv("PGDATABASE_URL")
database_url = env_db_url if env_db_url else settings.DATABASE_URL

# Debug: mostrar qué URL estamos usando (sin credenciales)
safe_url = database_url.split('@')[1] if '@' in database_url else database_url
print(f"[DB] DATABASE_URL desde env: {'SI' if env_db_url else 'NO (usando default)'}")
print(f"[DB] Host de BD configurado: {safe_url}")

# Si no hay DATABASE_URL en env, mostrar advertencia
if not env_db_url:
    print("[DB] ADVERTENCIA: DATABASE_URL no está configurada como variable de entorno")
    print("[DB] Usando valor por defecto (localhost). Esto puede fallar en producción.")
    # Verificar si estamos en Railway
    is_railway_check = bool(os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_SERVICE_NAME") or os.getenv("RAILWAY_PROJECT_ID"))
    if is_railway_check:
        print("[DB] ADVERTENCIA: Estás en Railway pero DATABASE_URL no está configurada.")
        print("[DB] SOLUCION: En Railway Dashboard:")
        print("[DB]   1. Ve a tu proyecto Railway")
        print("[DB]   2. Agrega un servicio PostgreSQL (New > Database > Add PostgreSQL)")
        print("[DB]   3. Conecta el servicio backend al servicio PostgreSQL (Settings > Variables)")
        print("[DB]   4. Railway configurará DATABASE_URL automáticamente cuando conectes los servicios")
        print("[DB]   5. Reinicia el servicio backend después de conectar")

# Convertir postgres:// a postgresql:// (compatibilidad con algunos proveedores)
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Detectar si estamos en Railway u otro servicio cloud
# Railway proporciona estas variables de entorno cuando el servicio está desplegado
is_railway = bool(os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_SERVICE_NAME") or os.getenv("RAILWAY_PROJECT_ID"))
is_heroku = bool(os.getenv("DYNO"))
is_cloud = is_railway or is_heroku

# Detectar si estamos en Docker y ajustar el host si es necesario
# SOLO si no hay DATABASE_URL de entorno Y NO estamos en un servicio cloud
# Si DATABASE_URL contiene localhost pero estamos en Docker local, cambiar a 'postgres'
is_docker = False
if not env_db_url and not is_cloud and ("localhost" in database_url or "127.0.0.1" in database_url):
    # Verificar si estamos en un contenedor Docker de varias formas
    docker_indicators = [
        "/proc/1/cgroup",  # Docker/containerd
        "/.dockerenv",     # Docker
    ]
    
    for indicator in docker_indicators:
        try:
            if os.path.exists(indicator):
                is_docker = True
                break
        except Exception:
            pass
    
    # También verificar variable de entorno común en Docker
    if os.getenv("DOCKER_CONTAINER") or os.getenv("container") == "docker":
        is_docker = True
    
    if is_docker:
        # Estamos en Docker local (docker-compose), cambiar localhost por postgres
        original_url = database_url
        database_url = database_url.replace("localhost", "postgres").replace("127.0.0.1", "postgres")
        if original_url != database_url:
            print(f"[DB] Detectado entorno Docker local, cambiando host a 'postgres'")
            print(f"[DB] Antes: {original_url.split('@')[1] if '@' in original_url else original_url}")
            print(f"[DB] Ahora: {database_url.split('@')[1] if '@' in database_url else database_url}")

# Log de conexión final (sin mostrar credenciales)
db_host = database_url.split('@')[1].split('/')[0] if '@' in database_url else 'configurada'
print(f"[DB] Conectando a base de datos: {db_host}")

engine = create_engine(
    database_url, 
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
