# Motion listicle reel

Turn an idea into a clean infographic — a 9:16 motion reel and a set of
static cards — from one JSON file. No editor, no timeline, no image
generator.

![Four frames from three different reels](https://raw.githubusercontent.com/IslamicStickReminders/stick-figure-reels/main/skills/motion-listicle-reel/docs/hero.png)

Every frame above came out of the same pipeline. Different subjects,
different palettes, one visual language.

**Included in the [all-in-one reel kit](../../README.md). Download that ZIP, attach it to Claude, and say “Get me started.”**

---

## What you get

One spec file produces two things:

```bash
python3 scripts/render.py spec.json out/reel.mp4          # 1080×1920 mp4
python3 scripts/render.py spec.json --stills out/cards/   # one PNG per scene
```

The stills are grabbed at 82% of each scene — where every reveal has landed
and nothing has faded — so a carousel post falls out of the reel for free.

<p align="center">
  <img src="https://raw.githubusercontent.com/IslamicStickReminders/stick-figure-reels/main/skills/motion-listicle-reel/docs/cards/compound-versus.png" width="240">
  <img src="https://raw.githubusercontent.com/IslamicStickReminders/stick-figure-reels/main/skills/motion-listicle-reel/docs/cards/compound-bars.png" width="240">
  <img src="https://raw.githubusercontent.com/IslamicStickReminders/stick-figure-reels/main/skills/motion-listicle-reel/docs/cards/compound-recap.png" width="240">
</p>

## The format

Four parts, always in this order:

1. **Title card** — a number and a promise
2. **N point scenes** — headline, optional subline, an animated diagram, an
   optional source chip
3. **Recap list** — every point as one numbered row
4. **Follow card** — a button that flips

The sameness is the point. A viewer learns the shape in four seconds and
spends the rest on the content.

## Art is shapes of claim, not pictures of things

The hard part of an explainer is never rendering. It is that people arrive
with a *topic*, and you can't draw a topic.

So the art library isn't a catalogue of objects. It's twelve shapes that
take their content from the spec:

| the claim sounds like | primitive |
|---|---|
| "people think X, it's actually Y" | `versus` |
| "A causes B causes C" | `steps` |
| "N things, each doing one job" | `columns` |
| "this grew / this is bigger" | `bars` |
| "a run of days, stages, states" | `tiles` |
| "people, crowds, how many" | `figures` |
| "a whole made of parts" | `grid`, `stack` |
| "one centre, several things around it" | `rings` |
| "a share, a fraction, a countdown" | `arc` |
| "weigh these two / nothing compares" | `balance` |
| "one concrete thing" | `symbol` |

Plus 39 flat symbols — clock, coin, seed, shield, bridge, brain — all drawn
on one 100×100 grid at one stroke weight, so they mix without looking
collaged. A new subject needs no new code.

If a claim fits none of the twelve it is usually two claims, or a mood.

## Themes

`"theme"` in the spec swaps the whole palette. Every theme keeps the same
invariant — one ground, one structural colour, one scarce accent that
is the only colour allowed to say *look here* — which is why a diagram built
for one looks right in all six.

![Examples of the six themes](https://raw.githubusercontent.com/IslamicStickReminders/stick-figure-reels/main/skills/motion-listicle-reel/docs/themes.png)

`plum` · `ink` · `forest` · `ember` · `slate` · `paper`

The first five use a dark ground; `paper` uses a warm light ground.

## A spec

```json
{
  "meta": { "handle": "@you", "theme": "ink", "w": 1080, "h": 1920, "fps": 30 },
  "scenes": [
    { "type": "title", "dur": 4.0,
      "text": "*Compound interest*, in [one minute]",
      "art": "bars", "artOpts": { "values": [4,6,9,14,22,36,60] } },

    { "type": "item", "dur": 6.2,
      "text": "Interest earns [its own interest]",
      "sub": "That is the whole trick. *Nothing else.*",
      "art": "steps",
      "artOpts": { "steps": ["you save","it earns","that earns","and on"] } }
  ]
}
```

Three marks in the copy: `[...]` is the cream highlight box (one per
headline, it's where the eye lands), `*...*` is serif italic, `**...**` is
extra weight.

Three worked examples are in `examples/`.

## Quick start

Needs Python 3, [Playwright](https://playwright.dev/python/) with Chromium,
and ffmpeg. Contact sheets (`--contact`) also need ImageMagick with the
`montage` command available on your PATH.

```bash
pip install playwright && playwright install chromium
python3 scripts/render.py examples/compound-interest.json out/reel.mp4
```

Roughly four minutes for a 60-second reel at 1080×1920/30fps. Add
`--preview` for a half-size 15fps pass while you iterate, and `--contact
sheet.jpg` for a 24-frame contact sheet to eyeball.

## Using it with Claude

This workflow is included in the [complete Islamic Stick Reminders bundle](../../README.md).
Attach that bundle to Claude, say *"Get me started"*, and ask for an
infographic reel or image cards. Claude reads this workflow's `SKILL.md`
and `reference/` and handles the setup. No separate download is needed.

| file | what it's for |
|---|---|
| `SKILL.md` | the workflow Claude follows |
| `reference/idea-to-art.md` | turning a vague topic into claims with shapes |
| `reference/style-system.md` | palette, type scale, layout bands, motion |
| `reference/scene-spec.md` | every field in the spec |
| `reference/art-library.md` | every primitive and its options |
| `reference/writing.md` | how the copy is written |
| `reference/sound.md` | why it renders silent |

## How it renders

`runtime/index.html` exposes `renderFrame(t)` — the whole reel is a pure
function of time, with no `requestAnimationFrame` and no CSS animation.
Playwright seeks to each frame and screenshots it; ffmpeg assembles. Frame
900 is identical every time you ask for it, which is what makes a re-render
safe.

## Audio

Renders silent on purpose. Add audio in the Instagram or TikTok composer
if you want it, checking the track's permitted uses for your account and
post. A track being available in an app does not mean every use is covered.
`scripts/sfx.py` can lay in near-inaudible transition ticks if a silent
file is awkward to review.

## Fonts

Four OFL families are bundled. Two of them — the sans and the serif — were
patched to add the dot-below letters used in transliteration (ḥ ṣ ṭ ḍ ẓ),
which neither upstream ships; without them a citation like `ṢAḤĪḤ MUSLIM
875` silently falls back mid-word and looks broken.

The modified Playfair Display faces are renamed **Reel Serif** because
Playfair Display is a Reserved Font Name under OFL 1.1 clause 3. Figtree
has no Reserved Font Name; its modified faces are renamed **Reel Sans**
to distinguish them from the originals. Chakra Petch and Amiri are
redistributed unmodified.

Full detail and licences: [`runtime/fonts/NOTICE.md`](runtime/fonts/NOTICE.md).

## Companion skill

For character-driven stick-figure scenes, see the included
[story-reel course](../../COURSE.md).

## Licence

MIT for the code — see [`LICENSE`](LICENSE). The bundled fonts are SIL OFL
1.1 and are **not** covered by it.
