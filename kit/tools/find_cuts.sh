#!/bin/bash
# Print the pauses inside a recitation mp3 so you can pick seg=(start, end) for quran_mix.py.
# Usage: bash tools/find_cuts.sh audio_src/hq/017023.mp3
ffmpeg -nostats -i "$1" -af silencedetect=n=-32dB:d=0.18 -f null - 2>&1 | grep -E "silence_(start|end)" | sed 's/.*silence_/  /'
ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"
