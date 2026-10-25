/* ===========================================================
   engine.js - deterministic timeline runtime
   Nothing here uses requestAnimationFrame or CSS animation.
   The whole reel is a pure function of time: renderFrame(T)
   sets inline styles and nothing else. That is what makes
   frame-grabbing reproducible - grab frame 900 twice, get
   identical pixels.
   =========================================================== */

const E = {};

/* ---- easing ------------------------------------------------ */
E.ease = {
  linear: t => t,
  out:    t => 1 - Math.pow(1 - t, 3),           // the house default
  outQuint: t => 1 - Math.pow(1 - t, 5),
  inOut:  t => t < .5 ? 4*t*t*t : 1 - Math.pow(-2*t+2, 3)/2,
  back:   t => { const c=1.70158+1, p=1.70158;
                 return 1 + (c)*Math.pow(t-1,3) + p*Math.pow(t-1,2); },
  spring: t => t>=1?1: 1 - Math.pow(2,-9*t)*Math.cos(t*11.5),
  step:   t => t>=1?1:0,
};

/* clamped normalised progress through [t0,t1] */
E.p = (t, t0, dur, ease) => {
  if (dur <= 0) return t >= t0 ? 1 : 0;
  let u = (t - t0) / dur;
  u = u < 0 ? 0 : u > 1 ? 1 : u;
  return (ease || E.ease.out)(u);
};
/* value tween */
E.tw = (t, t0, dur, a, b, ease) => a + (b - a) * E.p(t, t0, dur, ease);
/* a pulse that rises then falls, for emphasis beats */
E.pulse = (t, t0, dur) => {
  let u = (t - t0) / dur; if (u <= 0 || u >= 1) return 0;
  return Math.sin(u * Math.PI);
};

E.el = (tag, cls, parent, html) => {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (html != null) n.innerHTML = html;
  if (parent) parent.appendChild(n);
  return n;
};
E.svg = (markup) => {
  const d = document.createElement('div');
  d.innerHTML = markup.trim();
  return d.firstElementChild;
};

/* ---- rich text --------------------------------------------
   Author headlines as plain strings with three marks:
     *words*   -> serif italic accent
     [words]   -> cream highlight box that wipes in
     **words** -> extra weight
   Returns {node, words:[...], hls:[...]} so the caller can
   stagger each word and wipe each highlight independently.
   ----------------------------------------------------------- */
E.richText = (str, node) => {
  const words = [], hls = [];
  // tokenise into runs carrying their style
  const runs = [];
  let i = 0, mode = {it:false, hl:false, bd:false};
  const push = (txt) => { if (txt) runs.push({txt, ...mode}); };
  let buf = '';
  while (i < str.length) {
    const two = str.slice(i, i+2);
    if (two === '**') { push(buf); buf=''; mode.bd=!mode.bd; i+=2; continue; }
    const c = str[i];
    if (c === '*')  { push(buf); buf=''; mode.it=!mode.it; i++; continue; }
    if (c === '[')  { push(buf); buf=''; mode.hl=true;  i++; continue; }
    if (c === ']')  { push(buf); buf=''; mode.hl=false; i++; continue; }
    buf += c; i++;
  }
  push(buf);

  // group consecutive highlighted runs into one box
  let hlBox = null;
  for (const r of runs) {
    if (!r.hl) hlBox = null;
    for (const piece of r.txt.split(/(\s+)/)) {
      if (piece === '') continue;
      if (/^\s+$/.test(piece)) {
        // whitespace: inside a highlight it belongs to the box
        if (r.hl && hlBox) hlBox.appendChild(document.createTextNode(piece));
        else node.appendChild(document.createTextNode(piece));
        continue;
      }
      const w = document.createElement('span');
      w.className = 'w';
      if (r.it) { const em = document.createElement('em'); em.textContent = piece; w.appendChild(em); }
      else w.textContent = piece;
      if (r.bd) w.style.fontWeight = 800;

      if (r.hl) {
        if (!hlBox) {
          hlBox = document.createElement('span');
          hlBox.className = 'hl';
          const fill = document.createElement('span');
          fill.className = 'fill';
          hlBox.appendChild(fill);
          node.appendChild(hlBox);
          hls.push({box: hlBox, fill, firstWord: words.length});
        }
        hlBox.appendChild(w);
      } else {
        node.appendChild(w);
      }
      words.push(w);
    }
  }
  return {node, words, hls};
};

/* word-by-word reveal + highlight wipe, driven by t */
E.applyRichText = (rt, t, t0, {stagger=0.085, rise=26, dur=0.42} = {}) => {
  rt.words.forEach((w, k) => {
    const s = t0 + k * stagger;
    const p = E.p(t, s, dur, E.ease.out);
    w.style.opacity = p;
    w.style.transform = `translateY(${(1-p) * rise}px)`;
  });
  rt.hls.forEach(h => {
    const s = t0 + h.firstWord * stagger + 0.10;
    const p = E.p(t, s, 0.34, E.ease.outQuint);
    h.fill.style.transform = `scaleX(${p})`;
    // the ink only flips to dark once the cream is under it
    const inked = E.p(t, s + 0.10, 0.14, E.ease.linear);
    h.box.style.color = inked > .5 ? 'var(--cream-ink)' : 'var(--ink)';
  });
};

/* ---- shared furniture -------------------------------------- */
E.ground = (parent) => {
  const g = E.el('div', 'ground', parent);
  E.el('div', 'grid', g);
  const wash = E.el('div', 'wash', g);
  E.el('div', 'vignette', g);
  return {g, wash};
};

E.IG_GLYPH = `<svg class="glyph" viewBox="0 0 24 24" fill="none" stroke="#efe3ea" stroke-width="1.9">
  <rect x="2.6" y="2.6" width="18.8" height="18.8" rx="5.4"/>
  <circle cx="12" cy="12" r="4.6"/><circle cx="17.6" cy="6.4" r="1.25" fill="#efe3ea" stroke="none"/></svg>`;

/* An empty or missing meta.handle means no watermark anywhere and no name
   on the follow card. Use that for a reel whose destination account is not
   decided yet - a wrong handle burned into the frame is worse than none. */
E.watermark = (parent, handle) => {
  if (!handle) return null;
  const m = E.el('div', 'mark', parent);
  m.innerHTML = E.IG_GLYPH + `<div class="handle">${handle.toUpperCase()}</div>`;
  return m;
};

/* ---- reel builder ------------------------------------------ */
E.build = (spec) => {
  const stage = document.getElementById('stage');
  stage.innerHTML = '';
  const ground = E.ground(stage);
  const scenes = [];
  let clock = 0;

  for (const def of spec.scenes) {
    const root = E.el('section', 'scene', stage);
    const maker = E.scenes[def.type];
    if (!maker) throw new Error('unknown scene type: ' + def.type);
    const inst = maker(root, def, spec);
    scenes.push({start: clock, dur: def.dur, root, inst, def});
    clock += def.dur;
  }
  spec.totalDur = clock;

  window.renderFrame = (T) => {
    for (const s of scenes) {
      const local = T - s.start;
      const live = local >= -0.001 && local < s.dur + 0.001;
      s.root.classList.toggle('on', live);
      if (!live) continue;
      // scene-level cross fade: 140ms in, 160ms out
      const fin  = E.p(local, 0, 0.14, E.ease.linear);
      const fout = 1 - E.p(local, s.dur - 0.16, 0.16, E.ease.linear);
      s.root.style.opacity = Math.min(fin, fout);
      // the ground wash belongs to whichever scene is live
      ground.wash.style.background = s.def.wash || 'transparent';
      s.inst.apply(local);
    }
  };
  window.reelDuration = clock;
  return spec;
};

window.E = E;
