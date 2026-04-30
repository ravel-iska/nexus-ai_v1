import { useState, useEffect } from 'react'

export default function CryptoPage() {
  const [coins, setCoins] = useState([])
  const [loading, setLoading] = useState(true)
  const [fgi, setFgi] = useState(null)
  const [search, setSearch] = useState('')
  const [activeTab, setActiveTab] = useState('market')

  useEffect(() => { fetchData() }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [marketResp, fgiResp] = await Promise.all([
        fetch('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=20&sparkline=false&price_change_percentage=24h,7d'),
        fetch('https://api.alternative.me/fng/?limit=1'),
      ])
      setCoins(await marketResp.json())
      const fgiData = await fgiResp.json()
      setFgi(fgiData.data?.[0] || null)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }

  const filtered = coins.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.symbol.toLowerCase().includes(search.toLowerCase())
  )

  const fgiColor = fgi ? (fgi.value < 25 ? 'var(--neon2)' : fgi.value < 50 ? 'var(--neon3)' : fgi.value < 75 ? 'var(--green)' : 'var(--neon)') : 'var(--muted)'

  return (
    <>
      <div className="tabs">
        <button className={`tab ${activeTab==='market'?'active':''}`}
          onClick={()=>setActiveTab('market')}>📈 Market Overview</button>
        <button className={`tab ${activeTab==='alerts'?'active':''}`}
          onClick={()=>setActiveTab('alerts')}>🔔 Price Alerts</button>
      </div>

      {activeTab === 'market' && (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="label">Fear & Greed</div>
              <div className="value" style={{color:fgiColor}}>{fgi?.value || '—'}</div>
              <div className="sub">{fgi?.value_classification || 'Loading...'}</div>
            </div>
            <div className="stat-card">
              <div className="label">Coins Tracked</div>
              <div className="value">{coins.length}</div>
              <div className="sub">Top by market cap</div>
            </div>
            <div className="stat-card">
              <div className="label">Data Source</div>
              <div className="value" style={{fontSize:16,color:'var(--green)'}}>LIVE</div>
              <div className="sub">CoinGecko API</div>
            </div>
          </div>

          <div className="panel">
            <h3>📈 Market Overview</h3>
            <div className="input-group">
              <input className="input-field" value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search coin..." />
              <button className="btn btn-neon" onClick={fetchData} disabled={loading}>🔄 Refresh</button>
            </div>
            {loading ? <p style={{color:'var(--muted)'}}>Loading market data...</p> : (
              <table className="data-table">
                <thead>
                  <tr><th>#</th><th>Coin</th><th>Price</th><th>24h</th><th>7d</th><th>Market Cap</th><th>Volume</th></tr>
                </thead>
                <tbody>
                  {filtered.map(c => (
                    <tr key={c.id}>
                      <td>{c.market_cap_rank}</td>
                      <td style={{display:'flex',alignItems:'center',gap:8}}>
                        <img src={c.image} alt="" width={18} height={18} style={{borderRadius:4}} />
                        <span>{c.symbol.toUpperCase()}</span>
                      </td>
                      <td style={{fontFamily:'JetBrains Mono'}}>${c.current_price?.toLocaleString()}</td>
                      <td style={{color:c.price_change_percentage_24h>=0?'var(--green)':'var(--neon2)',fontFamily:'JetBrains Mono',fontSize:12}}>
                        {c.price_change_percentage_24h?.toFixed(2)}%
                      </td>
                      <td style={{color:(c.price_change_percentage_7d_in_currency||0)>=0?'var(--green)':'var(--neon2)',fontFamily:'JetBrains Mono',fontSize:12}}>
                        {c.price_change_percentage_7d_in_currency?.toFixed(2) || '—'}%
                      </td>
                      <td style={{fontSize:11}}>${(c.market_cap/1e9).toFixed(1)}B</td>
                      <td style={{fontSize:11}}>${(c.total_volume/1e9).toFixed(1)}B</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}

      {activeTab === 'alerts' && (
        <div className="panel">
          <h3>🔔 WhatsApp Price Alerts</h3>
          <p style={{fontSize:12,color:'var(--muted)',marginBottom:24}}>
            Manage threshold alerts that will be sent automatically to your WhatsApp.
          </p>
          
          <div className="input-group" style={{maxWidth: 500}}>
            <select className="input-field" style={{maxWidth: 120}}>
              <option>BTC</option>
              <option>ETH</option>
              <option>SOL</option>
            </select>
            <select className="input-field" style={{maxWidth: 120}}>
              <option>{`>`} Above</option>
              <option>{`<`} Below</option>
            </select>
            <input className="input-field" placeholder="Target Price (USD)" type="number" />
            <button className="btn btn-neon">Add Alert</button>
          </div>

          <table className="data-table" style={{marginTop: 24}}>
            <thead><tr><th>Asset</th><th>Condition</th><th>Target Price</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
              <tr>
                <td style={{fontWeight:600}}>BTC</td>
                <td>{`<`} Below</td>
                <td style={{fontFamily:'JetBrains Mono'}}>$60,000</td>
                <td><span className="badge badge-green">Active</span></td>
                <td><button className="btn" style={{padding:'4px 8px', fontSize:11}}>Delete</button></td>
              </tr>
              <tr>
                <td style={{fontWeight:600}}>ETH</td>
                <td>{`>`} Above</td>
                <td style={{fontFamily:'JetBrains Mono'}}>$4,000</td>
                <td><span className="badge badge-green">Active</span></td>
                <td><button className="btn" style={{padding:'4px 8px', fontSize:11}}>Delete</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
