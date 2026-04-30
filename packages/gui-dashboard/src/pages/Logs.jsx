import { useState } from 'react'

const DEMO_LOGS = [
  { ts: '14:31:02.341', level: 'INFO', source: 'orchestrator', msg: 'Task classified: search (confidence: 0.92)' },
  { ts: '14:31:02.123', level: 'INFO', source: 'nexus_agent', msg: 'Generating response via Ollama (nexus3:8b)' },
  { ts: '14:30:55.890', level: 'INFO', source: 'skill_loader', msg: 'Executed skill: osint-hunter → !recon example.com' },
  { ts: '14:30:41.567', level: 'WARN', source: 'nexus_agent', msg: 'Ollama timeout after 30s, retry 1/3' },
  { ts: '14:30:41.201', level: 'INFO', source: 'openrouter', msg: 'Fallback to cloud LLM: gpt-4o-mini ($0.0012)' },
  { ts: '14:30:12.456', level: 'INFO', source: 'blockchain', msg: 'BTC price alert: $67,234 (+2.4% 24h)' },
  { ts: '14:29:58.789', level: 'INFO', source: 'yara_scanner', msg: 'File scan complete: suspect.pdf → CLEAN (0 matches)' },
  { ts: '14:29:30.123', level: 'INFO', source: 'downloader', msg: 'Downloaded: amazing_video.mp4 (45.2MB, 1080p)' },
  { ts: '14:29:01.567', level: 'ERROR', source: 'wa_client', msg: 'Connection lost, reconnecting...' },
  { ts: '14:28:45.890', level: 'INFO', source: 'memory', msg: 'Knowledge base updated: +3 documents (total: 12,847)' },
  { ts: '14:28:30.234', level: 'INFO', source: 'personality', msg: 'Emotion state: EXCITED → user showed enthusiasm' },
  { ts: '14:28:12.678', level: 'DEBUG', source: 'rate_limit', msg: 'User 628xxx: 12/60 requests (20% of limit)' },
]

export default function LogsPage() {
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')

  const filtered = DEMO_LOGS.filter(log => {
    if (filter !== 'all' && log.level !== filter) return false
    if (search && !log.msg.toLowerCase().includes(search.toLowerCase()) && !log.source.includes(search.toLowerCase())) return false
    return true
  })

  const levelColor = { INFO: 'badge-blue', WARN: 'badge-yellow', ERROR: 'badge-red', DEBUG: 'badge-green' }

  return (
    <>
      <div style={{display:'flex',gap:8,marginBottom:16,flexWrap:'wrap'}}>
        {['all','INFO','WARN','ERROR','DEBUG'].map(l => (
          <button key={l} className={`btn ${filter===l?'btn-neon':'btn-purple'}`}
            onClick={()=>setFilter(l)} style={{padding:'6px 12px',fontSize:10}}>
            {l === 'all' ? '📋 ALL' : l}
          </button>
        ))}
        <input className="input-field" value={search} onChange={e=>setSearch(e.target.value)}
          placeholder="🔍 Filter logs..." style={{maxWidth:250}} />
      </div>

      <div className="panel">
        <h3>📋 System Logs ({filtered.length})</h3>
        <table className="data-table">
          <thead><tr><th>Timestamp</th><th>Level</th><th>Source</th><th>Message</th></tr></thead>
          <tbody>
            {filtered.map((log, i) => (
              <tr key={i}>
                <td style={{fontFamily:'JetBrains Mono',fontSize:10,color:'var(--dim)',whiteSpace:'nowrap'}}>{log.ts}</td>
                <td><span className={`badge ${levelColor[log.level]}`}>{log.level}</span></td>
                <td style={{fontFamily:'JetBrains Mono',fontSize:11,color:'var(--neon4)'}}>{log.source}</td>
                <td style={{fontSize:12}}>{log.msg}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
