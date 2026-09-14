import { Link } from 'react-router-dom'
import './Home.css'

export default function Home() {
  return (
    <div className="home">
      <section className="hero-section">
        <div className="hero-badge">Mercado Imobiliário</div>
        <h1>Classificador de Imóveis em <span className="highlight">Piracicaba</span></h1>
        <p className="hero-sub">
          Explore dados reais do mercado imobiliário, visualize preços por bairro no mapa
          e estime o valor do seu imóvel com machine learning.
        </p>
        <div className="hero-actions">
          <Link to="/busca" className="btn btn-primary">Buscar Imóveis</Link>
          <Link to="/mapa" className="btn btn-secondary">Ver Mapa</Link>
        </div>
      </section>

      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">🔍</div>
          <h3>Módulo de Busca</h3>
          <p>
            Filtre imóveis por bairro, número de quartos, banheiros, vagas e preço máximo.
            Resultados paginados com links diretos para os anúncios.
          </p>
          <Link to="/busca" className="feature-link">Buscar agora →</Link>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🗺️</div>
          <h3>Visualização Geoespacial</h3>
          <p>
            Mapa interativo de Piracicaba com o preço médio por metro quadrado em cada bairro,
            destacado por cores.
          </p>
          <Link to="/mapa" className="feature-link">Ver mapa →</Link>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🤖</div>
          <h3>Estimador de Preço</h3>
          <p>
            Use um modelo XGBoost treinado com dados reais de Piracicaba para estimar o
            valor de mercado do seu imóvel.
          </p>
          <Link to="/estimador" className="feature-link">Estimar preço →</Link>
        </div>
      </div>

      <section className="about-section card">
        <h2>Metodologia</h2>
        <p>
          Os dados foram coletados via webscraping nas principais imobiliárias de Piracicaba.
          O modelo de predição de preço utiliza XGBoost, treinado com características como
          localização (bairro), área, número de quartos, banheiros e vagas de garagem.
        </p>
        <p style={{ marginTop: '0.75rem', color: 'var(--text-light)', fontSize: '0.9rem' }}>
          Desenvolvido por <a href="https://github.com/aldemirneto" target="_blank" rel="noreferrer">Aldemir</a>
        </p>
      </section>
    </div>
  )
}
