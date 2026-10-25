"""Shared 'cinematic' helpers for the second generation of reels: camera moves, light, top text, loop fade."""
import math
import numpy as np
from nv import *

WARM = (255, 242, 222)
NIGHT = (18, 22, 34)


def camera(c, zoom, cx, cy, dx=0.0, dy=0.0):
    """apply a zoom around (cx, cy) plus a pan; call between save/restore."""
    c.translate(cx + dx, cy + dy)
    c.scale(zoom, zoom)
    c.translate(-cx, -cy)


def light_pool(c, x, y, rx, ry, color=WARM, a=0.2):
    if a <= 0:
        return
    sh = skia.GradientShader.MakeRadial(center=(x, y), radius=max(rx, ry),
                                        colors=[C(color, a), C(color, a * 0.45), C(color, 0)],
                                        positions=[0, 0.45, 1])
    c.save()
    c.translate(x, y)
    c.scale(1, ry / max(rx, ry))
    c.translate(-x, -y)
    c.drawCircle(x, y, max(rx, ry), skia.Paint(AntiAlias=True, Shader=sh))
    c.restore()


def beam(c, x_top0, x_top1, y_top, x_bot0, x_bot1, y_bot, a=0.12, color=WARM):
    if a <= 0:
        return
    p = skia.Path()
    p.moveTo(x_top0, y_top)
    p.lineTo(x_top1, y_top)
    p.lineTo(x_bot1, y_bot)
    p.lineTo(x_bot0, y_bot)
    p.close()
    sh = skia.GradientShader.MakeLinear(points=[(0, y_top), (0, y_bot)],
                                        colors=[C(color, a * 0.3), C(color, a), C(color, a * 0.6)],
                                        positions=[0, 0.7, 1])
    c.drawPath(p, skia.Paint(AntiAlias=True, Shader=sh,
                             MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18)))


def tint(c, color, a):
    if a > 0:
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=C(color, a)))


def fade_black(c, t, dur, length=0.4):
    a = seg(t, dur - length, dur)
    if a > 0:
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=C((0, 0, 0), a)))


def beats(c, t, items, y, size=36, color=LABEL, spacing=0.13, xfade=0.25):
    """items: [(t_in, t_out, text)] — crossfading one-line captions."""
    for (a, b, s) in items:
        al = (1.0 if a <= 0 else seg(t, a, a + xfade)) * (1 - seg(t, b - xfade, b))
        if al > 0:
            text(c, s, 540, y, size, color, a=al, spacing=spacing)


def thought_bubble(c, x, y, r, s=1.0, a=1.0, fill=(30, 32, 37)):
    """cloud-shaped bubble centred at (x, y), plus trailing dots toward lower-left."""
    if s <= 0 or a <= 0:
        return
    paint_f = skia.Paint(AntiAlias=True, Color=C(fill, a))
    paint_s = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=4, Color=C(WHITE, a))
    lobes = [(-0.55, 0.05, 0.55), (-0.2, -0.32, 0.6), (0.3, -0.3, 0.58), (0.62, 0.05, 0.52), (0.25, 0.32, 0.55),
             (-0.25, 0.33, 0.55)]
    path = skia.Path()
    for (dx, dy, rr) in lobes:
        path.addCircle(x + dx * r * s, y + dy * r * s, rr * r * s)
    path.setFillType(skia.PathFillType.kWinding)
    c.drawPath(path, paint_s)
    c.drawPath(path, paint_f)
    for k, (dx, dy, rr) in enumerate([(-0.95, 0.75, 0.13), (-1.2, 1.05, 0.085)]):
        c.drawCircle(x + dx * r * s, y + dy * r * s, rr * r * s, paint_f)
        c.drawCircle(x + dx * r * s, y + dy * r * s, rr * r * s,
                     skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3, Color=C(WHITE, a)))


def flower(c, x, base, h, u, petal=WHITE, a=1.0, sway=0.0, size=1.0):
    """u: 0..1 growth. stem grows first (0..0.6), then bloom opens (0.55..1)."""
    if u <= 0:
        return
    gu = ease(clamp(u / 0.6))
    top_x = x + sway * gu
    top_y = base - h * gu
    stem = skia.Path()
    stem.moveTo(x, base)
    stem.quadTo(x + sway * 0.2, base - h * gu * 0.5, top_x, top_y)
    c.drawPath(stem, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3.4 * size,
                                StrokeCap=skia.Paint.kRound_Cap, Color=C((150, 160, 150), a)))
    if gu > 0.4:
        lu = seg(gu, 0.4, 0.8)
        for s in (-1, 1):
            lx = x + sway * 0.12 + s * 9 * size * lu
            ly = base - h * 0.35 - s * 6
            c.save()
            c.translate(lx, ly)
            c.rotate(s * 35)
            c.drawOval(skia.Rect(-9 * size * lu, -3.5 * size * lu, 9 * size * lu, 3.5 * size * lu),
                       skia.Paint(AntiAlias=True, Color=C((150, 160, 150), a)))
            c.restore()
    bu = ease_out(seg(u, 0.55, 1.0))
    if bu > 0:
        pr = 7.5 * size * bu
        for k in range(5):
            ang = 2 * math.pi * k / 5 + 0.3
            c.drawCircle(top_x + math.cos(ang) * pr * 1.05, top_y + math.sin(ang) * pr * 1.05, pr,
                         skia.Paint(AntiAlias=True, Color=C(petal, a)))
        c.drawCircle(top_x, top_y, pr * 0.62, skia.Paint(AntiAlias=True, Color=C((44, 40, 40) if petal != RED
                                                                                   else (238, 214, 200), a)))
