import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import './App.css'
import { 
  Dashboard, 
  Users, 
  Resources, 
  Relationships, 
  PermissionChecker, 
  UserGroups, 
  ResourceGroups 
} from './features'
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
      <div className="min-h-screen flex flex-col bg-gray-50">
        <header className="bg-slate-800 text-white shadow-md">
          <div className="w-full px-4 lg:px-8 py-4 flex justify-between items-center">
            <h1 className="text-xl font-semibold">Rebecca API Dashboard</h1>
            <div className={`px-4 py-2 rounded text-sm font-medium ${
              apiStatus === 'checking' ? 'bg-yellow-500 text-white' :
              apiStatus === 'connected' ? 'bg-green-500 text-white' :
              'bg-red-500 text-white'
            }`}>
              {apiStatus === 'checking' && '⏳ Checking API...'}
              {apiStatus === 'connected' && '✅ API Connected'}
              {apiStatus === 'error' && '❌ API Disconnected'}
            </div>
          </div>
        </header>

        <nav className="bg-slate-700 shadow-md">
          <div className="w-full px-4 lg:px-8 flex">
            <Link to="/" className="px-6 py-4 text-gray-300 hover:text-white hover:bg-slate-800 border-b-4 border-transparent hover:border-blue-400 transition-all">Dashboard</Link>
            <Link to="/users" className="px-6 py-4 text-gray-300 hover:text-white hover:bg-slate-800 border-b-4 border-transparent hover:border-blue-400 transition-all">Users</Link>
            <Link to="/user-groups" className="px-6 py-4 text-gray-300 hover:text-white hover:bg-slate-800 border-b-4 border-transparent hover:border-blue-400 transition-all">User Groups</Link>
            <Link to="/resources" className="px-6 py-4 text-gray-300 hover:text-white hover:bg-slate-800 border-b-4 border-transparent hover:border-blue-400 transition-all">Resources</Link>
            <Link to="/resource-groups" className="px-6 py-4 text-gray-300 hover:text-white hover:bg-slate-800 border-b-4 border-transparent hover:border-blue-400 transition-all">Resource Groups</Link>
            <Link to="/relationships" className="px-6 py-4 text-gray-300 hover:text-white hover:bg-slate-800 border-b-4 border-transparent hover:border-blue-400 transition-all">Relationships</Link>
            <Link to="/permissions" className="px-6 py-4 text-gray-300 hover:text-white hover:bg-slate-800 border-b-4 border-transparent hover:border-blue-400 transition-all">Permission Check</Link>
          </div>
        </nav>

        <main className="flex-1 w-full px-4 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/users" element={<Users />} />
            <Route path="/user-groups" element={<UserGroups />} />
            <Route path="/resources" element={<Resources />} />
            <Route path="/resource-groups" element={<ResourceGroups />} />
            <Route path="/relationships" element={<Relationships />} />
            <Route path="/permissions" element={<PermissionChecker />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
