# The style system

Everything below is a constraint, not a suggestion. The format reads as
designed because nothing in it is decided twice.

## Palette

One ground, one accent, one structural colour, a small cast of figure fills.

| token | hex | what it is for |
|---|---|---|
| `--bg` | `#14030b` | the floor. Every scene sits on it. |
| `--bg-raise` | `#1c0713` | a scene wash one step up |
| `--panel` | `#280918` | recap rows, the follow card |
| `--maroon` | `#4d0d25` | the one saturated colour: buildings, chips, cards |
| `--maroon-dim` | `#35152a` | inactive tiles |
| `--cream` | `#f7edc2` | **the only colour that says "look here"** |
| `--cream-deep` | `#ead7a0` | finials, wood, secondary cream |
| `--cream-ink` | `#3a2410` | type sitting on a cream highlight |
| `--ink` | `#f3e9ef` | headline white, warmed so it belongs in plum |
| `--ink-soft` | `#d7c3cf` | sublines |
| `--ink-dim` | `#8d7482` | inactive labels, recap source text |

Figure fills: `--skin #e5cda9`, `--sky #b9e4f4`, `--rose #e3a9b8`,
`--sage #a9d3b8`, `--bone #f2efea`, `--clay #d8c09a`.

Rules:
- Cream is scarce. One highlight box per headline; one cream object per art
  piece. The moment a second cream thing appears, the first stops working.
- Never more than five figure colours in one frame.
- No gradients inside objects. The only gradients allowed are the full-frame
  scene `wash` and the vignette.

### Semantic tokens and themes

The diagram primitives never name a colour. They use `--structure` (the
thing being described), `--structure-lit` / `--structure-hot` (its lighter
and saturated variants), `--accent` (the one colour that says "look here"),
`--accent-deep`, `--accent-ink`, and the three inks.

`meta.theme` redefines the base tokens and everything follows:

| theme | ground | accent | suits |
|---|---|---|---|
| `plum` | near-black plum | warm cream | devotional, warm, default |
| `ink` | deep navy | gold | money, data, policy |
| `forest` | deep green | pale bone | growth, food, nature |
| `ember` | near-black brown | warm sand | urgency, craft, kitchen |
| `slate` | charcoal | pale sky | technical, neutral |
| `paper` | warm off-white | deep rust | light background, print |

A theme never changes the *structure*: one ground, one structural colour,
one scarce accent. That invariant is why a diagram built for one theme
looks right in all six.

### Scene washes

A `wash` on a scene swaps the ground for that scene only. Use it to mark a
change of *time*, never for variety:

- night / Fajr: `linear-gradient(180deg,#0a1226 0%,#101a33 48%,#16132a 100%)`
- dusk / the last hour: `linear-gradient(180deg,#1a0714 0%,#3a0f2a 56%,#1b0712 100%)`

Two washes in a reel. Three and the floor stops feeling like a floor.

## Type

Three faces, three jobs. Never a fourth.

- **Display** (Figtree) - headlines, numbers, buttons, recap rows. 600-800.
- **Accent** (Playfair Display Italic) - the italic half of a headline, the
  subline, surah names, units under a big number. 500.
- **Meta** (Chakra Petch) - citation chips, day tiles, kickers, the handle.
  600-700, uppercase, letter-spacing 0.1-0.3em.
- **Arabic** (Amiri) - Qur'anic words and divine names, inside art only.
  Never for a headline: the headline is the plain-English half of the
  thought, and the Arabic is the thing it points at.

Sizes, at 1080x1920:

| element | size | weight |
|---|---|---|
| title headline | 68px | 700 |
| item headline | 62px | 700 |
| subline | 40px | 500 italic |
| big number | 132px | 800 |
| recap row | 33px | 500 |
| citation chip | 21px | 600, +0.14em |
| handle | 23px | 700 |

Headline leading is 1.17 and tracking is -0.018em. Both matter: the format
wants headlines that sit as a block, not as lines.

## Layout bands

The frame is divided once and every scene obeys it.

```
0    - 300   IG chrome. Nothing here, ever.
300  - 560   headline
430  - 620   subline (when present)
500  - 760   big number (when present)
700  - 1660  art
1660 - 1760  citation chip   (bottom: 225)
1760 - 1860  watermark       (bottom: 92, left-aligned)
1860 - 1920  caption gutter. Nothing here.
```

`artTop` + (art height x `artScale`) must land above 1660. That one
arithmetic check prevents nearly every collision this format produces.

## Motion

- Everything is a pure function of time. `renderFrame(t)` twice gives the
  same pixels twice. Nothing uses rAF or CSS animation.
- Default ease is `out` (cubic). Objects that *arrive* use `back` (a small
  overshoot). Things that *travel* use `inOut`.
- Words reveal left to right, 85ms apart, rising 26px over 420ms.
- A highlight box wipes in from the left over 340ms, starting 100ms after
  its first word lands. The ink flips to dark only once cream is under it.
- Art starts 300ms after the headline, so the reader gets the sentence
  before the picture competes for them.
- Scene cross-fade: 140ms in, 160ms out. Shorter and it cuts; longer and it
  dissolves.
- Nothing bounces more than once. Nothing spins. Nothing scales past 1.05.

## Why it holds together

Three things do the work, and a change to any of them costs the look:

1. **One accent colour, used sparingly.** Cream is the reel's cursor.
2. **One art vocabulary.** Circle-head figures, flat fills, a single ground
   line. A photograph or a 3D render in this frame destroys it instantly.
3. **A fixed spine.** Same bands, same pacing, same four parts. The viewer's
   attention goes to the words because nothing else moves unexpectedly.

## When the highlight box does not fill

Symptom: the highlighted words turn dark but no cream appears behind them.

Cause: `.hl .fill` is absolutely positioned; if it is given a negative
`z-index` it escapes to the root stacking context and hides behind the
opaque `body` background. The fix in `theme.css` is `isolation:isolate` on
`.hl`, `z-index:0` on `.fill`, `z-index:1` on the word spans. Do not
reintroduce a negative z-index here.
