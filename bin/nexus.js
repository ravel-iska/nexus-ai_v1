#!/usr/bin/env node
// ═══════════════════════════════════════════════════════════════
// NEXUS-AGENT CLI — Global command entry point
// Usage: nexus-agent run | nexus-agent keygen | nexus-agent status
// ═══════════════════════════════════════════════════════════════

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const os = require('os');
const express = require('express');

const NEXUS_DIR = path.join(os.homedir(), '.nexus-agent');
const KEY_FILE = path.join(NEXUS_DIR, 'api-keys.json');
const CONFIG_FILE = path.join(NEXUS_DIR, 'config.json');
const DASHBOARD_DIR = path.resolve(__dirname, '..', 'packages', 'gui-dashboard');
const DEFAULT_PORT = 3100;

// ─── COLORS ───
const c = {
  reset: '\x1b[0m', bold: '\x1b[1m',
  cyan: '\x1b[36m', green: '\x1b[32m', red: '\x1b[31m',
  yellow: '\x1b[33m', magenta: '\x1b[35m', dim: '\x1b[2m',
};

function banner() {
  console.log(`
${c.cyan}${c.bold}  ╔══════════════════════════════════════════════╗
  ║   ⬡ NEXUS-AGENT v3.0                        ║
  ║   AI Agent Ecosystem — Production Ready       ║
  ╚══════════════════════════════════════════════╝${c.reset}
`);
}

function ensureDir() {
  if (!fs.existsSync(NEXUS_DIR)) {
    fs.mkdirSync(NEXUS_DIR, { recursive: true });
  }
}

// ─── API KEY MANAGEMENT ───
function loadKeys() {
  ensureDir();
  if (!fs.existsSync(KEY_FILE)) {
    fs.writeFileSync(KEY_FILE, JSON.stringify({ keys: [] }, null, 2));
  }
  return JSON.parse(fs.readFileSync(KEY_FILE, 'utf-8'));
}

function saveKeys(data) {
  ensureDir();
  fs.writeFileSync(KEY_FILE, JSON.stringify(data, null, 2));
}

function generateApiKey(label = 'default') {
  const key = `hms_${crypto.randomBytes(24).toString('hex')}`;
  const data = loadKeys();
  data.keys.push({
    key,
    label,
    created: new Date().toISOString(),
    lastUsed: null,
    active: true,
  });
  saveKeys(data);
  return key;
}

function validateKey(key) {
  const data = loadKeys();
  const found = data.keys.find(k => k.key === key && k.active);
  if (found) {
    found.lastUsed = new Date().toISOString();
    saveKeys(data);
    return true;
  }
  return false;
}

function listKeys() {
  const data = loadKeys();
  return data.keys;
}

function revokeKey(key) {
  const data = loadKeys();
  const found = data.keys.find(k => k.key === key);
  if (found) {
    found.active = false;
    saveKeys(data);
    return true;
  }
  return false;
}

// ─── CONFIG ───
function loadConfig() {
  ensureDir();
  if (!fs.existsSync(CONFIG_FILE)) {
    fs.writeFileSync(CONFIG_FILE, JSON.stringify({
      port: DEFAULT_PORT,
      autoOpen: true,
      theme: 'dark',
    }, null, 2));
  }
  return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
}

// ─── COMMANDS ───
const [,, cmd, ...args] = process.argv;

switch (cmd) {
  case 'run':
  case 'start':
    cmdRun();
    break;
  case 'keygen':
    cmdKeygen();
    break;
  case 'keys':
    cmdListKeys();
    break;
  case 'revoke':
    cmdRevoke();
    break;
  case 'status':
    cmdStatus();
    break;
  case 'help':
  case '--help':
  case '-h':
  default:
    cmdHelp();
    break;
}

function cmdRun() {
  banner();
  const config = loadConfig();
  const port = args.includes('--port') ? args[args.indexOf('--port') + 1] : config.port;
  const keys = loadKeys();

  // Auto-generate key on first run
  if (keys.keys.length === 0) {
    console.log(`${c.yellow}⚠  No API key found. Generating your first key...${c.reset}\n`);
    const key = generateApiKey('master');
    console.log(`${c.green}${c.bold}  ✅ API Key Generated:${c.reset}`);
    console.log(`${c.cyan}${c.bold}  ${key}${c.reset}`);
    console.log(`\n${c.yellow}  ⚠ SAVE THIS KEY! You need it to access the dashboard.${c.reset}`);
    console.log(`${c.dim}  Stored in: ${KEY_FILE}${c.reset}\n`);
  }

  console.log(`${c.green}  🚀 Starting Nexus Dashboard...${c.reset}`);
  console.log(`${c.dim}  Port: ${port}${c.reset}`);
  console.log(`${c.dim}  Keys: ${keys.keys.filter(k => k.active).length} active${c.reset}\n`);

  process.env.NEXUS_KEY_FILE = KEY_FILE;
  process.env.NEXUS_PORT = port;

  // SPAWN WA-CLIENT IN BACKGROUND
  const waClientDir = path.resolve(__dirname, '..', 'packages', 'wa-client');
  const waProcess = spawn('node', ['src/index.js'], {
    cwd: waClientDir,
    stdio: 'pipe',
    env: { ...process.env }
  });
  
  waProcess.stdout.on('data', data => {
    if (data.toString().includes('connected successfully')) {
      console.log(`${c.green}  ✅ WA Client Connected!${c.reset}`);
    }
  });
  
  // DASHBOARD SERVER (Vite dev or Express static)
  const distDir = path.join(DASHBOARD_DIR, 'dist');
  let dashboardProcess = null;

  if (fs.existsSync(distDir)) {
    console.log(`${c.cyan}  ⬡ Running in Production Mode (Serving static dist)${c.reset}`);
    const app = express();
    
    // Auth Endpoint
    app.post('/api/auth', express.json(), (req, res) => {
      try {
        const { key } = req.body;
        const data = loadKeys();
        const found = data.keys.find(k => k.key === key && k.active);
        if (found) {
          found.lastUsed = new Date().toISOString();
          saveKeys(data);
          return res.json({ success: true });
        }
        res.status(401).json({ success: false, error: 'Invalid API Key' });
      } catch (e) {
        res.status(500).json({ success: false, error: 'Server error' });
      }
    });

    // Protect subsequent API routes
    const requireAuth = (req, res, next) => {
      const authHeader = req.headers.authorization || '';
      const token = authHeader.replace('Bearer ', '');
      if (!token) return res.status(401).json({ error: 'Missing token' });
      
      const data = loadKeys();
      const found = data.keys.find(k => k.key === token && k.active);
      if (!found) return res.status(403).json({ error: 'Invalid or revoked token' });
      next();
    };

    app.get('/api/keys', requireAuth, (req, res) => {
      res.json(loadKeys().keys);
    });

    app.post('/api/keys', requireAuth, express.json(), (req, res) => {
      const { label } = req.body;
      const key = generateApiKey(label || 'gui-generated');
      res.json({ success: true, key });
    });

    app.delete('/api/keys/:key', requireAuth, (req, res) => {
      const success = revokeKey(req.params.key);
      if (success) res.json({ success: true });
      else res.status(404).json({ error: 'Key not found' });
    });

    app.use(express.static(distDir));
    // SPA fallback
    app.use((req, res, next) => {
      if (req.method === 'GET' && !req.path.startsWith('/api/')) {
        res.sendFile(path.join(distDir, 'index.html'));
      } else {
        next();
      }
    });

    const server = app.listen(port, () => {
      console.log(`${c.green}${c.bold}  ✅ Dashboard running at: http://localhost:${port}/${c.reset}`);
      console.log(`${c.dim}  Press Ctrl+C to stop${c.reset}\n`);
      if (config.autoOpen) {
        const openCmd = process.platform === 'win32' ? 'start' : process.platform === 'darwin' ? 'open' : 'xdg-open';
        try { execSync(`${openCmd} http://localhost:${port}`); } catch {}
      }
    });
    
    dashboardProcess = { kill: () => server.close() };

  } else {
    console.log(`${c.yellow}  ⬡ Running in Development Mode (Vite)${c.reset}`);
    dashboardProcess = spawn('npx', ['vite', '--port', String(port)], {
      cwd: DASHBOARD_DIR,
      stdio: 'pipe',
      shell: true,
      env: { ...process.env, VITE_NEXUS_PORT: port },
    });

    dashboardProcess.stdout.on('data', (data) => {
      if (data.toString().includes('ready in') || data.toString().includes('Local:')) {
        console.log(`${c.green}${c.bold}  ✅ Dashboard running at: http://localhost:${port}/${c.reset}`);
        console.log(`${c.dim}  Press Ctrl+C to stop${c.reset}\n`);
        if (config.autoOpen) {
          const openCmd = process.platform === 'win32' ? 'start' : process.platform === 'darwin' ? 'open' : 'xdg-open';
          try { execSync(`${openCmd} http://localhost:${port}`); } catch {}
        }
      }
    });
  }

  process.on('SIGINT', () => {
    waProcess.kill();
    if (dashboardProcess && dashboardProcess.kill) dashboardProcess.kill();
    console.log(`\n${c.cyan}  ⬡ Nexus stopped.${c.reset}`);
    process.exit(0);
  });
}

function cmdKeygen() {
  banner();
  const label = args[0] || 'api-key-' + Date.now();
  const key = generateApiKey(label);
  console.log(`${c.green}${c.bold}  ✅ New API Key Generated${c.reset}`);
  console.log(`${c.dim}  Label: ${label}${c.reset}`);
  console.log(`${c.cyan}${c.bold}  ${key}${c.reset}\n`);
  console.log(`${c.yellow}  ⚠ Save this key — it won't be shown again in full.${c.reset}`);
}

function cmdListKeys() {
  banner();
  const keys = listKeys();
  if (keys.length === 0) {
    console.log(`${c.yellow}  No API keys. Run: nexus-agent keygen${c.reset}`);
    return;
  }
  console.log(`${c.bold}  API Keys (${keys.length}):${c.reset}\n`);
  keys.forEach((k, i) => {
    const masked = k.key.slice(0, 8) + '...' + k.key.slice(-6);
    const status = k.active ? `${c.green}ACTIVE${c.reset}` : `${c.red}REVOKED${c.reset}`;
    console.log(`  ${i + 1}. ${c.cyan}${masked}${c.reset} [${status}]`);
    console.log(`     Label: ${k.label} | Created: ${k.created}`);
    if (k.lastUsed) console.log(`     Last used: ${k.lastUsed}`);
    console.log('');
  });
}

function cmdRevoke() {
  banner();
  const key = args[0];
  if (!key) {
    console.log(`${c.red}  Usage: nexus-agent revoke <api-key>${c.reset}`);
    return;
  }
  if (revokeKey(key)) {
    console.log(`${c.green}  ✅ Key revoked successfully${c.reset}`);
  } else {
    console.log(`${c.red}  ❌ Key not found${c.reset}`);
  }
}

function cmdStatus() {
  banner();
  const keys = loadKeys();
  const config = loadConfig();
  console.log(`${c.bold}  System Status:${c.reset}`);
  console.log(`  Config dir : ${c.dim}${NEXUS_DIR}${c.reset}`);
  console.log(`  API Keys   : ${keys.keys.filter(k => k.active).length} active`);
  console.log(`  Port       : ${config.port}`);
  console.log(`  Auto-open  : ${config.autoOpen}`);
}

function cmdHelp() {
  banner();
  console.log(`${c.bold}  Usage:${c.reset} nexus-agent <command>\n`);
  console.log(`${c.bold}  Commands:${c.reset}`);
  console.log(`    ${c.cyan}run${c.reset}              Start the dashboard GUI`);
  console.log(`    ${c.cyan}keygen${c.reset} [label]    Generate a new API key`);
  console.log(`    ${c.cyan}keys${c.reset}              List all API keys`);
  console.log(`    ${c.cyan}revoke${c.reset} <key>      Revoke an API key`);
  console.log(`    ${c.cyan}status${c.reset}            Show system status`);
  console.log(`    ${c.cyan}help${c.reset}              Show this help\n`);
  console.log(`${c.bold}  Examples:${c.reset}`);
  console.log(`    ${c.dim}nexus-agent run${c.reset}`);
  console.log(`    ${c.dim}nexus-agent run --port 4000${c.reset}`);
  console.log(`    ${c.dim}nexus-agent keygen my-project${c.reset}\n`);
}

// Export for API validation
module.exports = { validateKey, loadKeys, generateApiKey };
