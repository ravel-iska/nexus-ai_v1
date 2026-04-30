import { useState } from 'react'

export default function OsintPage() {
  const [domain, setDomain] = useState('')
  const [email, setEmail] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('domain')

  const scanDomain = async () => {
    if (!domain) return
    setLoading(true)
    setResults(null)
    try {
      const aiApi = import.meta.env.VITE_AI_API_URL || 'http://localhost:8000'
      const resp = await fetch(`${aiApi}/api/v1/osint/domain`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain }),
      })
      setResults(await resp.json())
    } catch (e) {
      setResults({ error: `Backend unreachable: ${e.message}`, hint: 'Jalankan uvicorn terlebih dahulu.' })
    }
    setLoading(false)
  }

  const checkLeak = async () => {
    if (!email) return
    setLoading(true)
    setResults(null)
    try {
      const aiApi = import.meta.env.VITE_AI_API_URL || 'http://localhost:8000'
      const resp = await fetch(`${aiApi}/api/v1/osint/leak`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      })
      setResults(await resp.json())
    } catch (e) {
      setResults({ error: `Backend unreachable: ${e.message}` })
    }
    setLoading(false)
  }

  return (
    <>
      <div className="tabs">
        <button className={`tab ${activeTab==='domain'?'active':''}`}
          onClick={()=>{setActiveTab('domain');setResults(null)}}>🔍 Domain Intelligence</button>
        <button className={`tab ${activeTab==='leak'?'active':''}`}
          onClick={()=>{setActiveTab('leak');setResults(null)}}>📧 Leak Checker</button>
        <button className={`tab ${activeTab==='headers'?'active':''}`}
          onClick={()=>{setActiveTab('headers');setResults(null)}}>🛡️ Security Headers</button>
      </div>

      {activeTab === 'domain' && (
        <div className="panel">
          <h3>🔍 Domain Intelligence</h3>
          <div className="input-group">
            <input className="input-field" value={domain} onChange={e=>setDomain(e.target.value)}
              placeholder="example.com" onKeyDown={e=>e.key==='Enter'&&scanDomain()} />
            <button className="btn btn-neon" onClick={scanDomain} disabled={loading}>
              {loading ? '⏳ Scanning...' : '🚀 Scan'}
            </button>
          </div>
          <p style={{fontSize:11,color:'var(--muted)'}}>WHOIS + DNS + SSL + Subdomain enumeration</p>
        </div>
      )}

      {activeTab === 'leak' && (
        <div className="panel">
          <h3>📧 Data Breach Check</h3>
          <div className="input-group">
            <input className="input-field" value={email} onChange={e=>setEmail(e.target.value)}
              placeholder="user@example.com" onKeyDown={e=>e.key==='Enter'&&checkLeak()} />
            <button className="btn btn-pink" onClick={checkLeak} disabled={loading}>
              {loading ? '⏳ Checking...' : '🔍 Check'}
            </button>
          </div>
          <p style={{fontSize:11,color:'var(--muted)'}}>Check against Have I Been Pwned database</p>
        </div>
      )}

      {activeTab === 'headers' && (
        <div className="panel">
          <h3>🛡️ Security Header Audit</h3>
          <div className="input-group">
            <input className="input-field" value={domain} onChange={e=>setDomain(e.target.value)}
              placeholder="https://example.com" />
            <button className="btn btn-blue" disabled={loading}>🔍 Audit</button>
          </div>
          <p style={{fontSize:11,color:'var(--muted)'}}>CSP, HSTS, X-Frame-Options, X-XSS-Protection</p>
        </div>
      )}

      {results && (
        <div className="panel">
          <h3>📊 Results</h3>
          <div className="term">{JSON.stringify(results, null, 2)}</div>
        </div>
      )}
    </>
  )
}
