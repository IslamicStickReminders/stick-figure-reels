"""Word-by-word times (seconds) for an ayah in the everyayah Alafasy_128kbps mp3.
Reads audio_src/hq/timings.json.gz, with support for older uncompressed timings.json.
Usage: python3 tools/word_times.py 17 23 -> word index, start, end.
Use these timings as a rough guide and listen to verify the exact phrase and cuts.
"""
import gzip
import json
import sys
from pathlib import Path

s, a = int(sys.argv[1]), int(sys.argv[2])
data_dir = Path(__file__).resolve().parents[1] / "audio_src" / "hq"
timings = data_dir / "timings.json.gz"
if not timings.is_file():
    timings = data_dir / "timings.json"
read = gzip.open if timings.suffix == ".gz" else open
with read(timings, "rt", encoding="utf-8") as source:
    entries = json.load(source)
for e in entries:
    if e['surah'] == s and e['ayah'] == a:
        for w0, w1, t0, t1 in e['segments']:
            print(f'word {w0 + 1:>2}  {t0 / 1000:7.2f}  {t1 / 1000:7.2f}')
        break
