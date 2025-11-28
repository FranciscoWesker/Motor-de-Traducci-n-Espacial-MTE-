from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/mte_db"
    
    # File storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
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
