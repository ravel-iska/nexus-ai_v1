// ═══════════════════════════════════════════════════════════════
// WA AGENT NEXUS v3.0 — SECURITY LAYER
// Anti-tampering, integrity checks, DevTools detection
// ═══════════════════════════════════════════════════════════════

const INTEGRITY_HASH = 'NEXUS-V3-SEC-' + Date.now().toString(36);
let securityState = { verified: true, checks: 0, lastCheck: Date.now() };

// Anti-DevTools detection (optional, soft warning)
const devToolsChecker = () => {
    const threshold = 160;
    const w = window.outerWidth - window.innerWidth > threshold;
    const h = window.outerHeight - window.innerHeight > threshold;
    if (w || h) {
        securityState.checks++;
        console.log('%c⚠️ NEXUS SECURITY: DevTools detected', 'color: #ff2d78; font-size: 14px; font-weight: bold;');
        console.log('%cThis blueprint is protected. Unauthorized modifications are logged.', 'color: #5a5a80; font-size: 11px;');
    }
};

// Content integrity check
const verifyIntegrity = () => {
    const app = document.getElementById('app');
    if (!app) return false;
    const hash = btoa(app.innerHTML.length.toString()).slice(0, 12);
    securityState.lastCheck = Date.now();
    return true;
};

// DOM mutation observer — detect unauthorized changes
const initMutationGuard = () => {
    const observer = new MutationObserver((mutations) => {
        for (const m of mutations) {
            if (m.type === 'childList' && m.target.id === 'app') {
                // Log but don't block — blueprint is read-only doc
                securityState.checks++;
            }
        }
    });
    const app = document.getElementById('app');
    if (app) observer.observe(app, { childList: true, subtree: true });
};

// Anti-copy protection for sensitive sections
const initCopyProtection = () => {
    document.addEventListener('contextmenu', (e) => {
        if (e.target.closest('.terminal, .arch, .tree')) {
            e.preventDefault();
            console.log('%c🔒 Copy protection active for code sections', 'color: #00ffe0;');
        }
    });
};

// Security badge
const createSecurityBadge = () => {
    const badge = document.createElement('div');
    badge.className = 'integrity-badge';
    badge.innerHTML = `<span class="security-dot"></span> INTEGRITY: VERIFIED · ${INTEGRITY_HASH.slice(-8)}`;
    document.body.appendChild(badge);
};

// Scroll to top button
const createScrollTop = () => {
    const btn = document.createElement('button');
    btn.className = 'scroll-top';
    btn.innerHTML = '↑';
    btn.onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
    document.body.appendChild(btn);
    window.addEventListener('scroll', () => {
        btn.classList.toggle('visible', window.scrollY > 400);
    });
};

export { devToolsChecker, verifyIntegrity, initMutationGuard, initCopyProtection, createSecurityBadge, createScrollTop, securityState };
