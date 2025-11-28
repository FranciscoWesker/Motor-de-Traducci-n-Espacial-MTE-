import { useEffect, useRef, useState } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import './MapViewer.css'

interface MapViewerProps {
  geojson: any
  bounds?: number[]
}

export default function MapViewer({ geojson, bounds }: MapViewerProps) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<maplibregl.Map | null>(null)
  const [mapLoaded, setMapLoaded] = useState(false)

  useEffect(() => {
    if (!mapContainer.current || map.current) return

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          'raster-tiles': {
            type: 'raster',
            tiles: [
              'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
            ],
            tileSize: 256,
            attribution: '© OpenStreetMap contributors'
          }
        },
        layers: [
          {
            id: 'simple-tiles',
            type: 'raster',
            source: 'raster-tiles',
            minzoom: 0,
            maxzoom: 22
          }
        ]
      },
      center: bounds ? [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2] : [-74.0, 4.6],
      zoom: bounds ? 10 : 5
    })

    map.current.on('load', () => {
      setMapLoaded(true)
    })

    return () => {
      map.current?.remove()
    }
  }, [])

  useEffect(() => {
    if (!map.current || !mapLoaded || !geojson) return

    // Agregar fuente GeoJSON
    if (map.current.getSource('data')) {
      (map.current.getSource('data') as maplibregl.GeoJSONSource).setData(geojson)
    } else {
      map.current.addSource('data', {
        type: 'geojson',
        data: geojson
      })

      map.current.addLayer({
        id: 'data-layer',
        type: 'fill',
        source: 'data',
        paint: {
          'fill-color': '#667eea',
          'fill-opacity': 0.6
        }
      })

      map.current.addLayer({
        id: 'data-outline',
        type: 'line',
        source: 'data',
        paint: {
          'line-color': '#667eea',
          'line-width': 2
        }
      })
    }

    // Ajustar vista a los bounds
    if (bounds && bounds.length === 4) {
      map.current.fitBounds(
        [[bounds[0], bounds[1]], [bounds[2], bounds[3]]],
        { padding: 50, duration: 1000 }
      )
    }
  }, [geojson, bounds, mapLoaded])

  return (
    <div className="map-viewer">
      <div ref={mapContainer} className="map-container" />
    </div>
  )
}
