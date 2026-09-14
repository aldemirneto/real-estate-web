import { useState, useEffect, useCallback } from 'react'
import './Search.css'

const API = ''

function formatBRL(value) {
  if (!value && value !== 0) return 'N/A'
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(value)
}

function extractSiteName(url) {
  try {
    const host = new URL(url).hostname.replace('www.', '')
    return host.split('.')[0].charAt(0).toUpperCase() + host.split('.')[0].slice(1)
  } catch {
    return 'Ver imóvel'
  }
}

export default function Search() {
  const [cities, setCities] = useState(["Piracicaba", "São Paulo"])
  const [neighborhoods, setNeighborhoods] = useState([])
  const [priceRange, setPriceRange] = useState({ mean: 500000, max: 2000000 })

  const [filters, setFilters] = useState({
    cidade: 'Piracicaba',
    bairro: '_Todos',
    quartos: 0,
    banheiros: 0,
    vagas: 0,
    area_min: 0,
    preco_max: 1000000,
  })

  const [results, setResults] = useState(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  useEffect(() => {
    fetch(`${API}/api/neighborhoods?cidade=${encodeURIComponent(filters.cidade)}`)
      .then(r => r.json())
      .then(d => setNeighborhoods(d.neighborhoods))
      .catch(console.error)

    fetch(`${API}/api/price-range?cidade=${encodeURIComponent(filters.cidade)}`)
      .then(r => r.json())
      .then(d => {
        setPriceRange(d)
        setFilters(f => ({ ...f, preco_max: Math.round(d.mean + 1000000) }))
      })
      .catch(console.error)
  }, [filters.cidade])

  useEffect(() => {
    fetch(`${API}/api/cities`).then(r => r.json()).then(d => setCities(d.cities)).catch(console.error)
  }, [])

  const doSearch = useCallback(async (currentPage = 1) => {
    setLoading(true)
    setSearched(true)
    const params = new URLSearchParams({
      cidade: filters.cidade,
      bairro: filters.bairro,
      quartos: filters.quartos,
      banheiros: filters.banheiros,
      vagas: filters.vagas,
      area_min: filters.area_min,
      preco_max: filters.preco_max,
      page: currentPage,
      per_page: 30,
    })
    try {
      const res = await fetch(`${API}/api/properties?${params}`)
      const data = await res.json()
      setResults(data)
      setPage(currentPage)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [filters])

  const handleSearch = (e) => {
    e.preventDefault()
    doSearch(1)
  }

  const setFilter = (key, value) => setFilters(f => ({ ...f, [key]: value }))

  return (
    <div className="search-page">
      <div className="search-header">
        <h1>Busca de Imóveis</h1>
        <p>Filtre por bairro, características e preço</p>
      </div>

      <form className="filters-card card" onSubmit={handleSearch}>
        <div className="filter-row">
          <div className="filter-group full-width">
            <label>Cidade</label>
            <select value={filters.cidade} onChange={e => { setFilters(f => ({ ...f, cidade: e.target.value, bairro: '_Todos' })); setResults(null); setSearched(false) }}>
              {cities.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
            <label>Bairro</label>
            <select value={filters.bairro} onChange={e => setFilter('bairro', e.target.value)}>
              <option value="_Todos">Todos os bairros</option>
              {neighborhoods.map(b => (
                <option key={b} value={b}>{b.replace(/_/g, ' ')}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="filter-row four-cols">
          <div className="filter-group">
            <label>Quartos (mín.)</label>
            <input type="number" min={0} max={10} value={filters.quartos}
              onChange={e => setFilter('quartos', Number(e.target.value))} />
          </div>
          <div className="filter-group">
            <label>Banheiros (mín.)</label>
            <input type="number" min={0} max={9} value={filters.banheiros}
              onChange={e => setFilter('banheiros', Number(e.target.value))} />
          </div>
          <div className="filter-group">
            <label>Vagas (mín.)</label>
            <input type="number" min={0} max={9} value={filters.vagas}
              onChange={e => setFilter('vagas', Number(e.target.value))} />
          </div>
          <div className="filter-group">
            <label>Área mínima (m²)</label>
            <input type="number" min={0} max={1000} step={10} value={filters.area_min}
              onChange={e => setFilter('area_min', Number(e.target.value))} />
          </div>
        </div>

        <div className="filter-group">
          <label>
            Preço máximo: <strong>{formatBRL(filters.preco_max)}</strong>
          </label>
          <input
            type="range"
            min={0}
            max={Math.max(1000000, Math.round(priceRange.max))}
            step={10000}
            value={filters.preco_max}
            onChange={e => setFilter('preco_max', Number(e.target.value))}
            className="price-slider"
          />
          <div className="slider-labels">
            <span>R$ 0</span>
            <span>{formatBRL(Math.max(1000000, Math.round(priceRange.max)))}</span>
          </div>
        </div>

        <button type="submit" className="btn btn-primary search-btn" disabled={loading}>
          {loading ? 'Buscando...' : 'Pesquisar'}
        </button>
      </form>

      {searched && (
        <div className="results-section">
          {loading && <div className="loading-msg">Carregando...</div>}

          {!loading && results && (
            <>
              <div className="results-meta">
                {results.total > 0 ? (
                  <span>{results.total} imóvel(eis) encontrado(s) · Última atualização: {results.last_update}</span>
                ) : (
                  <span className="no-results">Nenhum resultado encontrado. Tente ajustar os filtros.</span>
                )}
              </div>

              {results.total > 0 && (
                <>
                  <div className="table-wrapper">
                    <table className="results-table">
                      <thead>
                        <tr>
                          {filters.bairro === '_Todos' ? <th>Bairro</th> : <th>Imobiliária</th>}
                          <th>Preço</th>
                          <th>Área (m²)</th>
                          <th>Quartos</th>
                          <th>Banheiros</th>
                          <th>Vagas</th>
                          <th>Link</th>
                        </tr>
                      </thead>
                      <tbody>
                        {results.properties.map((p, i) => (
                          <tr key={i}>
                            <td>{(filters.bairro === '_Todos' ? p.bairro : p.imobiliaria || '-').replace(/_/g, ' ')}</td>
                            <td className="price-cell">{formatBRL(p.preco)}</td>
                            <td>{p.area ? `${p.area} m²` : '-'}</td>
                            <td>{p.quartos}</td>
                            <td>{p.banheiros}</td>
                            <td>{p.vagas}</td>
                            <td>
                              <a href={/^https?:\/\//.test(p.link) ? p.link : '#'} target="_blank" rel="noreferrer" className="property-link" title={p.link}>
                                {extractSiteName(p.link)} 🏠
                              </a>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {results.total_pages > 1 && (
                    <div className="pagination">
                      <button
                        className="btn btn-secondary"
                        onClick={() => doSearch(page - 1)}
                        disabled={page <= 1}
                      >
                        ← Anterior
                      </button>
                      <span className="page-info">Página {page} de {results.total_pages}</span>
                      <button
                        className="btn btn-secondary"
                        onClick={() => doSearch(page + 1)}
                        disabled={page >= results.total_pages}
                      >
                        Próxima →
                      </button>
                    </div>
                  )}
                </>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
