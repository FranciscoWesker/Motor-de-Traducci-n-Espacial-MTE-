from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.api.v1 import files, analysis
import os
from pathlib import Path

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

# Ruta de health check (debe ir antes del catch-all)
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Servir frontend estático en producción
frontend_dist_path = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
if frontend_dist_path.exists() and is_production:
    # Montar archivos estáticos (JS, CSS, imágenes, etc.)
    static_path = frontend_dist_path / "assets"
    if static_path.exists():
        app.mount("/assets", StaticFiles(directory=str(static_path)), name="assets")
    
    # Servir index.html para la ruta raíz y todas las rutas del frontend (SPA routing)
    # Esta ruta debe ir al final para no interferir con las rutas de la API
    @app.get("/")
    async def serve_root():
        index_path = frontend_dist_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"message": "Motor de Traducción Espacial API", "version": "1.0.0"}
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Si la ruta comienza con /api o /docs, no servir el frontend (debe retornar 404)
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path == "health":
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        
        index_path = frontend_dist_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Frontend not found")
else:
    # En desarrollo, solo mostrar JSON en la raíz
    @app.get("/")
    async def root():
        return {"message": "Motor de Traducción Espacial API", "version": "1.0.0"}
