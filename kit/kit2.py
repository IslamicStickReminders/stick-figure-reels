"""Shared helpers for the two-figure formula reels (#50+)."""
import json, math, os, sys, glob
import numpy as np
from nv import *
from cine import *

DUA_ST = P(t=0, hd=12, Lua=22, Lel=104, Rua=36, Rel=96)
DUA_SIT = dict(SIT_UP, hd=10, Lua=22, Lel=104, Rua=36, Rel=96)
HALF_DUA = P(t=2, hd=6, Lua=12, Lel=76, Rua=22, Rel=70)
SIT_F = P(t=-4, hd=36, Lth=112, Lkn=172, Rth=118, Rkn=176, Lua=58, Lel=62, Rua=64, Rel=58)


def rate(fig, dx, dur, stride):
    cyc = 2 * 2 * (fig.thigh + fig.shin) * math.sin(math.radians(stride))
    return abs(dx) / max(dur, 1e-3) / cyc


def walk_to(fig, t, t0, t1, xa, xb, stride=20, prev=STAND, end=STAND, back=False):
    u = seg(t, t0, t1)
    x = lerp(xa, xb, u)
    ph = (t - t0) * rate(fig, xb - xa, t1 - t0, stride)
    pose = walk(-ph if back else ph, stride=stride, back=back)
    if t < t0 + 0.14:
        pose = mix(prev, pose, ease((t - t0) / 0.14))
    if t > t1 - 0.16:
        pose = mix(pose, end, ease((t - (t1 - 0.16)) / 0.16))
    return pose, x


def arm_ik(fig, ash, target, f):
    U, Fa = fig.uarm, fig.farm
    dx, dy = target[0] - ash[0], target[1] - ash[1]
    D = max(1e-3, min(math.hypot(dx, dy), U + Fa - 0.5))
    phi = math.degrees(math.atan2(f * dx, dy))
    alpha = math.degrees(math.acos(clamp((U * U + D * D - Fa * Fa) / (2 * U * D), -1, 1)))
    ua = phi - alpha
    e = np.array(ash) + fig._down(f, ua) * U
    fa = math.degrees(math.atan2(f * (target[0] - e[0]), target[1] - e[1]))
    return ua, fa - ua


def with_arms(fig, p, x, f, G, targets, w=1.0):
    j = fig.solve(p, x, f, ground=G)
    hy = j['hip'][1]
    q = dict(p)
    for s_, tgt in targets.items():
        ua, el = arm_ik(fig, j['ash'], tgt, f)
        q[s_ + 'ua'] = lerp(p[s_ + 'ua'], ua, w)
        q[s_ + 'el'] = lerp(p[s_ + 'el'], el, w)
    return fig.joints(q, x, hy, f)


def heart_pt(fig, j):
    return (j['sh'][0] + 0.55 * (j['hip'][0] - j['sh'][0]) + 8 * j['f'], j['sh'][1] + 0.35 * (j['hip'][1] - j['sh'][1]))


def palms(c, j, a, size=1.0):
    if a <= 0:
        return
    for s_ in 'LR':
        hx, hy = j[s_ + 'h']
        ex, ey = j[s_ + 'e']
        ang = math.degrees(math.atan2(hy - ey, hx - ex))
        c.save()
        c.translate(hx, hy)
        c.rotate(ang)
        col = WHITE if s_ == 'R' else FAR
        c.drawRoundRect(skia.Rect(-5 * size, -12 * size, 22 * size, 12 * size), 11 * size, 11 * size,
                        skia.Paint(AntiAlias=True, Color=C(col, a)))
        c.restore()


def burst(c, x, y, r, rot, a=1.0, col=RED):
    if a <= 0:
        return
    p = skia.Path()
    n = 9
    for k in range(2 * n):
        rr = r if k % 2 == 0 else r * 0.5
        ang = math.pi * k / n + rot
        px, py = x + rr * math.cos(ang), y + rr * math.sin(ang)
        if k == 0:
            p.moveTo(px, py)
        else:
            p.lineTo(px, py)
    p.close()
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=C(col, a)))


def shake_head(p, t, t0, t1, amp=11, base=None):
    u = seg(t, t0, t1)
    q = dict(p)
    q['hd'] += amp * math.sin(u * 3 * 2 * math.pi) * math.sin(math.pi * u)
    return q


def end_card(c, t, e1, e2, line1, line2, arabic_txt=None, english=(), extra=None, cite='', size2=50):
    """verdict (two lines) at E1, then the source block at E2. returns when it's fully up."""
    text(c, line1, 540, 236, 29, LABEL, a=seg(t, e1, e1 + 0.35), spacing=0.1)
    text(c, line2, 540, 318, size2, WHITE, a=seg(t, e1 + 0.25, e1 + 0.6), spacing=0.12)
    y = 410
    k = 0.0
    if arabic_txt:
        arabic(c, arabic_txt, 540, y, 48, LABEL, a=seg(t, e2, e2 + 0.35))
        y += 52
        k = 0.15
    for ln in english:
        text(c, ln, 540, y, 20, LABEL, a=seg(t, e2 + k, e2 + k + 0.35), spacing=0.05)
        y += 30
    y += 14
    if extra:
        text(c, extra, 540, y, 22, WHITE, a=seg(t, e2 + 0.35, e2 + 0.7), spacing=0.08)
        y += 42
    text(c, cite, 540, y, 20, DIM, a=seg(t, e2 + 0.45, e2 + 0.8), tf=TF_REG)


def run(frame, name, n, dur, events):
    json.dump(events, open(f'out/{name}_events.json', 'w'), indent=1)
    print('dur', dur)
    if len(sys.argv) > 1 and sys.argv[1] == 'stills':
        os.makedirs(f'test/{name}', exist_ok=True)
        for f_ in glob.glob(f'test/{name}/*.png'):
            os.remove(f_)
        for tt in [float(x) for x in sys.argv[2:]]:
            s = skia.Surface(W, H)
            c = s.getCanvas()
            frame(c, tt, int(tt * FPS))
            s.makeImageSnapshot().save(f'test/{name}/t{tt:05.2f}.png', skia.kPNG)
    else:
        render(frame, n, f'out/{name}_silent.mp4')
