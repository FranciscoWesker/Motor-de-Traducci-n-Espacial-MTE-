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

# Crear directorio para uploads
RUN mkdir -p /app/uploads

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Exponer puerto
EXPOSE 8000

# Comando por defecto (puede ser sobrescrito por Railway)
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

