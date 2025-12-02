from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    # Por defecto usa localhost para desarrollo local
    # En Docker, debe sobrescribirse con DATABASE_URL=postgresql://postgres:postgres@postgres:5432/mte_db
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@localhost:5432/mte_db"
    )
    
    # File storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    def get_upload_dir(self) -> str:
        """Obtiene la ruta absoluta del directorio de uploads"""
        upload_dir = os.getenv("UPLOAD_DIR", self.UPLOAD_DIR)
        # Convertir a ruta absoluta
        if not os.path.isabs(upload_dir):
            # Si es relativa, convertirla a absoluta basada en el directorio de trabajo actual
            # En Docker, el WORKDIR es /app, así que ./uploads se convierte en /app/uploads
            upload_dir = os.path.abspath(upload_dir)
        # Asegurar que el directorio existe
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir
    
    # CORS - Se puede sobrescribir con variable de entorno CORS_ORIGINS (separados por comas)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    
    def get_cors_origins(self) -> List[str]:
        """Obtiene lista de orígenes CORS, con soporte para variable de entorno"""
        env_origins = os.getenv("CORS_ORIGINS", self.CORS_ORIGINS)
        if isinstance(env_origins, str):
            return [origin.strip() for origin in env_origins.split(",") if origin.strip()]
        return env_origins if isinstance(env_origins, list) else [self.CORS_ORIGINS]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
