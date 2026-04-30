// ═══════════════════════════════════════════════════════════════
// WA AGENT NEXUS v3.0 — MASTER BLUEPRINT FRONTEND
// Secured Vite Edition — 25 Sections
// ═══════════════════════════════════════════════════════════════

import { NAV_ITEMS } from './sections.js';
import { renderSections1 } from './sections-render-1.js';
import { renderSections2 } from './sections-render-2.js';
import {
  devToolsChecker, verifyIntegrity, initMutationGuard,
  initCopyProtection, createSecurityBadge, createScrollTop,
} from './security.js';

// ─── HERO ───
function renderHero() {
  return `<div class="hero">
    <div class="hero-eyebrow">
      <span class="pill neon">WA AGENT</span>
      <span class="pill pink">ENTERPRISE</span>
      <span class="pill amber">v3.0 SECURED</span>
      <span class="pill purple">25 SECTIONS</span>
      <span class="pill blue">MONOREPO</span>
    </div>
    <h1><span class="g">Nexus</span> Master<br>Blueprint <span class="p">v3.0</span></h1>
    <p class="hero-sub">
      Enterprise-grade AI agent ecosystem. 21 Python + Node.js packages dalam Turborepo monorepo.
      LangGraph orchestrator, Ollama local LLM, multi-chain crypto tracker, YARA malware sandbox,
      conversational AI dengan emosi, dan voice processing — semua terproteksi dengan keamanan tingkat lanjut.
    </p>
    <div class="stats-row">
      <div class="stat"><span class="stat-val">25</span><span class="stat-label">Sections</span></div>
      <div class="stat"><span class="stat-val">21</span><span class="stat-label">Packages</span></div>
      <div class="stat"><span class="stat-val">70+</span><span class="stat-label">Files</span></div>
      <div class="stat"><span class="stat-val">17</span><span class="stat-label">Python Pkgs</span></div>
      <div class="stat"><span class="stat-val">4</span><span class="stat-label">Node.js Pkgs</span></div>
      <div class="stat"><span class="stat-val">4</span><span class="stat-label">Phases</span></div>
    </div>
  </div>`;
}

// ─── FOOTER ───
function renderFooter() {
  return `<footer>
    <p>⬡ WA AGENT NEXUS v3.0 · MASTER BLUEPRINT · SECURED EDITION</p>
    <p>Built with LangGraph · FastAPI · Baileys · Vite · Docker · Turborepo</p>
    <p>© 2025 Nexus Agent Ecosystem · All rights reserved</p>
  </footer>`;
}

// ─── NAVIGATION ───
function renderNav() {
  const links = NAV_ITEMS.map(n =>
    `<a href="#${n.id}">${n.label}</a>`
  ).join('');
  document.getElementById('navLinks').innerHTML = links;
}

// ─── SCROLL SPY ───
function initScrollSpy() {
  const sections = document.querySelectorAll('.sec');
  const links = document.querySelectorAll('.nav-links a');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        links.forEach(l => l.classList.remove('active'));
        const active = document.querySelector(`.nav-links a[href="#${entry.target.id}"]`);
        if (active) active.classList.add('active');
      }
    });
  }, { rootMargin: '-20% 0px -70% 0px' });

  sections.forEach(s => observer.observe(s));
}

// ─── INIT ───
function init() {
  const app = document.getElementById('app');

  // Render all content
  app.innerHTML = renderHero() + renderSections1() + renderSections2() + renderFooter();

  // Nav
  renderNav();

  // Security
  createSecurityBadge();
  createScrollTop();
  initMutationGuard();
  initCopyProtection();
  setInterval(devToolsChecker, 5000);
  setInterval(verifyIntegrity, 30000);

  // Scroll spy
  setTimeout(initScrollSpy, 100);

  console.log('%c⬡ NEXUS v3.0 BLUEPRINT LOADED', 'color: #00ffe0; font-size: 16px; font-weight: bold;');
  console.log('%c25 Sections · 21 Packages · Secured Edition', 'color: #5a5a80; font-size: 11px;');
}

// Start
document.addEventListener('DOMContentLoaded', init);
