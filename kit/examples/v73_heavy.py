"""#73 Heavy — formula reel. Sahih Muslim 223 (al-hamdu lillah fills the scale), Sahih al-Bukhari 6406 (two phrases,
easy on the tongue, heavy in the balance), Jami' at-Tirmidhi 2002 (nothing heavier than good character).

A man stands beside his scale. His side is light; the other pan is heaped with dark stones, so it hangs low.
1. He says alhamdulillah: the word floats over and drops in, and his pan fills with light. The beam comes up.
2. Two phrases float over, light as feathers. Each one lands with a thud and the beam drops further his way.
3. A rude message comes in. He starts typing back, stops, hand on his chest, and sends something kind.
   A big warm block drops into his pan and it slams down; the stones jump.
"""
from formula import *

FIG = Figure(300)
G = FLOOR
N = int(DUR * FPS)
V1, L1, V2, L2, V3, CTA = T['v1'], T['l1'], T['v2'], T['l2'], T['v3'], T['cta']

MX = 150                          # man
PX, PY = 640, 900                 # pivot
R = 230                           # half beam
HANG = 190                        # string length

SAY1 = (V1[0] + 0.45, V1[0] + 1.55)       # alhamdulillah floats over
FILL = (SAY1[1], SAY1[1] + 0.6)
SAY2 = (V2[0] + 0.4, V2[0] + 1.5)
SAY3 = (V2[0] + 1.75, V2[0] + 2.85)
MSG_IN = V3[0] + 0.55
TYPE = (V3[0] + 0.95, V3[0] + 1.5)
CALM = (V3[0] + 1.55, V3[0] + 1.95)
REPLY = V3[0] + 2.15
BLOCK = (V3[0] + 2.35, V3[0] + 2.75)

IMPACTS = [(FILL[0] + 0.1, -11.0), (SAY2[1], -6.0), (SAY3[1], -6.0), (BLOCK[1], -13.0)]
ANG0 = 15.0                       # start: his side (left) high

STAND_ = dict(STAND, hd=10)
SAY_POSE = P(t=-3, hd=-8, Lua=-4, Lel=8, Rua=34, Rel=110)
PHONE_P = P(t=2, hd=34, Lua=36, Lel=92, Rua=40, Rel=88)
TYPE_P = dict(PHONE_P, t=6, hd=38)
CALM_P = P(t=0, hd=14, Lua=36, Lel=92, Rua=50, Rel=126)
END_P = P(t=0, hd=6, Lua=-4, Lel=8, Rua=50, Rel=126)


def ang(t):
    a = ANG0
    for ti, d in IMPACTS:
        if t > ti:
            tau = t - ti
            a += d * (1 - math.exp(-4.5 * tau) * math.cos(15 * tau))
    return a


def ends(t):
    a = math.radians(ang(t))
    dx, dy = R * math.cos(a), R * math.sin(a)
    return (PX - dx, PY - dy), (PX + dx, PY + dy)


def man(t):
    keys = [(0, STAND_), (SAY1[0] - 0.3, STAND_), (SAY1[0] - 0.05, SAY_POSE), (SAY1[0] + 0.5, SAY_POSE),
            (SAY1[1], STAND_),
            (SAY2[0] - 0.3, STAND_), (SAY2[0] - 0.05, SAY_POSE), (SAY2[0] + 0.4, SAY_POSE), (SAY2[0] + 0.8, STAND_),
            (SAY3[0] - 0.3, STAND_), (SAY3[0] - 0.05, SAY_POSE), (SAY3[0] + 0.4, SAY_POSE), (SAY3[0] + 0.8, STAND_),
            (V3[0] + 0.2, STAND_), (MSG_IN - 0.1, PHONE_P), (TYPE[0], PHONE_P)]
    p = chain(t, keys)
    if TYPE[0] <= t < CALM[0]:
        p = dict(TYPE_P)
        p['Rel'] += 8 * math.sin(t * 40) * (t < TYPE[1])
        p['Lel'] += 8 * math.sin(t * 40 + 1.3) * (t < TYPE[1])
        p['hd'] += 6 * seg(t, TYPE[1] - 0.1, TYPE[1] + 0.05)
    elif t >= CALM[0]:
        u = ease(seg(t, *CALM))
        v = ease(seg(t, REPLY - 0.2, REPLY + 0.05))
        w = ease(seg(t, V3[1] - 0.2, V3[1] + 0.3))
        p = mix(mix(mix(TYPE_P, CALM_P, u), PHONE_P, v), END_P, w)
    return FIG.solve(p, MX, 1, ground=G)


# ---------------------------------------------------------------- the scale
METAL = (150, 152, 160)


def pan(c, x, y, fill=0.0, gems=0, block=0.0, stones=0.0, jump=0.0):
    # strings
    for dx in (-70, 0, 70):
        line(c, x, y, x + dx, y + HANG, METAL, 2, a=0.8)
    by = y + HANG
    # contents behind the bowl rim
    if fill > 0:
        h = 30 * fill
        light_pool(c, x, by - h, 110, 50, WARM, a=0.25 * fill)
        c.drawOval(skia.Rect(x - 70 * (0.5 + 0.5 * fill), by - h - 9, x + 70 * (0.5 + 0.5 * fill), by - h + 9),
                   skia.Paint(AntiAlias=True, Color=C((255, 236, 200), 0.9 * fill)))
    for k in range(gems):
        gx = x - 26 + 52 * k
        c.drawCircle(gx, by - 30, 11, skia.Paint(AntiAlias=True, Color=C((255, 240, 214))))
        light_pool(c, gx, by - 30, 40, 40, WARM, a=0.22)
    if block > 0:
        rect(c, x - 44, by - 34 - 70, 88, 70, (255, 236, 200), a=block, r=10)
        light_pool(c, x, by - 70, 130, 90, WARM, a=0.3 * block)
    if stones > 0:
        for k, (sx, sy, rx, ry) in enumerate(((-42, -18, 30, 20), (0, -22, 34, 24), (40, -18, 30, 20),
                                               (-20, -48, 28, 20), (22, -50, 30, 20), (0, -74, 26, 18))):
            jy = -jump * (14 + 10 * (k % 3))
            c.drawOval(skia.Rect(x + sx - rx, by + sy - ry + jy, x + sx + rx, by + sy + ry + jy),
                       skia.Paint(AntiAlias=True, Color=C((52, 54, 60))))
            c.drawOval(skia.Rect(x + sx - rx, by + sy - ry + jy, x + sx + rx, by + sy + ry + jy),
                       skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2,
                                  Color=C((96, 98, 106))))
    # the bowl
    p = skia.Path()
    p.moveTo(x - 82, by - 8)
    p.quadTo(x, by + 40, x + 82, by - 8)
    p.close()
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=C((96, 98, 106))))
    line(c, x - 84, by - 8, x + 84, by - 8, METAL, 5)


def scale(c, t):
    # post and base
    line(c, PX, G, PX, PY, METAL, 10, cap=False)
    p = skia.Path()
    p.moveTo(PX - 70, G)
    p.lineTo(PX - 30, G - 26)
    p.lineTo(PX + 30, G - 26)
    p.lineTo(PX + 70, G)
    p.close()
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=C((96, 98, 106))))
    (lx, ly), (rx, ry) = ends(t)
    fill = ease(seg(t, *FILL))
    gems = int(t >= SAY2[1]) + int(t >= SAY3[1])
    block = seg(t, BLOCK[1] - 0.05, BLOCK[1])
    jump = 0.0
    if t > BLOCK[1]:
        tau = t - BLOCK[1]
        jump = max(0.0, math.sin(min(math.pi, tau * 7))) * math.exp(-tau * 2)
    pan(c, lx, ly, fill=fill, gems=gems, block=block)
    pan(c, rx, ry, stones=1.0, jump=jump)
    line(c, lx, ly, rx, ry, METAL, 8)
    c.drawCircle(PX, PY, 12, skia.Paint(AntiAlias=True, Color=C(METAL)))
    c.drawCircle(PX, PY, 5, skia.Paint(AntiAlias=True, Color=C((60, 62, 68))))
    # pointer
    a = math.radians(ang(t))
    line(c, PX, PY, PX + 70 * math.sin(a), PY - 70 * math.cos(a), RED, 4)


def floating(c, t, span, word, size, feather=False):
    """a said word drifting from his mouth into his pan."""
    u = seg(t, *span)
    if u <= 0 or u >= 1:
        return
    j = man(span[0])
    x0, y0 = j['head'][0] + 30, j['head'][1] - 20
    (lx, ly), _ = ends(span[1])
    x1, y1 = lx, ly + HANG - 40
    q = ease(u)
    x = lerp(x0, x1, q)
    y = lerp(y0, y1, q) - 120 * math.sin(math.pi * q)
    rot = 0.0
    if feather:
        x += 18 * math.sin(u * 9)
        rot = 8 * math.sin(u * 9 + 1)
    a = min(1.0, u * 5)
    light_pool(c, x, y, 80, 40, WARM, a=0.18 * a)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    arabic(c, word, 0, 12, size, (255, 240, 214), a=a)
    c.restore()


def phone_ui(c, t, j):
    if t < MSG_IN - 0.1 or t > V3[1] + 0.2:
        return
    hx, hy = j['Rh']
    c.save()
    c.translate(hx + 4, hy - 8)
    c.rotate(10)
    c.drawRoundRect(skia.Rect(-10, -17, 10, 17), 4, 4, skia.Paint(AntiAlias=True, Color=C((34, 36, 42))))
    c.drawRoundRect(skia.Rect(-10, -17, 10, 17), 4, 4, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                                                StrokeWidth=2.5, Color=C(LABEL)))
    c.restore()
    out = seg(t, V3[1] - 0.2, V3[1] + 0.2)
    bx, by = MX - 100, 880
    # their message: red, sharp
    a = seg(t, MSG_IN, MSG_IN + 0.15) * (1 - out)
    if a > 0:
        pop = 1 + 0.25 * math.sin(math.pi * seg(t, MSG_IN, MSG_IN + 0.25))
        rect(c, bx - 10, by - 22 * pop, 150 * pop, 44 * pop, (120, 34, 38), a=a, r=14)
        burst(c, bx - 14, by - 18, 18, 10, a=a)
        for k in range(3):
            rect(c, bx + 8 + 34 * k, by - 4, 22, 6, LABEL, a=a * 0.8, r=3)
    # his reply being typed: red dots, then deleted
    a2 = seg(t, TYPE[0], TYPE[0] + 0.1) * (1 - seg(t, TYPE[1], TYPE[1] + 0.25))
    if a2 > 0:
        n = int(min(5, (t - TYPE[0]) * 12))
        for k in range(n):
            c.drawCircle(bx + 20 + 16 * k, by + 46, 5, skia.Paint(AntiAlias=True, Color=C(RED, a2)))
    # the kind reply
    a3 = seg(t, REPLY, REPLY + 0.15) * (1 - out)
    if a3 > 0:
        rect(c, bx + 30, by + 34, 120, 40, (238, 238, 235), a=a3, r=14)
        c.save()
        c.translate(bx + 90, by + 54)
        heart = skia.Path()
        heart.moveTo(0, 8)
        heart.cubicTo(-14, -2, -8, -14, 0, -6)
        heart.cubicTo(8, -14, 14, -2, 0, 8)
        c.drawPath(heart, skia.Paint(AntiAlias=True, Color=C(RED, a3)))
        c.restore()


def falling_block(c, t):
    u = seg(t, *BLOCK)
    if u <= 0 or u >= 1:
        return
    (lx, ly), _ = ends(BLOCK[1])
    by = ly + HANG - 34 - 35
    y = lerp(640, by, ease_in(u))
    rect(c, lx - 44, y - 35, 88, 70, (255, 236, 200), r=10)
    light_pool(c, lx, y, 120, 90, WARM, a=0.3)


def world(c, t):
    stage(c)
    scale(c, t)
    j = man(t)
    FIG.draw(c, j)
    phone_ui(c, t, j)
    floating(c, t, SAY1, 'الحَمْدُ لِلَّه', 40)
    floating(c, t, SAY2, 'سُبْحَانَ اللهِ وَبِحَمْدِهِ', 30, feather=True)
    floating(c, t, SAY3, 'سُبْحَانَ اللهِ العَظِيم', 30, feather=True)
    falling_block(c, t)


def frame(c, t, i):
    background(c)
    pic = record(lambda rc: world(rc, t))
    finish(c, pic, i)
    c.drawPicture(pic)
    hook(c, t, ['3 THINGS THAT WEIGH THE MOST', 'ON YOUR SCALE.'])
    promise(c, t, 'NONE OF THEM COST A THING.')
    value(c, t, 1, 'ALHAMDULILLAH', ['ONE WORD. IT FILLS THE SCALE.'], V1)
    loop(c, t, 'THE NEXT ONE TAKES 3 SECONDS TO SAY.', L1)
    value(c, t, 2, 'SUBHANALLAHI WA BIHAMDIHI', ['SUBHANALLAHIL ‘ADHEEM.', 'EASY ON THE TONGUE. HEAVY ON THE SCALE.'], V2)
    loop(c, t, "THE HEAVIEST ONE ISN'T SOMETHING YOU SAY.", L2)
    value(c, t, 3, 'GOOD CHARACTER', ['NOTHING IS HEAVIER ON YOUR SCALE.'], V3)
    cta(c, t, 'SAY ONE RIGHT NOW.', 'SEND THIS TO SOMEONE WHO THINKS THEIR DEEDS ARE SMALL.',
        "SAHIH MUSLIM 223 · SAHIH AL-BUKHARI 6406 · JAMI' AT-TIRMIDHI 2002")
    vignette(c, 0.5)
    grain(c, i)


EVENTS = dict(dur=DUR, beats=T, say=[SAY1, SAY2, SAY3], fill=FILL, msg_in=MSG_IN, type=TYPE, calm=CALM, reply=REPLY,
              block=BLOCK, impacts=[i for i, _ in IMPACTS])

if __name__ == '__main__':
    run(frame, 'v73', N, DUR, EVENTS)
