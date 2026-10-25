"""Text layer for the 8-beat formula reels: HOOK → PROMISE → VALUE 1 → OPEN LOOP 1 → VALUE 2 → OPEN LOOP 2 →
VALUE 3 → CTA. One figure on one floor; all the text lives in the band above the scene."""
from kit2 import *

FLOOR = 1330
TXT = 300                       # top of the text band

# default beat times (seconds)
T = dict(hook=(0.0, 3.0), promise=(1.4, 3.0), v1=(3.0, 6.7), l1=(6.7, 7.8), v2=(7.8, 11.5), l2=(11.5, 12.6),
         v3=(12.6, 16.4), cta=(16.4, 99))
DUR = 18.4


def _in(t, a, b, fin=0.25, fout=0.25, hard_in=False):
    if t < a or t > b:
        return 0.0
    ai = 1.0 if hard_in else seg(t, a, a + fin)
    return ai * (1 - seg(t, b - fout, b))


def hook(c, t, lines, span=None):
    a0, a1 = span or T['hook']
    a = _in(t, a0, a1, hard_in=True)
    for k, ln in enumerate(lines):
        text(c, ln, 540, TXT + 120 + 64 * k, 46, WHITE, a=a, spacing=0.1)


def promise(c, t, line, span=None):
    a0, a1 = span or T['promise']
    a = _in(t, a0, a1)
    text(c, line, 540, TXT + 120 + 64 * 2 + 24, 26, LABEL, a=a, spacing=0.1)


def value(c, t, n, title, sub, span):
    a0, a1 = span
    a = _in(t, a0, a1)
    if a <= 0:
        return
    pop = 1 + 0.08 * math.sin(math.pi * seg(t, a0, a0 + 0.3))
    text(c, f'{n} / 3', 540, TXT + 36, 22, DIM, a=a, spacing=0.3)
    size = min(40.0, 940.0 / (len(title) * 0.72))
    text(c, title, 540, TXT + 110, size * pop, WHITE, a=a, spacing=0.1)
    for k, ln in enumerate(sub):
        text(c, ln, 540, TXT + 170 + 38 * k, 25, LABEL, a=_in(t, a0 + 0.35, a1), spacing=0.08)


def loop(c, t, line, span):
    """an open loop: one line, a red marker, the next thing teased but not given."""
    a0, a1 = span
    a = _in(t, a0, a1, fin=0.15, fout=0.15)
    if a <= 0:
        return
    w = text(c, line, 540, TXT + 140, 32, WHITE, a=a, spacing=0.08)
    x0 = 540 - (w or 0) / 2 - 24
    c.drawCircle(x0, TXT + 129, 7, skia.Paint(AntiAlias=True, Color=C(RED, a)))


def cta(c, t, l1, l2, cite, span=None):
    a0, a1 = span or T['cta']
    text(c, l1, 540, TXT + 110, 40, WHITE, a=seg(t, a0, a0 + 0.3), spacing=0.1)
    text(c, l2, 540, TXT + 170, 27, LABEL, a=seg(t, a0 + 0.3, a0 + 0.6), spacing=0.08)
    text(c, cite, 540, TXT + 222, 20, DIM, a=seg(t, a0 + 0.5, a0 + 0.8), tf=TF_REG)


def stage(c):
    line(c, 30, FLOOR, 1050, FLOOR, (70, 72, 78), 2, cap=False)


def finish(c, pic, i):
    c.save()
    c.clipRect(skia.Rect(0, FLOOR, W, FLOOR + 160))
    reflection(c, pic, FLOOR, strength=0.15, fade=140, blur=1.5)
    c.restore()
