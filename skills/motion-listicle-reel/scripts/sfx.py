#!/usr/bin/env python3
"""
sfx.py - lay subtle transition ticks under a rendered reel.

  python3 scripts/sfx.py spec.json in.mp4 out.mp4

A review aid and a fallback for platforms with no audio library. Real
distribution adds music in the app - see reference/sound.md. Deliberately
quiet: a soft wooden tick at each scene boundary, a short filtered rise
under each one.
"""
import json, math, subprocess, sys, tempfile, wave, struct, array
from pathlib import Path

SR = 44100


def tick(buf, at, freq=1180.0, amp=0.16, decay=38.0):
    i0 = int(at * SR)
    for n in range(int(SR * 0.16)):
        t = n / SR
        env = math.exp(-decay * t)
        v = (math.sin(2 * math.pi * freq * t) * 0.6 +
             math.sin(2 * math.pi * freq * 2.01 * t) * 0.25) * env * amp
        i = i0 + n
        if 0 <= i < len(buf):
            buf[i] += v


def rise(buf, at, dur=0.30, amp=0.055):
    """a short noise swell, low-passed by a one-pole, for the highlight wipe"""
    i0, n = int(at * SR), int(dur * SR)
    state, seed = 0.0, 0x2F6E2B1
    for k in range(n):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        white = (seed / 0x3FFFFFFF) - 1.0
        state += (white - state) * 0.035           # ~250 Hz one-pole
        env = math.sin(math.pi * k / n) ** 2
        i = i0 + k
        if 0 <= i < len(buf):
            buf[i] += state * env * amp


def main(spec_path, src, dst):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    total = sum(s["dur"] for s in spec["scenes"])
    buf = array.array("d", [0.0]) * 1
    buf = array.array("d", [0.0] * int((total + 0.6) * SR))

    at = 0.0
    for i, s in enumerate(spec["scenes"]):
        if i:
            tick(buf, at, freq=1180 if s["type"] == "item" else 880)
            rise(buf, at + 0.02)
        # a quieter tick under the highlight wipe, ~0.5s in
        if s.get("text", "").find("[") >= 0:
            tick(buf, at + 0.52, freq=1560, amp=0.07, decay=60)
        at += s["dur"]

    peak = max(abs(v) for v in buf) or 1.0
    scale = min(1.0, 0.5 / peak)
    tmp = Path(tempfile.mkdtemp()) / "sfx.wav"
    with wave.open(str(tmp), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(struct.pack("<%dh" % len(buf),
                                  *(int(max(-1, min(1, v * scale)) * 32000) for v in buf)))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-i", str(tmp),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", dst], check=True)
    print("wrote", dst)


if __name__ == "__main__":
    main(*sys.argv[1:4])
