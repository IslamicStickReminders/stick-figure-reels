"""#63 Same Word — MIRACLE vs NORMAL (Qur'an 36:82, recited from "an yaqula lahu kun fayakun").

Two lanes: MIRACLE on top, NORMAL underneath. Same fire, same water, same night sky in both.
One كُن sits between them. Each time it's said, one ring goes out to both lanes at once and both answer:
  1. the fire catches in both. Top: the log in it stays white. Bottom: it burns to ash.
  2. the water. Top: it splits and stands in two walls. Bottom: a cloud forms and rain falls into it.
  3. the moon rises in both. Top: it splits in two. Bottom: it just rises.
Header the whole time: WHICH ONE WAS HARDER FOR ALLAH?
At the end MIRACLE and NORMAL fade out and only the كُن is left: NEITHER. HE SAID THE SAME WORD TO BOTH.
"""
from kit2 import *

LANES = dict(A=900, B=1430)
KX, KY = 540, 1078               # the word, between the lanes
FX = 196                         # fire
WX0, WX1, WGAP = 352, 788, 34    # water span, half-gap of the split
WD = 52                          # water depth
MX = 930                         # moon

KUN = [0.55, 2.55, 4.55]
RING = 0.32                      # time for the ring to reach the lanes
E1 = 6.7
E2 = 7.75
DUR = 9.9
N = int(DUR * FPS)


def hit(k):
    return KUN[k] + RING


# ---------------------------------------------------------------- the word
def kun_word(c, t):
    a = 0.0
    pop = 0.0
    for k in KUN + [E1 + 0.35]:
        if t >= k:
            a = 0.42
            pop = max(pop, math.exp(-(t - k) * 5.0))
    if t >= E1 + 0.35:
        a = lerp(0.42, 1.0, seg(t, E1 + 0.35, E1 + 0.7))
    a = max(a, 0.35 * pop + a)
    if t < KUN[0]:
        a = 0.18
    s = 1 + 0.16 * pop
    arabic(c, 'كُنْ', KX, KY + 22, 62 * s, WHITE, a=min(1.0, a + 0.58 * pop))
    # rings: one command reaching both lanes
    for k in KUN + [E1 + 0.35]:
        u = seg(t, k, k + 0.75)
        if 0 < u < 1:
            r = 40 + 560 * ease_out(u)
            c.drawCircle(KX, KY, r, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.5,
                                               Color=C(LABEL, 0.45 * (1 - u))))


# ---------------------------------------------------------------- 1. fire
def tongue(c, x, y, w, h, sway, color, a):
    tip = (x + sway, y - h)
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    p.cubicTo(x - w / 2, y - h * 0.45, tip[0] - w * 0.18, tip[1] + h * 0.3, tip[0], tip[1])
    p.cubicTo(tip[0] + w * 0.18, tip[1] + h * 0.3, x + w / 2, y - h * 0.45, x + w / 2, y)
    p.quadTo(x, y + w * 0.28, x - w / 2, y)
    p.close()
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=C(color, a)))


def fire(c, G, t, lane):
    fa = ease(seg(t, hit(0), hit(0) + 0.45))
    for k, dx in enumerate((-58, -32, 0, 32, 58)):
        rect(c, FX + dx - 14, G - 16 + (3 if k in (0, 4) else 0), 28, 16, (112, 114, 122), r=7)
    # the log: stays white on top; burns to ash below
    burn = ease(seg(t, hit(0) + 0.35, hit(0) + 1.25)) if lane == 'B' else 0.0
    crumble = ease(seg(t, hit(0) + 1.1, hit(0) + 1.6)) if lane == 'B' else 0.0
    col = tuple(lerp(a, b, burn) for a, b in zip((236, 236, 232), (58, 56, 60)))
    lw = 132 * (1 - 0.75 * crumble)
    lh = 26 * (1 - 0.55 * crumble)
    rect(c, FX - lw / 2, G - 40 + 14 * crumble, lw, lh, col, r=lh / 2)
    if crumble > 0:
        c.drawOval(skia.Rect(FX - 40, G - 22, FX + 40, G - 6), skia.Paint(AntiAlias=True, Color=C((84, 82, 86), crumble)))
    if fa <= 0:
        return
    # below, the fire dies down once there's nothing left to burn
    size = fa * (1 - 0.55 * ease(seg(t, hit(0) + 1.4, hit(0) + 2.2)) if lane == 'B' else fa)
    flick = lambda k, s: math.sin(t * s + k * 1.7) + 0.5 * math.sin(t * s * 1.9 + k)
    base = G - 26
    for k, (dx, h0, w0) in enumerate(((0, 116, 46), (-26, 84, 36), (26, 78, 36))):
        h = h0 * size * (1 + 0.1 * flick(k, 9))
        tongue(c, FX + dx, base, w0, h, 7 * flick(k, 7), (255, 236, 206), 0.93)
    for k, (dx, h0, w0) in enumerate(((0, 62, 25), (12, 44, 17))):
        h = h0 * size * (1 + 0.12 * flick(k + 3, 11))
        tongue(c, FX + dx, base + 2, w0, h, 5 * flick(k + 5, 8), RED, 0.9)
    # the same log in front of the flames: untouched on top, blackening and crumbling below
    if lane == 'A':
        rect(c, FX - lw / 2, G - 40, lw, lh, (238, 238, 234), r=lh / 2, a=fa * 0.95)
    elif crumble < 1:
        rect(c, FX - lw / 2, G - 40 + 14 * crumble, lw, lh, col, r=lh / 2, a=fa * 0.95 * (1 - crumble))
    # ash flakes rising from the burning log below
    if lane == 'B':
        for k in range(9):
            ts = hit(0) + 0.6 + 0.12 * k
            dt = t - ts
            if 0 <= dt < 1.1:
                x = FX - 30 + 8 * k + 20 * math.sin(dt * 4 + k)
                y = G - 50 - 170 * dt
                rect(c, x - 3, y - 2, 6, 4, (52, 50, 54), a=0.9 * (1 - dt / 1.1), r=1)
    light_pool(c, FX, G - 40, 260, 170, WARM, a=0.12 * size)


# ---------------------------------------------------------------- 2. water
WATER = (34, 42, 56)
WATER_TOP = (70, 84, 102)


def water(c, G, t, lane):
    u = ease(seg(t, hit(1), hit(1) + 0.7))
    if lane == 'A' and u > 0.01:
        mid = (WX0 + WX1) / 2
        wall = WD + 210 * u
        gap = WGAP * u * 1.0
        wob = 4 * math.sin(t * 6) * u
        # two walls with straight faces at the split
        for side in (-1, 1):
            outer = WX0 if side < 0 else WX1
            inner = mid + side * gap
            p = skia.Path()
            p.moveTo(outer, G)
            p.lineTo(outer, G - WD)
            p.cubicTo(outer - side * 70, G - WD, inner + side * 70, G - wall + side * wob, inner + side * 16, G - wall + side * wob)
            p.quadTo(inner, G - wall + side * wob, inner, G - wall + 14 + side * wob)
            p.lineTo(inner, G)
            p.close()
            c.drawPath(p, skia.Paint(AntiAlias=True, Color=C(WATER)))
            c.drawPath(p, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.5, Color=C(WATER_TOP)))
            for k in range(1, 4):
                yy = G - wall * k / 4.2
                if yy < G - WD - 4:
                    line(c, inner - side * 4, yy, inner - side * 4 - side * 26 * (1 - k / 5), yy + 3, WATER_TOP, 2, a=0.6 * u)
        if u > 0.2:
            # the dry path between
            line(c, mid - gap + 2, G - 1, mid + gap - 2, G - 1, (150, 152, 158), 3, a=u)
        return
    if lane == 'A':
        rect(c, WX0, G - WD, WX1 - WX0, WD, WATER, r=3)
        line(c, WX0, G - WD, WX1, G - WD, WATER_TOP, 2.5)
        return
    # bottom: a cloud, rain, the water rises a little
    rise = 16 * ease(seg(t, hit(1) + 0.4, hit(1) + 1.6))
    d = WD + rise
    rect(c, WX0, G - d, WX1 - WX0, d, WATER, r=3)
    line(c, WX0, G - d, WX1, G - d, WATER_TOP, 2.5)
    ca = ease(seg(t, hit(1), hit(1) + 0.35))
    cx, cy = (WX0 + WX1) / 2 + 40, G - 222
    for dx, dy, r in ((-70, 8, 34), (-24, -14, 46), (30, -4, 40), (76, 10, 30)):
        c.drawCircle(cx + dx, cy + dy, r, skia.Paint(AntiAlias=True, Color=C((96, 98, 108), 0.95 * ca)))
    ra = ca * (1 - seg(t, hit(1) + 1.7, hit(1) + 2.0))
    if ra > 0:
        for k in range(26):
            x = cx - 100 + 8 * k
            ph = ((t * 2.6 + k * 0.37) % 1.0)
            y0 = cy + 30 + ph * (G - d - cy - 30)
            line(c, x - 3, y0, x, y0 + 16, (150, 160, 176), 2, a=0.75 * ra)
        for k in range(5):
            ph = ((t * 1.6 + k * 0.27) % 1.0)
            x = cx - 90 + 45 * k
            r = 4 + 20 * ph
            c.drawOval(skia.Rect(x - r, G - d - r * 0.25, x + r, G - d + r * 0.25),
                       skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.5,
                                  Color=C(WATER_TOP, ra * (1 - ph))))


# ---------------------------------------------------------------- 3. moon
def moon(c, G, t, lane):
    u = ease(seg(t, hit(2), hit(2) + 0.9))
    if u <= 0:
        return
    y = lerp(G + 40, G - 290, u)
    x = lerp(MX + 40, MX, u)
    r = 36
    sp = ease(seg(t, hit(2) + 1.0, hit(2) + 1.45)) if lane == 'A' else 0.0
    c.save()
    c.clipRect(skia.Rect(0, 0, W, G - 1))
    light_pool(c, x, y, 120, 120, (230, 232, 236), a=0.07 * u)
    if sp <= 0:
        c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Color=C((232, 232, 228))))
    else:
        d = 24 * sp
        for side in (-1, 1):
            c.save()
            c.translate(side * d, -4 * sp * side)
            c.clipRect(skia.Rect(x + (1.5 if side > 0 else -r - 2), y - r - 2, x + (r + 2 if side > 0 else -1.5), y + r + 2))
            c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Color=C((232, 232, 228))))
            c.restore()
    c.restore()


STARS = [(640, 0.62), (720, 0.48), (790, 0.7), (870, 0.55), (1010, 0.66), (980, 0.42), (560, 0.5)]


def stars(c, G, t):
    for k, (x, h) in enumerate(STARS):
        y = G - 170 - 170 * h
        tw = 0.35 + 0.3 * math.sin(t * (1.2 + 0.35 * k) + k * 2)
        c.drawCircle(x, y, 2.6, skia.Paint(AntiAlias=True, Color=C(LABEL, tw)))


def world(c, t):
    for lane in 'AB':
        G = LANES[lane]
        stars(c, G, t)
        moon(c, G, t, lane)
        line(c, 30, G, 1050, G, (70, 72, 78), 2, cap=False)
        water(c, G, t, lane)
        fire(c, G, t, lane)


# ---------------------------------------------------------------- text
SUBS = [("FIRE THAT DOESN'T BURN.", 'FIRE THAT BURNS.'), ('SEA THAT SPLITS.', 'RAIN THAT FALLS.'),
        ('MOON THAT SPLITS.', 'MOON THAT RISES.')]


def labels(c, t):
    fade = 1 - seg(t, E1, E1 + 0.4)
    GA, GB = LANES['A'], LANES['B']
    text(c, 'MIRACLE', 92, GA + 62, 27, WHITE, a=fade, spacing=0.3, align='left')
    text(c, 'NORMAL', 92, GB + 62, 27, WHITE, a=fade, spacing=0.3, align='left')
    for k, (sa, sb) in enumerate(SUBS):
        tk = hit(k) + (1.05 if k == 0 else 0.75 if k == 1 else 1.1)
        nxt = hit(k + 1) + 0.2 if k < 2 else 99
        a = seg(t, tk, tk + 0.25) * (1 - seg(t, nxt - 0.2, nxt)) * fade
        if a > 0:
            text(c, sa, 92, GA + 100, 21, LABEL, a=a, spacing=0.14, align='left')
            text(c, sb, 92, GB + 100, 21, LABEL, a=a, spacing=0.14, align='left')


def frame(c, t, i):
    background(c)
    tint(c, NIGHT, 0.3)
    pic = record(lambda rc: world(rc, t))
    for G in LANES.values():
        c.save()
        c.clipRect(skia.Rect(0, G, W, G + 120))
        reflection(c, pic, G, strength=0.14, fade=110, blur=1.5)
        c.restore()
    c.drawPicture(pic)
    kun_word(c, t)
    labels(c, t)
    text(c, 'WHICH ONE WAS HARDER FOR ALLAH?', 540, 300, 31, WHITE, a=0.95, spacing=0.12)
    text(c, 'NEITHER.', 540, 392, 56, WHITE, a=seg(t, E1, E1 + 0.3), spacing=0.16)
    text(c, 'HE SAID THE SAME WORD TO BOTH.', 540, 452, 26, LABEL, a=seg(t, E1 + 0.35, E1 + 0.7), spacing=0.1)
    arabic(c, 'أَن يَقُولَ لَهُ كُن فَيَكُونُ', 540, 538, 46, LABEL, a=seg(t, E2, E2 + 0.35))
    text(c, '“…THAT HE SAYS TO IT, ‘BE,’ AND IT IS.”', 540, 590, 21, LABEL, a=seg(t, E2 + 0.15, E2 + 0.5), spacing=0.06)
    text(c, "QUR'AN 36:82", 540, 634, 20, DIM, a=seg(t, E2 + 0.35, E2 + 0.7), tf=TF_REG)
    vignette(c, 0.5)
    grain(c, i)


EVENTS = dict(dur=DUR, e1=E1, e2=E2, kun=KUN, ring=RING, final_kun=E1 + 0.35)

if __name__ == '__main__':
    run(frame, 'v63', N, DUR, EVENTS)
