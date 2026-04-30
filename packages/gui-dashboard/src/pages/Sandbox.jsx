import { useState } from 'react'

export default function SandboxPage() {
  const [file, setFile] = useState(null)
  const [scanning, setScanning] = useState(false)
  const [result, setResult] = useState(null)
  const [hashInput, setHashInput] = useState('')
  const [activeTab, setActiveTab] = useState('scanner')

  const handleScan = async () => {
    if (!file) return
    setScanning(true)
    setResult(null)

    // Simulate scan
    setTimeout(() => {
      setResult({
        filename: file.name,
        filesize: `${(file.size / 1024).toFixed(1)} KB`,
        md5: 'a1b2c3d4e5f6789012345678abcdef01',
        sha256: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        yara_matches: [],
        risk_level: 'clean',
        risk_score: 0,
        verdict: '✅ CLEAN — No malware detected',
      })
      setScanning(false)
    }, 2000)
  }

  return (
    <>
      <div className="tabs">
        <button className={`tab ${activeTab==='scanner'?'active':''}`}
          onClick={()=>setActiveTab('scanner')}>🔬 YARA Scanner</button>
        <button className={`tab ${activeTab==='honeypot'?'active':''}`}
          onClick={()=>setActiveTab('honeypot')}>🍯 Honeypot Logs</button>
      </div>

      {activeTab === 'scanner' && (
        <>
          <div className="panel">
            <h3>🔬 Malware Sandbox</h3>
            <p style={{fontSize:12,color:'var(--muted)',marginBottom:16}}>
              Upload file untuk di-scan dengan YARA rules (Forge, Malpedia, Yaraify) + Imphash analysis
            </p>
            <div style={{border:'2px dashed var(--border)',borderRadius:8,padding:32,textAlign:'center',marginBottom:16, background:'var(--surface2)'}}>
              <input type="file" onChange={e=>setFile(e.target.files[0])} style={{display:'none'}} id="fileInput" />
              <label htmlFor="fileInput" style={{cursor:'pointer',color:'var(--text)',fontSize:13, fontWeight:500}}>
                {file ? `📎 ${file.name} (${(file.size/1024).toFixed(1)} KB)` : '📂 Click to select file or drag & drop'}
              </label>
            </div>
            <button className="btn btn-neon" onClick={handleScan} disabled={scanning || !file}>
              {scanning ? '⏳ Scanning...' : '🔬 Scan File'}
            </button>
          </div>

          <div className="panel">
            <h3>🔍 Hash Lookup</h3>
            <div className="input-group">
              <input className="input-field" value={hashInput} onChange={e=>setHashInput(e.target.value)}
                placeholder="Enter MD5 / SHA256 hash" />
              <button className="btn btn-blue">🔍 Lookup</button>
            </div>
            <p style={{fontSize:11,color:'var(--muted)'}}>Check against VirusTotal, MalwareBazaar, Yaraify</p>
          </div>

          {result && (
            <div className="panel">
              <h3>📊 Scan Result</h3>
              <div className="term">
    <span className="c">$ yara-scan {result.filename}</span>{'\n\n'}
    <span className="g">Filename  : {result.filename}</span>{'\n'}
    <span className="g">Size      : {result.filesize}</span>{'\n'}
    <span className="g">MD5       : {result.md5}</span>{'\n'}
    <span className="g">SHA256    : {result.sha256}</span>{'\n\n'}
    <span className="c">YARA Matches: {result.yara_matches.length}</span>{'\n'}
    <span className="c">Risk Score : {result.risk_score}/10</span>{'\n'}
    <span className="c">Risk Level : </span><span className={result.risk_level==='clean'?'g':'r'}>{result.risk_level.toUpperCase()}</span>{'\n\n'}
    <span className="g">{result.verdict}</span>
              </div>
            </div>
          )}
        </>
      )}

      {activeTab === 'honeypot' && (
        <div className="panel">
          <h3>🍯 Honeypot Status & Logs</h3>
          <p style={{fontSize:12,color:'var(--muted)',marginBottom:24}}>
            Monitoring file canary untuk mendeteksi ancaman Ransomware atau unauthorized access.
          </p>
          <table className="data-table">
            <thead><tr><th>Canary File</th><th>Status</th><th>Last Check</th><th>Actions</th></tr></thead>
            <tbody>
              {['important_passwords.xlsx','bitcoin_wallet_backup.dat','company_financials_2025.pdf','employee_database.csv','admin_credentials.txt'].map((f,i)=>(
                <tr key={i}>
                  <td style={{fontFamily:'JetBrains Mono',fontSize:12}}>{f}</td>
                  <td><span className="badge badge-green">INTACT</span></td>
                  <td style={{fontSize:12,color:'var(--muted)'}}>Just now</td>
                  <td><button className="btn" style={{padding:'4px 8px', fontSize:11}}>View Logs</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  )
}
