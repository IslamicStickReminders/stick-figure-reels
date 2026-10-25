---
name: motion-listicle-reel
description: Turn any idea into a clean infographic - a 9:16 motion reel (mp4) and/or a set of static cards (PNG carousel) from one JSON file. Title card, numbered points with animated flat-vector diagrams and source chips, a recap list and a follow card. Use for explainers, listicles, "N things you didn't know about X", how-somethings-works, myth-vs-fact, step-by-steps, and for editing or restyling an existing one.
---

# Motion listicle reel

Someone brings an idea. This turns it into a finished 1080x1920 mp4 and a
set of standalone cards, from one JSON file. No editor, no template, no
keyframing, no image generator.

The idea can be anything: compound interest, crop rotation, why bread
doesn't rise, a company's onboarding, a surah. Nothing in the pipeline
knows or cares about the subject.

## Requirements

Playwright with Chromium, ffmpeg, and ImageMagick with the `montage`
command for contact sheets. Python `fonttools` + `brotli` are needed only
if patching a new font. Chromium and Playwright are usually already
present; if `playwright` is missing, `pip install playwright` and
`playwright install chromium`. Do not install a second Playwright version
alongside an existing Chromium - it will not find the browser.

## The format

Four parts, always in this order:

1. **Title card** - a number and a promise. One hook line.
2. **N point scenes** - one idea each: headline, optional subline, an
   animated diagram, an optional source chip.
3. **Recap list** - every point as one numbered row.
4. **Follow card** - avatar, one line, a button that flips.

The sameness is the point. A viewer learns the shape in four seconds and
spends the rest on the content. Put the interest in the words and the
diagram, never in new scene types.

## Workflow

1. **Get the idea down to N claims, in chat, as prose.** One line each,
   N between 4 and 9. Show them and get agreement before building.
   If the person's idea is vague, the useful question is not "tell me
   more" - it is "what are the three or four things someone would be
   wrong about?" Claims, not topics.
2. **Pick a diagram per claim.** `reference/idea-to-art.md` is a table
   from shape-of-claim to primitive. If a claim has no shape, it is
   usually two claims, or it is a mood and should be cut.
3. **Verify anything that looks like a fact.** See "Sourcing".
4. **Write the spec JSON.** Copy the closest example and change it.
   Every field is in `reference/scene-spec.md`.
5. **Preview**: `python3 scripts/render.py spec.json --preview --contact build/sheet.jpg`
   then LOOK at the contact sheet with the Read tool. ~1 min.
6. **Fix what you see.** `reference/style-system.md` has the layout bands
   and the fix for each common fault.
7. **Render**: `python3 scripts/render.py spec.json out/reel.mp4` (~4 min),
   and `--stills out/cards/` for the static set.
8. **Send both.** Say that audio gets added in the app at upload.

## Video or cards

Same spec, two outputs, and most ideas want both:

```bash
python3 scripts/render.py spec.json out/reel.mp4        # the reel
python3 scripts/render.py spec.json --stills out/cards/ # one PNG per scene
```

`--stills` grabs each scene at 82% of its duration, where every reveal has
landed and nothing has faded. That is a carousel post, or a slide set, or
a single card to drop into a thread - the static infographic, free.

If someone only wants "a clean infographic" and never mentioned video,
build the spec anyway and give them the stills. The reel costs four extra
minutes and they usually want it once they see it.

## Choosing the diagram

The art library is not a catalogue of things. It is twelve **shapes of
claim**, and you pass them content:

| the claim sounds like | primitive |
|---|---|
| "people think X, it's actually Y" | `versus` |
| "A causes B causes C" | `steps` |
| "N things, each doing one job" | `columns` |
| "this grew / this is bigger than that" | `bars` |
| "a run of days, stages, states" | `tiles` |
| "people, crowds, how many, who" | `figures` |
| "a whole made of parts" | `grid` or `stack` |
| "one centre, several things around it" | `rings` |
| "a share, a fraction, a countdown" | `arc` |
| "weigh these two / nothing compares" | `balance` |
| "one concrete thing" | `symbol` |

Each takes labels and symbol names, so a new subject needs no new code.
`reference/idea-to-art.md` has the worked mapping and the symbol list;
`reference/art-library.md` has every option.

Only write new art when a claim genuinely has a shape none of the twelve
carry. Then follow the house rules at the top of `runtime/art.js` - flat
fills, circle-head figures, one ground line, five colours. Never reach for
an image generator: the whole look depends on one vector vocabulary, and a
single rendered image in the middle breaks it worse than a crude diagram.

## Writing the copy

Full rules in `reference/writing.md`. The short version:

- Headline: under 7 words. One idea. Second person or imperative.
- Mark exactly one phrase with `[...]` - the highlight box, where the eye
  lands. Two boxes cancel out.
- `*...*` sets serif italic: names, quantities, the soft half of a contrast.
- Subline is the payoff, not a restatement. If it restates, cut it.
- Recap row = the headline crushed to about four words.
- No exclamation marks. No "Did you know". The format is calm.

## Themes

`meta.theme` picks the palette: `plum` (default), `ink`, `forest`, `ember`,
`slate`, `paper`. Every theme keeps the same structure - one ground,
one structural colour, one contrasting accent that is the only colour
allowed to say "look here" - so a diagram looks right in all of them
without edits. `paper` has a light ground; the other five are dark.

Pick by subject temperature, not by taste: `ink` for money, data, policy;
`forest` for growth, food, nature; `ember` for urgency and craft; `slate`
for technical and neutral; `paper` for a light background; `plum` for
anything devotional or warm.

## Sourcing

When a scene carries a citation chip, that chip is a claim.

- Look up every reference before it goes in the spec.
- A number you cannot confirm does not go on screen. Reword the point so it
  needs no citation, or drop it.
- When the material comes from someone's talk, deck or book, the chip cites
  the *primary* source, not the talk. Tell the person to credit the author
  in the caption; do not decide that for them.
- An attribution carried from a secondary source is unverified. Confirm it,
  or make the chip generic and true - claiming less beats naming a work you
  have not opened.
- Working from a summary of a summary (someone's slide export, an AI deck)
  is two removes from the material. Say so, and ask for the original.

## Fonts

`runtime/fonts/` holds patched Figtree, Playfair Display, Chakra Petch, and
Amiri for Arabic. The patch matters: display faces ship without the
dot-below letters (h s t d z) used in transliteration, and without them the
browser falls back mid-word and the text looks broken.

- The bundled fonts are already patched. Just use them.
- To add a face: `python3 scripts/patch_font.py IN.ttf runtime/fonts/OUT.ttf --weight 600`
- Write the real characters in the JSON. Do not spell around them in ASCII.

## Checks before sending

- Is `meta.handle` the account this is going to? If that is not settled,
  set it to `""` and the watermark and name line disappear.
- Read the contact sheet. Every frame: does anything overlap anything?
- `artTop` + (art height x `artScale`) must land above 1660.
- Recap rows: 8 maximum.
- Total under 90s.

## Audio

Rendered silent on purpose. If audio is added in the app, check the
track's permitted uses for the account and post; availability is not
blanket permission. `scripts/sfx.py` lays in near-inaudible transition ticks
if a silent file is awkward to review - `reference/sound.md`.
