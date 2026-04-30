// ═══════════════════════════════════════════════════════════════
// NEXUS v3.0 — RENDER HELPERS
// ═══════════════════════════════════════════════════════════════

export function sec(id, num, title, desc, content) {
  return `<section class="sec" id="${id}">
    <div class="sec-head"><span class="sec-num">${num}</span><h2>${title}</h2></div>
    ${desc ? `<p class="sec-desc">${desc}</p>` : ''}${content}</section>`;
}

export function modCard(m) {
  const tags = (m.tags||[]).map(([t,c])=>`<span class="mtag ${c}">${t}</span>`).join('');
  return `<div class="mod-card ${m.color}"><div class="mod-top"><span class="mod-icon">${m.icon}</span><span class="pill ${m.pill}">${m.pillText}</span></div><h3>${m.title}</h3><p>${m.desc}</p><div class="mod-tags">${tags}</div></div>`;
}

export function terminal(title, lines) {
  return `<div class="terminal"><div class="term-bar"><span class="term-dot td-r"></span><span class="term-dot td-y"></span><span class="term-dot td-g"></span><span class="term-title">${title}</span></div><div class="term-body">${lines}</div></div>`;
}

export function featureBlock(icon, title, desc, extra='') {
  return `<div class="feature-block"><h3>${icon} ${title}</h3><p>${desc}</p>${extra}</div>`;
}

export function secCard(cls, icon, title, desc, items) {
  const lis = items.map(i=>`<li>${i}</li>`).join('');
  return `<div class="sec-card ${cls}"><h3>${icon} ${title}</h3><p>${desc}</p><ul>${lis}</ul></div>`;
}

export function phase(num, done, meta, title, items) {
  const dots = done ? 'phase-dot done' : 'phase-dot';
  const pis = items.map(i=>`<span class="pi">${i}</span>`).join('');
  return `<div class="phase"><div class="${dots}">${num}</div><div class="phase-box"><div class="phase-meta">${meta}</div><h3>${title}</h3><div class="phase-items">${pis}</div></div></div>`;
}
