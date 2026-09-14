import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import './GeoMap.css'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const API = ''

function priceColor(preco_m2) {
  if (!preco_m2) return '#94a3b8'
  if (preco_m2 < 3000) return '#16a34a'
  if (preco_m2 < 4500) return '#f59e0b'
  return '#dc2626'
}


export default function GeoMap() {
  const [geoData, setGeoData] = useState(null)
  const [stats, setStats] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API}/api/geo`)
      .then(r => r.json())
      .then(d => {
        setGeoData(d.geojson)
        setStats(d.stats)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const onEachFeature = (feature, layer) => {
    const name = feature.properties?.Name || ''
    const stat = stats[name] || null

    const safeName = name.replace(/_/g, ' ').replace(/[<>"'&]/g, '')
    const tooltipContent = stat
      ? `<strong>${safeName}</strong><br/>R$ ${stat.preco_m2.toFixed(0)}/m²<br/>Área média: ${stat.area_media.toFixed(0)} m²<br/>${stat.count} imóveis`
      : `<strong>${safeName}</strong><br/>Sem dados`

    layer.bindTooltip(tooltipContent, { sticky: true })

    const color = stat ? priceColor(stat.preco_m2) : '#94a3b8'
    layer.setStyle({
      fillColor: color,
      fillOpacity: 0.5,
      color: '#1e293b',
      weight: 1,
    })

    layer.on('mouseover', () => layer.setStyle({ fillOpacity: 0.75, weight: 2 }))
    layer.on('mouseout', () => layer.setStyle({ fillOpacity: 0.5, weight: 1 }))
  }

  if (loading) return <div className="map-loading">Carregando dados geoespaciais...</div>

  return (
    <div className="geomap-page">
      <div className="map-header">
        <h1>Mapa de Preços por Bairro</h1>
        <p>Preço médio por metro quadrado em cada bairro de Piracicaba</p>
      </div>

      <div className="legend card">
        <h3>Legenda</h3>
        <div className="legend-items">
          <div className="legend-item"><span className="legend-dot" style={{ background: '#16a34a' }}></span> Abaixo de R$ 3.000/m²</div>
          <div className="legend-item"><span className="legend-dot" style={{ background: '#f59e0b' }}></span> R$ 3.000 – R$ 4.500/m²</div>
          <div className="legend-item"><span className="legend-dot" style={{ background: '#dc2626' }}></span> Acima de R$ 4.500/m²</div>
          <div className="legend-item"><span className="legend-dot" style={{ background: '#94a3b8' }}></span> Sem dados</div>
        </div>
      </div>

      <div className="map-container">
        <MapContainer
          center={[-22.7253, -47.6476]}
          zoom={12}
          style={{ height: '600px', width: '100%', borderRadius: '8px' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {geoData && (
            <GeoJSON
              key={JSON.stringify(stats)}
              data={geoData}
              onEachFeature={onEachFeature}
            />
          )}
        </MapContainer>
      </div>

      <div className="stats-grid">
        {Object.entries(stats)
          .sort((a, b) => b[1].preco_m2 - a[1].preco_m2)
          .slice(0, 12)
          .map(([bairro, s]) => (
            <div key={bairro} className="stat-card card">
              <div className="stat-bairro">{bairro.replace(/_/g, ' ')}</div>
              <div className="stat-price" style={{ color: priceColor(s.preco_m2) }}>
                R$ {s.preco_m2.toFixed(0)}/m²
              </div>
              <div className="stat-meta">{s.count} imóveis · {s.area_media.toFixed(0)} m² médio</div>
            </div>
          ))}
      </div>
    </div>
  )
}
