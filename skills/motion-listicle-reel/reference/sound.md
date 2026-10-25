# Sound

The renderer writes a silent mp4 deliberately.

## Why silent

Upload silent and add audio in the Instagram or TikTok composer if wanted.
Check the track's permitted uses for the account and post, especially for
commercial content. Availability in an app is not blanket permission, and
permission on one platform does not establish permission elsewhere.

For audio added directly to the file, use material you have permission to
include in the intended distribution.

## Picking a track in the app

- Instrumental. A vocal track competes with on-screen words the viewer is
  reading, and this format is all reading.
- 85-110 BPM. The scene changes land every ~6.5s; a slow bed lets them land.
- No drop. The format has no climax to match it to.
- For religious content: instrument-free vocal beds (nasheed-style) are the
  safe default and are plentiful in both libraries.

## Optional transition ticks

If a silent file is awkward to review, or the reel is going somewhere that
has no audio library:

```bash
python3 scripts/sfx.py spec.json out/reel.mp4 out/reel-sfx.mp4
```

It synthesises a soft tick at each scene boundary and a short rise under
each highlight wipe, then muxes it in. It is a review aid and a fallback,
not a soundtrack - it is deliberately almost inaudible.
