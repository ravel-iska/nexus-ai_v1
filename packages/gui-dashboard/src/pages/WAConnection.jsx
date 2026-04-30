import { useState, useEffect } from 'react'

export default function WAConnection() {
  const [status, setStatus] = useState('disconnected')
  const [qrCode, setQrCode] = useState(null)
  const [pairingCode, setPairingCode] = useState(null)
  const [clientInfo, setClientInfo] = useState(null)
  const [phone, setPhone] = useState('')
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('qr')

  useEffect(() => {
    const waApi = import.meta.env.VITE_WA_API_URL || 'http://localhost:3101'
    const eventSource = new EventSource(`${waApi}/api/wa/events`)
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setStatus(data.status)
      setQrCode(data.qr)
      setPairingCode(data.pairingCode)
      setClientInfo(data.client)
    }

    return () => eventSource.close()
  }, [])

  const requestPairingCode = async () => {
    if (!phone) return
    setLoading(true)
    try {
      const waApi = import.meta.env.VITE_WA_API_URL || 'http://localhost:3101'
      await fetch(`${waApi}/api/wa/pair`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone })
      })
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  return (
    <div className="wa-connection-page">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="label">WA Engine Status</div>
          <div className="value" style={{ 
            color: status === 'connected' ? 'var(--green)' : 
                   status === 'connecting' || status === 'pairing' ? 'var(--neon3)' : 
                   'var(--neon2)' 
          }}>
            {status.toUpperCase()}
          </div>
          <div className="sub">Service Port: 3101</div>
        </div>
        
        {clientInfo && (
          <div className="stat-card">
            <div className="label">Connected Account</div>
            <div className="value" style={{ fontSize: 20 }}>{clientInfo.name}</div>
            <div className="sub">+{clientInfo.id}</div>
          </div>
        )}
      </div>

      <div className="panel" style={{ maxWidth: 600, margin: '0 auto', textAlign: 'center' }}>
        <h3>📱 Device Connection</h3>
        
        {status === 'connected' ? (
          <div style={{ padding: 40 }}>
            <div style={{ fontSize: 64, marginBottom: 16 }}>✅</div>
            <h2 style={{ color: 'var(--green)', marginBottom: 8 }}>WhatsApp Connected!</h2>
            <p style={{ color: 'var(--muted)' }}>Nexus AI is ready to receive messages.</p>
          </div>
        ) : status === 'connecting' ? (
          <div style={{ padding: 40 }}>
            <div style={{ fontSize: 40, marginBottom: 16 }}>⏳</div>
            <h2 style={{ color: 'var(--neon3)', marginBottom: 8 }}>Initializing Engine...</h2>
          </div>
        ) : (
          <>
            <div style={{ display: 'flex', gap: 8, justifyContent: 'center', marginBottom: 24, marginTop: 16 }}>
              <button className={`btn ${activeTab === 'qr' ? 'btn-neon' : 'btn-purple'}`} 
                onClick={() => setActiveTab('qr')}>📷 QR Code</button>
              <button className={`btn ${activeTab === 'pair' ? 'btn-neon' : 'btn-purple'}`} 
                onClick={() => setActiveTab('pair')}>🔢 Pairing Code</button>
            </div>

            {activeTab === 'qr' && (
              <div style={{ padding: 20 }}>
                {qrCode ? (
                  <div style={{ background: '#fff', padding: 16, borderRadius: 12, display: 'inline-block' }}>
                    <img src={qrCode} alt="WhatsApp QR Code" width={256} height={256} />
                  </div>
                ) : (
                  <div style={{ color: 'var(--muted)', padding: 40 }}>Waiting for QR Code...</div>
                )}
                <p style={{ fontSize: 12, color: 'var(--muted)', marginTop: 16 }}>
                  Open WhatsApp on your phone &gt; Linked Devices &gt; Link a Device
                </p>
              </div>
            )}

            {activeTab === 'pair' && (
              <div style={{ padding: 20 }}>
                {pairingCode ? (
                  <div>
                    <p style={{ color: 'var(--muted)', marginBottom: 12 }}>Enter this code in your WhatsApp notification:</p>
                    <div style={{ 
                      fontSize: 48, fontWeight: 'bold', color: 'var(--neon)', 
                      letterSpacing: '0.2em', fontFamily: 'JetBrains Mono',
                      background: 'var(--surface2)', padding: '20px', borderRadius: 12
                    }}>
                      {pairingCode}
                    </div>
                  </div>
                ) : (
                  <div>
                    <div className="input-group" style={{ maxWidth: 300, margin: '0 auto' }}>
                      <input 
                        className="input-field" 
                        placeholder="e.g. 62812345678" 
                        value={phone} 
                        onChange={e => setPhone(e.target.value)}
                        style={{ textAlign: 'center', fontSize: 16 }}
                      />
                    </div>
                    <button className="btn btn-neon" onClick={requestPairingCode} disabled={loading || !phone} style={{ marginTop: 16 }}>
                      {loading ? 'REQUESTING...' : 'GET PAIRING CODE'}
                    </button>
                    <p style={{ fontSize: 11, color: 'var(--muted)', marginTop: 16 }}>
                      Include country code (e.g. 62 for Indonesia). No + symbol.
                    </p>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
