"""#70 Fall Off — formula reel (Hook / Promise / Value / Open loop / Value / Open loop / Value / CTA).
Sahih Muslim 244 (wudu), Sahih Muslim 666 (steps to the masjid), Sahih al-Bukhari 6405 (subhanallahi wa bihamdihi x100).

One man, covered in dark stains.
1. Wudu: hands, face, feet. The stains there run off with the water.
2. Walking to the masjid, up four stairs: on the flat, a stain drops off; the next step lifts him a stair.
3. He sits at the top and the count runs 1 to 100. Below him a sea of foam; it clears as the count climbs, and at
   100 the last stains are gone.
"""
from formula import *

FIG = Figure(300)
G = FLOOR
SINK_X = 760
STAIR_X0, STAIR_W, STAIR_H, NSTAIR = 470, 112, 34, 4
TOP_X = STAIR_X0 + NSTAIR * STAIR_W - 10     # where he sits at the top, at the masjid door

N = int(DUR * FPS)
V1, L1, V2, L2, V3, CTA = T['v1'], T['l1'], T['v2'], T['l2'], T['v3'], T['cta']

# ---------------------------------------------------------------- stains
SEGS = dict(torso=('hip', 'sh', FIG.tw), Rth=('hip', 'Rk', FIG.lw), Rua=('ash', 'Re', FIG.lw),
            Rfa=('Re', 'Rh', FIG.lw), Lfa=('Le', 'Lh', FIG.lw), Rsh=('Rk', 'Rf', FIG.lw), Lsh=('Lk', 'Lf', FIG.lw))
WASH_HANDS = (3.5, 4.2)
WASH_FACE = (4.25, 4.95)
WASH_FEET = (5.05, 5.85)
STEP_T = [V2[0] + 0.35 + 0.42 * k for k in range(8)]          # 8 steps, odd ones on the flat
FOAM = (V3[0] + 0.3, V3[1] - 0.6)

SPOTS = [  # limb, u, perp, r, gone-at
    ('head', -0.4, 0.3, 7.5, WASH_FACE[0] + 0.45), ('head', 0.35, -0.2, 6.5, WASH_FACE[0] + 0.5),
    ('Rfa', 0.45, 0.1, 6.5, WASH_HANDS[0] + 0.45), ('Lfa', 0.55, -0.1, 6.0, WASH_HANDS[0] + 0.5),
    ('Rsh', 0.5, 0.1, 6.5, WASH_FEET[0] + 0.5), ('Lsh', 0.45, -0.1, 6.0, WASH_FEET[0] + 0.55),
    ('torso', 0.3, 0.2, 9.0, STEP_T[0] + 0.15), ('Rth', 0.5, 0.1, 7.0, STEP_T[2] + 0.15),
    ('Rua', 0.5, 0.1, 6.5, STEP_T[4] + 0.15), ('torso', 0.7, -0.25, 8.5, STEP_T[6] + 0.15),
    ('torso', 0.5, 0.0, 9.5, FOAM[1] - 0.3), ('torso', 0.85, 0.25, 7.5, FOAM[1] - 0.2),
]


def spot_xy(j, s):
    limb, u, perp = s[0], s[1], s[2]
    if limb == 'head':
        h = j['head']
        return h[0] + u * FIG.r, h[1] + perp * FIG.r
    a, b, w = SEGS[limb]
    p, q = j[a], j[b]
    d = q - p
    L = math.hypot(*d) + 1e-6
    n = np.array([-d[1], d[0]]) / L
    pt = p + d * u + n * perp * w
    return pt[0], pt[1]


def stains(c, j, t):
    for s in SPOTS:
        gone = s[4]
        a = 1 - seg(t, gone, gone + 0.25)
        if a <= 0:
            continue
        x, y = spot_xy(j, s)
        c.drawCircle(x, y, s[3] * (1 + 0.15 * math.sin(t * 5 + s[1] * 9) * (t < 3.0)),
                     skia.Paint(AntiAlias=True, Color=C((40, 40, 46), 0.96 * a)))


def drops(c, t, j_at):
    """each stain runs off as a few dark drops when it goes."""
    for s in SPOTS:
        gone = s[4]
        dt = t - gone
        if not (0 <= dt < 0.7):
            continue
        x, y = spot_xy(j_at(gone), s)
        for k in range(3):
            d2 = dt - 0.06 * k
            if d2 < 0:
                continue
            yy = y + 0.5 * 2400 * d2 * d2
            if yy > G:
                continue
            c.drawCircle(x + 5 * (k - 1), yy, 4.5 - k, skia.Paint(AntiAlias=True, Color=C((40, 40, 46), 0.9 * (1 - dt / 0.7))))


# ---------------------------------------------------------------- the man
STAND_P = dict(STAND, hd=10)


def stair_y(x):
    """floor height (px above G) at x."""
    if x < STAIR_X0:
        return 0.0
    k = min(NSTAIR, int((x - STAIR_X0) / STAIR_W) + 1)
    return k * STAIR_H


def climb_h(x):
    """smooth height as he steps up each stair edge."""
    h = 0.0
    for k in range(NSTAIR):
        edge = STAIR_X0 + k * STAIR_W
        h += STAIR_H * ease(clamp((x - edge + 30) / 46))
    return h


def man(t):
    # hook/promise: stands, head down
    if t < V1[0] + 0.1:
        p = dict(STAND, hd=26 + 2 * math.sin(t * 1.6), t=4)
        return FIG.solve(p, 540, 1, ground=G)
    # 1. wudu
    if t < WASH_HANDS[0]:
        pp, x = walk_to(FIG, t, V1[0] + 0.1, WASH_HANDS[0] - 0.05, 540, SINK_X - 140, stride=16, prev=dict(STAND, hd=26, t=4))
        return FIG.solve(pp, x, 1, ground=G)
    X = SINK_X - 140
    if t < V1[1]:
        j0 = FIG.solve(STAND_P, X, 1, ground=G)
        basin = (SINK_X - 40, G - 214)
        if t < WASH_HANDS[1]:
            u = seg(t, *WASH_HANDS)
            w = math.sin(math.pi * u)
            base = dict(STAND, t=22 * w, hd=24)
            rub = 7 * math.sin(u * 30)
            return with_arms(FIG, base, X, 1, G, {'R': (basin[0] + rub, basin[1]), 'L': (basin[0] - 10 - rub, basin[1] + 4)}, w)
        if t < WASH_FACE[1]:
            u = seg(t, *WASH_FACE)
            w = math.sin(math.pi * u)
            base = dict(STAND, t=18 * w, hd=26)
            jj = FIG.solve(base, X, 1, ground=G)
            face = (jj['head'][0] + 20, jj['head'][1] + 12)
            k = math.sin(math.pi * clamp((u - 0.15) / 0.7))
            tgt = (lerp(basin[0], face[0], k), lerp(basin[1], face[1], k))
            return with_arms(FIG, base, X, 1, G, {'R': tgt, 'L': (tgt[0] - 8, tgt[1] + 6)}, w)
        if t < WASH_FEET[1]:
            u = seg(t, *WASH_FEET)
            w = math.sin(math.pi * u)
            base = dict(STAND, t=62 * w, hd=30, Lth=-4, Rth=8 * w, Rkn=12 * w)
            jj = FIG.solve(base, X, 1, ground=G)
            shin = ((jj['Rk'][0] + jj['Rf'][0]) / 2 + 8, (jj['Rk'][1] + jj['Rf'][1]) / 2)
            return with_arms(FIG, base, X, 1, G, {'R': shin, 'L': (shin[0] - 10, shin[1] + 8)}, w)
        p = dict(STAND, hd=lerp(30, 4, ease(seg(t, WASH_FEET[1], WASH_FEET[1] + 0.4))), t=-2)
        return FIG.solve(p, X, 1, ground=G)
    # loop 1: walks back to the foot of the stairs
    if t < V2[0]:
        pp, x = walk_to(FIG, t, L1[0] + 0.1, V2[0], X, 330, stride=18, back=False)
        return FIG.solve(pp, x, -1, ground=G) if t < L1[0] + 0.25 else FIG.solve(pp, x, -1, ground=G)
    # 2. up the stairs: flat step (a stain drops), then a step up
    if t < V2[1] - 0.2:
        u = seg(t, V2[0] + 0.2, V2[0] + 0.2 + 0.42 * 8)
        x = lerp(330, TOP_X, u)
        ph = (t - V2[0] - 0.2) * rate(FIG, TOP_X - 330, 0.42 * 8, 20)
        pp = walk(ph, stride=20)
        pp['hd'] = 8
        return FIG.solve(pp, x, 1, ground=G - climb_h(x))
    # 3. sits at the top
    top = G - NSTAIR * STAIR_H
    u = ease(seg(t, V2[1] - 0.2, V3[0] + 0.2))
    p = mix(STAND_P, dict(JULUS, hd=10), u)
    if t > V3[0] + 0.2:
        p['hd'] = 10 + 4 * math.sin(t * 9) * seg(t, V3[0] + 0.3, FOAM[1]) * (1 - seg(t, FOAM[1], FOAM[1] + 0.1))
        p['t'] += 1.0 * math.sin(t * 2)
    return FIG.solve(p, TOP_X, 1, ground=top)


# ---------------------------------------------------------------- scenery
def sink(c, t):
    a = seg(t, V1[0], V1[0] + 0.3) * (1 - seg(t, L1[0], L1[0] + 0.35))
    if a <= 0:
        return
    col = (104, 104, 112)
    rect(c, SINK_X - 16, G - 190, 32, 190, (84, 86, 94), a=a, r=6)
    p = skia.Path()
    p.moveTo(SINK_X - 84, G - 224)
    p.lineTo(SINK_X + 84, G - 224)
    p.quadTo(SINK_X + 80, G - 180, SINK_X, G - 178)
    p.quadTo(SINK_X - 80, G - 180, SINK_X - 84, G - 224)
    p.close()
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=C(col, a)))
    rect(c, SINK_X - 88, G - 231, 176, 10, (120, 122, 130), a=a, r=4)
    line(c, SINK_X + 62, G - 231, SINK_X + 62, G - 278, (120, 122, 130), 9, a=a)
    line(c, SINK_X + 62, G - 276, SINK_X + 30, G - 276, (120, 122, 130), 9, a=a)
    run = seg(t, WASH_HANDS[0] - 0.1, WASH_HANDS[0]) * (1 - seg(t, WASH_FEET[1], WASH_FEET[1] + 0.1))
    if run > 0:
        wob = 1.4 * math.sin(t * 40)
        line(c, SINK_X + 30, G - 268, SINK_X + 30 + wob, G - 224, (190, 200, 212), 4, a=0.75 * run * a)


def stairs(c, t):
    a = seg(t, L1[0] + 0.2, L1[0] + 0.6)
    if a <= 0:
        return
    for k in range(NSTAIR):
        x0 = STAIR_X0 + k * STAIR_W
        h = (k + 1) * STAIR_H
        rise = ease(seg(t, L1[0] + 0.2 + 0.1 * k, L1[0] + 0.55 + 0.1 * k))
        rect(c, x0, G - h * rise, 1050 - x0 if k == NSTAIR - 1 else STAIR_W, h * rise, (88, 90, 98) if k % 2 else (96, 98, 106), a=a)
        line(c, x0, G - h * rise, x0 + (1050 - x0 if k == NSTAIR - 1 else STAIR_W), G - h * rise, (130, 132, 140), 2, a=a, cap=False)
    # the masjid at the top
    top = G - NSTAIR * STAIR_H
    ma = seg(t, L1[0] + 0.5, L1[0] + 0.9)
    pen = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=4, Color=C((120, 122, 130), ma),
                     StrokeJoin=skia.Paint.kRound_Join)
    mx = 990
    p = skia.Path()
    p.moveTo(mx - 70, top)
    p.lineTo(mx - 70, top - 150)
    p.lineTo(mx + 70, top - 150)
    p.lineTo(mx + 70, top)
    c.drawPath(p, pen)
    c.drawArc(skia.Rect(mx - 52, top - 230, mx + 52, top - 126), 180, 180, False, pen)
    p2 = skia.Path()
    p2.moveTo(mx - 24, top)
    p2.lineTo(mx - 24, top - 60)
    p2.quadTo(mx, top - 96, mx + 24, top - 60)
    p2.lineTo(mx + 24, top)
    c.drawPath(p2, pen)
    # each step up: a small ring of light under his feet
    for k in range(1, 8, 2):
        u = seg(t, STEP_T[k] + 0.12, STEP_T[k] + 0.5)
        if 0 < u < 1:
            x = lerp(330, TOP_X, seg(STEP_T[k] + 0.12, V2[0] + 0.2, V2[0] + 0.2 + 0.42 * 8))
            yy = G - stair_y(x)
            c.drawOval(skia.Rect(x - 50 * u - 20, yy - 6, x + 50 * u + 20, yy + 6),
                       skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3, Color=C(WHITE, 0.6 * (1 - u))))


def foam_sea(c, t):
    a = seg(t, L2[0], L2[0] + 0.6) * (1 - seg(t, FOAM[1] + 0.3, FOAM[1] + 0.9))
    if a <= 0:
        return
    top = G - 70
    c.drawRect(skia.Rect(0, top, STAIR_X0 + 2, G), skia.Paint(Color=C((30, 38, 50), 0.85 * a)))
    cleared = seg(t, FOAM[0], FOAM[1])
    rng = np.random.default_rng(70)
    for k in range(70):
        x = rng.uniform(10, STAIR_X0 - 10)
        y = top + rng.uniform(-6, 30)
        r = rng.uniform(6, 15)
        order = x / STAIR_X0
        gone = seg(cleared, order * 0.9, order * 0.9 + 0.1)
        if gone >= 1:
            continue
        bob = 3 * math.sin(t * 3 + k)
        c.drawCircle(x, y + bob, r * (1 - 0.5 * gone), skia.Paint(AntiAlias=True, Color=C((230, 232, 236), 0.85 * a * (1 - gone))))


def counter(c, t, j):
    if t < V3[0] + 0.3 or t > CTA[1]:
        return
    n = int(1 + 99 * ease_in(seg(t, FOAM[0], FOAM[1])) ** 0.8)
    a = seg(t, V3[0] + 0.3, V3[0] + 0.5)
    hx, hy = j['head']
    text(c, f'{n}', hx - 70, hy - 52, 44, WHITE, a=a, spacing=0.05)


def world(c, t):
    stage(c)
    stairs(c, t)
    foam_sea(c, t)
    sink(c, t)
    j = man(t)
    glow = seg(t, FOAM[1], FOAM[1] + 0.5)
    if glow > 0:
        light_pool(c, j['sh'][0], j['sh'][1], 200, 200, WARM, a=0.12 * glow)
    FIG.draw(c, j)
    stains(c, j, t)
    drops(c, t, man)
    counter(c, t, j)


def frame(c, t, i):
    background(c)
    pic = record(lambda rc: world(rc, t))
    finish(c, pic, i)
    c.drawPicture(pic)
    hook(c, t, ['YOUR SINS CAN FALL OFF YOU', "WHILE YOU'RE DOING THIS."])
    promise(c, t, '3 THINGS. THE LAST ONE TAKES 2 MINUTES.')
    value(c, t, 1, 'WUDU', ['EVERY SIN LEAVES WITH THE WATER.'], V1)
    loop(c, t, "THE NEXT ONE, YOU'RE PROBABLY SKIPPING.", L1)
    value(c, t, 2, 'WALKING TO THE MASJID', ['ONE STEP ERASES A SIN.', 'THE NEXT ONE RAISES YOU.'], V2)
    loop(c, t, 'THE LAST ONE, YOU CAN DO BEFORE THIS ENDS.', L2)
    value(c, t, 3, 'SUBHANALLAHI WA BIHAMDIHI', ['100 TIMES A DAY. EVEN IF YOUR SINS',
                                                  'WERE LIKE THE FOAM OF THE SEA.'], V3)
    cta(c, t, 'SAY IT 100 TIMES TODAY.', 'SEND THIS TO SOMEONE WHO NEEDS A FRESH START.',
        'SAHIH MUSLIM 244 · SAHIH MUSLIM 666 · SAHIH AL-BUKHARI 6405')
    vignette(c, 0.5)
    grain(c, i)


EVENTS = dict(dur=DUR, beats=T, wash=[WASH_HANDS, WASH_FACE, WASH_FEET], steps=STEP_T, foam=FOAM,
              gone=[s[4] for s in SPOTS])

if __name__ == '__main__':
    run(frame, 'v70', N, DUR, EVENTS)
