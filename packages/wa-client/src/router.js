// ═══════════════════════════════════════════════════════════════
// ROUTER — Command routing to API backend
// ═══════════════════════════════════════════════════════════════

const axios = require('axios');

class Router {
  constructor(config) {
    this.apiUrl = config.apiBackendUrl || 'http://localhost:8000';
    this.adminNumber = config.adminNumber || '';
  }

  async route({ text, media, sender, jid, isGroup, messageKey }) {
    // Skip empty messages
    if (!text && !media) return null;

    // Send to Python backend for AI processing
    try {
      const payload = {
        user_id: sender,
        session_id: jid,
        message: text || '[MEDIA]',
        media_type: media?.type || null,
        media_url: null,
      };

      const { data } = await axios.post(`${this.apiUrl}/api/v1/agent/chat`, payload, {
        timeout: 120000, // 2 minute timeout for complex tasks
        headers: { 'Content-Type': 'application/json' },
      });

      return data.response || '⚠️ Tidak ada respons dari agent.';

    } catch (error) {
      if (error.response) {
        console.error(`❌ API Error ${error.response.status}:`, error.response.data);
        return `⚠️ API Error: ${error.response.data?.error || 'Unknown error'}`;
      }
      console.error('❌ Network error:', error.message);
      return '⚠️ Tidak bisa menghubungi server AI. Pastikan backend berjalan.';
    }
  }
}

module.exports = { Router };
