import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import './App.css'
import { Dashboard, Users, Resources, Relationships, PermissionChecker } from './features'
import { healthService } from './services'

function App() {
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'error'>('checking')

  useEffect(() => {
    // Check API health on startup
    healthService.checkHealth()
      .then(() => setApiStatus('connected'))
      .catch(() => setApiStatus('error'))
  }, [])

  return (
    <Router>
      <div className="app">
        <header className="header">
          <div className="container">
            <h1>Rebecca API Dashboard</h1>
            <div className={`status-indicator ${apiStatus}`}>
              {apiStatus === 'checking' && '⏳ Checking API...'}
              {apiStatus === 'connected' && '✅ API Connected'}
              {apiStatus === 'error' && '❌ API Disconnected'}
            </div>
          </div>
        </header>

        <nav className="nav">
          <div className="container">
            <Link to="/" className="nav-link">Dashboard</Link>
            <Link to="/users" className="nav-link">Users</Link>
            <Link to="/resources" className="nav-link">Resources</Link>
            <Link to="/relationships" className="nav-link">Relationships</Link>
            <Link to="/permissions" className="nav-link">Permission Check</Link>
          </div>
        </nav>

        <main className="main">
          <div className="container">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/users" element={<Users />} />
              <Route path="/resources" element={<Resources />} />
              <Route path="/relationships" element={<Relationships />} />
              <Route path="/permissions" element={<PermissionChecker />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  )
}

export default App
