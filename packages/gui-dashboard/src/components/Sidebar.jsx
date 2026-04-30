export default function Sidebar({ pages, active, onNavigate, onLogout }) {
  return (
    <div className="sidebar">
      <div className="sidebar-brand">
        <h1>⬡ NEXUS v3</h1>
        <p>AI Agent Dashboard</p>
      </div>
      <nav className="sidebar-nav">
        {Object.entries(pages).map(([key, { label, icon }]) => (
          <div key={key} className={`nav-item ${active === key ? 'active' : ''}`}
            onClick={() => onNavigate(key)}>
            <span className="icon">{icon}</span>
            <span>{label}</span>
          </div>
        ))}
      </nav>
      <div style={{ padding: '0 20px 20px' }}>
        <button className="btn btn-pink" style={{ width: '100%', fontSize: 10 }} onClick={onLogout}>
          🔓 LOGOUT KEY
        </button>
      </div>
      <div className="sidebar-status">
        <div><span className="status-dot online" /> API Backend</div>
        <div style={{ marginTop: 6 }}><span className="status-dot online" /> Ollama LLM</div>
        <div style={{ marginTop: 6 }}><span className="status-dot offline" /> WA Client</div>
      </div>
    </div>
  )
}
