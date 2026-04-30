import { useState } from 'react'

export default function DownloaderPage() {
  const [url, setUrl] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState('video')

  const download = async () => {
    if (!url) return
    setLoading(true)
    const entry = { url, mode, status: 'downloading', time: new Date().toLocaleTimeString() }
    setResults(prev => [entry, ...prev])

    try {
      const aiApi = import.meta.env.VITE_AI_API_URL || 'http://localhost:8000'
      const resp = await fetch(`${aiApi}/api/v1/downloader`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, audio_only: mode === 'music' }),
      })
      const data = await resp.json()
      setResults(prev => prev.map((r, i) => i === 0 ? {
        ...r, status: data.status || 'done',
        filename: data.filename, size: data.filesize,
        title: data.title,
      } : r))
    } catch (e) {
      setResults(prev => prev.map((r, i) => i === 0 ? {
        ...r, status: 'error', error: e.message,
      } : r))
    }
    setUrl('')
    setLoading(false)
  }

  return (
    <>
      <div className="panel">
        <h3>⬇️ Media Downloader</h3>
        <div style={{display:'flex',gap:8,marginBottom:12}}>
          <button className={`btn ${mode==='video'?'btn-neon':'btn-purple'}`} onClick={()=>setMode('video')}>🎬 Video</button>
          <button className={`btn ${mode==='music'?'btn-neon':'btn-purple'}`} onClick={()=>setMode('music')}>🎵 Music</button>
        </div>
        <div className="input-group">
          <input className="input-field" value={url} onChange={e=>setUrl(e.target.value)}
            placeholder="Paste URL (YouTube, TikTok, Instagram, dll)" onKeyDown={e=>e.key==='Enter'&&download()} />
          <button className="btn btn-neon" onClick={download} disabled={loading}>
            {loading ? '⏳ Downloading...' : '⬇️ Download'}
          </button>
        </div>
        <p style={{fontSize:11,color:'var(--muted)'}}>
          Mendukung 1000+ situs via yt-dlp. Mode: {mode === 'video' ? 'Video MP4' : 'Audio MP3 192kbps'}
        </p>
      </div>

      {results.length > 0 && (
        <div className="panel">
          <h3>📦 Download History</h3>
          <table className="data-table">
            <thead><tr><th>Time</th><th>URL</th><th>Mode</th><th>Status</th><th>File</th></tr></thead>
            <tbody>
              {results.map((r, i) => (
                <tr key={i}>
                  <td style={{fontFamily:'JetBrains Mono',fontSize:11}}>{r.time}</td>
                  <td style={{maxWidth:200,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{r.url}</td>
                  <td><span className="badge badge-blue">{r.mode}</span></td>
                  <td>
                    <span className={`badge ${r.status==='done'||r.status==='success'?'badge-green':r.status==='error'?'badge-red':'badge-yellow'}`}>
                      {r.status}
                    </span>
                  </td>
                  <td style={{fontSize:11}}>{r.filename || r.error || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
