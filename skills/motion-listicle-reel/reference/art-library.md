# Art library

Two kinds of piece live in `runtime/`.

**`diagrams.js` - the generic set.** Twelve shapes of claim that take their
content from the spec. Use these. They cover almost every idea and need no
new code for a new subject. `reference/idea-to-art.md` maps claims to them.

**`art.js` - the specific set.** Twenty-five hand-drawn pieces built for
particular reels (a masjid, a wardrobe, a minbar, a trefoil). Useful when a
subject repeats often enough to earn bespoke art, and useful as worked
examples of the house drawing rules. Not where to start.

Every piece returns `{el, apply(t)}` and animates itself from `t = 0` at
its `artDelay`.

## The generic twelve

| name | natural size | key options |
|---|---|---|
| `versus` | 960x520 | `left`/`right` each `{symbol, label, note, tone}`, `strike:'left'\|'right'`, `divider` |
| `steps` | 1030x300 | `steps:[label]`, `strikeLast`, `highlightLast` |
| `columns` | 1010x470 | `items:[{top, script, symbol, caption, strike}]`, `numbered` |
| `bars` | 940x440 | `values:[]`, `labels:[]`, `highlight`, `showValues` |
| `tiles` | 960x140 | `items:[]`, `active:[i]`, `sweep` |
| `figures` | 960x440 | `count`, `highlight`, `lean`, `seated`, `anchor`, `heights:'equal'` |
| `grid` | auto | `cols`, `rows`, `loose:[i]`, `cell` |
| `rings` | 900x620 | `center`, `script`, `caption`, `labels:[]`, `symbol` |
| `arc` | 760x480 | `pct`, `center`, `caption` |
| `balance` | 880x490 | `leftLabel`, `rightLabel`, `tip`, `breakRight`, `right` |
| `symbol` | 620x500 | `name`, `caption`, `size`, `tone`, `strike` |
| `stack` | 920x500 | `count`, `split`, `solid` |

All of them speak the semantic tokens (`--accent`, `--structure`,
`--ink`), so they follow `meta.theme` with no edits.

## The specific set

### Practice and ritual

| name | natural size | options | shows |
|---|---|---|---|
| `masjid` | 900x560 | - | dome, two minarets, a row of worshippers arriving |
| `weekStrip` | 900x130 | `days: [..]` | seven day tiles, light sweeping across |
| `reader` | 700x420 | - | seated figure, book stand, open book |
| `wardrobe` | 620x560 | - | rail, three garments, one tagged FRIDAY |
| `nightRow` | 900x420 | `count` | night row of figures, mihrab, crescent |
| `cards` | 900x190 | `items:[{t,s}]`, `cw` | labelled maroon cards |
| `walk` | 940x420 | `bars` | house, footsteps, rising bars, masjid |
| `khutbah` | 940x400 | - | minbar steps, khatib, seated crowd, a latecomer |
| `badge` | 300x220 | `label` | a numbered card with a tick |
| `stepOver` | 900x360 | - | seated row, a figure stepping over, a no-sign |
| `rakahSlots` | 900x280 | `count` | n cards filling with standing/bowing glyphs |
| `dial` | 900x480 | - | asr-to-maghrib arc, descending sun, seated figure |
| `dua` | 940x560 | - | arc dial, sun, raised hands, bubbles, a dropped phone |

### Creed and argument

| name | natural size | options | shows |
|---|---|---|---|
| `humanDefault` | 960x560 | - | a carved idol and a sky-god, both struck out |
| `blueprint` | 1010x486 | `items:[{ar,icon,kills}]` | n columns: Arabic word, icon, strike, what it rules out. `icon`: `rings` \| `cube` \| `twins` \| `scales` |
| `indivisible` | 920x500 | - | a stack that comes apart beside a block that will not |
| `senses` | 920x460 | - | an eye, and a grid with one cell falling out |
| `leaning` | 960x460 | - | a row of figures all tilting toward one fixed point |
| `hollowSolid` | 940x400 | - | a hollow frame with its cavity marked, beside a solid mass |
| `cubeDirections` | 940x460 | - | a wireframe cube labelled top/bottom/front/back, struck |
| `refuge` | 960x440 | - | a figure sheltering in a cave, beside one in open light |
| `offspringChain` | 1030x352 | `steps:["a","b\nc"]` | boxes chained by arrows to a struck conclusion |
| `scales` | 880x470 | - | a balance tipping until the empty arm snaps off |
| `threeVsOne` | 940x470 | - | three circles that drift apart and are struck, beside one solid disc |
| `nameOrb` | 900x620 | `ar`, `tr` | an Arabic name in concentric rings |

Multiply by `artScale` when checking the 1660 floor. The wide pieces
(`blueprint`, `offspringChain`) cannot scale past about 1.05 before they
run off the frame - give them room by raising `artTop` instead.

### Drawing a negation

Set 2 argues rather than illustrates, and the house rule for that is: **draw
the negation, do not label it.** A thing that cannot be divided is a blade
that stops; a body that cannot exist is a cube with a line through it; an
incomparable thing is a scale whose other arm breaks off. Two helpers make
this consistent:

```js
strike(id, x1, y1, x2, y2, colour, width)   // a bar that wipes in
drawStrike(el, id, t, startTime, dur)       // drives it from apply(t)
```

Rose (`--rose`) for a wrong idea being cancelled, cream for a conclusion
being sealed. Never both in one frame.

## Choosing one

Pick the piece that shows the **mechanism** of the claim.

- "light until next Friday" -> `weekStrip`, because the claim is about the
  seven days, and the strip is the seven days.
- "a year of fasting per step" -> `walk`, because the bars grow per step.
- "pray 2 rak'ahs even if it started" -> `khutbah` + `badge`, because the
  tension is the khutbah already running and the badge is the instruction.

If no piece shows the mechanism, the item is probably two items.

## Adding a piece

House rules, enforced at the top of `art.js`:

- Flat fills only. No gradients inside objects, no shadows, no strokes under
  3px, no perspective.
- Figures are `fig(x, baseY, h, color, skin, {seated})` - a circle head on a
  capsule body. No faces, no hands, no feet.
- Everything sits on one `groundLine(x1, x2, y)`.
- Five figure colours maximum.
- Animate with `E.p(t, start, dur, E.ease.X)`; never with CSS keyframes.

Skeleton:

```js
A.myPiece = (o = {}) => {
  const W = 900, H = 400, base = 330;
  return mk(`<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
      ${groundLine(60, 840, base)}
      <g id="thing">${fig(300, base, 120, 'var(--sky)')}</g>
    </svg>`,
    (t, el) => {
      const p = E.p(t, 0.2, 0.5, E.ease.back);
      q(el, 'thing').style.opacity = p;
      q(el, 'thing').style.transform = `translateY(${(1 - p) * 30}px)`;
    });
};
```

Do not generate art with an image model for this format. The look depends on
every object sharing one vector vocabulary; one rendered image in the middle
breaks it more than a crude vector does.
