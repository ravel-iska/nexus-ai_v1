export default function Topbar({ title, icon }) {
  return (
    <div className="topbar">
      <h2>{icon} {title}</h2>
      <div className="topbar-actions">
        <span className="badge badge-green">SECURED</span>
        <span className="badge badge-blue">v3.0</span>
      </div>
    </div>
  )
}
