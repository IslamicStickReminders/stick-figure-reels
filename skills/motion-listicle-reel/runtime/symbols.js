/* ===========================================================
   symbols.js - a flat glyph set the diagram primitives place.

   The point of this file: an idea should become art by naming
   a symbol, not by writing new code. Every glyph is drawn on a
   100x100 box with its origin at the top-left, uses currentColor
   so the primitive decides the tone, and uses only strokes and
   flat fills. Add to it freely; keep the 100x100 contract.
   =========================================================== */

const S = {};
const sw = 7;   // one stroke weight for the whole set, so they mix

S.person   = `<circle cx="50" cy="26" r="17"/><path d="M19 92v-8a31 31 0 0 1 62 0v8" />`;
S.people   = `<circle cx="34" cy="28" r="14"/><path d="M8 92v-7a26 26 0 0 1 52 0v7"/>
              <circle cx="72" cy="32" r="12"/><path d="M58 92v-6a22 22 0 0 1 36 -17"/>`;
S.house    = `<path d="M12 48 50 16l38 32"/><path d="M22 44v44h56V44"/><path d="M42 88V62h16v26"/>`;
S.building = `<path d="M22 90V18h56v72"/><path d="M36 34h10M54 34h10M36 52h10M54 52h10M36 70h10M54 70h10"/>`;
S.clock    = `<circle cx="50" cy="50" r="36"/><path d="M50 28v24l16 10"/>`;
S.calendar = `<rect x="16" y="24" width="68" height="62" rx="7"/><path d="M16 44h68M34 14v18M66 14v18"/>`;
S.book     = `<path d="M50 28c-10-8-22-10-34-9v54c12-1 24 1 34 9 10-8 22-10 34-9V19c-12-1-24 1-34 9z"/><path d="M50 28v54"/>`;
S.phone    = `<rect x="30" y="12" width="40" height="76" rx="8"/><path d="M44 24h12"/><circle cx="50" cy="76" r="4"/>`;
S.screen   = `<rect x="12" y="20" width="76" height="50" rx="6"/><path d="M36 86h28M50 70v16"/>`;
S.money    = `<rect x="12" y="28" width="76" height="44" rx="7"/><circle cx="50" cy="50" r="13"/><path d="M26 50h2M72 50h2"/>`;
S.coin     = `<circle cx="50" cy="50" r="33"/><path d="M50 30v40M40 40h16a8 8 0 0 1 0 16h-12a8 8 0 0 0 0 16h16"/>`;
S.chart    = `<path d="M16 86V30M16 86h70"/><path d="M32 72v-18M48 72v-32M64 72v-24M80 72v-40"/>`;
S.seed     = `<path d="M50 88V46"/><path d="M50 46c0-16 12-28 28-28 0 16-12 28-28 28z"/><path d="M50 56c0-14-10-24-24-24 0 14 10 24 24 24z"/>`;
S.tree     = `<path d="M50 90V58"/><circle cx="50" cy="38" r="26"/>`;
S.bulb     = `<path d="M34 54a20 20 0 1 1 32 0c-5 6-7 10-7 16H41c0-6-2-10-7-16z"/><path d="M41 80h18M44 88h12"/>`;
S.brain    = `<path d="M44 18a16 16 0 0 0-16 16 14 14 0 0 0-6 24 14 14 0 0 0 12 20 14 14 0 0 0 10 4V18z"/>
              <path d="M56 18a16 16 0 0 1 16 16 14 14 0 0 1 6 24 14 14 0 0 1-12 20 14 14 0 0 1-10 4V18z"/>`;
S.eye      = `<path d="M8 50s16-26 42-26 42 26 42 26-16 26-42 26S8 50 8 50z"/><circle cx="50" cy="50" r="13"/>`;
S.heart    = `<path d="M50 84S14 62 14 38a20 20 0 0 1 36-12 20 20 0 0 1 36 12c0 24-36 46-36 46z"/>`;
S.shield   = `<path d="M50 88S18 74 18 44V24l32-12 32 12v20c0 30-32 44-32 44z"/>`;
S.lock     = `<rect x="22" y="44" width="56" height="44" rx="8"/><path d="M34 44V32a16 16 0 0 1 32 0v12"/>`;
S.key      = `<circle cx="32" cy="50" r="18"/><path d="M50 50h38M76 50v14M64 50v10"/>`;
S.door     = `<rect x="26" y="12" width="48" height="78" rx="5"/><circle cx="62" cy="52" r="4"/>`;
S.bridge   = `<path d="M8 66h84"/><path d="M8 66c20-34 64-34 84 0"/><path d="M30 66V50M50 66V42M70 66V50"/>`;
S.mountain = `<path d="M8 82 38 34l18 26 10-14 18 36z"/>`;
S.cloud    = `<path d="M30 76a20 20 0 0 1 2-40 24 24 0 0 1 44-4 18 18 0 0 1 4 44z"/>`;
S.star     = `<path d="M50 12l11 24 26 3-19 18 5 26-23-13-23 13 5-26-19-18 26-3z"/>`;
S.flag     = `<path d="M26 92V14"/><path d="M26 18h46l-10 15 10 15H26"/>`;
S.target   = `<circle cx="50" cy="50" r="34"/><circle cx="50" cy="50" r="20"/><circle cx="50" cy="50" r="6"/>`;
S.scale    = `<path d="M50 16v72M26 88h48"/><path d="M14 36h72"/><path d="M14 36 4 60h20zM86 36 76 60h20z"/>`;
S.gear     = `<circle cx="50" cy="50" r="16"/><path d="M50 10v12M50 78v12M10 50h12M78 50h12M22 22l8 8M70 70l8 8M78 22l-8 8M30 70l-8 8"/>`;
S.link     = `<path d="M42 58 58 42"/><path d="M38 34l8-8a18 18 0 0 1 26 26l-8 8"/><path d="M62 66l-8 8a18 18 0 0 1-26-26l8-8"/>`;
S.arrowUp  = `<path d="M50 86V20"/><path d="M26 44 50 20l24 24"/>`;
S.warning  = `<path d="M50 14 90 84H10z"/><path d="M50 44v20M50 74v2"/>`;
S.check    = `<circle cx="50" cy="50" r="36"/><path d="M32 52l12 13 24-28"/>`;
S.cross    = `<circle cx="50" cy="50" r="36"/><path d="M34 34l32 32M66 34 34 66"/>`;
S.question = `<circle cx="50" cy="50" r="36"/><path d="M38 40a12 12 0 1 1 14 14v8"/><path d="M52 72v2"/>`;
S.drop     = `<path d="M50 12c16 20 26 32 26 44a26 26 0 0 1-52 0c0-12 10-24 26-44z"/>`;
S.fire     = `<path d="M50 88a24 24 0 0 0 24-24c0-20-24-36-24-52-6 14-20 20-20 34a12 12 0 0 0 8 11c-6 4-12 8-12 19a24 24 0 0 0 24 12z"/>`;
S.box      = `<path d="M50 14 86 32v36L50 86 14 68V32z"/><path d="M14 32 50 50l36-18M50 50v36"/>`;

/* render a symbol into a group at (x,y) sized s, in `tone` */
S.at = (name, x, y, s, tone = 'var(--accent)', fill = 'none') => {
  const g = S[name] || S.question;
  return `<g transform="translate(${x},${y}) scale(${s / 100})"
            stroke="${tone}" stroke-width="${sw}" fill="${fill}"
            stroke-linecap="round" stroke-linejoin="round" color="${tone}">${g}</g>`;
};
S.names = Object.keys(S).filter(k => typeof S[k] === 'string');

window.S = S;
