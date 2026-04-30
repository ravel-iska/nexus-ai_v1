// ═══════════════════════════════════════════════════════════════
// SECTIONS RENDER — Sections 01-13
// ═══════════════════════════════════════════════════════════════
import { sec, modCard, terminal, featureBlock, secCard, phase } from './render.js';
import { MODULES } from './sections.js';

export function renderSections1() {
  let html = '';

  // SEC 01 — Architecture
  html += sec('arch','01','Arsitektur Sistem Nexus v3.0',
    'Monorepo berbasis Turborepo: frontend Vite + backend FastAPI + Node.js WA client, terhubung via REST/WebSocket dengan Docker orchestration.',
    `<div class="arch">
<span class="ng">┌──────────────────────────────────────────────────────────────┐</span>
<span class="ng">│</span>  <span class="nc">NEXUS v3.0 — MONOREPO ARCHITECTURE</span>                        <span class="ng">│</span>
<span class="ng">├──────────────────────────────────────────────────────────────┤</span>
<span class="ng">│</span>                                                              <span class="ng">│</span>
<span class="ng">│</span>  <span class="np">┌─ FRONTEND (Vite + React) ──────────────────────────┐</span>    <span class="ng">│</span>
<span class="ng">│</span>  <span class="np">│</span>  Dashboard · Blueprint · Skill Editor · Charts    <span class="np">│</span>    <span class="ng">│</span>
<span class="ng">│</span>  <span class="np">└───────────────────────┬────────────────────────────┘</span>    <span class="ng">│</span>
<span class="ng">│</span>                          <span class="ny">│ REST / WebSocket</span>                  <span class="ng">│</span>
<span class="ng">│</span>  <span class="nc">┌─ API BACKEND (FastAPI) ┴────────────────────────────┐</span>   <span class="ng">│</span>
<span class="ng">│</span>  <span class="nc">│</span>  JWT Auth · Rate Limit · Celery Workers            <span class="nc">│</span>   <span class="ng">│</span>
<span class="ng">│</span>  <span class="nc">└───┬───────┬───────┬───────┬───────┬───────┬───────┘</span>   <span class="ng">│</span>
<span class="ng">│</span>      <span class="ny">│</span>       <span class="ny">│</span>       <span class="ny">│</span>       <span class="ny">│</span>       <span class="ny">│</span>       <span class="ny">│</span>         <span class="ng">│</span>
<span class="ng">│</span>  <span class="nr">Agents</span>  <span class="no">Skill</span>  <span class="nc">Memory</span>  <span class="np">ML/DL</span>  <span class="ny">Crypto</span>  <span class="ng">Voice</span>      <span class="ng">│</span>
<span class="ng">│</span>      <span class="ny">│</span>       <span class="ny">│</span>       <span class="ny">│</span>       <span class="ny">│</span>       <span class="ny">│</span>       <span class="ny">│</span>         <span class="ng">│</span>
<span class="ng">│</span>  <span class="nr">┌───┴───┐</span> <span class="no">┌───┴──┐</span> <span class="nc">┌──┴──┐</span> <span class="np">┌──┴──┐</span> <span class="ny">┌──┴──┐</span> <span class="ng">┌──┴──┐</span>  <span class="ng">│</span>
<span class="ng">│</span>  <span class="nr">│Nexus │</span> <span class="no">│Plugin│</span> <span class="nc">│Redis│</span> <span class="np">│BERT │</span> <span class="ny">│Web3 │</span> <span class="ng">│Whisp│</span>  <span class="ng">│</span>
<span class="ng">│</span>  <span class="nr">│Cloud  │</span> <span class="no">│Hot-RL│</span> <span class="nc">│PgSQL│</span> <span class="np">│YARA │</span> <span class="ny">│DeFi │</span> <span class="ng">│gTTS │</span>  <span class="ng">│</span>
<span class="ng">│</span>  <span class="nr">└───────┘</span> <span class="no">└──────┘</span> <span class="nc">└─────┘</span> <span class="np">└─────┘</span> <span class="ny">└─────┘</span> <span class="ng">└─────┘</span>  <span class="ng">│</span>
<span class="ng">│</span>                                                              <span class="ng">│</span>
<span class="ng">│</span>  <span class="nr">┌─ WA CLIENT (Baileys) ──────────────────────────────┐</span>    <span class="ng">│</span>
<span class="ng">│</span>  <span class="nr">│</span>  Multi-session · QR Login · Media · Group · Voice  <span class="nr">│</span>    <span class="ng">│</span>
<span class="ng">│</span>  <span class="nr">└────────────────────────────────────────────────────┘</span>    <span class="ng">│</span>
<span class="ng">└──────────────────────────────────────────────────────────────┘</span>
</div>`);

  // SEC 02 — Modules
  const cards = MODULES.map(m => modCard(m)).join('');
  html += sec('modules','02','Module Registry (24 Packages)',
    'Setiap module bersifat modular, bisa di-enable/disable, dan memiliki Docker container sendiri.',
    `<div class="mod-grid">${cards}</div>`);

  // SEC 03 — Error Tracking
  html += sec('error','03','Error Tracking & AI Diagnosis','Sentry-compatible error tracking dengan AI-powered root cause analysis dan auto-fix suggestions.',
    `<div class="error-panel"><div class="error-header"><span class="error-type">⚠ ConnectionRefusedError</span><span class="error-time">2025-01-15 14:32:07 UTC</span></div><div class="error-body"><div class="error-msg">Connection refused: Ollama server at localhost:11434</div><div class="error-trace"><span class="fn">orchestrator.py</span>:<span class="loc">_run_nexus()</span> line <span class="hl">142</span>
  <span class="fn">nexus_agent.py</span>:<span class="loc">generate()</span> line <span class="hl">58</span>
    → <span class="hl">httpx.ConnectError</span>: Connection refused</div></div><div class="error-actions"><button class="btn fix">⚡ AI Auto-Fix</button><button class="btn view">📋 Stack Trace</button><button class="btn send">📧 Notify Admin</button><button class="btn ai">🤖 Ask Nexus</button></div></div>
    ${featureBlock('🤖','AI Debugger','Otomatis analisa error, suggest fix, dan execute perbaikan dengan persetujuan developer.',terminal('AI Diagnosis','<span class="prompt">nexus&gt;</span> <span class="cmd">diagnose --error=ConnectionRefused</span>\n<span class="out">🔍 Analyzing error pattern...</span>\n<span class="ok">✅ Root Cause: Ollama server not running</span>\n<span class="info">💡 Fix: docker-compose up ollama</span>\n<span class="warn">⚠️  Auto-fix requires developer approval</span>'))}`);

  // SEC 04 — Gmail Notification
  html += sec('gmail','04','Multi-Channel Notification Engine','Kirim alert ke Gmail, Telegram, Discord, dan Slack secara otomatis berdasarkan severity.',
    `<div class="gmail-flow"><div class="gf-step"><div class="gf-num">STEP 01</div><h4>🔴 Event Trigger</h4><p>Error/alert/blockchain event terdeteksi oleh sistem</p></div><div class="gf-step"><div class="gf-num">STEP 02</div><h4>🎯 Classify Severity</h4><p>Sistem menentukan level: info, warning, critical</p></div><div class="gf-step"><div class="gf-num">STEP 03</div><h4>📧 Route Channel</h4><p>Critical → Gmail+Telegram, Warning → Slack, Info → Discord</p></div><div class="gf-step"><div class="gf-num">STEP 04</div><h4>✅ Deliver + Log</h4><p>Kirim notifikasi + simpan ke audit trail</p></div></div>`);

  // SEC 05 — Skill Engine
  html += sec('skill','05','Skill Engine & Marketplace','Hot-reload plugin system. Install dari file/GitHub/URL/marketplace tanpa restart bot.',
    `<div class="skill-flow"><h4>⚡ Skill Execution Flow</h4><div class="skill-row"><span class="s-box src">!scan example.com</span><span class="s-arrow">→</span><span class="s-box proc">TaskClassifier</span><span class="s-arrow">→</span><span class="s-box proc">SkillLoader</span><span class="s-arrow">→</span><span class="s-box out">OSINT Engine</span></div><div class="skill-row"><span class="s-box src">!download yt.link</span><span class="s-arrow">→</span><span class="s-box proc">TaskClassifier</span><span class="s-arrow">→</span><span class="s-box proc">SkillLoader</span><span class="s-arrow">→</span><span class="s-box out">yt-dlp Downloader</span></div><div class="skill-row"><span class="s-box src">voice: "cari harga laptop"</span><span class="s-arrow">→</span><span class="s-box proc">Whisper STT</span><span class="s-arrow">→</span><span class="s-box proc">IntentParser</span><span class="s-arrow">→</span><span class="s-box out">Browser Search</span></div></div>
    ${terminal('Skill Management','<span class="prompt">nexus&gt;</span> <span class="cmd">skill install github:user/osint-hunter</span>\n<span class="out">📦 Downloading skill from GitHub...</span>\n<span class="ok">✅ Validated: osint-hunter v2.1.0 (python)</span>\n<span class="ok">✅ Commands registered: !osint, !recon, !whois</span>\n<span class="info">🔄 Hot-reload complete — no restart needed</span>')}`);

  // SEC 06 — Security
  html += sec('security','06','Security & Penetration Suite','Full-stack security: pentest, OSINT, YARA malware scan, SSL check, leak detection. Semua dengan audit log wajib.',
    `<div class="sec-grid">
    ${secCard('sc-r','🔍','Port Scanner (Nmap)','Scan port & service detection',['TCP/UDP port scan','Service version detection','OS fingerprinting','Vulnerability mapping'])}
    ${secCard('sc-p','🕵️','OSINT Engine','Intelligence gathering otomatis',['WHOIS + DNS recon','Subdomain enumeration','Email harvesting','Shodan integration'])}
    ${secCard('sc-n','🔒','SSL & Header Check','Audit keamanan web',['SSL certificate validity','Security headers audit','CSP / HSTS / X-Frame','Missing header alerts'])}
    ${secCard('sc-y','📧','Leak Checker','Cek kebocoran data',['Have I Been Pwned API','Dark web monitoring','Credential exposure','Auto-alert on breach'])}
    ${secCard('sc-b','🛡️','YARA Scanner','Malware detection',['YARA-Forge rules','Malpedia + Yaraify','Imphash (Ruppde)','File hash analysis'])}
    ${secCard('sc-o','🍯','Honeypot Monitor','Ransomware trap',['Canary file deployment','Modification detection','Auto-isolate alert','Stealer detection'])}
    </div>`);

  // SEC 07 — Tech Stack
  html += sec('stack','07','Technology Stack','Semua teknologi yang digunakan dalam ekosistem Nexus v3.0.',
    `<table class="stk-table"><thead><tr><th>Layer</th><th>Technology</th><th>Purpose</th></tr></thead><tbody>
    <tr><td>🤖 AI Core</td><td>LangGraph · LangChain · Ollama</td><td>Multi-agent orchestration + local LLM</td></tr>
    <tr><td>☁️ Cloud LLM</td><td>OpenRouter (GPT-4o · Claude · Gemini)</td><td>Complex reasoning fallback</td></tr>
    <tr><td>🐍 Backend</td><td>FastAPI · Celery · Redis</td><td>API server + async task queue</td></tr>
    <tr><td>📱 WA Client</td><td>Baileys · whatsapp-web.js</td><td>WhatsApp multi-session</td></tr>
    <tr><td>🗄️ Database</td><td>PostgreSQL · Redis · MongoDB</td><td>Persistent + cache + document store</td></tr>
    <tr><td>🧠 Knowledge</td><td>ChromaDB · Neo4j</td><td>Vector search + knowledge graph</td></tr>
    <tr><td>🔬 ML/DL</td><td>Transformers · TensorFlow · scikit-learn</td><td>Sentiment, anomaly, satellite</td></tr>
    <tr><td>🎤 Voice</td><td>Whisper · gTTS · pyttsx3</td><td>Speech-to-text + text-to-speech</td></tr>
    <tr><td>🔗 Blockchain</td><td>Web3.py · Alchemy · CoinGecko</td><td>Multi-chain tracker</td></tr>
    <tr><td>🛡️ Security</td><td>YARA · Nmap · Shodan · HIBP</td><td>Pentest + OSINT + malware</td></tr>
    <tr><td>📲 Scraper</td><td>instaloader · tweepy · yt-dlp</td><td>Social media scraping</td></tr>
    <tr><td>🚀 Infra</td><td>Docker · Turborepo · GitHub Actions</td><td>Container + monorepo + CI/CD</td></tr>
    <tr><td>📊 Monitoring</td><td>Prometheus · Grafana · Sentry</td><td>Metrics + dashboards + error tracking</td></tr>
    </tbody></table>`);

  // SEC 08 — Roadmap
  html += sec('roadmap','08','Development Roadmap','4-phase development timeline.',
    `<div class="timeline">
    ${phase('1','done','Phase 1 · Week 1-2','Core Foundation',['Monorepo setup','Agent orchestrator','FastAPI backend','Memory system','WA client','Skill engine'])}
    ${phase('2','done','Phase 2 · Week 3-4','Intelligence Layer',['ML sentiment','YARA sandbox','Voice engine','Conversational AI','Emotion system','Knowledge graph'])}
    ${phase('3','done','Phase 3 · Week 5-7','Tools & Services',['Social scraper','Downloader','Doc converter','Blockchain','Security/OSINT','Notifications'])}
    ${phase('4','','Phase 4 · Week 8-10','Frontend & Production',['GUI dashboard','Blueprint UI','Brainstorm tool','Code generator','CI/CD pipeline','Documentation'])}
    </div>`);

  // SEC 09 — Folder Structure
  html += sec('folder','09','Monorepo Folder Structure','21 packages + infra + frontend dalam satu repository.',
    `<div class="tree"><span class="d">nexus-blueprint-v3/</span>
├── <span class="conf">.env.example</span>         <span class="cm">// environment variables</span>
├── <span class="conf">docker-compose.yml</span>   <span class="cm">// 11 Docker services</span>
├── <span class="conf">pyproject.toml</span>       <span class="cm">// Python workspace</span>
├── <span class="conf">turbo.json</span>           <span class="cm">// Turborepo config</span>
├── <span class="conf">requirements.txt</span>     <span class="cm">// Python deps</span>
│
├── <span class="d">packages/</span>
│   ├── <span class="d">agents/</span>           <span class="cm">// 🤖 LangGraph orchestrator</span>
│   │   ├── <span class="py">orchestrator.py</span> <span class="py">nexus_agent.py</span> <span class="py">openrouter_agent.py</span>
│   │   ├── <span class="py">task_classifier.py</span>
│   │   └── <span class="d">memory/</span>       <span class="py">short_term.py</span> <span class="py">long_term.py</span>
│   ├── <span class="d">api-backend/</span>      <span class="cm">// 🐍 FastAPI + middleware</span>
│   ├── <span class="d">wa-client/</span>        <span class="cm">// 📱 Baileys WhatsApp</span>
│   ├── <span class="d">memory-manager/</span>   <span class="cm">// 📚 RAG + Neo4j</span>
│   ├── <span class="d">skill-engine/</span>     <span class="cm">// ✂️ Hot-reload plugins</span>
│   ├── <span class="d new">ml-engine/</span>        <span class="cm">// 🧠 BERT + Heuristic</span>
│   ├── <span class="d new">sandbox/</span>          <span class="cm">// 🔬 YARA + Docker VM</span>
│   ├── <span class="d new">voice-engine/</span>     <span class="cm">// 🎤 Whisper + TTS</span>
│   ├── <span class="d new">conversational-ai/</span><span class="cm">// 💬 Emotions + personality</span>
│   ├── <span class="d new">social-scraper/</span>   <span class="cm">// 📲 IG/TT/X/YT scraper</span>
│   ├── <span class="d new">downloader/</span>       <span class="cm">// ⬇️ yt-dlp video/music</span>
│   ├── <span class="d new">doc-converter/</span>    <span class="cm">// 📄 PDF↔Word, Excel</span>
│   ├── <span class="d new">blockchain/</span>       <span class="cm">// 🔗 Multi-chain tracker</span>
│   ├── <span class="d new">crypto-dashboard/</span> <span class="cm">// 📈 CoinGecko + DeFi</span>
│   ├── <span class="d new">security/</span>         <span class="cm">// 🛡️ Pentest + OSINT</span>
│   ├── <span class="d new">observability/</span>    <span class="cm">// 🔴 Error + AI debug</span>
│   ├── <span class="d new">notifications/</span>    <span class="cm">// 📧 Gmail + Telegram</span>
│   ├── <span class="d new">devtools-monitor/</span> <span class="cm">// 🔧 Playwright inspect</span>
│   ├── <span class="d new">crud-executor/</span>    <span class="cm">// ⚡ Safe CRUD ops</span>
│   ├── <span class="d new">brainstorm/</span>       <span class="cm">// 💡 RAG + Flowchart</span>
│   └── <span class="d new">code-generator/</span>   <span class="cm">// ⚡ Multi-lang codegen</span>
│
├── <span class="d">infra/</span>
│   └── <span class="conf">prometheus.yml</span>
├── <span class="d">.github/workflows/</span>
│   └── <span class="conf">ci.yml</span>
└── <span class="js">index.html</span> <span class="js">main.js</span> <span class="c">style.css</span> <span class="cm">// Blueprint frontend</span></div>`);

  // SEC 10 — Recommendations
  html += sec('reco','10','Rekomendasi Strategis','Rekomendasi untuk mempercepat development dan production readiness.',
    `<div class="reco-cards">
    <div class="reco-card"><div class="reco-num">01</div><div><h4>Gunakan Ollama + Nexus-3 sebagai default</h4><p>Zero cost, full privacy, bisa fine-tune. Cloud LLM hanya untuk fallback complex tasks.</p></div></div>
    <div class="reco-card"><div class="reco-num">02</div><div><h4>Docker-first deployment</h4><p>Setiap package punya Dockerfile sendiri. docker-compose up untuk full stack dalam 1 command.</p></div></div>
    <div class="reco-card"><div class="reco-num">03</div><div><h4>Implement RAG pipeline early</h4><p>ChromaDB + Neo4j dari awal agar bot belajar dan improve dari setiap percakapan.</p></div></div>
    <div class="reco-card"><div class="reco-num">04</div><div><h4>Security audit setiap release</h4><p>YARA scan semua skill, audit log wajib, developer approval untuk operasi berbahaya.</p></div></div>
    <div class="reco-card"><div class="reco-num">05</div><div><h4>Modular skill marketplace</h4><p>Buat skill marketplace agar komunitas bisa kontribusi plugin tanpa ubah core code.</p></div></div>
    </div>`);

  return html;
}
