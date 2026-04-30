import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import OsintPage from './pages/Osint'
import DownloaderPage from './pages/Downloader'
import CryptoPage from './pages/Crypto'
import SandboxPage from './pages/Sandbox'
import ApiKeysPage from './pages/ApiKeys'
import SkillsPage from './pages/Skills'
import LogsPage from './pages/Logs'
import WAConnection from './pages/WAConnection'
import './index.css'

const PAGES = {
  dashboard: { label: 'Dashboard', icon: '📊', component: Dashboard },
  wa_device: { label: 'WA Device', icon: '📱', component: WAConnection },
  chat: { label: 'Chat AI', icon: '💬', component: Chat },
  osint: { label: 'OSINT', icon: '🔍', component: OsintPage },
  downloader: { label: 'Downloader', icon: '⬇️', component: DownloaderPage },
  crypto: { label: 'Crypto', icon: '📈', component: CryptoPage },
  sandbox: { label: 'Sandbox', icon: '🔬', component: SandboxPage },
  apikeys: { label: 'API Keys', icon: '🔑', component: ApiKeysPage },
  skills: { label: 'Skills', icon: '⚡', component: SkillsPage },
  logs: { label: 'Logs', icon: '📋', component: LogsPage },
}

export default function App() {
  const [activePage, setActivePage] = useState('dashboard')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [apiKey, setApiKey] = useState('')
  const [loginError, setLoginError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const savedKey = localStorage.getItem('nexusApiKey')
    if (savedKey) {
      validateKey(savedKey)
    }
  }, [])

  const validateKey = async (key) => {
    setLoading(true)
    setLoginError('')
    try {
      const resp = await fetch('/api/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key })
      })
      const data = await resp.json()
      if (data.success) {
        localStorage.setItem('nexusApiKey', key)
        setIsAuthenticated(true)
      } else {
        setLoginError(data.error || 'Invalid API Key')
        localStorage.removeItem('nexusApiKey')
        setIsAuthenticated(false)
      }
    } catch (e) {
      setLoginError('Error connecting to local auth server.')
    }
    setLoading(false)
  }

  const handleLogin = (e) => {
    e.preventDefault()
    if (!apiKey.trim()) return
    validateKey(apiKey.trim())
  }

  const handleLogout = () => {
    localStorage.removeItem('nexusApiKey')
    setIsAuthenticated(false)
    setApiKey('')
  }

  // ─── LOGIN SCREEN ───
  if (!isAuthenticated) {
    return (
      <div className="login-container">
        <div className="login-box">
          <div className="login-brand">⬡ NEXUS v3</div>
          <p className="login-sub">RESTRICTED ACCESS — MASTER KEY REQUIRED</p>
          
          <form onSubmit={handleLogin}>
            <input 
              type="password" 
              className="login-input" 
              placeholder="Enter API Key (hms_...)" 
              value={apiKey} 
              onChange={e => setApiKey(e.target.value)}
              disabled={loading}
              autoFocus
            />
            {loginError && <div className="login-error">🚨 {loginError}</div>}
            
            <button type="submit" className="btn btn-neon login-btn" disabled={loading}>
              {loading ? 'VERIFYING...' : 'ACCESS DASHBOARD'}
            </button>
          </form>
          
          <div className="login-hint">
            To generate a new Master Key, run in terminal:<br/>
            <code>nexus-agent keygen</code>
          </div>
        </div>
      </div>
    )
  }

  // ─── DASHBOARD ───
  const page = PAGES[activePage]
  const PageComponent = page.component

  return (
    <div className="app">
      <Sidebar pages={PAGES} active={activePage} onNavigate={setActivePage} onLogout={handleLogout} />
      <div className="main">
        <Topbar title={page.label} icon={page.icon} />
        <div className="content">
          <PageComponent />
        </div>
      </div>
    </div>
  )
}
