#!/usr/bin/env python3
"""
render.py - turn a reel spec into an mp4.

  python3 scripts/render.py examples/jumuah-8-sunnahs.json out/reel.mp4
  python3 scripts/render.py spec.json out/preview.mp4 --preview
  python3 scripts/render.py spec.json --contact out/sheet.jpg
  python3 scripts/render.py spec.json --stills out/cards/     # static carousel

Frames are grabbed one at a time from a paused page: the runtime
exposes renderFrame(t), so frame N is a pure function of N/fps and
the render is reproducible. No video capture, no dropped frames.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / "runtime" / "index.html"


def render(spec_path, out_path, fps=30, scale=1.0, contact=None, keep=False,
           quiet=False, stills=None):
    from playwright.sync_api import sync_playwright

    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    W = int(spec["meta"].get("w", 1080) * scale)
    H = int(spec["meta"].get("h", 1920) * scale)
    tmp = Path(tempfile.mkdtemp(prefix="reelframes_"))

    with sync_playwright() as pw:
        br = pw.chromium.launch(args=["--force-color-profile=srgb",
                                      "--disable-lcd-text",
                                      "--font-render-hinting=none"])
        pg = br.new_page(viewport={"width": 1080, "height": 1920},
                         device_scale_factor=scale)
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.goto(RUNTIME.as_uri())
        pg.wait_for_function("() => document.fonts.status === 'loaded'", timeout=20000)
        dur = pg.evaluate("spec => window.boot(spec)", spec)
        if errors:
            br.close(); raise SystemExit("page error:\n  " + "\n  ".join(errors[:6]))

        # stills: one settled frame per scene - a carousel, or a static
        # infographic set, from the same spec that makes the video
        if stills:
            out = Path(stills); out.mkdir(parents=True, exist_ok=True)
            at = 0.0
            for i, sc in enumerate(spec["scenes"]):
                # 82% through a scene: every reveal has landed, nothing has faded
                pg.evaluate("t => window.renderFrame(t)", at + sc["dur"] * 0.82)
                pg.screenshot(path=str(out / f"{i + 1:02d}-{sc['type']}.png"), type="png")
                at += sc["dur"]
            print(f"  stills -> {out}/  ({len(spec['scenes'])} png)")
            if not out_path and not contact:
                br.close(); return dur

        n = int(round(dur * fps))
        if not quiet:
            print(f"  {dur:.2f}s  {n} frames  {W}x{H} @{fps}fps")
        t0 = time.time()
        for i in range(n):
            pg.evaluate("t => window.renderFrame(t)", i / fps)
            pg.screenshot(path=str(tmp / f"{i:06d}.jpg"), type="jpeg", quality=95)
            if not quiet and i % 120 == 0 and i:
                el = time.time() - t0
                print(f"    {i}/{n}  {el:.0f}s elapsed, ~{el/i*(n-i):.0f}s left")
        if errors:
            print("  warnings:", errors[:3], file=sys.stderr)
        br.close()

    if contact:
        pick = [tmp / f"{int(i*(n-1)/23):06d}.jpg" for i in range(24)]
        Path(contact).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["montage", *[str(p) for p in pick], "-tile", "6x4",
                        "-geometry", "+6+6", "-background", "#0b0206", str(contact)], check=True)
        print(f"  contact sheet -> {contact}")

    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        cmd = ["ffmpeg", "-y", "-v", "error", "-framerate", str(fps),
               "-i", str(tmp / "%06d.jpg"),
               "-c:v", "libx264", "-preset", "slow", "-crf", "18",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart",
               "-vf", f"scale={W}:{H}:flags=lanczos", str(out_path)]
        subprocess.run(cmd, check=True)
        print(f"  video -> {out_path}  ({os.path.getsize(out_path)/1e6:.1f} MB)")

    if keep:
        print(f"  frames kept in {tmp}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    return dur


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--preview", action="store_true", help="half size, 15fps - for iterating")
    ap.add_argument("--contact", help="also write a 24-frame contact sheet here")
    ap.add_argument("--stills", help="write one settled PNG per scene into this dir")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    render(a.spec, a.out, fps=15 if a.preview else a.fps,
           scale=0.5 if a.preview else 1.0, contact=a.contact, keep=a.keep,
           stills=a.stills)
