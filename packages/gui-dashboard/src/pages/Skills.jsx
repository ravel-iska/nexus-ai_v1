import { useState } from 'react'

const DEMO_SKILLS = [
  { name: 'osint-hunter', version: '2.1.0', runtime: 'python', commands: ['!osint','!recon','!whois'], status: 'active', permissions: ['network'] },
  { name: 'crypto-tracker', version: '1.5.0', runtime: 'python', commands: ['!crypto','!wallet','!portfolio'], status: 'active', permissions: ['network'] },
  { name: 'media-downloader', version: '3.0.0', runtime: 'python', commands: ['!download','!music','!batch'], status: 'active', permissions: ['network','filesystem'] },
  { name: 'document-tools', version: '1.2.0', runtime: 'python', commands: ['!pdf','!excel','!convert'], status: 'active', permissions: ['filesystem'] },
  { name: 'social-scraper', version: '2.0.0', runtime: 'python', commands: ['!ig','!tiktok','!twitter'], status: 'active', permissions: ['network'] },
  { name: 'malware-sandbox', version: '1.0.0', runtime: 'python', commands: ['!scan','!yara','!honeypot'], status: 'active', permissions: ['system','filesystem'] },
]

export default function SkillsPage() {
  const [skills, setSkills] = useState(DEMO_SKILLS)
  const [installUrl, setInstallUrl] = useState('')

  const toggleSkill = (name) => {
    setSkills(prev => prev.map(s =>
      s.name === name ? { ...s, status: s.status === 'active' ? 'disabled' : 'active' } : s
    ))
  }

  const reloadSkill = (name) => {
    setSkills(prev => prev.map(s =>
      s.name === name ? { ...s, status: 'reloading' } : s
    ))
    setTimeout(() => {
      setSkills(prev => prev.map(s =>
        s.name === name ? { ...s, status: 'active' } : s
      ))
    }, 1500)
  }

  return (
    <>
      <div className="panel">
        <h3>📦 Install New Skill</h3>
        <div className="input-group">
          <input className="input-field" value={installUrl} onChange={e=>setInstallUrl(e.target.value)}
            placeholder="github:user/skill-name or file path" />
          <button className="btn btn-neon">⬇️ Install</button>
        </div>
      </div>

      <div className="panel">
        <h3>⚡ Loaded Skills ({skills.filter(s=>s.status==='active').length}/{skills.length})</h3>
        <table className="data-table">
          <thead><tr><th>Name</th><th>Version</th><th>Runtime</th><th>Commands</th><th>Permissions</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            {skills.map(s => (
              <tr key={s.name}>
                <td style={{fontFamily:'JetBrains Mono',fontSize:12,color:'var(--neon)'}}>{s.name}</td>
                <td><span className="badge badge-blue">v{s.version}</span></td>
                <td><span className="badge badge-green">{s.runtime}</span></td>
                <td style={{fontSize:11}}>{s.commands.join(', ')}</td>
                <td>{s.permissions.map(p=><span key={p} className={`badge ${p==='system'?'badge-red':'badge-yellow'}`} style={{marginRight:4}}>{p}</span>)}</td>
                <td><span className={`badge ${s.status==='active'?'badge-green':s.status==='reloading'?'badge-yellow':'badge-red'}`}>{s.status}</span></td>
                <td>
                  <button className="btn btn-blue" style={{padding:'4px 8px',fontSize:10,marginRight:4}} onClick={()=>reloadSkill(s.name)}>🔄</button>
                  <button className="btn btn-pink" style={{padding:'4px 8px',fontSize:10}} onClick={()=>toggleSkill(s.name)}>
                    {s.status==='active'?'⏸':'▶'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
