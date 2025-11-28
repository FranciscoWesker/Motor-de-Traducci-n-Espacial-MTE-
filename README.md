# Motor de Traducción Espacial (MTE)

Sistema multiplataforma para análisis, diagnóstico, corrección y estandarización de datos espaciales heterogéneos.

## Características

- **Detección automática de CRS**: Identifica sistemas de coordenadas incluso cuando están ausentes o mal declarados
- **Detección de unidades**: Identifica metros, pies, centímetros, etc.
- **Detección de origen**: Distingue entre sistemas locales y oficiales (MAGNA-SIRGAS)
- **Validación geométrica**: Evalúa la calidad de los datos espaciales
- **Sistema de confiabilidad**: Clasificación semáforo (🟢🟡🔴) para evaluar la idoneidad de los datos

## Requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ con PostGIS
- Docker y Docker Compose (opcional)

## Instalación

### Opción 1: Desarrollo Local

```bash
# Ejecutar script de configuración
./scripts/setup.sh

# Iniciar PostgreSQL (requiere tenerlo instalado)
# O usar Docker solo para PostgreSQL:
docker run -d --name postgres-mte -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=mte_db -p 5432:5432 postgis/postgis:15-3.3

# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend (en otra terminal)
cd frontend
npm run dev
```

### Opción 2: Docker Compose

```bash
# Desarrollo
docker-compose -f docker/docker-compose.dev.yml up

# Producción
docker-compose -f docker/docker-compose.yml up
```

## Uso

1. Accede a `http://localhost:3000`
2. Sube un archivo espacial (SHP, GeoJSON o CSV)
3. El sistema analizará automáticamente el archivo
4. Revisa el diagnóstico y las recomendaciones

## Pruebas Unitarias

El sistema incluye pruebas unitarias completas para verificar la detección de CRS y traducción.

### Ejecutar pruebas

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

### Ver ejemplos de uso

```bash
pytest tests/test_example_usage.py -v -s
```

Ver `README_TESTS.md` para más detalles sobre las pruebas.

## Formatos Soportados (MVP)

- Shapefile (.shp)
- GeoJSON (.geojson, .json)
- CSV con coordenadas (.csv)

## API

La API está disponible en `http://localhost:8000` con documentación automática en `/docs`.

### Endpoints principales:

- `POST /api/v1/files/upload` - Cargar archivo
- `POST /api/v1/analysis/{file_id}/diagnose` - Analizar archivo
- `GET /api/v1/analysis/{analysis_id}` - Obtener resultados
- `GET /api/v1/analysis/{analysis_id}/preview` - Vista previa GeoJSON

## Estructura del Proyecto

```
spatial-translator-engine/
├── backend/          # API FastAPI
├── frontend/         # Aplicación React
├── docker/           # Configuración Docker
├── docs/             # Documentación
└── scripts/          # Scripts de utilidad
```

## Licencia

Este proyecto está en desarrollo.

