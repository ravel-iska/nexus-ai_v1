// ═══════════════════════════════════════════════════════════════
// DEVTOOLS MONITOR — Website inspector, leak detector, cache manager
// ═══════════════════════════════════════════════════════════════

const { chromium } = require('playwright');

class WebsiteInspector {
  constructor() {
    this.browser = null;
  }

  async init() {
    if (!this.browser) {
      this.browser = await chromium.launch({ headless: true });
    }
  }

  async inspectUrl(url) {
    await this.init();
    const page = await this.browser.newPage();

    const results = {
      url,
      status: null,
      loadTime: 0,
      links: { total: 0, broken: [], external: [] },
      resources: { total: 0, failed: [] },
      securityHeaders: {},
      seo: {},
      performance: {},
    };

    const failedResources = [];
    page.on('requestfailed', (req) => {
      failedResources.push({ url: req.url(), error: req.failure()?.errorText });
    });

    try {
      const start = Date.now();
      const response = await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
      results.loadTime = Date.now() - start;
      results.status = response?.status();

      // Security headers
      const headers = response?.headers() || {};
      results.securityHeaders = {
        csp: headers['content-security-policy'] || null,
        xFrame: headers['x-frame-options'] || null,
        xContentType: headers['x-content-type-options'] || null,
        hsts: headers['strict-transport-security'] || null,
      };

      // SEO check
      results.seo = await page.evaluate(() => ({
        title: document.title,
        description: document.querySelector('meta[name="description"]')?.content || null,
        h1Count: document.querySelectorAll('h1').length,
        imgWithoutAlt: document.querySelectorAll('img:not([alt])').length,
        hasCanonical: !!document.querySelector('link[rel="canonical"]'),
      }));

      // Broken links
      const links = await page.evaluate(() =>
        Array.from(document.querySelectorAll('a[href]')).map(a => ({
          href: a.href, text: a.textContent?.trim().slice(0, 50),
          isExternal: !a.href.startsWith(location.origin),
        }))
      );
      results.links.total = links.length;
      results.links.external = links.filter(l => l.isExternal).slice(0, 20);

      results.resources.failed = failedResources;
      results.resources.total = failedResources.length;

    } catch (error) {
      results.error = error.message;
    } finally {
      await page.close();
    }

    return results;
  }

  async detectLeaks(url) {
    await this.init();
    const page = await this.browser.newPage();
    const leaks = [];

    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 20000 });

      // Check for exposed sensitive data in page source
      const source = await page.content();
      const patterns = [
        { name: 'API Key', regex: /['"](sk-[a-zA-Z0-9]{20,}|AKIA[A-Z0-9]{16})['"]/g },
        { name: 'Email', regex: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g },
        { name: 'AWS Secret', regex: /['"](AKIA[A-Z0-9]{16})['"]/g },
        { name: 'Private Key', regex: /-----BEGIN (RSA |EC )?PRIVATE KEY-----/g },
        { name: 'JWT Token', regex: /eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}/g },
        { name: 'Password in URL', regex: /password[=:]["']?[^&\s'"]{3,}/gi },
      ];

      for (const pattern of patterns) {
        const matches = source.match(pattern.regex);
        if (matches) {
          leaks.push({
            type: pattern.name,
            count: matches.length,
            severity: 'critical',
            samples: matches.slice(0, 3).map(m => m.slice(0, 30) + '...'),
          });
        }
      }

    } catch (error) {
      leaks.push({ type: 'error', message: error.message });
    } finally {
      await page.close();
    }

    return { url, leaks, leak_count: leaks.length };
  }

  async close() {
    if (this.browser) await this.browser.close();
  }
}

module.exports = { WebsiteInspector };
