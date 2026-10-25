/* ===========================================================
   scenes.js - the four scene types.
   A reel is: title -> N item scenes -> recap -> cta.
   Nothing else. The format's power is its sameness; the only
   thing that changes frame to frame is the art and the words.
   =========================================================== */

E.scenes = {};

/* shared: watermark + optional citation chip ---------------- */
function furniture(root, def, spec) {
  E.watermark(root, spec.meta.handle);
  let cite = null;
  if (def.cite) {
    cite = E.el('div', 'cite', root, def.cite);
    cite.style.bottom = (def.citeBottom || 225) + 'px';
  }
  return cite;
}
function applyFurniture(cite, t, dur) {
  if (!cite) return;
  const p = E.p(t, 0.85, 0.45, E.ease.out);
  const out = 1 - E.p(t, dur - 0.4, 0.3, E.ease.linear);
  cite.style.opacity = p * out;
  cite.style.transform = `translateX(-50%) translateY(${(1 - p) * 14}px)`;
}

/* ---------- title ------------------------------------------ */
E.scenes.title = (root, def, spec) => {
  const h = E.el('div', 'headline lead', root);
  h.style.top = (def.top || 230) + 'px';
  const rt = E.richText(def.text, h);
  const holder = E.el('div', 'art', root);
  holder.style.top = (def.artTop || 620) + 'px';
  if (def.artScale) holder.style.transform = `scale(${def.artScale})`;
  const art = (A[def.art] || A.masjid)(def.artOpts || {});
  holder.appendChild(art.el);
  furniture(root, def, spec);
  return {apply: (t) => {
    E.applyRichText(rt, t, 0.18, {stagger: 0.10, rise: 34});
    art.apply(t - 0.25);
  }};
};

/* ---------- item ------------------------------------------- */
E.scenes.item = (root, def, spec) => {
  const h = E.el('div', 'headline', root);
  h.style.top = (def.top || 300) + 'px';
  const rt = E.richText(def.text, h);

  let sub = null, subRt = null;
  if (def.sub) {
    sub = E.el('div', 'subline', root);
    sub.style.top = (def.subTop || 470) + 'px';
    subRt = E.richText(def.sub, sub);
  }

  let num = null;
  if (def.big) {
    num = E.el('div', 'bignum', root,
      `<span class="v">${def.big}</span>${def.bigUnit ? `<span class="unit">${def.bigUnit}</span>` : ''}`);
    num.style.top = (def.bigTop || 560) + 'px';
  }

  const holder = E.el('div', 'art', root);
  holder.style.top = (def.artTop || 980) + 'px';
  if (def.artScale) holder.style.transform = `scale(${def.artScale})`;
  let art = null;
  if (def.art) {
    art = (A[def.art] || (() => ({el: E.svg('<svg width="10" height="10"></svg>'), apply(){}})))(def.artOpts || {});
    holder.appendChild(art.el);
  }
  let art2 = null;
  if (def.art2) {
    const h2 = E.el('div', 'art', root);
    h2.style.top = (def.art2Top || 700) + 'px';
    if (def.art2Scale) h2.style.transform = `scale(${def.art2Scale})`;
    art2 = A[def.art2](def.art2Opts || {});
    h2.appendChild(art2.el);
  }

  const cite = furniture(root, def, spec);

  return {apply: (t) => {
    E.applyRichText(rt, t, 0.12, {stagger: 0.085, rise: 26});
    if (subRt) E.applyRichText(subRt, t, 0.42, {stagger: 0.06, rise: 18});
    if (num) {
      // count up, then settle with a small overshoot
      const p = E.p(t, 0.55, 0.9, E.ease.outQuint);
      const target = parseFloat(String(def.big).replace(/[^\d.]/g, '')) || 0;
      const shown = Math.round(target * p);
      const prefix = String(def.big).startsWith('+') ? '+' : '';
      num.querySelector('.v').textContent = prefix + shown;
      const pop = 1 + E.pulse(t, 1.35, 0.4) * 0.05;
      num.style.opacity = E.p(t, 0.5, 0.3, E.ease.out);
      num.style.transform = `scale(${pop})`;
    }
    if (art)  art.apply(t - (def.artDelay  != null ? def.artDelay  : 0.30));
    if (art2) art2.apply(t - (def.art2Delay != null ? def.art2Delay : 0.45));
    applyFurniture(cite, t, def.dur);
  }};
};

/* ---------- recap ------------------------------------------ */
E.scenes.recap = (root, def, spec) => {
  const box = E.el('div', 'recap', root);
  box.style.top = (def.top || 440) + 'px';
  E.el('div', 'kicker', box, def.kicker || 'THIS FRIDAY');
  const rows = def.items.map((it, i) => {
    const r = E.el('div', 'row', box);
    E.el('div', 'n', r, String(i + 1));
    E.el('div', 't', r, it.t);
    if (it.s) E.el('div', 's', r, it.s);
    return r;
  });
  E.watermark(root, spec.meta.handle);
  return {apply: (t) => {
    box.querySelector('.kicker').style.opacity = E.p(t, 0.1, 0.35, E.ease.out);
    rows.forEach((r, i) => {
      const p = E.p(t, 0.28 + i * 0.22, 0.42, E.ease.out);
      r.style.opacity = p;
      r.style.transform = `translateY(${(1 - p) * 26}px)`;
    });
  }};
};

/* ---------- cta -------------------------------------------- */
E.scenes.cta = (root, def, spec) => {
  const card = E.el('div', 'cta', root);
  const av = E.el('div', 'av', card, '<b></b><i></i>');
  const name = spec.meta.handle ? E.el('div', 'name', card, spec.meta.handle) : null;
  const say = E.el('div', 'say', card, def.say || 'Follow for more');
  const arrow = E.el('div', 'arrow', card, '&#8595;');
  const wrap = E.el('div', 'btnwrap', card);
  const ring = E.el('div', 'ring', wrap);
  const btn = E.el('div', 'btn', wrap, def.btn || 'Follow');
  E.watermark(root, spec.meta.handle);
  return {apply: (t) => {
    const p = E.p(t, 0.1, 0.6, E.ease.back);
    card.style.opacity = p;
    card.style.transform = `translateY(${(1 - p) * 40}px) scale(${0.92 + 0.08 * p})`;
    [av, name, say, arrow].filter(Boolean).forEach((n, i) => {
      const q = E.p(t, 0.3 + i * 0.12, 0.4, E.ease.out);
      n.style.opacity = q;
      n.style.transform = `translateY(${(1 - q) * 16}px)`;
    });
    const bp = E.p(t, 0.85, 0.45, E.ease.back);
    btn.style.opacity = bp;
    btn.style.transform = `scale(${0.8 + 0.2 * bp})`;
    // the follow flips near the end - the whole point of the card
    const flipped = t > (def.flipAt != null ? def.flipAt : def.dur - 1.5);
    btn.classList.toggle('done', flipped);
    btn.textContent = flipped ? (def.btnDone || 'Following') : (def.btn || 'Follow');
    const rp = E.p(t, 1.0, 1.1, E.ease.out);
    ring.style.opacity = rp * 0.9;
    ring.style.transform = `scale(${0.55 + 0.45 * rp})`;
  }};
};
