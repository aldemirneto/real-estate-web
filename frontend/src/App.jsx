import { Routes, Route, NavLink } from 'react-router-dom'
import Home from './pages/Home'
import Search from './pages/Search'
import GeoMap from './pages/GeoMap'
import Estimator from './pages/Estimator'
import './App.css'

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span>🏠</span> Imóveis Piracicaba
      </div>
      <div className="navbar-links">
        <NavLink to="/" end>Início</NavLink>
        <NavLink to="/busca">Busca</NavLink>
        <NavLink to="/mapa">Mapa</NavLink>
        <NavLink to="/estimador">Estimador</NavLink>
      </div>
    </nav>
  )
}

function App() {
  return (
    <div className="app">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/busca" element={<Search />} />
          <Route path="/mapa" element={<GeoMap />} />
          <Route path="/estimador" element={<Estimator />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
