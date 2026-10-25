# Third-party materials

## Python renderer dependencies

`kit/offline/wheels.tar.xz` bundles official PyPI wheels for **skia-python
144.1**, **uharfbuzz 0.57.0** and **pybind11 3.1.0**. Only their archive
compression was changed; file payloads, RECORD entries and included upstream
licences remain unchanged. Each wheel retains its own licence in its
`.dist-info/licenses/` directory. Those terms apply independently of the
course and font permissions.

See [`kit/offline/README.md`](kit/offline/README.md) for supported runtimes and
upstream project links. `kit/offline/manifest.json` records the original PyPI
download URLs and checksums, plus checksums for the distributed archive and
repacked wheels.

## Fonts

The bundled font files retain their own SIL Open Font License 1.1 terms:

- **Amiri Regular and Bold** — The Amiri Project Authors. See `kit/fonts/OFL-Amiri.txt`.
- **IBM Plex Mono Regular and Medium** — IBM Corp. See `kit/fonts/OFL-IBMPlexMono.txt`.
- **Space Mono Regular** — The Space Mono Project Authors. See `kit/fonts/OFL-SpaceMono.txt`.

Keep these license and copyright notices with redistributed copies of the fonts. The font licenses do not license the course, Python code, or audio recordings.

## Qur'an recitations and timing data

The 28 MP3 files in `kit/audio_src/hq/` are attributed in the supplied course to **Mishary Rashid Alafasy**, sourced through **EveryAyah**, using the `Alafasy_128kbps` collection (`https://everyayah.com/data/Alafasy_128kbps/`). Their filenames encode the surah and ayah as `SSSAAA.mp3`.

`kit/audio_src/hq/timings.json.gz` contains the supplied word-segment timing data, losslessly compressed from `timings.json` and used by the included tools. No timing records were changed. The supplied package does not identify a separate license or original data author for this file.

These credits identify the supplied sources; they are not a new license grant for the recordings or timing data. The course's permission to use its code for your own reels and the fonts' OFL terms do not grant rights to these third-party materials. Check the relevant source's terms or obtain permission before uses or redistribution that require it.
