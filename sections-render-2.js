// ═══════════════════════════════════════════════════════════════
// SECTIONS RENDER — Sections 11-25
// ═══════════════════════════════════════════════════════════════
import { sec, terminal, featureBlock, secCard } from './render.js';

export function renderSections2() {
  let html = '';

  // SEC 11 — Risk
  html += sec('risk','11','Risk Assessment','Identifikasi risiko utama dan strategi mitigasi.',
    `<div class="risk-rows">
    <div class="risk-row"><span class="rn">API Key Exposure</span><span class="rd">API key bocor di code/logs</span><span class="rm rm-h">HIGH</span><span class="rs">HashiCorp Vault + .env</span></div>
    <div class="risk-row"><span class="rn">LLM Hallucination</span><span class="rd">AI memberikan info salah</span><span class="rm rm-m">MEDIUM</span><span class="rs">RAG grounding + confidence threshold</span></div>
    <div class="risk-row"><span class="rn">WA Ban Risk</span><span class="rd">Nomor bot di-ban oleh WhatsApp</span><span class="rm rm-h">HIGH</span><span class="rs">Rate limit + multi-session + delay</span></div>
    <div class="risk-row"><span class="rn">Data Breach</span><span class="rd">Database diakses tanpa izin</span><span class="rm rm-h">HIGH</span><span class="rs">Encryption at rest + RLS + audit log</span></div>
    <div class="risk-row"><span class="rn">Service Downtime</span><span class="rd">Server/service mati</span><span class="rm rm-m">MEDIUM</span><span class="rs">Docker restart + health check + alert</span></div>
    <div class="risk-row"><span class="rn">Malicious Skill</span><span class="rd">Plugin jahat diinstall</span><span class="rm rm-m">MEDIUM</span><span class="rs">Sandbox execution + manifest validation</span></div>
    </div>`);

  // SEC 12 — Budget
  html += sec('budget','12','Resource & Budget Estimation','Estimasi biaya bulanan untuk production deployment.',
    `<div class="budget-grid">
    <div class="bud-card"><span class="bud-val">$0</span><div class="bud-label">Ollama (Local)</div><div class="bud-note">Self-hosted GPU</div></div>
    <div class="bud-card"><span class="bud-val">~$20</span><div class="bud-label">OpenRouter</div><div class="bud-note">Pay-per-token fallback</div></div>
    <div class="bud-card"><span class="bud-val">~$15</span><div class="bud-label">VPS (4GB)</div><div class="bud-note">Contabo/Hetzner</div></div>
    <div class="bud-card"><span class="bud-val">$0</span><div class="bud-label">PostgreSQL</div><div class="bud-note">Self-hosted Docker</div></div>
    <div class="bud-card"><span class="bud-val">$0</span><div class="bud-label">Redis</div><div class="bud-note">Self-hosted Docker</div></div>
    <div class="bud-card"><span class="bud-val">~$5</span><div class="bud-label">APIs (Shodan/HIBP)</div><div class="bud-note">Optional paid tiers</div></div>
    </div>`);

  // SEC 13 — Social Scraper
  html += sec('social','13','Social Media Scraper Engine 📲','Scrape data dari Instagram, TikTok, Twitter/X, YouTube dengan anti-detection dan export data.',
    `<div class="sec-grid">
    ${secCard('sc-p','📸','Instagram','Posts, stories, reels, profile',['instaloader library','Profile metadata','Hashtag analysis','Anti-rate-limit'])}
    ${secCard('sc-r','🎵','TikTok','Video, profil, trending',['TikTokApi async','Video metadata','User timeline','Sound tracking'])}
    ${secCard('sc-b','🐦','Twitter/X','Tweets, trends, search',['tweepy v2 API','Recent tweets search','Hashtag tracking','Engagement metrics'])}
    ${secCard('sc-n','📺','YouTube','Video, comments, search',['yt-dlp metadata','Search results','Channel info','View/like counts'])}
    </div>
    ${terminal('Social Scrape Demo','<span class="prompt">nexus&gt;</span> <span class="cmd">!ig scrape @elonmusk --limit=5</span>\n<span class="out">📸 Fetching Instagram profile...</span>\n<span class="ok">✅ @elonmusk — 200M followers, 1200 posts</span>\n<span class="info">📊 Last 5 posts scraped with engagement data</span>')}`);

  // SEC 14 — Downloader
  html += sec('downloader','14','File Downloader Engine ⬇️','Download video/musik dari YouTube, TikTok, Instagram. Format selection, batch download, resume.',
    `${featureBlock('🎬','Video Download','yt-dlp mendukung 1000+ situs. Format MP4/WEBM, resolusi selectable.',terminal('Download Flow','<span class="prompt">nexus&gt;</span> <span class="cmd">!download https://youtube.com/watch?v=xxx</span>\n<span class="out">📥 Fetching video info...</span>\n<span class="info">🎬 Title: "Amazing Video" | 10:32 | 1080p</span>\n<span class="ok">✅ Downloaded: amazing_video.mp4 (45.2MB)</span>'))}
    ${featureBlock('🎵','Music Download','Extract audio ke MP3 192kbps dari video apapun.',terminal('Music','<span class="prompt">nexus&gt;</span> <span class="cmd">!music https://youtube.com/watch?v=xxx</span>\n<span class="ok">✅ Extracted: song.mp3 (4.8MB, 192kbps)</span>'))}`);

  // SEC 15 — Doc Converter
  html += sec('docmgmt','15','Document Converter & Tools 📄','Konversi PDF↔Word, generate Excel dengan styling, merge/split PDF, extract text.',
    `<div class="sec-grid">
    ${secCard('sc-b','📄','PDF → Word','Konversi PDF ke DOCX',['pdf2docx library','Layout preservation','Table extraction','Batch convert'])}
    ${secCard('sc-p','📝','Word → PDF','Konversi DOCX ke PDF',['LibreOffice headless','Format preservation','Auto-conversion','CLI interface'])}
    ${secCard('sc-n','📊','Excel Generator','Buat Excel dengan data + styling',['openpyxl templates','Nexus dark theme','Chat export','Data dashboard'])}
    ${secCard('sc-y','✂️','PDF Tools','Merge, split, extract text',['PyPDF2 merge/split','pdfplumber extract','Compression','Batch processing'])}
    </div>`);

  // SEC 16 — ML/DL
  html += sec('ml','16','Machine Learning & Deep Learning 🧠','BERT sentiment analysis, heuristic behaviour ML, anomaly detection.',
    `${featureBlock('📊','Sentiment Analysis','BERT multilingual pre-trained model. Per-kalimat breakdown + AI summary. Support Indonesian.',terminal('Sentiment','<span class="prompt">nexus&gt;</span> <span class="cmd">!sentimen "Produk ini bagus tapi pengirimannya lambat"</span>\n<span class="out">🔍 Analyzing 2 sentences...</span>\n<span class="ok">📊 Overall: NEUTRAL (0.52)</span>\n<span class="info">  ✅ "Produk ini bagus" → POSITIVE (0.91)</span>\n<span class="warn">  ⚠️ "pengirimannya lambat" → NEGATIVE (0.87)</span>'))}
    ${featureBlock('🔬','Heuristic Behaviour ML','Deteksi anomali: C2 beaconing, DNS tunneling, data exfiltration, ransomware, stealer behaviour.',terminal('Heuristic','<span class="prompt">nexus&gt;</span> <span class="cmd">analyze-traffic --pcap=suspect.pcap</span>\n<span class="err">🚨 CRITICAL: Regular beaconing ~30s interval (C2)</span>\n<span class="err">🚨 CRITICAL: Outbound 250MB >> inbound (exfiltration)</span>\n<span class="warn">⚠️ HIGH: Port 4444 accessed 15x (backdoor)</span>\n<span class="info">Risk Score: 9.5/10 — ISOLATE IMMEDIATELY</span>'))}`);

  // SEC 17 — Sandbox
  html += sec('sandbox','17','Real Sandbox & Malware Analysis 🔬','Docker/QEMU VM sandbox, YARA-Forge, honeypot ransomware, Imphash detection, PS/CMD extractor.',
    `${featureBlock('🐳','Docker VM Sandbox','Jalankan file mencurigakan dalam container terisolasi. Network disabled, memory limited, timeout enforced.',terminal('Sandbox','<span class="prompt">nexus&gt;</span> <span class="cmd">!sandbox analyze suspect.exe</span>\n<span class="out">🐳 Starting isolated container...</span>\n<span class="out">⏱️ Execution timeout: 120s | Memory: 512MB</span>\n<span class="err">🚨 YARA Match: Win32.Emotet (confidence: HIGH)</span>\n<span class="err">🚨 Imphash match: d5502a1d... (known Emotet)</span>\n<span class="warn">⚠️ PS -EncodedCommand detected — decoded:</span>\n<span class="info">   IEX(New-Object Net.WebClient).DownloadString(...)</span>\n<span class="ok">📸 3 screenshots captured</span>\n<span class="err">🔴 Verdict: MALICIOUS (Score: 9.2/10)</span>'))}`);

  // SEC 18 — Conversational AI
  html += sec('convo','18','Conversational AI & Personality 💬','Bot dengan emosi dinamis, skill interpersonal, social experiment, belajar dari manusia.',
    `<div class="sec-grid">
    ${secCard('sc-p','😊','10 Emosi Dinamis','State machine emosi',['Happy · Sad · Angry','Excited · Curious','Surprised · Empathetic','Proud · Worried · Neutral'])}
    ${secCard('sc-n','🤝','Interpersonal Skills','Bijak dan empati',['Validasi perasaan user','Humor kontekstual','Saran inovatif proaktif','Rapport building'])}
    ${secCard('sc-b','🧪','Social Experiments','5 strategi percakapan',['Empathy First','Socratic Method','Storytelling Mode','Humor Mode · Mentor'])}
    ${secCard('sc-y','📈','Self-Learning','Belajar dari manusia',['Topic frequency tracking','Language pattern learning','Preference adaptation','Personality evolution'])}
    </div>`);

  // SEC 19 — Voice
  html += sec('voice','19','Voice Note Processing 🎤','Whisper STT untuk voice note WA, TTS untuk jawab dengan suara, intent understanding.',
    `${featureBlock('🎤','Speech-to-Text (Whisper)','OpenAI Whisper model untuk transcribe voice note. Auto-detect bahasa. Support Indonesian, English, dll.',terminal('Voice Flow','<span class="prompt">nexus&gt;</span> <span class="cmd">[Voice Note Received: 8.5s]</span>\n<span class="out">🎤 Transcribing with Whisper (base)...</span>\n<span class="ok">✅ Language: Indonesian (confidence: 0.94)</span>\n<span class="info">📝 "Tolong carikan harga laptop gaming terbaru"</span>\n<span class="out">🎯 Intent: SEARCH | Query: harga laptop gaming</span>\n<span class="ok">🔍 Searching...</span>'))}
    ${featureBlock('🔊','Text-to-Speech','Respond dengan voice menggunakan gTTS atau pyttsx3. Multi-language support.','')}`);

  // SEC 20 — Knowledge
  html += sec('knowledge','20','Knowledge & Memory Manager 📚','RAG pipeline + Knowledge Graph untuk self-improving AI. Bot belajar dan tidak bodoh.',
    `${featureBlock('🧠','Self-Improving Loop','Setiap percakapan disimpan → di-embed ke ChromaDB → linked di Neo4j → digunakan untuk RAG retrieval di percakapan berikutnya.',terminal('Learning','<span class="prompt">nexus&gt;</span> <span class="cmd">memory stats</span>\n<span class="ok">📚 Knowledge Base: 12,847 documents</span>\n<span class="ok">🕸️ Knowledge Graph: 3,241 entities, 8,722 relations</span>\n<span class="ok">💬 Conversations learned: 5,392</span>\n<span class="ok">🧠 Topics mastered: 847</span>\n<span class="info">📈 Improvement rate: +12.4% this week</span>'))}`);

  // SEC 21 — DevTools
  html += sec('devtools','21','DevTools & Website Monitor 🔧','Browser DevTools-like: link inspection, leak identification, SEO audit, cache management.',
    `${featureBlock('🔍','Website Inspector','Playwright-powered full audit: broken links, security headers, SEO check, resource errors.',terminal('Inspect','<span class="prompt">nexus&gt;</span> <span class="cmd">!inspect https://example.com</span>\n<span class="ok">✅ Status: 200 | Load: 1.2s</span>\n<span class="ok">✅ Links: 45 total, 0 broken</span>\n<span class="warn">⚠️ Missing: Content-Security-Policy, HSTS</span>\n<span class="ok">✅ SEO: Title ✓, H1 ✓, Meta desc ✓</span>\n<span class="info">📊 Security Score: 7/10</span>'))}`);

  // SEC 22 — CRUD
  html += sec('crud','22','CRUD Monorepo Executor ⚡','Eksekusi CRUD di monorepo: buat/edit/hapus file, code scaffolding. AI safety check.',
    `${featureBlock('🛡️','Safety-First Execution','Setiap command dicek oleh AI safety checker. Dangerous patterns (rm -rf, DROP TABLE, dll) otomatis diblok.',terminal('CRUD','<span class="prompt">nexus&gt;</span> <span class="cmd">!scaffold skill-plugin --name=weather-bot</span>\n<span class="out">🛡️ Safety check: PASSED</span>\n<span class="ok">✅ Created: skills/weather-bot/skill.json</span>\n<span class="ok">✅ Created: skills/weather-bot/handler.py</span>\n<span class="info">📦 Scaffold complete — 2 files created</span>'))}`);

  // SEC 23 — Crypto
  html += sec('crypto','23','Crypto Dashboard & Analytics 📈','Fundamental analysis, multi-chain tracking, DeFi TVL, Fear & Greed Index.',
    `${featureBlock('📊','Market Overview','CoinGecko + DeFiLlama + Alternative.me. Realtime market cap, dominance, volume, sentiment.',terminal('Crypto','<span class="prompt">nexus&gt;</span> <span class="cmd">!crypto analisa bitcoin</span>\n<span class="ok">📈 Bitcoin (BTC) — Rank #1</span>\n<span class="info">💰 Price: $67,234 | MCap: $1.32T</span>\n<span class="ok">📈 24h: +2.4% | 7d: +5.1%</span>\n<span class="info">🔧 GitHub: 45.2k stars, 127 commits/4w</span>\n<span class="warn">😱 Fear & Greed: 72 (Greed)</span>'))}
    ${featureBlock('🔗','Multi-Chain Portfolio','Track wallet di ETH, BSC, Solana, Polygon, Avalanche. Portfolio aggregator.',terminal('Portfolio','<span class="prompt">nexus&gt;</span> <span class="cmd">!wallet 0x742d...4c2E --chain=ethereum</span>\n<span class="ok">💰 Balance: 2.45 ETH ($7,842.30)</span>\n<span class="info">📊 Tokens: 5 ERC-20 detected</span>'))}`);

  // SEC 24 — Brainstorm
  html += sec('brainstorm','24','Brainstorm & Flowchart 💡','RAG-powered brainstorming, Mermaid flowchart generator, PlantUML use-case diagrams.',
    `${featureBlock('💡','AI Brainstorm','Input topik → RAG cari knowledge terkait → Generate ide terstruktur (Feature, Improvement, Innovation).','')}
    ${featureBlock('📊','Flowchart Generator','Auto-generate Mermaid flowcharts dan PlantUML use-case diagrams dari deskripsi natural language.','')}`);

  // SEC 25 — Code Gen
  html += sec('codegen','25','Code Generator & Tester ⚡','Multi-language code generation menggunakan LLM + auto syntax validation + test generation.',
    `${featureBlock('⚡','AI Code Generation','Generate Python, JavaScript, TypeScript, Java, Go, Rust dari deskripsi natural language.',terminal('CodeGen','<span class="prompt">nexus&gt;</span> <span class="cmd">!code python "function to calculate fibonacci"</span>\n<span class="out">⚡ Generating Python code...</span>\n<span class="ok">✅ Syntax validation: PASSED</span>\n<span class="ok">✅ Auto-generated: test_fibonacci.py</span>\n<span class="info">📝 3 test cases created</span>'))}`);

  return html;
}
