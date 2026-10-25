/* ===========================================================
   diagrams.js - the generic set.

   art.js draws THINGS (a masjid, a wardrobe). This file draws
   SHAPES OF ARGUMENT, and takes its content from the spec. You
   do not add code to make a reel about compound interest or
   crop rotation or hiring - you pick the primitive whose shape
   matches the claim and pass it words and symbols.

   Twelve primitives cover almost everything:
     versus steps columns bars tiles figures
     grid rings arc balance symbol stack
   =========================================================== */

(() => {
const A = window.A, S = window.S;

const rr = (x,y,w,h,r,fill,extra='') =>
  `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" ${extra}/>`;
const mk = (markup, apply) => {
  const el = E.svg(markup);
  return {el, apply: apply ? (t) => apply(t, el) : () => {}};
};
const q = (el, id) => el.querySelector('#' + id);
const esc = (s) => String(s == null ? '' : s)
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

const strike = (id, x1, y1, x2, y2, c = 'var(--rose)', w = 10) =>
  `<line id="${id}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${c}"
     stroke-width="${w}" stroke-linecap="round"
     pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>`;
const drawStrike = (el, id, t, t0, dur = .42) => {
  const n = q(el, id); if (n) n.setAttribute('stroke-dashoffset', 1 - E.p(t, t0, dur, E.ease.out));
};
const vrule = (x, y1, y2) =>
  `<line x1="${x}" y1="${y1}" x2="${x}" y2="${y2}" stroke="var(--hairline)" stroke-width="2"/>`;

/* wrap a label onto at most 2 lines of `per` characters */
const wrap2 = (txt, per) => {
  const w = String(txt).split(' '); const out = ['']; 
  for (const word of w) {
    const i = out.length - 1;
    if ((out[i] + ' ' + word).trim().length <= per || !out[i]) out[i] = (out[i] + ' ' + word).trim();
    else out.push(word);
  }
  return out.slice(0, 2);
};
const lines = (txt, x, y, size, weight, fill, per = 16, lh = 1.18) =>
  wrap2(txt, per).map((ln, k, a) =>
    `<text x="${x}" y="${y + (k - (a.length - 1) / 2) * size * lh}" text-anchor="middle"
       font-family="Display" font-weight="${weight}" font-size="${size}"
       fill="${fill}" dominant-baseline="middle">${esc(ln)}</text>`).join('');

/* ---------- 1. versus: two things, side by side ----------- */
A.versus = (o = {}) => {
  const L = o.left || {}, R = o.right || {};
  const W = 960, H = 520, lx = 250, rx = 710, sy = 90, ss = o.size || 190;
  const side = (id, d, cx, tone) => `<g id="${id}">
      ${d.symbol ? S.at(d.symbol, cx - ss / 2, sy, ss, tone) : rr(cx - ss/2, sy, ss, ss, 22, tone)}
      ${d.label ? lines(d.label, cx, sy + ss + 78, 38, 600, 'var(--ink)', 15) : ''}
      ${d.note ? lines(d.note, cx, sy + ss + 158, 27, 400, 'var(--ink-dim)', 22) : ''}
    </g>`;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    ${side('vL', L, lx, L.tone || 'var(--structure-lit)')}
    ${o.divider === false ? '' : vrule(480, 40, H - 30)}
    ${side('vR', R, rx, R.tone || 'var(--accent)')}
    ${o.strike === 'left'  ? strike('kL', lx - 130, sy + ss + 30, lx + 130, sy - 30) : ''}
    ${o.strike === 'right' ? strike('kR', rx - 130, sy + ss + 30, rx + 130, sy - 30) : ''}
  </svg>`, (t, el) => {
    const a = E.p(t, .15, .55, E.ease.back), b = E.p(t, .55, .55, E.ease.back);
    const nL = q(el,'vL'), nR = q(el,'vR');
    nL.style.opacity = a; nL.style.transform = `translateY(${(1-a)*26}px)`;
    nR.style.opacity = b; nR.style.transform = `translateY(${(1-b)*26}px)`;
    drawStrike(el, 'kL', t, 1.35); drawStrike(el, 'kR', t, 1.35);
  });
};

/* ---------- 2. steps: a chain of consequence -------------- */
A.steps = (o = {}) => {
  const st = o.steps || [];
  const W = 1030, H = 300, n = st.length;
  const bw = Math.min(236, (W - 40 - (n - 1) * 44) / n), gap = 44;
  const x0 = (W - (n * bw + (n - 1) * gap)) / 2, by = 60, bh = 170;
  let g = '';
  st.forEach((s, i) => {
    const label = typeof s === 'string' ? s : s.label;
    const x = x0 + i * (bw + gap), last = i === n - 1 && o.strikeLast !== false && !!o.strikeLast;
    const hot = last || (o.highlightLast && i === n - 1);
    g += `<g id="sp${i}">
      <rect x="${x}" y="${by}" width="${bw}" height="${bh}" rx="20"
        fill="${hot ? 'var(--structure-hot)' : 'none'}"
        stroke="${hot ? 'none' : 'var(--accent-deep)'}" stroke-width="3.5"/>
      ${lines(label, x + bw/2, by + bh/2, 34, hot ? 700 : 500,
              hot ? 'var(--accent)' : 'var(--ink)', 13)}
      ${last ? strike('fs', x + 14, by + bh - 16, x + bw - 14, by + 16, 'var(--accent)', 9) : ''}
    </g>`;
    if (i < n - 1) {
      const ax = x + bw + 8;
      g += `<g id="sa${i}" opacity="0">
        <line x1="${ax}" y1="${by + bh/2}" x2="${ax + gap - 22}" y2="${by + bh/2}"
          stroke="var(--accent-deep)" stroke-width="5"/>
        <path d="M${ax + gap - 22} ${by + bh/2} l-16 -12 v24 Z" fill="var(--accent-deep)"/></g>`;
    }
  });
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${g}</svg>`, (t, el) => {
    st.forEach((_, i) => {
      const p = E.p(t, .2 + i * .42, .38, E.ease.out), nd = q(el, 'sp' + i);
      nd.style.opacity = p; nd.style.transform = `translateY(${(1 - p) * 16}px)`;
      const ar = q(el, 'sa' + i); if (ar) ar.style.opacity = E.p(t, .46 + i * .42, .3, E.ease.out);
    });
    drawStrike(el, 'fs', t, .3 + st.length * .42);
  });
};

/* ---------- 3. columns: n parallel items ------------------ */
A.columns = (o = {}) => {
  const items = o.items || [], n = items.length;
  const W = 1010, cw = Math.min(240, (W - 30 - (n - 1) * 18) / n), gap = 18;
  const H = 470, x0 = (W - (n * cw + (n - 1) * gap)) / 2;
  let g = '';
  items.forEach((it, i) => {
    const x = x0 + i * (cw + gap), cx = x + cw / 2;
    g += `<g id="cl${i}">
      ${o.numbered === false ? '' : `<text x="${cx}" y="40" text-anchor="middle" font-family="Meta"
        font-weight="700" font-size="29" fill="var(--ink-dim)">${i + 1}</text>`}
      ${it.top ? `<text x="${cx}" y="128" text-anchor="middle"
        font-family="${it.script === 'arabic' ? 'Arabic' : 'Display'}" font-weight="700"
        font-size="${it.script === 'arabic' ? 66 : 44}" fill="var(--accent)">${esc(it.top)}</text>` : ''}
      ${it.symbol ? S.at(it.symbol, cx - 64, 186, 128, 'var(--accent)') : ''}
      ${it.strike ? strike('cs' + i, cx - 84, 342, cx + 84, 192) : ''}
      ${it.caption ? lines(it.caption, cx, 420, 30, 700, 'var(--ink)', 14) : ''}
      ${i ? vrule(x - gap / 2, 18, H - 20) : ''}
    </g>`;
  });
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${g}</svg>`, (t, el) =>
    items.forEach((_, i) => {
      const p = E.p(t, .25 + i * .3, .45, E.ease.out), nd = q(el, 'cl' + i);
      nd.style.opacity = p; nd.style.transform = `translateY(${(1 - p) * 20}px)`;
      drawStrike(el, 'cs' + i, t, .58 + i * .3, .34);
    }));
};

/* ---------- 4. bars: magnitude and growth ----------------- */
A.bars = (o = {}) => {
  const v = o.values || [], labels = o.labels || [];
  const W = 940, H = 440, base = 350, n = v.length;
  const bw = Math.min(96, (W - 120) / n - 16);
  const gap = Math.min(bw * 1.15, (W - 120 - n * bw) / Math.max(1, n - 1));
  const bx0 = (W - (n * bw + (n - 1) * gap)) / 2;
  const max = Math.max(...v, 1), hi = o.highlight == null ? n - 1 : o.highlight;
  let g = '';
  v.forEach((val, i) => {
    const x = bx0 + i * (bw + gap), h = Math.max(10, (val / max) * 262);
    g += `<rect id="bb${i}" x="${x}" y="${base - h}" width="${bw}" height="${h}" rx="9"
        fill="${i === hi ? 'var(--accent)' : 'var(--structure-lit)'}"/>
      ${labels[i] ? `<text x="${x + bw/2}" y="${base + 40}" text-anchor="middle" font-family="Meta"
        font-weight="600" font-size="23" fill="var(--ink-dim)">${esc(labels[i])}</text>` : ''}
      ${o.showValues ? `<text id="bv${i}" x="${x + bw/2}" y="${base - h - 20}" text-anchor="middle"
        font-family="Display" font-weight="700" font-size="28"
        fill="${i === hi ? 'var(--accent)' : 'var(--ink-dim)'}">${esc(val)}</text>` : ''}`;
  });
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <line x1="48" y1="${base}" x2="${W - 48}" y2="${base}" stroke="var(--structure)" stroke-width="3"/>
    ${g}</svg>`, (t, el) => v.forEach((_, i) => {
      const p = E.p(t, .2 + i * .16, .45, E.ease.out), b = q(el, 'bb' + i);
      b.style.transform = `scaleY(${p})`;
      b.style.transformOrigin = `0px ${base}px`;
      b.style.opacity = p > 0 ? 1 : 0;
      const val = q(el, 'bv' + i); if (val) val.style.opacity = E.p(t, .4 + i * .16, .3, E.ease.out);
    }));
};

/* ---------- 5. tiles: a row of states --------------------- */
A.tiles = (o = {}) => {
  const items = o.items || [], active = o.active || [];
  const W = 960, H = 140, n = items.length;
  const tw = Math.min(112, (W - 40 - (n - 1) * 10) / n), gap = 10;
  const x0 = (W - (n * tw + (n - 1) * gap)) / 2;
  let g = '';
  items.forEach((d, i) => {
    const x = x0 + i * (tw + gap), on = active.includes(i);
    g += `<g id="tl${i}"><rect x="${x}" y="18" width="${tw}" height="98" rx="18"
        fill="${on ? 'var(--structure-hot)' : 'var(--structure)'}"/>
      <text x="${x + tw/2}" y="74" text-anchor="middle" font-family="Meta" font-weight="600"
        font-size="25" letter-spacing="1.5"
        fill="${on ? 'var(--accent)' : 'var(--ink-dim)'}">${esc(d)}</text></g>`;
  });
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${g}
    <g id="sweep" opacity="0"><rect x="${x0}" y="124" width="${tw}" height="7" rx="3.5" fill="var(--accent)"/></g>
  </svg>`, (t, el) => {
    items.forEach((_, i) => {
      const p = E.p(t, .2 + i * .055, .4, E.ease.back), nd = q(el, 'tl' + i);
      nd.style.opacity = p; nd.style.transform = `scale(${.72 + .28 * p})`;
      nd.style.transformOrigin = `${x0 + i * (tw + gap) + tw / 2}px 67px`;
    });
    if (o.sweep) {
      const s = E.p(t, .2 + items.length * .055 + .3, 1.4, E.ease.inOut), sw2 = q(el, 'sweep');
      sw2.style.opacity = s > 0 ? 1 : 0;
      sw2.style.transform = `translateX(${s * (items.length - 1) * (tw + gap)}px)`;
    }
  });
};

/* ---------- 6. figures: people --------------------------- */
A.figures = (o = {}) => {
  const n = o.count || 6, W = 960, H = 440, base = 350;
  const P = ['var(--rose)','var(--sky)','var(--skin)','var(--sage)','var(--bone)','var(--clay)'];
  const span = Math.min(86, 620 / n);
  const x0 = o.anchor ? 96 : (W - (n - 1) * span) / 2;
  const fig = (x, h, color, seated) => {
    const hr = h * (seated ? .21 : .165), bw = h * (seated ? .60 : .44);
    const bt = base - h + hr * 2 + h * .035;
    return `${rr(x - bw/2, bt, bw, base - bt, bw/2, color)}
            <circle cx="${x}" cy="${base - h + hr}" r="${hr}" fill="${color === 'var(--accent)' ? color : 'var(--skin)'}"/>`;
  };
  let row = '';
  for (let i = 0; i < n; i++) {
    const x = x0 + i * span;
    const h = o.heights === 'equal' ? 150 : [130,176,146,206,142,182,126,158][i % 8];
    const hot = o.highlight === i;
    row += `<g id="fg${i}" opacity="0" style="transform-origin:${x}px ${base}px">
      ${fig(x, hot ? h + 26 : h, hot ? 'var(--accent)' : P[i % P.length], !!o.seated)}</g>`;
  }
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <line x1="48" y1="${base}" x2="${W-48}" y2="${base}" stroke="var(--structure)" stroke-width="3"/>
    ${row}
    ${o.anchor ? `<g id="anc" opacity="0">
      <circle cx="844" cy="${base-150}" r="70" fill="var(--accent)"/>
      <circle cx="844" cy="${base-150}" r="106" fill="none" stroke="var(--halo)" stroke-width="6"/>
      <circle cx="844" cy="${base-150}" r="144" fill="none" stroke="var(--halo)" stroke-width="6" opacity=".5"/></g>` : ''}
  </svg>`, (t, el) => {
    for (let i = 0; i < n; i++) {
      const p = E.p(t, .3 + i * .08, .4, E.ease.back);
      const lean = o.lean ? E.p(t, 1.3 + i * .05, .6, E.ease.out) * 12 : 0;
      const g = q(el, 'fg' + i);
      g.style.opacity = p;
      g.style.transform = `translateY(${(1 - p) * 26}px) rotate(${lean}deg)`;
    }
    const an = q(el, 'anc');
    if (an) { const a = E.p(t, .15, .55, E.ease.back);
      an.style.opacity = a; an.style.transform = `scale(${.7 + .3 * a})`;
      an.style.transformOrigin = `844px ${base - 150}px`; }
  });
};

/* ---------- 7. grid: a matrix, some cells loose ----------- */
A.grid = (o = {}) => {
  const cols = o.cols || 3, rows = o.rows || 3, loose = o.loose || [];
  const cell = o.cell || 108, gap = 10;
  const W = cols * cell + (cols - 1) * gap, H = rows * cell + (rows - 1) * gap;
  let g = '';
  for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
    const i = r * cols + c, isLoose = loose.includes(i);
    g += `<g id="gc${i}">${rr(c * (cell + gap), r * (cell + gap), cell, cell, 11,
      isLoose ? 'var(--accent)' : 'var(--structure-lit)')}</g>`;
  }
  return mk(`<svg width="${W}" height="${H + 90}" viewBox="0 0 ${W} ${H + 90}">${g}</svg>`,
    (t, el) => {
      for (let i = 0; i < cols * rows; i++) {
        const nd = q(el, 'gc' + i);
        nd.style.opacity = E.p(t, .15 + i * .05, .35, E.ease.out);
        if (loose.includes(i)) {
          const l = E.p(t, 1.1 + loose.indexOf(i) * .2, .75, E.ease.back);
          nd.style.transform = `translate(${l * 86}px, ${l * 72}px) rotate(${l * 17}deg)`;
        }
      }
    });
};

/* ---------- 8. rings: a centre and what orbits it --------- */
A.rings = (o = {}) => {
  const W = 900, H = 620, cx = 450, cy = 300, labs = o.labels || [];
  let g = '';
  [138, 190, 244, 298].forEach((r, i) =>
    g += `<circle id="rg${i}" cx="${cx}" cy="${cy}" r="${r}" fill="none"
      stroke="var(--halo)" opacity="${1 - i * .22}" stroke-width="${4 - i * .5}"/>`);
  labs.forEach((l, i) => {
    const a = (-90 + i * (360 / labs.length)) * Math.PI / 180;
    g += `<text id="rl${i}" x="${cx + Math.cos(a) * 262}" y="${cy + Math.sin(a) * 262}"
      text-anchor="middle" dominant-baseline="middle" font-family="Display" font-weight="600"
      font-size="27" fill="var(--ink-soft)">${esc(l)}</text>`;
  });
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${g}
    ${o.symbol ? S.at(o.symbol, cx - 80, cy - 80, 160, 'var(--accent)') : ''}
    ${o.center ? `<text id="rc" x="${cx}" y="${cy}" text-anchor="middle" dominant-baseline="middle"
      font-family="${o.script === 'arabic' ? 'Arabic' : 'Display'}" font-weight="700"
      font-size="${o.script === 'arabic' ? 150 : 78}" fill="var(--accent)">${esc(o.center)}</text>` : ''}
    ${o.caption ? `<text id="rp" x="${cx}" y="${cy + 214}" text-anchor="middle" font-family="Meta"
      font-weight="700" font-size="29" letter-spacing="6" fill="var(--ink-soft)">${esc(o.caption)}</text>` : ''}
  </svg>`, (t, el) => {
    [0,1,2,3].forEach(i => {
      const p = E.p(t, .2 + i * .14, .7, E.ease.out), r = q(el, 'rg' + i);
      r.style.opacity = p; r.style.transform = `scale(${.72 + .28 * p})`;
      r.style.transformOrigin = `${cx}px ${cy}px`;
    });
    ['rc','rp'].forEach((id, k) => { const nd = q(el, id);
      if (nd) { const p = E.p(t, .4 + k * .6, .7, E.ease.back);
        nd.style.opacity = p; nd.style.transform = `scale(${.84 + .16 * p})`;
        nd.style.transformOrigin = `${cx}px ${cy}px`; } });
    labs.forEach((_, i) => { const nd = q(el, 'rl' + i);
      if (nd) nd.style.opacity = E.p(t, .9 + i * .18, .4, E.ease.out); });
  });
};

/* ---------- 9. arc: a share, a span, a countdown ---------- */
A.arc = (o = {}) => {
  const W = 760, H = 480, cx = 380, cy = 230, r = 150, C = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(1, o.pct == null ? .75 : o.pct));
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="var(--structure)" stroke-width="22"/>
    <circle id="ac" cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="var(--accent)" stroke-width="22"
      stroke-linecap="round" stroke-dasharray="${C}" stroke-dashoffset="${C}"
      transform="rotate(-90 ${cx} ${cy})"/>
    ${o.center ? `<text id="at" x="${cx}" y="${cy}" text-anchor="middle" dominant-baseline="middle"
      font-family="Display" font-weight="800" font-size="86" fill="var(--accent)">${esc(o.center)}</text>` : ''}
    ${o.caption ? `<text x="${cx}" y="${cy + 230}" text-anchor="middle" font-family="Display"
      font-weight="500" font-size="32" fill="var(--ink-soft)">${esc(o.caption)}</text>` : ''}
  </svg>`, (t, el) => {
    const p = E.p(t, .25, 1.5, E.ease.inOut);
    q(el, 'ac').setAttribute('stroke-dashoffset', C * (1 - p * pct));
    const n = q(el, 'at');
    if (n) n.style.opacity = E.p(t, .4, .5, E.ease.out);
  });
};

/* ---------- 10. balance: weigh two things ----------------- */
A.balance = (o = {}) => {
  const W = 880, H = 490, cx = 440, pivot = 160;
  const pan = (x, label) => `
      <line x1="${x}" y1="${pivot}" x2="${x}" y2="${pivot + 78}" stroke="var(--accent-deep)" stroke-width="5"/>
      <path d="M${x - 80} ${pivot + 78} h160 l-32 58 h-96 Z" fill="var(--accent-deep)"/>
      ${label ? rr(x - 36, pivot + 2, 72, 76, 11, 'var(--structure-lit)') : ''}`;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    ${rr(cx - 20, pivot, 40, 250, 10, 'var(--accent-deep)')}
    ${rr(cx - 110, 410, 220, 22, 11, 'var(--accent-deep)')}
    <g id="bm" style="transform-origin:${cx}px ${pivot}px">
      ${rr(cx - 240, pivot - 11, 480, 22, 11, 'var(--accent-deep)')}
      <g id="pL">${pan(cx - 210, o.left !== false)}</g>
      <g id="pR">${pan(cx + 210, !!o.right)}</g>
    </g>
    ${o.leftLabel ? lines(o.leftLabel, cx - 210, 452, 29, 600, 'var(--ink-soft)', 14) : ''}
    ${o.rightLabel ? lines(o.rightLabel, cx + 210, 452, 29, 600, 'var(--ink-soft)', 14) : ''}
  </svg>`, (t, el) => {
    const b = E.p(t, .2, .55, E.ease.out), bm = q(el, 'bm');
    bm.style.opacity = b;
    bm.style.transform = `rotate(${E.p(t, .85, .85, E.ease.out) * (o.tip == null ? 16 : o.tip)}deg)`;
    if (o.breakRight) {
      const br = E.p(t, 1.9, .5, E.ease.out), pr = q(el, 'pR');
      pr.style.opacity = 1 - br;
      pr.style.transform = `translate(${br * 62}px, ${br * 110}px) rotate(${br * 40}deg)`;
      pr.style.transformOrigin = `${cx + 210}px ${pivot}px`;
    }
  });
};

/* ---------- 11. symbol: one thing, large ------------------ */
A.symbol = (o = {}) => {
  const W = 620, H = 500, s = o.size || 300;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    <g id="sy">${S.at(o.name || 'question', (W - s) / 2, 40, s, o.tone || 'var(--accent)')}</g>
    ${o.caption ? lines(o.caption, W/2, 40 + s + 66, 34, 600, 'var(--ink-soft)', 22) : ''}
    ${o.strike ? strike('ss', (W-s)/2 - 20, 60 + s, (W+s)/2 + 20, 20) : ''}
  </svg>`, (t, el) => {
    const p = E.p(t, .2, .6, E.ease.back), n = q(el, 'sy');
    n.style.opacity = p; n.style.transform = `scale(${.78 + .22 * p})`;
    n.style.transformOrigin = `${W/2}px ${40 + s/2}px`;
    drawStrike(el, 'ss', t, 1.3);
  });
};

/* ---------- 12. stack: one thing or many pieces ----------- */
A.stack = (o = {}) => {
  const n = o.count || 4, W = 920, H = 500, top = 70, bh = 92, bw = 230;
  let g = '';
  for (let i = 0; i < n; i++)
    g += `<g id="sk${i}">${rr(96, top + i * (bh + 4), bw, bh, 10, 'var(--structure-lit)')}</g>`;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
    ${g}
    ${o.solid === false ? '' : vrule(460, 50, 450)}
    ${o.solid === false ? '' : `<g id="sol">${rr(594, top, bw, bh * n + (n - 1) * 4, 14, 'var(--accent)')}</g>`}
  </svg>`, (t, el) => {
    for (let i = 0; i < n; i++) {
      const p = E.p(t, .15 + i * .08, .4, E.ease.out), g2 = q(el, 'sk' + i);
      g2.style.opacity = p;
      const sp = o.split === false ? 0 : E.p(t, 1.0, .65, E.ease.back);
      g2.style.transform = `translate(${(i % 2 ? 1 : -1) * sp * 58}px, ${(i - (n-1)/2) * sp * 30}px)
                            rotate(${(i % 2 ? 1 : -1) * sp * 5}deg)`;
      g2.style.transformOrigin = `211px ${top + i * (bh + 4) + bh / 2}px`;
    }
    const so = q(el, 'sol');
    if (so) { const s2 = E.p(t, .75, .55, E.ease.back);
      so.style.opacity = s2; so.style.transform = `scale(${.84 + .16 * s2})`;
      so.style.transformOrigin = `709px ${top + (bh * n) / 2}px`; }
  });
};

A.GENERIC = ['versus','steps','columns','bars','tiles','figures','grid','rings','arc','balance','symbol','stack'];
})();
