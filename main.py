"""
Punto de entrada principal para Railway.
Importa y ejecuta la aplicación FastAPI desde backend/app/main.py
"""
import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Importar la aplicación FastAPI
from app.main import app

# Para compatibilidad con Railway
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

