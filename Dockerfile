FROM node:20-slim AS frontend-builder

# Construir frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
# Usar npm install si no hay package-lock.json, npm ci si existe
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY frontend/ .
RUN npm run build
# Verificar que el build se completó correctamente
RUN ls -la dist/ && test -f dist/index.html && echo "Frontend build successful"

FROM python:3.11-slim

# Instalar dependencias del sistema para geoespaciales
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    gdal-data \
    proj-bin \
    proj-data \
    libproj-dev \
    libgeos-dev \
    libgeos++-dev \
    postgresql-client \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Configurar variables de entorno para GDAL y PROJ
ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV PROJ_DIR=/usr
ENV PROJ_LIB=/usr/share/proj
ENV GEOS_DIR=/usr

WORKDIR /app

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
# Las variables de entorno PROJ_DIR, PROJ_LIB y GDAL_CONFIG están configuradas arriba
# Instalar NumPy 1.x primero (Shapely 2.0.2 y GeoPandas 0.14.1 fueron compilados con NumPy 1.x)
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir "numpy<2.0" && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY main.py .
COPY backend/ ./backend/

# Copiar frontend construido desde el stage anterior
COPY --from=frontend-builder /frontend/dist ./frontend/dist
# Verificar que el frontend se copió correctamente
RUN ls -la frontend/dist/ && test -f frontend/dist/index.html && echo "Frontend copied successfully"

# Crear directorio para uploads
RUN mkdir -p /app/uploads

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Exponer puerto
EXPOSE 8000

# Comando por defecto (puede ser sobrescrito por Railway)
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

