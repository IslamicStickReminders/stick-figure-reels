# Stick reel kit

The engine that renders two-lane stick-figure reminder reels (1080×1920, 30 fps). Run everything from this folder.
The full method is in [CLAUDE-INSTRUCTIONS.md](../CLAUDE-INSTRUCTIONS.md) one folder up.
The person starts by attaching the complete bundle to Claude and saying **Get me started**.
Claude follows [START-HERE.md](../START-HERE.md); the full course is in [COURSE.md](../COURSE.md).

    bash setup.sh                                   # reuse working packages; local wheels first
    source .venv/bin/activate                        # repeat in each new shell
    cp examples/v69_callfirst_ember.py .            # scripts live next to the engine
    python3 v69_callfirst_ember.py stills 1.2 8.8   # test frames -> test/v69e/
    python3 tools/sheet.py test/v69e test/v69e_sheet.png "0,200,1080,1500"   # contact sheet
    python3 v69_callfirst_ember.py                  # full render -> out/v69e_silent.mp4 + out/v69e_events.json
    python3 sfx_reels.py v69e                       # sound -> out/v69e_audio.wav (add build_vXX for a new reel)

Setup creates a local `.venv` with access to working system packages. Missing
packages are tried from the verified `offline/wheels.tar.xz` payload first;
`offline/manifest.json` identifies the bundled wheels. Coverage is limited to
those package/platform combinations. If network access is unavailable, run
`STICK_REEL_OFFLINE=1 bash setup.sh` for an offline-only dependency diagnostic.
Read the exact failure before suggesting a settings change.

The commands above produce the silent video and its separate sound file. Follow
[the sound and export steps](../CLAUDE-INSTRUCTIONS.md#6-making-a-reel-step-by-step)
to combine them and level the finished MP4.

For the bundled Qur'an example, render its video and sound before mixing the recitation:

    cp examples/v67_twentyone.py .
    python3 v67_twentyone.py
    python3 sfx_reels.py v67
    python3 quran_mix.py v67                        # -> out/Twenty_One.mp4

Then follow the same instructions to level the final file. This older example shows the
recitation workflow; use `v69_callfirst_ember.py` as the starting point for new course reels.

Files
- nv.py: canvas, colors, fonts, Figure (pictogram rig), pose library, easing, text, Arabic, reflections, grain, render.
- cine.py: light pools, beams, night tint, beats() text, thought bubbles, flowers.
- kit2.py: walk_to, arm IK, palms, burst, shake_head, end_card, run() (stills or full render, ungraded).
- lanes.py: the two-lane layer (frame_two: header, round label, lane labels, end card). Use this for every reel.
- palette.py + ember.py: the Ember colour grade and run_graded(), the drop-in for run() that every reel renders through.
- formula.py: an older single-figure text layer. Not used for new reels; kept for the examples that need it.
- sfx.py: synth sound library (step, cloth, thump, pluck, swell, whoosh, splash, wind, crickets, Mix...).
- sfx_reels.py: one build_vXX per reel; v60–v75 are worked examples (build_v69 / build_v69e are two-lane).
- quran_mix.py: recitation overlay for Qur'an end cards (CFG per reel).
- audio_src/hq: 28 cached Alafasy ayah mp3s (SSSAAA.mp3) + timings.json.gz (losslessly compressed word times for every ayah in the Qur'an).
- tools/: sheet.py (contact sheets), find_cuts.sh (pauses in a recitation), word_times.py. Treat cached
  word timings as a rough guide; listen to verify the exact phrase and cut boundaries.
- examples/: v69_callfirst_ember.py is the current format (two lanes, Ember). v63 (explainer, Qur'an), v67 (two-lane,
  Qur'an, older end card), v69 (same reel, older end card), v70/v73/v75 (the older formula layer).

Fonts: Amiri, IBM Plex Mono and Space Mono, all under the SIL Open Font License. Recitations: Mishary Rashid Alafasy,
from everyayah.com.

Third-party source credits and licence scope: [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md).
