"""#67 Twenty-One — ALREADY TOLD HIM vs TELLS HIM AGAIN (Qur'an 17:23, recited: "fa la taqul lahuma uffin wa la tanharhuma").

Two sons at their desks; behind each, their old father in his armchair. Five times he asks the same question.
Bottom: turns and answers every time. The fourth time he gets up, comes over and kneels beside him.
Top: answers, answers shorter, answers over his shoulder. The fourth time he starts to turn... and an UFF comes
out instead. The fifth time he holds up a hand without looking, and his father's question shrinks away.
Then, faintly, in both rooms: a young father kneeling to a small boy who asks "?" again and again, 21 times,
and is answered every time.
"""
from kit2 import *

FIG = Figure(236)
KID = Figure(122)
LANES = dict(A=930, B=1390)
FX = 250                          # father's chair
SX = 704                          # son's chair
DESK0, DESK1 = 770, 930

ASKS = [0.5, 1.5, 2.45, 3.3, 4.05]
ANS_LAG = 0.38
MEM = (4.75, 6.55)                # the memory
KID_ASKS = 21
E1 = 6.8
E2 = E1 + 1.05
DUR = 9.45
N = int(DUR * FPS)

SEAT_Y = 66
OLD_SIT = P(t=16, hd=22, Lth=98, Lkn=106, Rth=102, Rkn=110, Lua=30, Lel=50, Rua=36, Rel=56)
OLD_DOWN = P(t=26, hd=44, Lth=98, Lkn=106, Rth=102, Rkn=110, Lua=34, Lel=64, Rua=40, Rel=70)
OLD_SMILE = P(t=10, hd=4, Lth=98, Lkn=106, Rth=102, Rkn=110, Lua=30, Lel=50, Rua=36, Rel=56)
WORK = P(t=12, hd=20, Lth=96, Lkn=100, Rth=100, Rkn=104, Lua=44, Lel=70, Rua=50, Rel=66)
TURNED = P(t=-2, hd=4, Lth=96, Lkn=100, Rth=100, Rkn=104, Lua=20, Lel=40, Rua=26, Rel=40)
STOP_HAND = P(t=12, hd=20, Lth=96, Lkn=100, Rth=100, Rkn=104, Lua=44, Lel=70, Rua=-90, Rel=-20)
KNEEL = dict(JULUS, hd=10)


def seated(fig, p, x, f, G, seat=SEAT_Y):
    j = fig.solve(p, x, f, ground=G)
    hy = G - seat - fig.tw / 2 + 6
    if j['hip'][1] > hy:
        j = fig.joints(p, x, hy, f)
    return j


def ask_k(t):
    k = -1
    for i, a in enumerate(ASKS):
        if t >= a - 0.02:
            k = i
    return k


# ---------------------------------------------------------------- the father
def father(t, lane):
    G = LANES[lane]
    p = dict(OLD_SIT, hd=OLD_SIT['hd'] + 2 * math.sin(t * 1.6))
    k = ask_k(t)
    if k >= 0:
        u = seg(t, ASKS[k], ASKS[k] + 0.3)
        p['hd'] -= 10 * math.sin(math.pi * u)      # lifts his head to ask
    if lane == 'A' and t > ASKS[4] + 0.45:
        p = mix(p, OLD_DOWN, ease(seg(t, ASKS[4] + 0.45, ASKS[4] + 1.0)))
    if lane == 'B' and t > ASKS[3] + 0.9:
        p = mix(p, OLD_SMILE, ease(seg(t, ASKS[3] + 0.9, ASKS[3] + 1.4)))
    if t > MEM[1] - 0.3:
        p['hd'] += 0 if lane == 'A' else 0
    return seated(FIG, p, FX, 1, G)


def father_bubble(c, j, t, lane):
    k = ask_k(t)
    if k < 0:
        return
    a0 = ASKS[k]
    dur = 0.75
    u = seg(t, a0, a0 + dur)
    if u <= 0 or u >= 1:
        return
    a = ease(clamp(u / 0.15)) * (1 - ease(clamp((u - 0.8) / 0.2)))
    s = 1.0
    if lane == 'A' and k == 4:
        # the fifth time it shrinks away under his raised hand
        s = 1 - 0.7 * ease(clamp((u - 0.35) / 0.35))
        a *= 1 - clamp((u - 0.55) / 0.2)
    hx, hy = j['head']
    qbubble(c, hx + 58, hy - 70, a, s)


def qbubble(c, x, y, a, s=1.0, mark='?', ink=None, fill=WHITE):
    if a <= 0 or s <= 0.05:
        return
    w, h = 58 * s, 50 * s
    c.drawRoundRect(skia.Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2), 18 * s, 18 * s,
                    skia.Paint(AntiAlias=True, Color=C(fill, 0.94 * a)))
    tail = skia.Path()
    tail.moveTo(x - w * 0.28, y + h / 2 - 2)
    tail.lineTo(x - w * 0.46, y + h / 2 + 13 * s)
    tail.lineTo(x - w * 0.06, y + h / 2 - 2)
    tail.close()
    c.drawPath(tail, skia.Paint(AntiAlias=True, Color=C(fill, 0.94 * a)))
    text(c, mark, x + 1, y + 11 * s, 32 * s, ink or BG_IN, a=a, spacing=0.0)


def dots_bubble(c, x, y, a, s=1.0, fill=WHITE, flip=False):
    if a <= 0:
        return
    w, h = 62 * s, 38 * s
    c.drawRoundRect(skia.Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2), 16 * s, 16 * s,
                    skia.Paint(AntiAlias=True, Color=C(fill, 0.92 * a)))
    tail = skia.Path()
    sx = 1 if not flip else -1
    tail.moveTo(x + sx * w * 0.25, y + h / 2 - 2)
    tail.lineTo(x + sx * w * 0.42, y + h / 2 + 11 * s)
    tail.lineTo(x + sx * w * 0.05, y + h / 2 - 2)
    tail.close()
    c.drawPath(tail, skia.Paint(AntiAlias=True, Color=C(fill, 0.92 * a)))
    for k in (-1, 0, 1):
        c.drawCircle(x + k * 13 * s, y, 3.4 * s, skia.Paint(AntiAlias=True, Color=C(BG_IN, a)))


# ---------------------------------------------------------------- B: tells him again
B_WALK = (ASKS[3] + 0.05, ASKS[3] + 0.6)
KX = FX + 152                      # where he kneels beside his father


def son_b(t):
    G = LANES['B']
    k = ask_k(t)
    if t < B_WALK[0]:
        p = dict(WORK)
        p['Rel'] += 10 * math.sin(t * 11)
        f = 1
        if k >= 0:
            u = seg(t, ASKS[k] + 0.12, ASKS[k] + ANS_LAG) * (1 - seg(t, ASKS[k] + 0.85, ASKS[k] + 1.0))
            if u > 0.5:
                f = -1
            p = mix(WORK, TURNED, math.sin(math.pi * min(1.0, u)) if u < 0.5 else 1.0) if u < 1 else WORK
            if u >= 0.5:
                p = TURNED
            if u <= 0:
                p = dict(WORK)
        return seated(FIG, p, SX, f, G)
    if t < B_WALK[1]:
        u = seg(t, *B_WALK)
        if u < 0.25:
            j0 = seated(FIG, TURNED, SX, -1, G)
            j1 = FIG.solve(dict(STAND, hd=8), SX, -1, ground=G)
            v = ease(u / 0.25)
            return FIG.joints(mix(TURNED, dict(STAND, hd=8), v), SX, lerp(j0['hip'][1], j1['hip'][1], v), -1)
        pp, x = walk_to(FIG, t, B_WALK[0] + 0.25 * (B_WALK[1] - B_WALK[0]), B_WALK[1], SX, KX, stride=20,
                        end=dict(STAND, hd=10))
        return FIG.solve(pp, x, -1, ground=G)
    u = ease(seg(t, B_WALK[1], B_WALK[1] + 0.3))
    p = mix(dict(STAND, hd=10), KNEEL, u)
    j0 = FIG.solve(p, KX, -1, ground=G)
    if u >= 1:
        jf = father(t, 'B')
        knee = (jf['Rk'][0] + 6, jf['Rk'][1] - 6)
        return with_arms(FIG, dict(KNEEL, hd=8 + 2 * math.sin(t * 1.5)), KX, -1, G, {'R': knee}, 1.0)
    return j0


def son_b_bubble(c, j, t):
    k = ask_k(t)
    if k < 0:
        return
    a0 = ASKS[k] + ANS_LAG + 0.08
    u = seg(t, a0, a0 + 0.62)
    if 0 < u < 1:
        a = ease(clamp(u / 0.15)) * (1 - ease(clamp((u - 0.8) / 0.2)))
        hx, hy = j['head']
        dots_bubble(c, hx - 46, hy - 62, a, flip=True)


# ---------------------------------------------------------------- A: already told him
def son_a(t):
    G = LANES['A']
    k = ask_k(t)
    p = dict(WORK)
    p['Rel'] += 10 * math.sin(t * 11)
    f = 1
    if k < 0:
        return seated(FIG, p, SX, f, G), None
    a0 = ASKS[k]
    if k in (0, 1, 2):
        # turns a little less every time
        amt = [1.0, 0.55, 0.25][k]
        u = seg(t, a0 + 0.12, a0 + ANS_LAG) * (1 - seg(t, a0 + 0.8, a0 + 0.95))
        if k == 0 and u > 0.5:
            return seated(FIG, TURNED, SX, -1, G), 'dots'
        q = mix(WORK, dict(WORK, hd=-6, t=2), u * amt)
        return seated(FIG, q, SX, 1, G), ('dots' if u > 0.4 else None)
    if k == 3:
        # starts to turn... then UFF
        u = seg(t, a0 + 0.1, a0 + 0.7)
        q = mix(WORK, dict(WORK, hd=-4, t=0), math.sin(math.pi * u) * 0.6)
        return seated(FIG, q, SX, 1, G), ('uff' if u > 0.45 else None)
    u = seg(t, a0 + 0.12, a0 + 0.4) * (1 - seg(t, a0 + 1.0, a0 + 1.3))
    q = mix(WORK, STOP_HAND, ease(u))
    return seated(FIG, q, SX, 1, G), None


def son_a_bubble(c, j, t, what):
    k = ask_k(t)
    if k < 0 or what is None:
        return
    hx, hy = j['head']
    if what == 'dots':
        a0 = ASKS[k] + ANS_LAG + 0.05
        u = seg(t, a0, a0 + 0.5)
        s = [1.0, 0.8, 0.62][k]
        a = ease(clamp(u / 0.15)) * (1 - ease(clamp((u - 0.75) / 0.25)))
        fill = WHITE if k == 0 else (170, 172, 178)
        dots_bubble(c, hx - 46 * s, hy - 60, a, s=s, fill=fill, flip=True)
    elif what == 'uff':
        a0 = ASKS[3] + 0.38
        u = seg(t, a0, a0 + 0.75)
        a = ease(clamp(u / 0.12)) * (1 - ease(clamp((u - 0.75) / 0.25)))
        pop = 1 + 0.25 * math.sin(math.pi * clamp(u / 0.3))
        qbubble(c, hx - 52, hy - 66, a, s=1.15 * pop, mark='UFF', ink=WHITE, fill=RED)


# ---------------------------------------------------------------- the memory
def memory(c, G, t):
    a = ease(seg(t, MEM[0], MEM[0] + 0.4)) * (1 - 0.0 * seg(t, MEM[1], MEM[1] + 0.4))
    if a <= 0:
        return
    a *= 0.42
    cx = 520
    # a young father kneeling to a small boy
    yf = FIG.solve(dict(KNEEL, hd=6, t=2), cx + 40, -1, ground=G)
    kid_p = dict(STAND, hd=-12 + 4 * math.sin(t * 6))
    kid = KID.solve(kid_p, cx - 52, 1, ground=G)
    light_pool(c, cx, G - 80, 240, 130, WARM, a=0.06 * a / 0.42)
    FIG.draw(c, yf, a=a)
    KID.draw(c, kid, a=a)
    # the boy asks, again and again; the bubbles come faster and faster
    n = count_kid(t)
    for i in range(max(0, n - 3), n):
        ti = kid_ask_time(i)
        u = seg(t, ti, ti + 0.32)
        if 0 < u < 1:
            hx, hy = kid['head']
            qbubble(c, hx + 30 + 6 * math.sin(i * 2.1), hy - 40 - 30 * u, a * 2.0 * (1 - u), s=0.7)
            fx, fy = yf['head']
            dots_bubble(c, fx - 6, fy - 58, a * 1.8 * math.sin(math.pi * u), s=0.7, flip=True)


def kid_ask_time(i):
    span = MEM[1] - 0.25 - (MEM[0] + 0.35)
    u = i / (KID_ASKS - 1)
    return MEM[0] + 0.35 + span * (u ** 1.5)


def count_kid(t):
    return sum(1 for i in range(KID_ASKS) if t >= kid_ask_time(i))


# ---------------------------------------------------------------- room
def room(c, G):
    # armchair
    rect(c, FX - 52, G - 150, 22, 150, (84, 86, 94), r=8)
    rect(c, FX - 44, G - SEAT_Y, 92, 20, (104, 104, 112), r=8)
    rect(c, FX - 44, G - SEAT_Y + 18, 92, SEAT_Y - 18, (84, 86, 94), r=4)
    # cane
    line(c, FX + 62, G, FX + 50, G - 120, (150, 148, 146), 5)
    line(c, FX + 50, G - 120, FX + 62, G - 128, (150, 148, 146), 5)
    # son's desk, chair and laptop
    rect(c, DESK0, G - 92, DESK1 - DESK0, 10, (110, 112, 120), r=3)
    rect(c, DESK0 + 10, G - 84, 8, 84, (92, 94, 100))
    rect(c, DESK1 - 18, G - 84, 8, 84, (92, 94, 100))
    rect(c, DESK0 + 40, G - 98, 56, 6, (150, 152, 160), r=2)
    c.save()
    c.translate(DESK0 + 96, G - 98)
    c.rotate(-72)
    rect(c, 0, -3, 48, 5, (150, 152, 160), r=2)
    c.restore()
    rect(c, SX - 26, G - SEAT_Y, 50, 8, (92, 94, 100), r=2)
    rect(c, SX - 30, G - SEAT_Y - 70, 8, 78, (92, 94, 100), r=2)
    rect(c, SX - 4, G - SEAT_Y, 6, SEAT_Y, (80, 82, 88))


def world(c, t):
    for lane in 'AB':
        G = LANES[lane]
        line(c, 30, G, 1050, G, (70, 72, 78), 2, cap=False)
        room(c, G)
        memory(c, G, t)
        jf = father(t, lane)
        FIG.draw(c, jf)
        if lane == 'A':
            js, what = son_a(t)
            FIG.draw(c, js)
            son_a_bubble(c, js, t, what)
        else:
            js = son_b(t)
            FIG.draw(c, js)
            son_b_bubble(c, js, t)
        father_bubble(c, jf, t, lane)


def frame(c, t, i):
    background(c)
    pic = record(lambda rc: world(rc, t))
    for G in LANES.values():
        c.save()
        c.clipRect(skia.Rect(0, G, W, G + 120))
        reflection(c, pic, G, strength=0.14, fade=110, blur=1.5)
        c.restore()
    c.drawPicture(pic)
    beats(c, t, [(0.0, 2.4, 'YOUR FATHER IS GETTING OLD.'), (2.4, MEM[0], 'HE ASKS THE SAME THING AGAIN.'),
                 (MEM[0] + 0.1, E1 - 0.1, 'YOU ASKED HIM TOO.')], 486, size=32, spacing=0.12)
    ca = seg(t, 0.4, 0.6) * (1 - seg(t, E1 - 0.35, E1))
    k = ask_k(t)
    if t < MEM[0] + 0.3:
        n = max(1, k + 1)
        pop = 1 + 0.12 * math.sin(math.pi * seg(t, ASKS[max(0, k)] - 0.05, ASKS[max(0, k)] + 0.2))
        text(c, f'ASKED {n} TIME' + ('S' if n > 1 else ''), 540, 572, 34 * pop, WHITE, a=0.92 * ca, spacing=0.18)
    else:
        n = max(1, count_kid(t))
        text(c, f'ASKED {n} TIME' + ('S' if n > 1 else ''), 540, 572, 34, WHITE, a=0.92 * ca, spacing=0.18)
    text(c, 'ALREADY TOLD HIM', 540, LANES['A'] + 66, 24, LABEL, spacing=0.16)
    text(c, 'TELLS HIM AGAIN', 540, LANES['B'] + 66, 24, LABEL, spacing=0.16)
    text(c, "HE'D ANSWERED THREE TIMES.", 540, 262, 29, LABEL, a=seg(t, E1, E1 + 0.35), spacing=0.1)
    text(c, 'HIS FATHER ANSWERED TWENTY-ONE.', 540, 342, 40, WHITE, a=seg(t, E1 + 0.3, E1 + 0.65), spacing=0.1)
    arabic(c, 'فَلَا تَقُل لَّهُمَا أُفٍّ وَلَا تَنْهَرْهُمَا', 540, 430, 46, LABEL, a=seg(t, E2, E2 + 0.35))
    text(c, '“…SAY NOT TO THEM [SO MUCH AS], ‘UFF,’ AND DO NOT REPEL THEM…”', 540, 486, 20, LABEL,
         a=seg(t, E2 + 0.15, E2 + 0.5), spacing=0.05)
    text(c, "QUR'AN 17:23", 540, 530, 20, DIM, a=seg(t, E2 + 0.35, E2 + 0.7), tf=TF_REG)
    vignette(c, 0.5)
    grain(c, i)


EVENTS = dict(dur=DUR, e1=E1, e2=E2, asks=ASKS, ans_lag=ANS_LAG, mem=MEM, b_walk=B_WALK,
              kid_asks=[kid_ask_time(i) for i in range(KID_ASKS)])

if __name__ == '__main__':
    run(frame, 'v67', N, DUR, EVENTS)
