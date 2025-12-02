from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.db_health import check_db_connection
from app.api.v1 import files, analysis, export, transformation, layers, stats
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

# Verificar conexión a base de datos al iniciar
@app.on_event("startup")
async def startup_event():
    print("[APP] Iniciando aplicacion...")
    check_db_connection()

# Routers
app.include_router(files.router, prefix="/api/v1", tags=["files"])
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(export.router, prefix="/api/v1", tags=["export"])
app.include_router(transformation.router, prefix="/api/v1", tags=["transformation"])
app.include_router(layers.router, prefix="/api/v1", tags=["layers"])
app.include_router(stats.router, prefix="/api/v1", tags=["stats"])

# Ruta de health check (debe ir antes del catch-all)
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Servir frontend estático
# Buscar frontend en diferentes ubicaciones posibles
possible_paths = [
    Path(__file__).parent.parent.parent.parent / "frontend" / "dist",  # Desde backend/app/main.py
    Path("/app/frontend/dist"),  # En Docker
    Path("./frontend/dist"),  # Relativo
]

frontend_dist_path = None
for path in possible_paths:
    if path.exists() and (path / "index.html").exists():
        frontend_dist_path = path
        break

if frontend_dist_path:
    print(f"Frontend encontrado en: {frontend_dist_path}")
    
    # Montar archivos estáticos (JS, CSS, imágenes, etc.)
    static_path = frontend_dist_path / "assets"
    if static_path.exists():

        app.mount("/assets", StaticFiles(directory=str(static_path)), name="assets")
        print(f"Assets montados en: {static_path}")
    
    # Servir index.html para la ruta raíz
    @app.get("/")
    async def serve_root():
        index_path = frontend_dist_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"message": "Motor de Traducción Espacial API", "version": "1.0.0", "frontend": "not found"}
    
    # Servir archivos estáticos y SPA routing
    # Esta ruta debe ir al final para no interferir con las rutas de la API
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Si la ruta comienza con api/ o docs, no servir el frontend
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path == "health":
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")
        
        # Si es un archivo estático (assets), ya está manejado por el mount
        if full_path.startswith("assets/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Intentar servir archivos estáticos del frontend (favicon.ico, vite.svg, etc.)
        file_path = frontend_dist_path / full_path
        if file_path.exists() and file_path.is_file() and file_path.name != "index.html":
            return FileResponse(str(file_path))
        
        # Para todas las demás rutas (SPA routing), servir index.html
        index_path = frontend_dist_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Frontend not found")
else:
    print("Frontend no encontrado, sirviendo solo API")
    # En desarrollo, solo mostrar JSON en la raíz
    @app.get("/")
    async def root():
        return {"message": "Motor de Traducción Espacial API", "version": "1.0.0", "frontend": "not built"}
