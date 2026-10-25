"""The two-lane layer: two men, same situation, one choice apart.

A reel script does `from lanes import *`, draws both lanes in `world(c, t)`, and its `frame` calls
`frame_two(...)`, which adds the header, the round label, the lane labels and the end card, then
grain and vignette. Render with `run_graded(frame, 'vNN', N, DUR, EVENTS)`.

Layout: lane A (top, the losing man) floor at y 930; lane B (bottom, the winner) floor at y 1390.
Three rounds at ROUNDS; the end card comes in at E1 while the scene keeps running underneath.
"""
from kit2 import *
from ember import run_graded

LANES = dict(A=930, B=1390)
ROUNDS = [0.4, 2.6, 4.8]
E1 = 7.2
E2 = E1 + 1.05
DUR = round(E2 + 0.55 + 1.05, 2)
N = int(DUR * FPS)


def rnd(t):
    """index of the current round (-1 before the first)."""
    k = -1
    for i, r in enumerate(ROUNDS):
        if t >= r - 0.02:
            k = i
    return k


def frame_two(c, t, i, world, header, round_names, label_a, label_b, verdict, source, cite, src_size=17):
    """header: [(t0, t1, TEXT), ...] for beats(); round_names: one string per round;
    verdict: (line 1, line 2); source: list of lines; cite: 'SAHIH AL-BUKHARI 5991' or "QUR'AN 17:23"."""
    background(c)
    pic = record(lambda rc: world(rc, t))
    for G in LANES.values():
        c.save(); c.clipRect(skia.Rect(0, G, W, G + 120))
        reflection(c, pic, G, strength=0.08, fade=60, blur=1.5); c.restore()
    c.drawPicture(pic)
    beats(c, t, header, 486, size=32, spacing=0.12)
    k = max(0, rnd(t))
    ya = seg(t, ROUNDS[0] - 0.05, ROUNDS[0] + 0.15) * (1 - seg(t, E1 - 0.35, E1))
    pop = 1 + 0.12 * math.sin(math.pi * seg(t, ROUNDS[k] - 0.05, ROUNDS[k] + 0.2))
    text(c, round_names[k], 540, 572, 36 * pop, WHITE, a=0.92 * ya, spacing=0.18)
    text(c, label_a, 540, LANES['A'] + 66, 24, LABEL, spacing=0.15)
    text(c, label_b, 540, LANES['B'] + 66, 24, LABEL, spacing=0.15)
    text(c, verdict[0], 540, 262, 28, LABEL, a=seg(t, E1, E1 + 0.35), spacing=0.08)
    text(c, verdict[1], 540, 344, 48, WHITE, a=seg(t, E1 + 0.3, E1 + 0.65), spacing=0.13)
    for kk, ln in enumerate(source):
        text(c, ln, 540, 424 + 30 * kk, src_size, LABEL, a=seg(t, E2 + 0.08 * kk, E2 + 0.08 * kk + 0.35), spacing=0.03)
    text(c, cite, 540, 424 + 30 * len(source) + 18, 20, DIM, a=seg(t, E2 + 0.35, E2 + 0.7), tf=TF_REG)
    vignette(c, 0.5)
    grain(c, i)
