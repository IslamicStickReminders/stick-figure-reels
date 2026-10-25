"""Word-by-word times (seconds) for an ayah in the everyayah Alafasy_128kbps mp3, from audio_src/hq/timings.json.
Usage: python3 tools/word_times.py 17 23     -> word index, start, end. Use them to cut just the relevant words."""
import json, sys
s, a = int(sys.argv[1]), int(sys.argv[2])
for e in json.load(open('audio_src/hq/timings.json')):
    if e['surah'] == s and e['ayah'] == a:
        for w0, w1, t0, t1 in e['segments']:
            print(f'word {w0 + 1:>2}  {t0 / 1000:7.2f}  {t1 / 1000:7.2f}')
        break
