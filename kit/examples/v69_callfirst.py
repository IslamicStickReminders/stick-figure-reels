"""#69 Call First — WANTS HIM TO CALL FIRST vs CALLS FIRST (Sahih al-Bukhari 5991).

Two brothers who stopped speaking, each sitting outside his own house, a gap in the ground between them.
Eid, year 1, year 3, year 7.
Bottom: calls every Eid. The phone rings across the gap; his brother turns it face down. Each call lays a plank
across the gap anyway. In year 7 his brother answers, lays the last plank from his side, and walks across.
Top: every Eid he picks up the phone, his thumb hovers, and he puts it down. Across the gap, his brother does
exactly the same thing, every year. The gap gets wider.
"""
from kit2 import *

FIG = Figure(226)
LANES = dict(A=930, B=1390)
LX, RX = 196, 884                 # the brothers
GAP0, GAP1 = 418, 662             # the gap in the ground
YEARS = [0.5, 2.5, 4.5]
YLAB = [1, 3, 7]
SEAT_Y = 44
E1 = 7.0
E2 = E1 + 1.05
DUR = round(E2 + 0.55 + 1.05, 2)
N = int(DUR * FPS)

SIT_P = P(t=10, hd=18, Lth=94, Lkn=104, Rth=98, Rkn=108, Lua=30, Lel=60, Rua=36, Rel=64)
SIT_DOWN = P(t=18, hd=34, Lth=94, Lkn=104, Rth=98, Rkn=108, Lua=40, Lel=70, Rua=46, Rel=74)
HUG = P(t=4, hd=10, Lua=80, Lel=40, Rua=86, Rel=34)


def yr(t):
    k = -1
    for i, y in enumerate(YEARS):
        if t >= y - 0.02:
            k = i
    return k


def seated(p, x, f, G):
    j = FIG.solve(p, x, f, ground=G)
    hy = G - SEAT_Y - FIG.tw / 2 + 6
    if j['hip'][1] > hy:
        j = FIG.joints(p, x, hy, f)
    return j


def phone_up(p, x, f, G, v, ear=False):
    """bring the phone up: in front of his face, or to his ear."""
    j0 = seated(p, x, f, G)
    hx, hy = j0['head']
    tgt = (hx + f * (8 if ear else 34), hy + (6 if ear else 30))
    return with_arms(FIG, p, x, f, G, {'R': tgt}, v)


def drift(t):
    """top lane: the gap widens every year (brother's side slides away)."""
    d = 0.0
    for y in YEARS:
        d += 38 * ease(seg(t, y + 1.05, y + 1.55))
    return d


# ---------------------------------------------------------------- top: both wait
def hover(t, offset):
    k = yr(t)
    if k < 0:
        return 0.0, 0.0
    y = YEARS[k] + offset
    v = ease(seg(t, y + 0.15, y + 0.4)) * (1 - ease(seg(t, y + 0.95, y + 1.25)))
    thumb = math.sin(t * 30) * seg(t, y + 0.45, y + 0.95) * (1 - seg(t, y + 0.9, y + 0.95))
    return v, thumb


def brother_a(t, side):
    G = LANES['A']
    x = LX if side == 'L' else RX + drift(t)
    f = 1 if side == 'L' else -1
    v, thumb = hover(t, 0.0 if side == 'L' else 0.22)
    p = dict(SIT_P, hd=SIT_P['hd'] + 1.5 * math.sin(t * 1.7 + (0 if side == 'L' else 1)))
    if yr(t) == 2 and t > YEARS[2] + 1.3:
        p = mix(p, SIT_DOWN, ease(seg(t, YEARS[2] + 1.3, YEARS[2] + 1.8)))
    if v > 0:
        q = dict(p, hd=lerp(p['hd'], 30, v))
        j = phone_up(q, x, f, G, v)
        return j, (v, thumb)
    return seated(p, x, f, G), None


# ---------------------------------------------------------------- bottom: one calls
CROSS = (YEARS[2] + 1.15, YEARS[2] + 1.95)
MEET_X = (GAP0 + GAP1) / 2


def brother_b_left(t):
    G = LANES['B']
    k = yr(t)
    p = dict(SIT_P, hd=SIT_P['hd'] + 1.5 * math.sin(t * 1.7))
    if k < 0:
        return seated(p, LX, 1, G), None
    y = YEARS[k]
    if k == 2 and t >= CROSS[0]:
        # gets up and goes to meet him
        if t < CROSS[0] + 0.25:
            u = ease(seg(t, CROSS[0], CROSS[0] + 0.25))
            j0 = seated(SIT_P, LX, 1, G)
            j1 = FIG.solve(dict(STAND, hd=6), LX, 1, ground=G)
            return FIG.joints(mix(SIT_P, dict(STAND, hd=6), u), LX, lerp(j0['hip'][1], j1['hip'][1], u), 1), None
        if t < CROSS[1]:
            pp, x = walk_to(FIG, t, CROSS[0] + 0.25, CROSS[1], LX, MEET_X - 46, stride=20, end=HUG)
            return FIG.solve(pp, x, 1, ground=G), None
        return FIG.solve(dict(HUG, t=4 + 1.5 * math.sin(t * 2)), MEET_X - 46, 1, ground=G), None
    v = ease(seg(t, y + 0.1, y + 0.3)) * (1 - ease(seg(t, y + 1.25, y + 1.5)))
    if v > 0:
        return phone_up(p, LX, 1, G, v, ear=True), ('call', v)
    return seated(p, LX, 1, G), None


def brother_b_right(t):
    G = LANES['B']
    k = yr(t)
    p = dict(SIT_P, hd=SIT_P['hd'] + 1.5 * math.sin(t * 1.7 + 1))
    if k < 0:
        return seated(p, RX, -1, G), None
    y = YEARS[k]
    if k < 2:
        # looks at it ringing... turns it face down
        v = ease(seg(t, y + 0.5, y + 0.75)) * (1 - ease(seg(t, y + 1.0, y + 1.25)))
        look = [0.6, 1.0][k]
        if v > 0:
            q = dict(p, hd=lerp(p['hd'], 30, v))
            return phone_up(q, RX, -1, G, v * look), ('look', v)
        return seated(p, RX, -1, G), None
    # year 7: he answers
    if t < CROSS[0] - 0.1:
        v = ease(seg(t, y + 0.5, y + 0.8))
        return phone_up(p, RX, -1, G, v, ear=v > 0.5), ('answer', v)
    if t < CROSS[0] + 0.15:
        u = ease(seg(t, CROSS[0] - 0.1, CROSS[0] + 0.15))
        j0 = seated(SIT_P, RX, -1, G)
        j1 = FIG.solve(dict(STAND, hd=6), RX, -1, ground=G)
        return FIG.joints(mix(SIT_P, dict(STAND, hd=6), u), RX, lerp(j0['hip'][1], j1['hip'][1], u), -1), None
    if t < CROSS[1]:
        pp, x = walk_to(FIG, t, CROSS[0] + 0.15, CROSS[1], RX, MEET_X + 46, stride=20, end=HUG)
        return FIG.solve(pp, x, -1, ground=G), None
    return FIG.solve(dict(HUG, t=4 + 1.5 * math.sin(t * 2 + 1)), MEET_X + 46, -1, ground=G), None


def planks(c, G, t):
    n_left = [(YEARS[k] + 1.0) for k in range(3)]
    w = (GAP1 - GAP0) / 4
    slots = [(GAP0, n_left[0]), (GAP0 + w, n_left[1]), (GAP0 + 2 * w, n_left[2]), (GAP0 + 3 * w, YEARS[2] + 0.95)]
    for k, (x0, t0) in enumerate(slots):
        u = ease(seg(t, t0, t0 + 0.35))
        if u <= 0:
            continue
        fromx = GAP0 - 60 if k < 3 else GAP1 + 60
        x = lerp(fromx, x0, u)
        y = G - 7 - 90 * math.sin(math.pi * u)
        rect(c, x + 1, y - 6, w - 2, 15, (186, 178, 166), a=u, r=3)


def gap(c, G, t, lane):
    d = drift(t) if lane == 'A' else 0.0
    depth = 72
    # the drop between them
    sh = skia.GradientShader.MakeLinear(points=[(0, G), (0, G + depth)], colors=[C((8, 8, 10), 0.95), C((8, 8, 10), 0.0)])
    c.drawRect(skia.Rect(GAP0, G, GAP1 + d, G + depth), skia.Paint(Shader=sh))
    for x0, x1, edge, sgn in ((0, GAP0, GAP0, 1), (GAP1 + d, W, GAP1 + d, -1)):
        p = skia.Path()
        p.moveTo(x0, G)
        p.lineTo(x1, G)
        p.lineTo(edge - sgn * 0, G)
        p.lineTo(edge - sgn * 10, G + 22)
        p.lineTo(edge + sgn * 4, G + 40)
        p.lineTo(edge - sgn * 8, G + depth)
        p.lineTo(x0 if sgn > 0 else x1, G + depth)
        p.lineTo(x0 if sgn > 0 else x1, G)
        p.close()
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=C((40, 42, 48))))
        line(c, x0, G, x1, G, (96, 98, 106), 3, cap=False)


def house(c, x, G, f):
    pen = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3.5, Color=C((96, 98, 106)),
                     StrokeJoin=skia.Paint.kRound_Join)
    x0 = x - (150 if f > 0 else -150)
    a, b = min(x0, x0 + 150 * (1 if f > 0 else -1) * 0 + (120 if f > 0 else -120)), 0
    hx0 = x - 175 if f > 0 else x + 55
    hx1 = hx0 + 120
    p = skia.Path()
    p.moveTo(hx0, G)
    p.lineTo(hx0, G - 170)
    p.lineTo((hx0 + hx1) / 2, G - 230)
    p.lineTo(hx1, G - 170)
    p.lineTo(hx1, G)
    c.drawPath(p, pen)
    rect(c, (hx0 + hx1) / 2 - 18, G - 70, 36, 70, (84, 86, 94), r=2)
    # step he sits on
    rect(c, x - 40, G - SEAT_Y, 80, SEAT_Y, (96, 98, 106), r=3)


def phone_draw(c, j, f, glow=0.0, face_down=False):
    hx, hy = j['Rh']
    c.save()
    c.translate(hx, hy - 4)
    c.rotate(-10 * f)
    c.drawRoundRect(skia.Rect(-9, -15, 9, 15), 4, 4, skia.Paint(AntiAlias=True, Color=C((34, 36, 42))))
    c.drawRoundRect(skia.Rect(-9, -15, 9, 15), 4, 4, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                                              StrokeWidth=2.5, Color=C(LABEL)))
    if glow > 0:
        c.drawRoundRect(skia.Rect(-6, -11, 6, 11), 2, 2, skia.Paint(AntiAlias=True, Color=C((235, 235, 230), glow)))
    c.restore()


def rings(c, j, t, t0, a=1.0):
    hx, hy = j['Rh']
    for k in range(3):
        u = ((t - t0) * 2.2 + k / 3) % 1.0
        if t < t0:
            return
        r = 14 + 34 * u
        c.drawArc(skia.Rect(hx - r, hy - 4 - r, hx + r, hy - 4 + r), -60, 120, False,
                  skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.5, Color=C(LABEL, a * (1 - u))))
        c.drawArc(skia.Rect(hx - r, hy - 4 - r, hx + r, hy - 4 + r), 120, 120, False,
                  skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.5, Color=C(LABEL, a * (1 - u))))


def world(c, t):
    k = yr(t)
    for lane in 'AB':
        G = LANES[lane]
        d = drift(t) if lane == 'A' else 0.0
        gap(c, G, t, lane)
        house(c, LX, G, 1)
        house(c, RX + d, G, -1)
        if lane == 'A':
            for side in 'LR':
                j, info = brother_a(t, side)
                FIG.draw(c, j)
                if info:
                    v, thumb = info
                    phone_draw(c, j, 1 if side == 'L' else -1, glow=0.8 * v)
        else:
            planks(c, G, t)
            jl, il = brother_b_left(t)
            jr, ir = brother_b_right(t)
            FIG.draw(c, jl)
            FIG.draw(c, jr)
            if il:
                phone_draw(c, jl, 1, glow=0.8 * il[1])
            if ir:
                phone_draw(c, jr, -1, glow=0.9 * ir[1])
            # his brother's phone rings every year
            if k >= 0:
                y = YEARS[k]
                ring_on = seg(t, y + 0.3, y + 0.4) * (1 - seg(t, y + (0.85 if k < 2 else 0.75), y + (0.95 if k < 2 else 0.8)))
                if ring_on > 0:
                    rings(c, jr, t, y + 0.3, ring_on)


def frame(c, t, i):
    background(c)
    pic = record(lambda rc: world(rc, t))
    for G in LANES.values():
        c.save()
        c.clipRect(skia.Rect(0, G, W, G + 120))
        reflection(c, pic, G, strength=0.08, fade=60, blur=1.5)
        c.restore()
    c.drawPicture(pic)
    beats(c, t, [(0.0, 2.45, "YOU HAVEN'T SPOKEN IN YEARS."), (2.45, E1 - 0.1, 'HE CUT YOU OFF FIRST.')], 486,
          size=32, spacing=0.12)
    k = max(0, yr(t))
    ya = seg(t, 0.35, 0.55) * (1 - seg(t, E1 - 0.35, E1))
    pop = 1 + 0.12 * math.sin(math.pi * seg(t, YEARS[k] - 0.05, YEARS[k] + 0.2))
    text(c, f'EID · YEAR {YLAB[k]}', 540, 572, 36 * pop, WHITE, a=0.92 * ya, spacing=0.18)
    text(c, 'WANTS HIM TO CALL FIRST', 540, LANES['A'] + 66, 24, LABEL, spacing=0.15)
    text(c, 'CALLS FIRST', 540, LANES['B'] + 66, 24, LABEL, spacing=0.15)
    text(c, 'HE WANTED HIS BROTHER TO CALL FIRST.', 540, 262, 28, LABEL, a=seg(t, E1, E1 + 0.35), spacing=0.08)
    text(c, 'SO DID HIS BROTHER.', 540, 344, 48, WHITE, a=seg(t, E1 + 0.3, E1 + 0.65), spacing=0.13)
    for kk, ln in enumerate(['“AL-WASIL IS NOT THE ONE WHO RECOMPENSES THE GOOD DONE TO HIM BY HIS RELATIVES,',
                             'BUT AL-WASIL IS THE ONE WHO KEEPS GOOD RELATIONS WITH THOSE RELATIVES',
                             'WHO HAD SEVERED THE BOND OF KINSHIP WITH HIM.”']):
        text(c, ln, 540, 424 + 30 * kk, 17, LABEL, a=seg(t, E2 + 0.08 * kk, E2 + 0.08 * kk + 0.35), spacing=0.03)
    text(c, 'SAHIH AL-BUKHARI 5991', 540, 532, 20, DIM, a=seg(t, E2 + 0.35, E2 + 0.7), tf=TF_REG)
    vignette(c, 0.5)
    grain(c, i)


EVENTS = dict(dur=DUR, e1=E1, e2=E2, years=YEARS, cross=CROSS)

if __name__ == '__main__':
    run(frame, 'v69', N, DUR, EVENTS)
