import React, { useState } from 'react'
import { motion } from 'framer-motion'

export default function App() {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText('npm install -g nexus-agent\nnexus-agent run')
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <>
      <div className="bg-grid"></div>
      <div className="glow-orb"></div>

      <div className="container">
        <nav>
          <div className="brand">
            ⬡ <span>NEXUS</span>
          </div>
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#docs">Documentation</a>
            <a href="https://github.com" target="_blank" rel="noreferrer">GitHub</a>
          </div>
        </nav>

        <section className="hero">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <div className="badge">v3.0 PRODUCTION READY</div>
            <h1>The Ultimate<br /><span>AI Agent Ecosystem</span></h1>
            <p>
              Nexus is a powerful, self-hosted WhatsApp AI agent with a built-in GUI dashboard, OSINT tools, live crypto tracking, and a secure CLI workflow.
            </p>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, y: 40 }} 
            animate={{ opacity: 1, y: 0 }} 
            transition={{ duration: 0.6, delay: 0.2 }}
            className="terminal-window"
          >
            <div className="term-header">
              <div className="term-dots">
                <div className="term-dot r"></div>
                <div className="term-dot y"></div>
                <div className="term-dot g"></div>
              </div>
              <button className="copy-btn" onClick={handleCopy}>
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <div className="term-body">
              <div className="comment"># 1. Install Nexus Agent globally</div>
              <div className="cmd">
                <span className="prompt">❯</span>
                <span className="command">npm install -g nexus-agent</span>
              </div>
              
              <div className="comment" style={{ marginTop: 24 }}># 2. Start the Engine & GUI Dashboard</div>
              <div className="cmd">
                <span className="prompt">❯</span>
                <span className="command">nexus-agent run</span>
              </div>
              <div className="output">
                <span style={{ color: '#3fb950' }}>✅ API Key Generated: hms_09a957...</span><br/>
                <span style={{ color: '#58a6ff' }}>🚀 Dashboard running at: http://localhost:3100/</span>
              </div>
            </div>
          </motion.div>
        </section>

        {/* COMPREHENSIVE DOCUMENTATION SECTION */}
        <section id="docs" className="docs-section">
          <div className="docs-layout">
            <aside className="docs-sidebar">
              <h3>On this page</h3>
              <ul>
                <li><a href="#doc-intro">Introduction</a></li>
                <li><a href="#doc-prereq">Prerequisites</a></li>
                <li><a href="#doc-install">Installation</a></li>
                <li><a href="#doc-security">Security & API Keys</a></li>
                <li><a href="#doc-whatsapp">WhatsApp Integration</a></li>
                <li><a href="#doc-commands">CLI Commands</a></li>
                <li><a href="#doc-architecture">Architecture</a></li>
              </ul>
            </aside>
            
            <div className="docs-content">
              <h2 id="doc-intro">Documentation</h2>
              <p>Welcome to the official documentation for <strong>Nexus Agent v3.0</strong>. Nexus is not just a WhatsApp bot; it is a full-fledged <em>Enterprise AI Agent Ecosystem</em>.</p>
              
              <h3 id="doc-prereq">1. Prerequisites</h3>
              <p>Before installing Nexus, ensure your server or local machine meets the following requirements:</p>
              <ul>
                <li><strong>Node.js v18.0.0 or higher</strong>: Required for the WA Client and GUI Dashboard.</li>
                <li><strong>Python 3.10+</strong>: Required for the FastAPI AI Backend, LangGraph, and OSINT tools.</li>
                <li><strong>PostgreSQL</strong>: (Optional but recommended) For persistent memory and database storage.</li>
                <li><strong>Ollama</strong>: If you plan to run local LLMs (Llama 3, Mistral) instead of using Cloud APIs (OpenAI/Anthropic).</li>
              </ul>

              <h3 id="doc-install">2. Installation</h3>
              <p>Nexus is built as a global NPM package. This allows you to install it once and run it anywhere on your machine.</p>
              <div className="code-block">
                <code>npm install -g nexus-agent</code>
              </div>
              <p>To verify the installation, run:</p>
              <div className="code-block">
                <code>nexus-agent status</code>
              </div>

              <h3 id="doc-security">3. Security & API Keys</h3>
              <p>Unlike standard bots, Nexus exposes a powerful GUI Dashboard that can control the agent remotely. To prevent unauthorized access, Nexus uses a strict API Key system.</p>
              <ul>
                <li><strong>Auto-generation</strong>: When you run <code>nexus-agent run</code> for the very first time, the CLI will automatically generate a Master Key (e.g., <code>hms_...</code>).</li>
                <li><strong>Secure Storage</strong>: Keys are stored outside your project directory in <code>~/.nexus-agent/api-keys.json</code> to prevent accidental commits to GitHub.</li>
                <li><strong>Usage</strong>: When opening the GUI Dashboard (<code>http://localhost:3100</code>), you <strong>must</strong> input this key. Without it, the dashboard is completely locked.</li>
              </ul>

              <h3 id="doc-whatsapp">4. WhatsApp Integration</h3>
              <p>Nexus utilizes the `@whiskeysockets/baileys` library under the hood. There are two ways to connect your WhatsApp account:</p>
              <div className="info-box">
                <h4>QR Code Scanning</h4>
                <p>Standard method. Open WhatsApp on your phone &gt; Linked Devices &gt; Link a Device, and scan the QR code displayed on the Nexus Dashboard.</p>
              </div>
              <div className="info-box">
                <h4>Pairing Code (Recommended for VPS)</h4>
                <p>If you are running Nexus on a headless VPS where scanning a QR is difficult, simply input your bot's phone number into the Dashboard, and Nexus will generate an 8-digit Pairing Code. Enter this code into your WhatsApp app to link instantly.</p>
              </div>

              <h3 id="doc-commands">5. CLI Commands Reference</h3>
              <p>The <code>nexus-agent</code> CLI is your main control plane:</p>
              <table className="docs-table">
                <thead>
                  <tr>
                    <th>Command</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><code>nexus-agent run</code></td>
                    <td>Starts the Production GUI Dashboard on port 3100 and spawns the WA engine.</td>
                  </tr>
                  <tr>
                    <td><code>nexus-agent keygen [label]</code></td>
                    <td>Generates a new Master API Key manually (e.g., for sharing with a co-admin).</td>
                  </tr>
                  <tr>
                    <td><code>nexus-agent keys</code></td>
                    <td>Lists all active and revoked keys.</td>
                  </tr>
                  <tr>
                    <td><code>nexus-agent revoke &lt;key&gt;</code></td>
                    <td>Instantly revokes access for a specific API Key. Any active sessions using it will be terminated.</td>
                  </tr>
                </tbody>
              </table>

              <h3 id="doc-architecture">6. Architecture</h3>
              <p>Nexus uses a microservices architecture to ensure high availability:</p>
              <ul>
                <li><strong>Port 3100 (GUI)</strong>: Static React application served via an Express Production Server.</li>
                <li><strong>Port 3101 (WA Client)</strong>: The WhatsApp engine. Communicates with the GUI via SSE (Server-Sent Events) for real-time connection status.</li>
                <li><strong>Port 8000 (AI Backend)</strong>: FastAPI server handling LangGraph orchestration, OSINT execution, and Crypto tracking.</li>
                <li><strong>Port 5000 (Docs)</strong>: This public landing page.</li>
              </ul>

            </div>
          </div>
        </section>

        <footer style={{ textAlign: 'center', padding: '40px 0', borderTop: '1px solid var(--border)', color: 'var(--muted)', fontSize: 13 }}>
          &copy; 2026 Nexus AI Agent. Built with React & Vite.
        </footer>
      </div>
    </>
  )
}
