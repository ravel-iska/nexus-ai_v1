import { useState, useEffect } from 'react'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalMessages: 1247, activeUsers: 38, skillsLoaded: 12,
    uptime: '14h 32m', tokensUsed: 842300, errorRate: '0.2%',
  })
  const [recentLogs, setRecentLogs] = useState([
    { time: '14:31:02', type: 'chat', msg: 'User 628xxx mengirim pesan', status: 'ok' },
    { time: '14:30:55', type: 'skill', msg: 'Skill osint-hunter executed', status: 'ok' },
    { time: '14:30:41', type: 'error', msg: 'Ollama timeout (retry 1/3)', status: 'warn' },
    { time: '14:30:12', type: 'crypto', msg: 'BTC price alert triggered', status: 'ok' },
    { time: '14:29:58', type: 'scan', msg: 'YARA scan completed: clean', status: 'ok' },
    { time: '14:29:30', type: 'download', msg: 'Video downloaded: 45.2MB', status: 'ok' },
  ])

  return (
    <>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="label">Total Messages</div>
          <div className="value">{stats.totalMessages.toLocaleString()}</div>
          <div className="sub">Last 24 hours</div>
        </div>
        <div className="stat-card">
          <div className="label">Active Users</div>
          <div className="value">{stats.activeUsers}</div>
          <div className="sub">Currently online</div>
        </div>
        <div className="stat-card">
          <div className="label">Skills Loaded</div>
          <div className="value">{stats.skillsLoaded}</div>
          <div className="sub">Hot-reload ready</div>
        </div>
        <div className="stat-card">
          <div className="label">Uptime</div>
          <div className="value">{stats.uptime}</div>
          <div className="sub">Since last restart</div>
        </div>
        <div className="stat-card">
          <div className="label">Tokens Used</div>
          <div className="value">{(stats.tokensUsed/1000).toFixed(0)}K</div>
          <div className="sub">Today (Ollama + Cloud)</div>
        </div>
        <div className="stat-card">
          <div className="label">Error Rate</div>
          <div className="value" style={{color:'var(--green)'}}>{stats.errorRate}</div>
          <div className="sub">Last 24 hours</div>
        </div>
      </div>

      <div className="panel-grid">
        <div className="panel">
          <h3>📋 Recent Activity</h3>
          <table className="data-table">
            <thead><tr><th>Time</th><th>Type</th><th>Event</th><th>Status</th></tr></thead>
            <tbody>
              {recentLogs.map((log, i) => (
                <tr key={i}>
                  <td style={{fontFamily:'JetBrains Mono',fontSize:11}}>{log.time}</td>
                  <td><span className={`badge badge-${log.status==='warn'?'yellow':'blue'}`}>{log.type}</span></td>
                  <td>{log.msg}</td>
                  <td><span className={`badge badge-${log.status==='warn'?'yellow':'green'}`}>{log.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="panel">
          <h3>🖥️ System Health</h3>
          <div className="term">
<span className="c">$ nexus status</span>{'\n'}
<span className="g">✅ API Backend    → Running (port 8000)</span>{'\n'}
<span className="g">✅ Redis          → Connected (6379)</span>{'\n'}
<span className="g">✅ PostgreSQL     → Connected (5432)</span>{'\n'}
<span className="g">✅ Ollama         → Running (11434)</span>{'\n'}
<span className="y">⚠️  WA Client      → Disconnected</span>{'\n'}
<span className="g">✅ ChromaDB       → 12,847 vectors</span>{'\n'}
<span className="g">✅ Neo4j          → 3,241 entities</span>{'\n'}
{'\n'}
<span className="c">Memory: 2.4GB / 8GB | CPU: 12% | GPU: 34%</span>
          </div>
        </div>
      </div>
    </>
  )
}
