import { useState, useRef, useEffect } from 'react'

const API = import.meta.env.VITE_AI_API_URL || 'http://localhost:8000'

export default function Chat() {
  const [messages, setMessages] = useState([
    { role: 'bot', text: '🤖 Halo! Saya Nexus v3.0. Ada yang bisa saya bantu?\n\nKetik pesan apapun, atau coba:\n• !scan <domain>\n• !download <url>\n• !crypto btc\n• !sentimen <teks>', time: new Date().toLocaleTimeString() },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: userMsg, time: new Date().toLocaleTimeString() }])
    setLoading(true)

    try {
      const resp = await fetch(`${API}/api/v1/agent/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'dashboard', session_id: 'gui', message: userMsg }),
      })
      const data = await resp.json()
      setMessages(prev => [...prev, {
        role: 'bot', text: data.response || data.error || 'Tidak ada respons.',
        time: new Date().toLocaleTimeString(), agent: data.agent_used, taskType: data.task_type,
      }])
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'bot', text: `⚠️ Tidak bisa terhubung ke backend.\n\nPastikan:\n1. API backend berjalan: uvicorn main:app --port 8000\n2. Ollama berjalan: ollama serve\n\nError: ${e.message}`,
        time: new Date().toLocaleTimeString(),
      }])
    }
    setLoading(false)
  }

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`msg ${msg.role}`}>
            <div style={{whiteSpace:'pre-wrap'}}>{msg.text}</div>
            <div className="meta">
              {msg.time}
              {msg.agent && <> · <span className="badge badge-blue">{msg.agent}</span></>}
              {msg.taskType && <> · <span className="badge badge-green">{msg.taskType}</span></>}
            </div>
          </div>
        ))}
        {loading && <div className="msg bot"><em style={{color:'var(--neon)'}}>🤖 Thinking...</em></div>}
        <div ref={bottomRef} />
      </div>
      <div className="chat-input-area">
        <input className="chat-input" value={input} onChange={e=>setInput(e.target.value)}
          onKeyDown={e=>e.key==='Enter'&&sendMessage()} placeholder="Ketik pesan ke Nexus..."
          disabled={loading} />
        <button className="btn btn-neon" onClick={sendMessage} disabled={loading}>Send</button>
      </div>
    </div>
  )
}
