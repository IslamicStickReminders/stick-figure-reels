"""#75 Go Home — formula reel. Sahih al-Bukhari 6514: "When carried to his grave, a dead person is followed by three,
two of which return (after his burial) and one remains with him: his relative, his property, and his deeds follow him;
relatives and his property go back while his deeds remain with him."

A funeral leaves a house: two men carry the bier, a child walks behind, a cart with a big sack of money rolls after
them, and three small lights (his deeds) float over the bier.
1. At the grave the bier goes down and the mound rises. The family turns and walks home; the child looks back once.
   The door closes behind them.
2. The cart turns around and rolls home too. The door opens, it goes in, the door closes.
3. Only the three small lights are left. They sink into the grave and stay with him.
"""
from formula import *

SM = Figure(240)
KID = Figure(170)
G = FLOOR
N = int(DUR * FPS)
V1, L1, V2, L2, V3, CTA = T['v1'], T['l1'], T['v2'], T['l2'], T['v3'], T['cta']

HOUSE_X = 120
GX = 850                                   # grave
WALK_IN = (0.0, 2.55)
LOWER = (2.65, 3.35)
MOUND = (3.2, 3.8)
TURN = (3.95, 4.15)
WALK_HOME = (4.15, 6.25)
LOOK_BACK = (5.0, 5.55)
DOOR1 = (5.85, 6.95)
CART_HOME = (V2[0] + 0.2, V2[0] + 2.4)
DOOR2 = (V2[0] + 2.0, V2[0] + 2.9)
SINK = (V3[0] + 0.5, V3[0] + 1.6)

BIER0, BIER1 = 360, GX
OFF = dict(front=82, rear=-82, kid=-180, cart=-300)


def bier_x(t):
    return lerp(BIER0, BIER1, ease(seg(t, *WALK_IN)) * 0.15 + 0.85 * seg(t, *WALK_IN))


CARRY_ARMS = dict(Lua=168, Lel=18, Rua=172, Rel=14)


def bearer(t, key):
    if t < WALK_IN[1]:
        x = bier_x(t) + OFF[key]
        p = dict(walk(t * 1.6 + (0.5 if key == 'rear' else 0)), **CARRY_ARMS)
        return SM.solve(p, x, 1, ground=G), x
    x_end = BIER1 + OFF[key]
    lag = 0.4 if key == 'front' else 0.0
    if t < TURN[0] + lag:
        lower = dict(CROUCH, hd=24, Lua=8, Lel=8, Rua=12, Rel=8)
        keys = [(LOWER[0], dict(STAND, **CARRY_ARMS)), (LOWER[0] + 0.3, dict(STAND, hd=10, Lua=20, Lel=10, Rua=24, Rel=10)),
                (LOWER[1] - 0.1, lower), (LOWER[1] + 0.35, dict(STAND, hd=24)), (TURN[0] + lag, dict(STAND, hd=24))]
        return SM.solve(chain(t, keys), x_end, 1, ground=G), x_end
    # home
    home_x = HOUSE_X + (70 if key == 'front' else 40)
    u = seg(t, WALK_HOME[0] + lag, WALK_HOME[1] + lag)
    x = lerp(x_end, home_x, u)
    p = dict(walk(t * 1.5 + (0.5 if key == 'rear' else 0)), hd=16)
    a = 1 - seg(t, DOOR1[0] + 0.1 + lag, DOOR1[0] + 0.3 + lag)
    return SM.solve(p, x, -1, ground=G), x, a


def kid(t):
    if t < WALK_IN[1]:
        x = bier_x(t) + OFF['kid']
        return KID.solve(dict(walk(t * 1.9), hd=12), x, 1, ground=G), x, 1, 1.0
    x_end = BIER1 + OFF['kid']
    if t < WALK_HOME[0] + 0.25:
        return KID.solve(dict(STAND, hd=8 + 14 * seg(t, LOWER[0], LOWER[1])), x_end, 1, ground=G), x_end, 1, 1.0
    u = seg(t, WALK_HOME[0] + 0.25, WALK_HOME[1] + 0.3)
    # he stops once and looks back at the grave
    look = seg(t, *LOOK_BACK)
    if 0 < look < 1:
        u0 = seg(LOOK_BACK[0], WALK_HOME[0] + 0.25, WALK_HOME[1] + 0.3)
        x = lerp(x_end, HOUSE_X + 50, u0)
        return KID.solve(dict(STAND, hd=4), x, 1, ground=G), x, 1, 1.0
    if t > LOOK_BACK[1]:
        u = seg(t, WALK_HOME[0] + 0.25 + 0.55, WALK_HOME[1] + 0.3 + 0.1)
        u0 = seg(LOOK_BACK[0], WALK_HOME[0] + 0.25, WALK_HOME[1] + 0.3)
        x = lerp(lerp(x_end, HOUSE_X + 50, u0), HOUSE_X + 50, u)
    else:
        x = lerp(x_end, HOUSE_X + 50, u)
    a = 1 - seg(t, DOOR1[0] + 0.6, DOOR1[0] + 0.8)
    return KID.solve(dict(walk(t * 1.9), hd=14), x, -1, ground=G), x, -1, a


def cart_x(t):
    if t < WALK_IN[1]:
        return bier_x(t) + OFF['cart']
    x_end = BIER1 + OFF['cart']
    return lerp(x_end, HOUSE_X + 40, ease(seg(t, *CART_HOME)) * 0.2 + 0.8 * seg(t, *CART_HOME))


# ---------------------------------------------------------------- drawing
def house(c, t):
    x = HOUSE_X
    col = (96, 98, 106)
    pen = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=4, Color=C(col),
                     StrokeJoin=skia.Paint.kRound_Join)
    c.drawRect(skia.Rect(x - 90, G - 150, x + 90, G), skia.Paint(AntiAlias=True, Color=C((30, 32, 38))))
    c.drawRect(skia.Rect(x - 90, G - 150, x + 90, G), pen)
    p = skia.Path()
    p.moveTo(x - 108, G - 150)
    p.lineTo(x, G - 228)
    p.lineTo(x + 108, G - 150)
    c.drawPath(p, pen)
    # lit window
    rect(c, x - 70, G - 120, 44, 40, (255, 226, 170), a=0.75, r=3)
    light_pool(c, x - 48, G - 100, 70, 50, WARM, a=0.12)
    # door: open while someone goes in
    op = 0.0
    for d0, d1 in (DOOR1, DOOR2):
        op = max(op, math.sin(math.pi * seg(t, d0, d1)))
    dx0, dw = x + 20, 46
    rect(c, dx0, G - 96, dw, 96, (255, 226, 170), a=0.85 * op, r=2)
    rect(c, dx0, G - 96, dw * (1 - op), 96, (74, 76, 84), r=2)
    c.drawRect(skia.Rect(dx0, G - 96, dx0 + dw, G), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                                               StrokeWidth=3, Color=C(col)))


def grave(c, t):
    # the open pit and its pile of earth, then the mound
    pit = 1 - seg(t, *MOUND)
    if pit > 0:
        rect(c, GX - 80, G - 2, 160, 34, (14, 15, 18), a=pit)
        p = skia.Path()
        p.moveTo(GX + 96, G)
        p.quadTo(GX + 150, G - 70 * pit, GX + 204, G)
        p.close()
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=C((74, 76, 84), pit)))
    u = ease(seg(t, *MOUND))
    if u > 0:
        h = 44 * u
        p = skia.Path()
        p.moveTo(GX - 110, G)
        p.cubicTo(GX - 90, G - h * 1.25, GX + 90, G - h * 1.25, GX + 110, G)
        p.close()
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=C((74, 76, 84))))
        c.drawPath(p, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3, Color=C((112, 114, 122))))
        sh = 60 * ease(seg(t, MOUND[0] + 0.2, MOUND[1] + 0.1))
        if sh > 1:
            x = GX - 122
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x - 14, G - sh, x + 14, G), 4, 4),
                        skia.Paint(AntiAlias=True, Color=C((112, 114, 122))))
            c.drawCircle(x, G - sh + 13, 14, skia.Paint(AntiAlias=True, Color=C((112, 114, 122))))


def bier(c, t, jf, jr):
    if t > LOWER[1]:
        return
    if t < WALK_IN[1]:
        x = bier_x(t)
        y = min(jf['Rh'][1], jr['Rh'][1]) + 4
    else:
        x = BIER1
        y0 = bearer(LOWER[0], 'front')[0]['Rh'][1] + 4
        y = lerp(y0, G - 40, ease(seg(t, LOWER[0], LOWER[1] - 0.15)))
        y = lerp(y, G + 30, ease(seg(t, LOWER[1] - 0.2, LOWER[1])))
    c.save()
    c.clipRect(skia.Rect(0, 0, W, G + 2))
    rect(c, x - 120, y - 6, 240, 10, (112, 114, 122), r=3)
    p = skia.Path()
    p.moveTo(x - 110, y - 6)
    p.cubicTo(x - 100, y - 40, x + 100, y - 40, x + 110, y - 6)
    p.close()
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=C((232, 230, 224))))
    c.restore()


def cart(c, t):
    x = cart_x(t)
    a = 1 - seg(t, DOOR2[0] + 0.35, DOOR2[0] + 0.6)
    if a <= 0:
        return
    moving = (t < WALK_IN[1]) or (CART_HOME[0] < t < CART_HOME[1])
    rot = (x * 1.6) % 360
    c.saveLayerAlpha(None, int(255 * a))
    rect(c, x - 50, G - 62, 100, 40, (96, 98, 106), r=4)
    for wx in (x - 30, x + 30):
        c.drawCircle(wx, G - 16, 16, skia.Paint(AntiAlias=True, Color=C((60, 62, 68))))
        c.drawCircle(wx, G - 16, 16, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3,
                                                Color=C((128, 131, 136))))
        r = math.radians(rot)
        line(c, wx - 12 * math.cos(r), G - 16 - 12 * math.sin(r), wx + 12 * math.cos(r), G - 16 + 12 * math.sin(r),
             (128, 131, 136), 2)
    # the sack, heavy and full
    p = skia.Path()
    p.moveTo(x - 44, G - 62)
    p.cubicTo(x - 60, G - 150, x + 60, G - 150, x + 44, G - 62)
    p.close()
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=C((150, 136, 104))))
    line(c, x - 14, G - 132, x + 14, G - 132, (120, 108, 82), 6)
    text(c, '$', x, G - 82, 34, (96, 86, 64), spacing=0)
    # spilled coins on top
    for k, (cx, cy) in enumerate(((-20, -146), (6, -150), (24, -144))):
        c.drawOval(skia.Rect(x + cx - 12, G + cy - 5, x + cx + 12, G + cy + 5),
                   skia.Paint(AntiAlias=True, Color=C((200, 180, 120))))
    c.restore()


def deeds(c, t, jf, jr):
    """three small lights: all he brought."""
    sink = ease(seg(t, *SINK))
    for k in range(3):
        if t < WALK_IN[1]:
            bx = bier_x(t)
            by = min(jf['Rh'][1], jr['Rh'][1]) - 70
        else:
            bx, by = BIER1, min(jf['Rh'][1], jr['Rh'][1]) - 70 if t < LOWER[0] else lerp(
                min(jf['Rh'][1], jr['Rh'][1]) - 70, G - 120, ease(seg(t, LOWER[0], LOWER[1])))
        x = bx + (-26 + 26 * k) + 6 * math.sin(t * 2 + k)
        y = by + 8 * math.sin(t * 2.6 + k * 2)
        y = lerp(y, G - 18, sink)
        x = lerp(x, GX - 30 + 30 * k, sink)
        a = 1.0
        light_pool(c, x, y, 30, 30, WARM, a=0.2)
        c.drawCircle(x, y, 6, skia.Paint(AntiAlias=True, Color=C((255, 240, 214), a)))
    if sink > 0.9:
        light_pool(c, GX, G - 16, 120, 50, WARM, a=0.12 * seg(t, SINK[1] - 0.1, SINK[1] + 0.6))


def world(c, t):
    stage(c)
    house(c, t)
    grave(c, t)
    cart(c, t)
    jf = bearer(t, 'front')
    jr = bearer(t, 'rear')
    kd = kid(t)
    jfj, jrj = jf[0], jr[0]
    if t >= TURN[0]:
        af = jf[2] if len(jf) > 2 else 1.0
        ar_ = jr[2] if len(jr) > 2 else 1.0
    else:
        af = ar_ = 1.0
    if kd[3] > 0:
        KID.draw(c, kd[0], a=kd[3])
    if ar_ > 0:
        SM.draw(c, jrj, a=ar_)
    bier(c, t, jfj, jrj)
    if af > 0:
        SM.draw(c, jfj, a=af)
    deeds(c, t, jfj, jrj)


def frame(c, t, i):
    background(c)
    pic = record(lambda rc: world(rc, t))
    finish(c, pic, i)
    c.drawPicture(pic)
    hook(c, t, ['3 FOLLOW YOU TO YOUR GRAVE.', '2 OF THEM GO HOME.'])
    promise(c, t, 'ONLY ONE STAYS. MOST PEOPLE WORK FOR THE OTHER 2.')
    value(c, t, 1, 'YOUR FAMILY', ['THEY CARRY YOU THERE.', 'THEN THEY GO HOME.'], V1)
    loop(c, t, 'THE NEXT ONE, YOU SPENT YOUR LIFE EARNING.', L1)
    value(c, t, 2, 'YOUR MONEY', ['IT GOES HOME TOO.', 'TO SOMEONE ELSE.'], V2)
    loop(c, t, 'THE LAST ONE IS THE ONE YOU KEEP PUTTING OFF.', L2)
    value(c, t, 3, 'YOUR DEEDS', ['THE ONLY ONE THAT STAYS.'], V3)
    cta(c, t, 'WORK FOR THE ONE THAT STAYS.', "SEND THIS TO SOMEONE WHO'S ALWAYS AT WORK.", 'SAHIH AL-BUKHARI 6514')
    vignette(c, 0.5)
    grain(c, i)


EVENTS = dict(dur=DUR, beats=T, walk_in=WALK_IN, lower=LOWER, mound=MOUND, walk_home=WALK_HOME, look_back=LOOK_BACK,
              door1=DOOR1, cart_home=CART_HOME, door2=DOOR2, sink=SINK)

if __name__ == '__main__':
    run(frame, 'v75', N, DUR, EVENTS)
