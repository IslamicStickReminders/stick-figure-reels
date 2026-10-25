# The spec file

One JSON file describes the whole reel.

```json
{
  "meta": { "handle": "@yourhandle", "theme": "plum",
            "title": "...", "w": 1080, "h": 1920, "fps": 30 },
  "scenes": [ ... ]
}
```

Scene durations are summed in order; there is no explicit timeline.

### Theme

`meta.theme` is one of `plum` (default), `ink`, `forest`, `ember`, `slate`,
`paper`. It swaps the whole palette; every diagram follows without edits
because they all speak semantic tokens. See style-system.md.

### Going handle-free

Set `"handle": ""` and the watermark disappears from every scene and the
follow card loses its name line; the card and its button stay. Do this
whenever the destination account is not settled - a wrong handle burned
into 2,500 frames is worse than no handle, and the platform shows the
account beside the reel anyway. Ask which account a reel is for rather
than filling in a plausible one.

## Common to every scene

| field | type | notes |
|---|---|---|
| `type` | string | `title` \| `item` \| `recap` \| `cta` |
| `dur` | number | seconds. title 4, item 6.2-6.8, recap 7.2, cta 5.2 |
| `wash` | css | full-frame background for this scene only. Max two per reel. |

## Text markup

Used in `text` and `sub`:

| mark | renders as |
|---|---|
| `[words]` | cream highlight box, dark ink, wipes in from the left |
| `*words*` | serif italic accent |
| `**words**` | extra weight (800) |

One `[...]` per headline. A `[...]` in the subline is allowed only when the
headline has none.

## `title`

| field | default | notes |
|---|---|---|
| `text` | - | the hook. Markup allowed. |
| `top` | 230 | headline top |
| `art` | `masjid` | any art name |
| `artTop` | 620 | |
| `artScale` | 1 | |

Used twice in a reel: once to open, once for the closing question before
the CTA.

## `item`

| field | default | notes |
|---|---|---|
| `text` | - | headline, markup allowed |
| `top` | 300 | |
| `sub` | - | subline, markup allowed |
| `subTop` | 470 | |
| `big` | - | big number, e.g. `"+8"` or `"4"`. Counts up over 0.9s. |
| `bigUnit` | - | small italic line under it |
| `bigTop` | 560 | |
| `art` | - | primary art name |
| `artTop` | 980 | |
| `artScale` | 1 | scales from centre-top |
| `artDelay` | 0.30 | seconds after scene start |
| `artOpts` | `{}` | per-piece options, see art-library.md |
| `art2` ... | - | a second art piece: `art2Top`, `art2Scale`, `art2Delay`, `art2Opts` |
| `cite` | - | citation chip text, uppercase |
| `citeBottom` | 225 | raise only if the art genuinely needs the room |

`art2` is the small supporting graphic (a week strip, a badge, two labelled
cards) that sits between the words and the main art. Use it when the item has
a quantity or a name worth pinning; leave it out otherwise.

## `recap`

| field | default | notes |
|---|---|---|
| `top` | 440 | |
| `kicker` | `THIS FRIDAY` | small uppercase line above the list |
| `items` | - | `[{ "t": "row text", "s": "SOURCE 123" }]`, max 8 |

Rows stagger in 220ms apart. With 8 rows the last one lands at 2.0s, so a
7.2s scene leaves five seconds to read - which is the minimum that works.

## `cta`

| field | default | notes |
|---|---|---|
| `say` | `Follow for more` | one line, `<br>` allowed |
| `btn` | `Follow` | |
| `btnDone` | `Following` | |
| `flipAt` | `dur - 1.5` | when the button flips |

The avatar is a drawn placeholder. To use a real photo, add an `<img>` to
`.cta .av` in `scenes.js` and reference a local file.

## Running it

```bash
python3 scripts/render.py spec.json --preview --contact build/sheet.jpg   # ~1 min
python3 scripts/render.py spec.json out/reel.mp4                          # ~4 min
python3 scripts/render.py spec.json --stills out/cards/                   # PNG per scene
python3 scripts/shot.py  spec.json 9.5 25.8 build                         # single frames
```

`--stills` writes one settled PNG per scene (grabbed at 82% of the scene,
where every reveal has landed). That is the static carousel, from the same
spec, at no extra authoring cost.

`--preview` is half size at 15fps. Always preview and actually look at the
contact sheet before a full render.
