// ═══════════════════════════════════════════════════════════════
// WA CLIENT — WhatsApp connection using Baileys with REST API
// ═══════════════════════════════════════════════════════════════

const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const pino = require('pino');
const express = require('express');
const cors = require('cors');
const qrcode = require('qrcode');

const { Router } = require('./router');
const { Formatter } = require('./formatter');

const PORT = process.env.WA_API_PORT || 3101;
const logger = pino({ level: 'silent' });

class WAClient {
  constructor(config = {}) {
    this.config = {
      sessionName: config.sessionName || process.env.WA_SESSION_NAME || 'nexus-main',
      adminNumber: config.adminNumber || process.env.WA_ADMIN_NUMBER || '',
      autoRead: config.autoRead !== false,
      apiBackendUrl: config.apiBackendUrl || process.env.API_BACKEND_URL || 'http://localhost:8000',
      ...config,
    };

    this.sock = null;
    this.router = new Router(this.config);
    this.formatter = new Formatter();
    
    // Status tracking for API
    this.status = 'disconnected'; // disconnected, connecting, connected, qr, pairing
    this.qrBase64 = null;
    this.pairingCode = null;
    this.clientInfo = null;
    
    // SSE Clients
    this.sseClients = [];

    // Setup API Server
    this.app = express();
    this.app.use(cors());
    this.app.use(express.json());
    this.setupApiRoutes();
  }

  // ─── API ROUTES ───
  setupApiRoutes() {
    this.app.get('/api/wa/status', (req, res) => {
      res.json({
        status: this.status,
        qr: this.qrBase64,
        pairingCode: this.pairingCode,
        client: this.clientInfo
      });
    });

    // Request Pairing Code
    this.app.post('/api/wa/pair', async (req, res) => {
      const { phone } = req.body;
      if (!phone) return res.status(400).json({ error: 'Phone number is required' });
      
      try {
        if (!this.sock) {
          await this.start(false); // Start without printing QR
        }
        
        let formattedPhone = phone.replace(/[^0-9]/g, '');
        if (formattedPhone.startsWith('0')) formattedPhone = '62' + formattedPhone.slice(1);

        setTimeout(async () => {
          try {
            const code = await this.sock.requestPairingCode(formattedPhone);
            this.pairingCode = code.match(/.{1,4}/g)?.join('-') || code;
            this.status = 'pairing';
            this.broadcastState();
          } catch (e) {
            console.error('Pairing error:', e);
          }
        }, 3000); // Wait for sock to initialize completely

        res.json({ message: 'Pairing code requested', phone: formattedPhone });
      } catch (e) {
        res.status(500).json({ error: e.message });
      }
    });

    // Server-Sent Events (SSE) for Realtime GUI Updates
    this.app.get('/api/wa/events', (req, res) => {
      res.setHeader('Content-Type', 'text/event-stream');
      res.setHeader('Cache-Control', 'no-cache');
      res.setHeader('Connection', 'keep-alive');
      
      this.sseClients.push(res);
      res.write(`data: ${JSON.stringify({ status: this.status, qr: this.qrBase64, pairingCode: this.pairingCode })}\n\n`);

      req.on('close', () => {
        this.sseClients = this.sseClients.filter(c => c !== res);
      });
    });
  }

  broadcastState() {
    const data = JSON.stringify({
      status: this.status,
      qr: this.qrBase64,
      pairingCode: this.pairingCode,
      client: this.clientInfo
    });
    this.sseClients.forEach(res => res.write(`data: ${data}\n\n`));
  }

  // ─── WA ENGINE ───
  async start(printQR = true) {
    console.log('🤖 WA Agent Nexus v3.0 starting...');
    this.status = 'connecting';
    this.broadcastState();

    const { state, saveCreds } = await useMultiFileAuthState(`sessions/${this.config.sessionName}`);
    const { version } = await fetchLatestBaileysVersion();

    this.sock = makeWASocket({
      version,
      auth: state,
      printQRInTerminal: printQR,
      logger,
      browser: ['Nexus Agent', 'Chrome', '120.0.0'],
      markOnlineOnConnect: true,
      syncFullHistory: false,
    });

    this.sock.ev.on('connection.update', (update) => this._handleConnection(update));
    this.sock.ev.on('creds.update', saveCreds);

    this.sock.ev.on('messages.upsert', async ({ messages }) => {
      for (const msg of messages) {
        if (!msg.key.fromMe && msg.message) {
          await this._handleMessage(msg);
        }
      }
    });
  }

  async _handleConnection(update) {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      this.status = 'qr';
      this.qrBase64 = await qrcode.toDataURL(qr);
      this.broadcastState();
    }

    if (connection === 'close') {
      this.status = 'disconnected';
      this.qrBase64 = null;
      this.pairingCode = null;
      this.clientInfo = null;
      this.broadcastState();

      const reason = new Boom(lastDisconnect?.error)?.output?.statusCode;
      console.log(`❌ Connection closed. Reason: ${reason}`);

      if (reason !== DisconnectReason.loggedOut) {
        console.log('🔄 Reconnecting...');
        setTimeout(() => this.start(), 5000);
      } else {
        console.log('🚫 Logged out. Scan QR again.');
      }
    }

    if (connection === 'open') {
      this.status = 'connected';
      this.qrBase64 = null;
      this.pairingCode = null;
      this.clientInfo = {
        name: this.sock.authState.creds.me?.name || 'Nexus Bot',
        id: this.sock.authState.creds.me?.id.split(':')[0]
      };
      this.broadcastState();
      console.log('✅ WhatsApp connected successfully!');

      if (this.config.adminNumber) {
        await this.sendMessage(this.config.adminNumber, this.formatter.systemBoot());
      }
    }
  }

  async _handleMessage(msg) {
    const jid = msg.key.remoteJid;
    const sender = msg.key.participant || jid;
    const isGroup = jid.endsWith('@g.us');

    if (this.config.autoRead) {
      await this.sock.readMessages([msg.key]);
    }

    try {
      const text = msg.message?.conversation || msg.message?.extendedTextMessage?.text || msg.message?.imageMessage?.caption || '';
      let media = null;
      
      if (msg.message?.imageMessage) media = { type: 'image', msg: msg.message.imageMessage };
      if (msg.message?.audioMessage) media = { type: 'audio', msg: msg.message.audioMessage };
      if (msg.message?.videoMessage) media = { type: 'video', msg: msg.message.videoMessage };
      
      const response = await this.router.route({
        text, media, sender: sender.replace(/[^0-9]/g, ''), jid, isGroup, messageKey: msg.key,
      });

      if (response) await this.sendMessage(jid, response);
    } catch (error) {
      console.error(`❌ Message handling error:`, error);
      await this.sendMessage(jid, this.formatter.error(error.message));
    }
  }

  async sendMessage(jid, content) {
    if (typeof content === 'string') {
      await this.sock.sendMessage(jid, { text: content });
    } else {
      await this.sock.sendMessage(jid, content);
    }
  }

  listenAPI() {
    this.app.listen(PORT, () => {
      console.log(`🌐 WA API Server running on port ${PORT}`);
    });
  }
}

// ─── START ───
const client = new WAClient();
client.listenAPI();
client.start().catch(console.error);

module.exports = { WAClient };
