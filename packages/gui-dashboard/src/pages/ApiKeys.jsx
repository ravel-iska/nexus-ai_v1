import { useState, useEffect } from 'react'

export default function ApiKeysPage() {
  const [keys, setKeys] = useState([])
  const [loading, setLoading] = useState(true)
  const [newLabel, setNewLabel] = useState('')
  const [newKey, setNewKey] = useState('')

  useEffect(() => { fetchKeys() }, [])

  const fetchKeys = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('nexusApiKey')
      const resp = await fetch('/api/keys', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (resp.ok) {
        setKeys(await resp.json())
      }
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  const handleGenerate = async () => {
    try {
      const token = localStorage.getItem('nexusApiKey')
      const resp = await fetch('/api/keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ label: newLabel })
      })
      if (resp.ok) {
        const data = await resp.json()
        setNewKey(data.key)
        setNewLabel('')
        fetchKeys()
      }
    } catch (e) {
      console.error(e)
    }
  }

  const handleRevoke = async (keyToRevoke) => {
    if (!confirm('Are you sure you want to revoke this API key? Any device using it will lose access immediately.')) return
    
    try {
      const token = localStorage.getItem('nexusApiKey')
      const resp = await fetch(`/api/keys/${keyToRevoke}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (resp.ok) {
        fetchKeys()
      }
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <>
      <div className="panel">
        <h3>🔑 Access & API Keys</h3>
        <p style={{fontSize:13,color:'var(--muted)',marginBottom:24,lineHeight:1.6}}>
          Master API Keys allow external services or remote dashboards to securely authenticate and control your Nexus Agent. <br />
          Keep these keys secret. If compromised, revoke them immediately.
        </p>

        {newKey && (
          <div className="info-box" style={{borderColor:'var(--green)', background:'rgba(63,185,80,0.05)', borderLeftColor:'var(--green)'}}>
            <h4 style={{color:'var(--green)',margin:0,marginBottom:8}}>✅ New API Key Generated</h4>
            <p style={{fontSize:13,color:'var(--text)',marginBottom:16}}>Please copy this key now. For security reasons, it will not be shown in full again.</p>
            <div className="code-block" style={{margin:0,background:'var(--bg)'}}>
              <code style={{color:'var(--green)'}}>{newKey}</code>
            </div>
            <button className="btn" style={{marginTop:16}} onClick={()=>setNewKey('')}>Dismiss</button>
          </div>
        )}

        <div className="input-group" style={{maxWidth: 400, marginTop: 24}}>
          <input className="input-field" value={newLabel} onChange={e=>setNewLabel(e.target.value)} placeholder="Key Label (e.g., iPhone Dashboard)" />
          <button className="btn btn-neon" onClick={handleGenerate}>Generate New Key</button>
        </div>

        {loading ? <p style={{color:'var(--muted)', marginTop:24}}>Loading keys...</p> : (
          <table className="data-table" style={{marginTop: 32}}>
            <thead>
              <tr>
                <th>API Key</th>
                <th>Label</th>
                <th>Created</th>
                <th>Last Used</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {keys.map((k, i) => {
                const masked = k.key.slice(0, 8) + '••••••••••••' + k.key.slice(-6)
                return (
                  <tr key={i} style={{opacity: k.active ? 1 : 0.5}}>
                    <td style={{fontFamily:'JetBrains Mono',fontSize:13,color:k.active?'var(--text)':'var(--muted)'}}>{masked}</td>
                    <td style={{fontWeight:500}}>{k.label}</td>
                    <td style={{fontSize:12,color:'var(--muted)'}}>{new Date(k.created).toLocaleString()}</td>
                    <td style={{fontSize:12,color:'var(--muted)'}}>{k.lastUsed ? new Date(k.lastUsed).toLocaleString() : 'Never'}</td>
                    <td>
                      {k.active ? <span className="badge badge-green">Active</span> : <span className="badge badge-red">Revoked</span>}
                    </td>
                    <td>
                      {k.active && (
                        <button className="btn" style={{padding:'4px 8px', fontSize:11, color:'var(--neon2)'}} onClick={() => handleRevoke(k.key)}>
                          Revoke
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </>
  )
}
