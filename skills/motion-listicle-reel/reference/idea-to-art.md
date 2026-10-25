# From an idea to a diagram

The hard part of this format is not rendering. It is turning "I want a
reel about X" into four to nine claims, each with a shape.

## Step 1: claims, not topics

A topic is "compound interest". A claim is "interest earns its own
interest". You cannot draw a topic.

When someone gives you a topic, the question that works is **"what would
someone be wrong about?"** Wrongness has shape; topics don't. Three or
four wrong beliefs plus the correction is a whole reel.

Other reliable ways in:

- What surprised *you* when you learned this?
- What is the step everybody skips?
- What does it look like when it goes right vs wrong?
- If they only remember one sentence, which one?

Stop at nine. Past that the recap type drops under 30px and the reel runs
past ninety seconds.

## Step 2: give each claim a shape

| claim shape | sounds like | primitive | content you pass |
|---|---|---|---|
| contrast | "people think X, actually Y" | `versus` | two labels, two symbols, optional `strike` |
| causation | "A leads to B leads to C" | `steps` | 3-5 short step labels |
| parallel set | "four things, each doing one job" | `columns` | per column: a word, a symbol, a caption |
| magnitude | "this one is much bigger" | `bars` | numbers, labels, which to highlight |
| sequence | "a run of days, stages, states" | `tiles` | labels, which are active, `sweep` |
| population | "most people", "one in five", "a crowd" | `figures` | count, which to highlight, `lean`, `seated` |
| part-whole | "made of pieces" / "one piece missing" | `grid`, `stack` | rows/cols and which cells come loose |
| centre | "one thing, several aspects" | `rings` | centre word, orbiting labels |
| proportion | "a share, a fraction, a countdown" | `arc` | `pct`, a centre number, a caption |
| incomparable | "weigh these" / "nothing compares" | `balance` | two labels, `tip`, `breakRight` |
| one thing | a single concrete object | `symbol` | a symbol name and a caption |

If a claim fits none of these, it is almost always one of three things:

- **Two claims wearing one coat.** Split it; each half will have a shape.
- **A mood, not a claim.** "It's beautiful when you understand it" draws
  nothing. Cut it or move it to the closing question.
- **A number with no comparison.** A bare figure is a `big` on the scene,
  not a diagram. Use `"big": "+8"` and skip the art.

## Step 3: vary the shapes

Two `versus` scenes in a row read as one scene. Across a reel, aim for
four or five different primitives. A good default rhythm for six points:

```
columns  (lay out the whole argument)
versus   (the first correction)
bars     (the thing that is bigger than you think)
steps    (the mechanism)
versus   (the second correction)
arc      (the one that leaves them with a feeling)
```

## Symbols

`versus`, `columns` and `symbol` take a glyph by name. The set:

```
person people house building clock calendar book phone screen
money coin chart seed tree bulb brain eye heart shield lock key
door bridge mountain cloud star flag target scale gear link
arrowUp warning check cross question drop fire box
```

They are all drawn on the same 100x100 grid at one stroke weight, so they
mix without looking collaged. Adding one is ten lines in
`runtime/symbols.js` - keep the 100x100 box and use `currentColor`.

Pick the symbol for the *mechanism*, not the mood. For "time matters more
than the amount", `clock` against `coin` is the claim; a sunrise is
decoration.

## Worked example

Someone says: *"I want something about why people's bread doesn't rise."*

Claims, after asking what they'd be wrong about:

1. Water that kills the yeast → `versus` (`fire` / `drop`), strike the left
2. Yeast that was already dead → `steps` (proof it → bubbles → or bin it)
3. Salt dumped straight on the yeast → `versus` (two bowls)
4. Not enough kneading, so no gluten web → `grid` with loose cells
5. Rushing the rise → `arc`, `pct: 0.4`, "most people stop here"

Title promises five. Recap lists five. Theme `ember`, because it is a
kitchen. Nothing about the pipeline changed.
