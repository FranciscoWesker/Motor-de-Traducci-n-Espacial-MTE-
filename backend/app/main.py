from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import files, analysis
import os

# Detectar si estamos en producción
is_production = os.getenv("ENVIRONMENT") == "production" or os.getenv("DATABASE_URL", "").startswith("postgres://")

app = FastAPI(
    title="Motor de Traducción Espacial (MTE)",
    description="Sistema para análisis, diagnóstico y estandarización de datos espaciales",
    version="1.0.0",
    docs_url="/docs" if not is_production else "/api/docs",
    redoc_url="/redoc" if not is_production else None
)

# CORS - Configurar según el entorno
cors_origins = settings.get_cors_origins()
if is_production and not cors_origins:
    # En producción, si no hay CORS configurado, permitir todos
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins != ["*"] else ["*"],
    allow_credentials=True if cors_origins != ["*"] else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(files.router, prefix="/api/v1", tags=["files"])
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])

@app.get("/")
async def root():
    return {"message": "Motor de Traducción Espacial API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
