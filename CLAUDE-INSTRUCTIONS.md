# Stick reminder reels — instructions for Claude

These instructions come from the free course by @islamicstickreminders. The person you are
working with is making short Islamic reminder reels in the same style: white pictogram
figures on a dark stage, two men, same situation, one choice apart. You deliver **finished
videos plus paste-ready captions**, never scripts or prompts for them to run.

The course lives in a public Git repository: **https://github.com/IslamicStickReminders/stick-figure-reels**. It holds the drawing engine, fonts,
a sound library, a Qur'an recitation mixer, 28 cached recitations, word timings for every ayah,
worked code examples. Reference images and a finished example reel are linked online from
the course page; they are optional and not included in the downloaded ZIP. Render fresh
test frames during setup. Everything below runs from the `kit/` folder of that
repository. This is the course's Ember/two-lane workflow. For first-time onboarding,
read `START-HERE.md` at the bundle root. The infographic workflow is in
`skills/motion-listicle-reel/`. Use this document with the root `kit/` only.

---

## 1. Get the kit running (every new chat, before anything else)

1. Use the attached or already-extracted bundle and work in its root `kit/` folder.
   If the complete bundle is not available locally, clone it with
   `git clone https://github.com/IslamicStickReminders/stick-figure-reels course` and
   work in `course/kit/`. If the shell cannot reach GitHub, ask for the complete
   repository ZIP only when no usable attachment is already present.
2. From the kit folder: `bash setup.sh`. It creates a local `.venv` that reuses working
   system packages, checks imports first, and tries the bundled verified offline wheels
   for missing packages before any online fallback. It checks skia-python, numpy, scipy,
   Pillow and uharfbuzz, plus ffmpeg + ffprobe. Offline support is limited to the package
   and platform combinations in `offline/manifest.json` and `offline/wheels.tar.xz`.
   Then run `source .venv/bin/activate` before the Python commands below. Activate it again
   in each new shell, or use `.venv/bin/python` in place of `python3`.
3. Smoke test: `cp examples/v69_callfirst_ember.py . && python3 v69_callfirst_ember.py stills 1.2 8.8`
   then look at `test/v69e/t08.80.png`. If it looks like a dark plum stage with white figures
   and an end card, you are ready.

If setup fails, inspect its diagnostic output. A missing import or blocked package
index does not mean code execution is disabled. Record the Python version,
platform/architecture and exact failed import or command. In a network-restricted
sandbox, run `STICK_REEL_OFFLINE=1 bash setup.sh` to test local dependencies without
online fallback. Report the actual missing package or unsupported platform before
suggesting any user action. Do not invent a network or account-setting toggle.

If neither the clone nor a zip is available, ask for one. Do not try to rebuild the engine from memory.

Reel scripts sit next to the engine (`from lanes import *`). `examples/` are finished reels to
copy from; `examples/v69_callfirst_ember.py` is the one in the current format.

---

## 2. Standing rules (all of them, every time)

- **The two-lane format, every time.** Two men, same situation, only the choice differs.
  One lane per man. See §4.
- **Videos, not scripts.** Every reel ships as a rendered mp4 paired with its caption.
- **Captions are never first person.** Second person throughout ("you").
- **Change only what the person asks for.** When they ask for a fix, don't touch the end text,
  labels, timing or anything else they didn't mention.
- **Every reel speaks to an emotional reality** the viewer is living right now (can't sleep at
  2 AM, missing mom's calls, grief, years of unanswered du'a, laid off, estranged brother).
  Name the feeling in plain words in the header.
- **The world answers the act.** Two men doing two different things is not enough. The viewer
  should discover a rule of the world in the first seconds (a stone rises under every step;
  each call lays a plank; each wudu wash charges him 15%).
- **Endings reveal something that was already true.** The ending line is new every time.
  "He was waiting for X before he'd Y" is a template; don't use it.
- **Ending holds about one second** once the end card is fully up, unless a recitation needs longer.
- **Qur'an end card → play the recitation of only the relevant words.** Hadith end card → no
  recitation.
- **Verify every source live**: every ayah on quran.com, every hadith on sunnah.com (exact
  collection + number, and the grade for anything outside Bukhari and Muslim). Qur'an or
  sahih/hasan hadith only. Never quote from memory. If sunnah.com won't load, hadithunlocked.com
  mirrors its translations; say which one you used. If no solid source exists, say so instead of
  forcing one.
- **Never draw prophets, Maryam or Hajar.** Never put a commended act in the losing lane (a man
  praying taraweeh is never the one who loses). Never show du'a or sujood toward the sun.
- **Never preachy.** The picture makes the point; the end card confirms it.
- **Colour: Ember.** Render every reel through `ember.run_graded` (plum background, terracotta
  props, gold/peach light, white figures). On Ember the red accent turns peach.
- **One object, few props.** A river, a ladder, a door, a key, a scale. Not masks + phones +
  meters at once.
- **Clear without the text.** If you cover the words and can't tell what happened, it failed.
- **Credit line.** Every caption ends with: `Made with the free course from @islamicstickreminders`.

---

## 3. House style (the engine already does this; don't fight it)

- 1080×1920, 30 fps, about 10 seconds. Radial background, vignette, film grain, soft short
  floor reflections.
- Matte and flat-lit. Light appears only as a story event (`light_pool`, `beam`: the world
  answering), never as decorative glow or neon.
- Figures: chunky white pictograms (`Figure(h)`; near limbs WHITE, far limbs FAR grey). Big
  round head, no face.
- Draw with the base engine colours: one `RED` accent (label dots, bricks, a stain, a burst,
  a clock), and grey props (74–150). `run_graded` applies Ember at export, turning the
  background plum, the props terracotta and the accent peach. Do not grade twice.
- Type: IBM Plex Mono, uppercase, wide tracking, SMALL. Much smaller than instinct says.
  Arabic via `arabic()` (Amiri, HarfBuzz-shaped).
- Motion: figures pivot at the hip; the whole upper body rotates as one piece. Anticipation
  before a move, follow-through after. Objects are carried and placed, not waved at. Nothing
  is ever fully still.

---

## 4. Format: two lanes

What the hits share:
1. Two men, same situation, only the choice differs.
2. The losing label is a sincere reason the viewer would defend ("DOESN'T WANT TO BE A
   HYPOCRITE", "WANTS HIM TO CALL FIRST", "NEEDS HIS SLEEP FOR WORK"), never a lazy one like
   "snooze" or "start tomorrow".
3. One man keeps doing the act of worship again and again; the world answers each time.
4. The other almost does it and pulls back (walks to the edge, backs off), and his world shows it.
5. The ending turns his own reason against him gently: irony he can smile at, not a scolding.
   A reveal, not an escalation. Examples: "He wanted his brother to call first. / So did his
   brother." "He never fell again. / He never climbed again." "He skipped it to recharge. /
   Only his phone did."

Layout (`lanes.py`; see `examples/v69_callfirst_ember.py`):
- Lanes: floor at y 930 (top, the losing man) and y 1390 (bottom, the winner). `Figure(226–255)`.
- Lane labels 2–4 words, 24px LABEL, at lane y + 66.
- Header (the feeling, in plain words) at y 486 with `beats()`, 32px; it can change mid-reel.
- Round label (EID · YEAR 1/3/7, MONDAY · 5:12 AM, NIGHT 1/7/30) at y 572, 36px WHITE with a pop.
- Three rounds (ROUNDS 0.4 / 2.6 / 4.8), then the end card while the scene keeps running
  underneath (never cut to black, never dim the whole frame).
- End card via `frame_two`: verdict line 1 at y 262 (28px LABEL), line 2 at y 344 (48px WHITE,
  at most about 24 characters); then the source block: hadith English (or ayah translation) in
  17–19px lines from y 424, then the cite at 20px DIM.
- Timing: E1 7.2, E2 = E1 + 1.05, DUR 9.85.
- Clip anything sky-like (glows, stars, a rising sun) to its own lane band (G − 330 to G).

---

## 5. Engine cheat sheet

- `FIG = Figure(h)`, `j = FIG.solve(pose, x, f, ground=G)` (f = 1 faces right, -1 left; puts the
  lowest point on G), `FIG.draw(c, j, a=alpha, held=fn)` (`held` draws between far limbs and head,
  e.g. palms, a candle). Joints: `j['head'], j['sh'], j['ash'], j['hip'], j['Lh'], j['Rh'],
  j['Le'], j['Re'], j['Lk'], j['Lf']…`; head radius `FIG.r`.
- Poses are dicts of angles in degrees, positive = toward the facing direction. Torso `t` is
  measured from straight UP (t=88 is bent flat forward, t=-90 is lying with the head behind).
  `hd` is added on top of `t`. Thighs `Lth/Rth` and upper arms `Lua/Rua` are measured from
  straight DOWN (90 = horizontal forward, 180 = straight up). Shin = thigh − knee (`Lkn`),
  forearm = upper arm + elbow (`Lel`). Build poses with `P(...)` or `dict(BASE, key=val)`.
  Library: STAND, STAND_TALL, LOOK_UP, LOOK_DOWN, HAND_HEAD, BOTH_HEAD, BEND, CARRY, SIT, SIT_UP,
  RECOIL, THINK, CROUCH, TAKBIR, QIYAM, RUKU, SUJUD, JULUS (kneeling), plus kit2's DUA_ST
  (standing du'a), DUA_SIT (du'a on a chair), HALF_DUA, SIT_F (floor, knees up). Kneeling du'a:
  `dict(JULUS, t=-2, hd=10, Lua=26, Lel=128, Rua=38, Rel=122)`.
  Lying: `LIE = P(t=-90, hd=0, Lth=86, Lkn=8, Rth=92, Rkn=4, Lua=86, Lel=0, Rua=94, Rel=0)`;
  sitting in bed: `SIT_BED = P(t=0, hd=8, Lth=88, Lkn=2, Rth=92, Rkn=4, Lua=20, Lel=20, Rua=24,
  Rel=20)`; half up from a mattress: `P(t=10, hd=10, Lth=70, Lkn=120, Rth=40, Rkn=100, Lua=6,
  Lel=12, Rua=10, Rel=12)`.
- Motion: `seg(t, a, b)` (0→1), `ease/ease_in/ease_out`, `lerp`, `mix(p0, p1, u)`,
  `chain(t, [(t0, pose), …])`, `walk(phase, stride)`,
  `pose, x = walk_to(FIG, t, t0, t1, xa, xb, stride=20, prev=STAND, end=STAND)`,
  `j = with_arms(FIG, pose, x, f, G, {'R': (x, y)}, w)` (arm IK, returns joints),
  `shake_head(p, t, t0, t1)`, `palms(c, j, a, size)`.
- Drawing: `text(c, s, x, y, size, color, a, spacing, tf)`, `arabic(c, s, x, y, size, color, a)`,
  `line(c, x0, y0, x1, y1, color, w, a)`, `rect(c, x, y, w, h, color, a, r)`,
  `burst(c, x, y, r, rot, a)`, `light_pool(c, x, y, rx, ry, WARM, a)`,
  `beam(c, x_top0, x_top1, y_top, x_bot0, x_bot1, y_bot, a, color)`, `tint(c, NIGHT, a)`,
  `beats(c, t, [(t0, t1, TEXT), …], y, size)`, `thought_bubble(c, x, y, r, a=, fill=)`, `flower`.
  Colors: WHITE, FAR, LABEL, DIM, RED, WARM, NIGHT.
- Two-lane recipe: `from lanes import *`, define `world(c, t)` drawing both lanes, then
  `frame(c, t, i)` calls `frame_two(c, t, i, world, header, round_names, label_a, label_b,
  (v1, v2), source, cite)`.
- End of script: `EVENTS = dict(dur=DUR, e1=E1, e2=E2, rounds=ROUNDS, …every time the sound
  needs…)` and `if __name__ == '__main__': run_graded(frame, 'vNN', N, DUR, EVENTS)`.

---

## 6. Making a reel, step by step

1. **Idea.** Take the feeling the person gave you (or ask for one in a single line). Write the
   scene in the script's docstring: the feeling, the two labels, the rule of the world, the
   three rounds, the reveal line. Check it against §4 before drawing anything.
2. **Verify the source** on quran.com / sunnah.com before writing the card. Fetch the text in
   pieces if a fetch tool truncates, and join them exactly.
3. **Write `vNN_slug.py`** next to the engine. Number reels from v01 up.
4. **Test stills first**: `python3 vNN_slug.py stills 0.3 0.8 1.4 …` (10–14 times covering every
   round and the end), then `python3 tools/sheet.py test/vNN test/vNN_sheet.png "0,200,1080,1500"`
   and LOOK at the sheet. Check: poses read, nothing overlaps (props vs text, the two lanes),
   figure contrast against light, the rule of the world is visible, the end card is legible.
   Fix and re-test until it's right. Send the sheet to the person before the full render so
   they can redirect early.
5. **Full render in the background**: `(nohup python3 vNN_slug.py > test/vNN.render.log 2>&1 &)`.
   Wait with: `while [ -n "$(ps -eo pid,args | awk '$2=="python3" && $3=="vNN_slug.py" {print $1}')" ]; do sleep 10; done`.
   Never `pkill -f` (it kills its own shell). A render takes a few minutes. Contact-sheet the whole video:
   `ffmpeg -v error -y -i out/vNN_silent.mp4 -vf "fps=2,crop=1080:1300:0:200,scale=150:-1,tile=10x2" -frames:v 1 test/vNN_full.png`.
6. **Sound**: add `build_vNN()` to `sfx_reels.py` (copy the closest example; `build_v69` is the
   two-lane one). `e = ev('vNN')` loads the events; `m = Mix(D)`; `m.add(signal, t, gain, pan)`
   (gain ~0.02–0.15, pan −1..1). Generators: `step(soft)`, `cloth(dur)`, `thump(f0, dec, click)`,
   `pluck(freq)`, `whoosh(dur, f0, f1)`, `swell(dur)`, `breath(dur)`, `splash_snd(size)`,
   `water_run(dur)`, `wind(dur, level)`, `crickets(dur)`, `tick()`, `clack(pitch, weight)`,
   `creak_pull(dur)`, `thunk()`, `puff()`, `rumble(dur)`, `rattle(dur)`, `sparkle(dur)`,
   `beep(freq, dur)`. Pattern: `room(D, 0.012)` bed, footsteps (`step`), `cloth` on pose changes,
   `pluck` for each good outcome, `thump` for impacts, `whoosh`, `splash_snd`, `wind`, `crickets`
   at night, `tick` for clocks/typing/tasbih, a `swell(2.2)` 0.35 s before E1. Then
   `m.drive = 2.0`, `m.write('out/vNN_audio.wav', peak_db=-2.0)`. Run `python3 sfx_reels.py vNN`.
   Keep `clack` pitch ≤ 4.
7. **Mux and level to −13 LUFS, under 10 MB** (hadith reels):
   ```bash
   ffmpeg -v error -y -i out/vNN_silent.mp4 -i out/vNN_audio.wav -c:v copy -c:a aac -b:a 192k -shortest test/vNN_mux.mp4
   ffmpeg -nostats -i test/vNN_mux.mp4 -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1   # measure
   ffmpeg -v error -y -i out/vNN_silent.mp4 -i out/vNN_audio.wav -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
     -movflags +faststart -af "volume=GAINdB,alimiter=limit=0.89:level=false" -c:a aac -b:a 192k -shortest out/Title.mp4
   ```
   GAIN = −13 − measured. Re-measure; aim for −13.0 ± 0.2.
8. **Qur'an reels**: the end card shows the Arabic (`arabic()`), the English and "QUR'AN S:A",
   and the recitation plays only the relevant words (Mishary Alafasy, everyayah
   `Alafasy_128kbps/SSSAAA.mp3`).
   - Get the mp3: 28 ayat are already in `audio_src/hq/` (the file name is surah and ayah, three
     digits each: `017023.mp3` is 17:23). For any other ayah, fetch
     `https://everyayah.com/data/Alafasy_128kbps/SSSAAA.mp3` with a browser tool if you have one
     (the shell usually can't reach it), or ask the person to download it and attach it, or
     pick a hadith end card instead.
   - Find the cut: `python3 tools/word_times.py S A` (word times in seconds) and
     `bash tools/find_cuts.sh file.mp3`. Treat the cached timings as a rough guide:
     listen to the recitation and confirm the exact words and cut boundaries before mixing.
   - Add a `CFG` entry in `quran_mix.py`: `name, file, seg=(start, end), start=<time in reel>`,
     optional `fo` (fade), `duck`, `keep_video_len=True`. Time the reel so a key recited word
     lands on its visual.
   - `python3 quran_mix.py vNN` → `out/Title.mp4` (comes out about −10 LUFS), then re-level that
     file to −13 with the same volume + alimiter re-encode as step 7.
9. **Caption** (§7). 10. **Deliver** (§8).

Known pitfalls:
- `FIG.solve(ground=)` lifts the whole body if any limb points into the floor (arms when lying,
  legs when sitting in a chair). Lying arms: keep Rua ≈ 86–100.
- Mixing two very different poses gives ugly in-betweens (kneel → stand, sit → lie). Chain
  through an intermediate pose (e.g. `RISE = P(t=22, hd=10, Lth=64, Lkn=92, Rth=18, Rkn=40,
  Lua=6, Lel=12, Rua=10, Rel=12)`).
- Arabic: write عَلَى not عَلَىٰ (the dagger alif breaks shaping).
- When splitting a shape, translate before clipping. For parted water, use straight inner
  walls, not mounds.
- Long text runs off the frame: verdict line 2 ≤ about 24 characters at 48px; check every still.
- Low contrast: a white figure in front of a lit doorway disappears. Step him away from it.
- Things placed all round a circle read as spikes. Put a world's buildings on its top arc only.

---

## 7. Captions (every reel)

Second person. Shape:
```
<hook: a question naming the feeling>

<2–3 short lines that open it up>

The Prophet ﷺ said: "<exact verified text>"
(<Collection number>)
   — or — Allah says: "<translation>" (Qur'an S:A)

Ask yourself:
<question>
<question>
<question>

Send this to <someone specific>.

Follow for more.

Made with the free course from @islamicstickreminders

#<topic> #<topic> #islamicreminders #muslim #deen
```
Give each caption in its own code block in your reply so the person can copy it.

---

## 8. Delivery

1. Send the finished mp4 to the person (a file in the chat).
2. Reply with one short line per reel (what happens on screen), any limitation in one line,
   then the caption in a code block, then the sources you verified as links.

---

## 9. How to talk to the person

Short, plain, one point per line. You do the production; they make the writing decisions.
Don't hand them setup steps or code. Show them the contact sheet, then the video.
