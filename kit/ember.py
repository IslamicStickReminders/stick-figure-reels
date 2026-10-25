"""run_graded(): a drop-in for kit2.run() that colour-grades every still and every video frame
with a palette from palette.py (default 'ember', the house look)."""
import json, glob
import numpy as np
from PIL import Image
from kit2 import *
from palette import PALETTES, grade_rgb


def _graded(surface, pal):
    a = surface.makeImageSnapshot().toarray()            # BGRA
    g = grade_rgb(a[..., [2, 1, 0]], pal)
    out = np.empty_like(a)
    out[..., 0], out[..., 1], out[..., 2], out[..., 3] = g[..., 2], g[..., 1], g[..., 0], 255
    return out, g


def run_graded(frame, name, n, dur, events, pal='ember'):
    P_ = PALETTES[pal]
    os.makedirs('out', exist_ok=True)
    json.dump(events, open(f'out/{name}_events.json', 'w'), indent=1)
    s = skia.Surface(W, H)
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        os.makedirs(f'test/{name}', exist_ok=True)
        for f_ in glob.glob(f'test/{name}/*.png'):
            os.remove(f_)
        for tt in [float(x) for x in sys.argv[2:]]:
            c = s.getCanvas(); c.clear(skia.ColorBLACK); frame(c, tt, int(tt * FPS))
            Image.fromarray(_graded(s, P_)[1]).save(f'test/{name}/t{tt:05.2f}.png')
        return
    wr = Writer(f'out/{name}_silent.mp4')
    for i in range(n):
        c = s.getCanvas(); c.clear(skia.ColorBLACK); frame(c, i / FPS, i)
        wr.p.stdin.write(_graded(s, P_)[0].tobytes())
    wr.close()
