"""Colour grades applied to a finished frame. 'ember' is the house palette:
deep plum background, terracotta props, warm gold/peach light, white figures."""
import numpy as np

PALETTES = {'ember': dict(stops=[0.0, 0.12, 0.45, 1.0],
                          cols=[(20, 10, 18), (62, 28, 44), (176, 96, 72), (255, 246, 236)], k=1.5, gold=(1.0, 0.82, 0.5))}


def grade_rgb(rgb, pal):
    f = rgb.astype(np.float32) / 255.0
    y = f[..., 0] * 0.2126 + f[..., 1] * 0.7152 + f[..., 2] * 0.0722
    stops = np.array(pal['stops'], np.float32)
    cols = np.array(pal['cols'], np.float32) / 255.0
    out = np.stack([np.interp(y, stops, cols[:, ch]) for ch in range(3)], -1)
    out += (f - y[..., None]) * pal['k']
    warm = np.clip((f[..., 0] - f[..., 2]) * 7.0, 0, 1)[..., None]
    gold = np.array(pal['gold'], np.float32)
    out = out * (1 - 0.65 * warm) + gold * 0.65 * warm * np.maximum(out.max(-1, keepdims=True), y[..., None] + 0.3)
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)
