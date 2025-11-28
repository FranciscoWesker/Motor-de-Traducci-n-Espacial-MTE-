#!/bin/bash
# Script para configurar variables de entorno para pyproj y gdal

# Buscar el ejecutable proj primero
PROJ_BIN=$(which proj 2>/dev/null || find /nix/store -name proj -type f -path "*/bin/*" 2>/dev/null | head -1)
if [ -n "$PROJ_BIN" ]; then
  # PROJ_DIR debe ser el directorio raíz de la instalación (donde están bin/, lib/, etc.)
  export PROJ_DIR=$(dirname $(dirname "$PROJ_BIN"))
  export PROJ_LIB="$PROJ_DIR/lib"
else
  # Fallback: buscar directorio proj
  PROJ_PATH=$(find /nix/store -maxdepth 3 -name proj -type d 2>/dev/null | head -1)
  if [ -n "$PROJ_PATH" ]; then
    export PROJ_DIR=$(dirname "$PROJ_PATH")
    export PROJ_LIB="$PROJ_PATH/lib"
  else
    export PROJ_DIR=/usr
    export PROJ_LIB=/usr/lib
  fi
fi

# Encontrar gdal-config
export GDAL_CONFIG=$(which gdal-config 2>/dev/null || find /nix/store -name gdal-config -type f 2>/dev/null | head -1 || echo /usr/bin/gdal-config)

echo "PROJ_DIR=$PROJ_DIR"
echo "PROJ_LIB=$PROJ_LIB"
echo "GDAL_CONFIG=$GDAL_CONFIG"

