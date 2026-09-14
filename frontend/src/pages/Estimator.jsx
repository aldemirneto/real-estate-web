import { useState, useEffect } from 'react'
import './Estimator.css'

const API = ''

function formatBRL(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(value)
}

export default function Estimator() {
  const [neighborhoods, setNeighborhoods] = useState([])
  const [form, setForm] = useState({
    bairro: '',
    area: 80,
    quartos: 2,
    banheiros: 1,
    vagas: 1,
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API}/api/neighborhoods`)
      .then(r => r.json())
      .then(d => {
        setNeighborhoods(d.neighborhoods)
        if (d.neighborhoods.length > 0) setForm(f => ({ ...f, bairro: d.neighborhoods[0] }))
      })
      .catch(console.error)
  }, [])

  const setField = (key, value) => {
    setForm(f => ({ ...f, [key]: value }))
    setResult(null)
    setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await fetch(`${API}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, area: Number(form.area), quartos: Number(form.quartos), banheiros: Number(form.banheiros), vagas: Number(form.vagas) }),
      })
      const data = await res.json()
      if (data.error) { setError(data.error); return }
      setResult(data.predicted_price)
    } catch {
      setError('Erro ao conectar com o servidor.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="estimator-page">
      <div className="estimator-header">
        <h1>Estimador de Preço</h1>
        <p>Estime o valor de mercado de um imóvel usando XGBoost treinado com dados reais de Piracicaba</p>
      </div>

      <div className="estimator-layout">
        <form className="estimator-form card" onSubmit={handleSubmit}>
          <h2>Características do Imóvel</h2>

          <div className="form-group">
            <label>Bairro</label>
            <select value={form.bairro} onChange={e => setField('bairro', e.target.value)} required>
              {neighborhoods.map(b => (
                <option key={b} value={b}>{b.replace(/_/g, ' ')}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Área (m²)</label>
            <input type="number" min={10} max={2000} value={form.area}
              onChange={e => setField('area', e.target.value)} required />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Quartos</label>
              <input type="number" min={0} max={10} value={form.quartos}
                onChange={e => setField('quartos', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Banheiros</label>
              <input type="number" min={0} max={10} value={form.banheiros}
                onChange={e => setField('banheiros', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Vagas</label>
              <input type="number" min={0} max={10} value={form.vagas}
                onChange={e => setField('vagas', e.target.value)} />
            </div>
          </div>

          <button type="submit" className="btn btn-primary estimate-btn" disabled={loading}>
            {loading ? 'Calculando...' : 'Estimar Preço'}
          </button>
        </form>

        <div className="result-area">
          {result !== null && (
            <div className="result-card card">
              <div className="result-label">Preço Estimado</div>
              <div className="result-value">{formatBRL(result)}</div>
              <div className="result-breakdown">
                <div className="breakdown-item">
                  <span>Por m²</span>
                  <strong>{formatBRL(result / form.area)}/m²</strong>
                </div>
                <div className="breakdown-item">
                  <span>Bairro</span>
                  <strong>{form.bairro.replace(/_/g, ' ')}</strong>
                </div>
                <div className="breakdown-item">
                  <span>Área</span>
                  <strong>{form.area} m²</strong>
                </div>
              </div>
              <p className="result-disclaimer">
                * Estimativa baseada em dados históricos. O valor real pode variar.
              </p>
            </div>
          )}

          {error && (
            <div className="error-card card">
              <span>⚠️ {error}</span>
            </div>
          )}

          {!result && !error && (
            <div className="empty-result card">
              <div className="empty-icon">🏠</div>
              <p>Preencha as características e clique em <strong>Estimar Preço</strong></p>
            </div>
          )}

          <div className="model-info card">
            <h3>Sobre o modelo</h3>
            <ul>
              <li>Algoritmo: <strong>XGBoost</strong></li>
              <li>Treinado com dados de imóveis de Piracicaba</li>
              <li>Features: bairro, área, quartos, banheiros, vagas</li>
              <li>Dados coletados via webscraping das principais imobiliárias</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
