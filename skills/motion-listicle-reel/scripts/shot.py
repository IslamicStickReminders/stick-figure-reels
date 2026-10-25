#!/usr/bin/env python3
"""shot.py SPEC t1 [t2 ...] OUTDIR - grab single full-res frames for inspection."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
from playwright.sync_api import sync_playwright
spec_path, *times, outdir = sys.argv[1:]
spec = json.loads(Path(spec_path).read_text(encoding='utf-8'))
Path(outdir).mkdir(parents=True, exist_ok=True)
with sync_playwright() as pw:
    br = pw.chromium.launch(args=["--force-color-profile=srgb","--font-render-hinting=none"])
    pg = br.new_page(viewport={"width":1080,"height":1920}, device_scale_factor=1)
    errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto((ROOT/"runtime"/"index.html").as_uri())
    pg.wait_for_function("() => document.fonts.status === 'loaded'")
    print("dur", pg.evaluate("s => window.boot(s)", spec))
    for t in times:
        pg.evaluate("t => window.renderFrame(t)", float(t))
        pg.screenshot(path=f"{outdir}/t{t}.jpg", type="jpeg", quality=95)
    if errs: print("ERRORS", errs[:5])
    br.close()
print("ok")
