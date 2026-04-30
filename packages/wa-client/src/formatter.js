// ═══════════════════════════════════════════════════════════════
// FORMATTER — Beautiful WA output formatting
// ═══════════════════════════════════════════════════════════════

class Formatter {
  systemBoot() {
    return [
      '╔══════════════════════════════════════╗',
      '║   🤖 WA AGENT NEXUS v3.0            ║',
      '║   Status: ONLINE & SECURED           ║',
      '╚══════════════════════════════════════╝',
      '',
      '⚡ AI Engine  : Active (Local + Cloud)',
      '🧠 Memory     : Redis + PostgreSQL',
      '🔒 Security   : JWT + Rate Limit + CSP',
      '📦 Skills     : Hot-reload ready',
      '🔗 Blockchain : Multi-chain tracker',
      '🔍 OSINT      : Intelligence engine',
      '',
      '💡 Ketik !help untuk daftar perintah.',
    ].join('\n');
  }

  error(message) {
    return [
      '╔══════════════════════════════════════╗',
      '║   🚨 ERROR                            ║',
      '╚══════════════════════════════════════╝',
      '',
      `❌ ${message}`,
      '',
      '💡 Coba lagi atau ketik !help',
    ].join('\n');
  }

  searchResult(results) {
    let output = [
      '╔══════════════════════════════════════╗',
      '║   🔍 SEARCH RESULTS                  ║',
      '╚══════════════════════════════════════╝',
      '',
    ];

    results.forEach((item, i) => {
      output.push(`${i + 1}. *${item.title}*`);
      output.push(`   💰 ${item.price || 'N/A'}`);
      output.push(`   🔗 ${item.url || ''}`);
      output.push('');
    });

    return output.join('\n');
  }

  osintReport(data) {
    return [
      '╔══════════════════════════════════════╗',
      '║   🔍 OSINT RECON REPORT              ║',
      '╚══════════════════════════════════════╝',
      '',
      `🎯 Target: ${data.target}`,
      '─────────────────────────────────────',
      `✔ WHOIS       → ${data.whois || 'N/A'}`,
      `✔ DNS         → ${data.dns || 'N/A'}`,
      `✔ Subdomains  → ${data.subdomains || 'N/A'}`,
      `✔ Tech Stack  → ${data.tech || 'N/A'}`,
      `${data.sslWarning ? '⚠ SSL         → ' + data.sslWarning : '✔ SSL         → Valid'}`,
      '─────────────────────────────────────',
      `📊 Risk Score: ${data.riskScore || 'N/A'}`,
    ].join('\n');
  }

  cryptoPortfolio(data) {
    let output = [
      '╔══════════════════════════════════════╗',
      '║   📈 CRYPTO PORTFOLIO                ║',
      '╚══════════════════════════════════════╝',
      '',
      `💰 Total Value: $${data.totalValue || '0'}`,
      `📊 24h Change:  ${data.change24h || '0%'}`,
      '',
    ];

    (data.assets || []).forEach(asset => {
      const icon = asset.change >= 0 ? '🟢' : '🔴';
      output.push(`${icon} ${asset.symbol}: $${asset.value} (${asset.change}%)`);
    });

    return output.join('\n');
  }
}

module.exports = { Formatter };
