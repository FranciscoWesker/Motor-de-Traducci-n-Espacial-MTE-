import { useEffect, useRef, useState } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { AnalysisPreview } from '@/services/api'
import './SideBySideMap.css'

interface SideBySideMapProps {
  originalData: AnalysisPreview | null
  transformedData: AnalysisPreview | null
}

export default function SideBySideMap({ originalData, transformedData }: SideBySideMapProps) {
  const leftMapContainer = useRef<HTMLDivElement>(null)
  const rightMapContainer = useRef<HTMLDivElement>(null)
  const leftMap = useRef<maplibregl.Map | null>(null)
  const rightMap = useRef<maplibregl.Map | null>(null)
  const [mapsLoaded, setMapsLoaded] = useState(false)

  useEffect(() => {
    if (!leftMapContainer.current || !rightMapContainer.current) return

    // Crear mapa izquierdo (original)
    leftMap.current = new maplibregl.Map({
      container: leftMapContainer.current,
      style: {
        version: 8,
        sources: {
          'raster-tiles': {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '© OpenStreetMap contributors'
          }
        },
        layers: [{
          id: 'simple-tiles',
          type: 'raster',
          source: 'raster-tiles',
          minzoom: 0,
          maxzoom: 22
        }]
      },
      center: originalData?.bounds ? [
        (originalData.bounds[0] + originalData.bounds[2]) / 2,
        (originalData.bounds[1] + originalData.bounds[3]) / 2
      ] : [-74.0, 4.6],
      zoom: originalData?.bounds ? 10 : 5
    })

    // Crear mapa derecho (transformado o mismo si no hay transformación)
    rightMap.current = new maplibregl.Map({
      container: rightMapContainer.current,
      style: {
        version: 8,
        sources: {
          'raster-tiles': {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '© OpenStreetMap contributors'
          }
        },
        layers: [{
          id: 'simple-tiles',
          type: 'raster',
          source: 'raster-tiles',
          minzoom: 0,
          maxzoom: 22
        }]
      },
      center: transformedData?.bounds || originalData?.bounds ? [
        ((transformedData?.bounds || originalData?.bounds)![0] + (transformedData?.bounds || originalData?.bounds)![2]) / 2,
        ((transformedData?.bounds || originalData?.bounds)![1] + (transformedData?.bounds || originalData?.bounds)![3]) / 2
      ] : [-74.0, 4.6],
      zoom: transformedData?.bounds || originalData?.bounds ? 10 : 5
    })

    // Sincronizar movimientos de mapas
    const syncMaps = () => {
      if (!leftMap.current || !rightMap.current) return

      leftMap.current.on('move', () => {
        if (rightMap.current && leftMap.current) {
          const center = leftMap.current.getCenter()
          const zoom = leftMap.current.getZoom()
          rightMap.current.setCenter(center)
          rightMap.current.setZoom(zoom)
        }
      })

      rightMap.current.on('move', () => {
        if (leftMap.current && rightMap.current) {
          const center = rightMap.current.getCenter()
          const zoom = rightMap.current.getZoom()
          leftMap.current.setCenter(center)
          leftMap.current.setZoom(zoom)
        }
      })
    }

    leftMap.current.on('load', () => {
      if (rightMap.current) {
        rightMap.current.on('load', () => {
          setMapsLoaded(true)
          syncMaps()
        })
      } else {
        setMapsLoaded(true)
      }
    })

    return () => {
      leftMap.current?.remove()
      rightMap.current?.remove()
    }
  }, [])

  useEffect(() => {
    if (!mapsLoaded || !leftMap.current) return

    // Agregar datos originales al mapa izquierdo
    if (originalData?.geojson) {
      if (leftMap.current.getSource('original-data')) {
        (leftMap.current.getSource('original-data') as maplibregl.GeoJSONSource).setData(originalData.geojson)
      } else {
        leftMap.current.addSource('original-data', {
          type: 'geojson',
          data: originalData.geojson
        })

        leftMap.current.addLayer({
          id: 'original-fill',
          type: 'fill',
          source: 'original-data',
          paint: {
            'fill-color': '#667eea',
            'fill-opacity': 0.6
          }
        })

        leftMap.current.addLayer({
          id: 'original-outline',
          type: 'line',
          source: 'original-data',
          paint: {
            'line-color': '#667eea',
            'line-width': 2
          }
        })
      }

      if (originalData.bounds && originalData.bounds.length === 4) {
        leftMap.current.fitBounds(
          [[originalData.bounds[0], originalData.bounds[1]], [originalData.bounds[2], originalData.bounds[3]]],
          { padding: 50, duration: 1000 }
        )
      }
    }
  }, [originalData, mapsLoaded])

  useEffect(() => {
    if (!mapsLoaded || !rightMap.current) return

    // Agregar datos transformados o originales al mapa derecho
    const dataToShow = transformedData || originalData
    if (dataToShow?.geojson) {
      if (rightMap.current.getSource('transformed-data')) {
        (rightMap.current.getSource('transformed-data') as maplibregl.GeoJSONSource).setData(dataToShow.geojson)
      } else {
        rightMap.current.addSource('transformed-data', {
          type: 'geojson',
          data: dataToShow.geojson
        })

        rightMap.current.addLayer({
          id: 'transformed-fill',
          type: 'fill',
          source: 'transformed-data',
          paint: {
            'fill-color': transformedData ? '#48bb78' : '#667eea',
            'fill-opacity': 0.6
          }
        })

        rightMap.current.addLayer({
          id: 'transformed-outline',
          type: 'line',
          source: 'transformed-data',
          paint: {
            'line-color': transformedData ? '#48bb78' : '#667eea',
            'line-width': 2
          }
        })
      }

      if (dataToShow.bounds && dataToShow.bounds.length === 4) {
        rightMap.current.fitBounds(
          [[dataToShow.bounds[0], dataToShow.bounds[1]], [dataToShow.bounds[2], dataToShow.bounds[3]]],
          { padding: 50, duration: 1000 }
        )
      }
    }
  }, [transformedData, originalData, mapsLoaded])

  return (
    <div className="side-by-side-map">
      <div className="map-container-wrapper">
        <div className="map-panel">
          <h3>Original</h3>
          <div className="map-label">
            CRS: {originalData?.crs_aplicado || 'No especificado'}
          </div>
          <div ref={leftMapContainer} className="map-container" />
        </div>
        <div className="map-panel">
          <h3>{transformedData ? 'Transformado' : 'Original (sin transformación)'}</h3>
          <div className="map-label">
            CRS: {transformedData?.crs_aplicado || originalData?.crs_aplicado || 'No especificado'}
          </div>
          <div ref={rightMapContainer} className="map-container" />
        </div>
      </div>
    </div>
  )
}

