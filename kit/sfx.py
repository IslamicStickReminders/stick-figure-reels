"""Synthesised sound effects (no music) for the two reels."""
import json, math, sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000
rng = np.random.default_rng(5)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype='low', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype='high', fs=SR, output='sos'), x)


def lerp(a, b, u):
    return a + (b - a) * u


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def tsec(n):
    return np.arange(n) / SR


class Mix:
    def __init__(self, dur):
        self.L = np.zeros(int(dur * SR) + SR)
        self.R = np.zeros_like(self.L)
        self.dur = dur

    def add(self, sig, t, gain=1.0, pan=0.0):
        i = int(t * SR)
        if i >= len(self.L) or i + len(sig) <= 0:
            return
        if i < 0:
            sig = sig[-i:]
            i = 0
        n = min(len(sig), len(self.L) - i)
        gl = gain * math.cos((pan + 1) * math.pi / 4)
        gr = gain * math.sin((pan + 1) * math.pi / 4)
        self.L[i:i + n] += sig[:n] * gl
        self.R[i:i + n] += sig[:n] * gr

    drive = 3.2

    def write(self, path, peak_db=-1.0):
        n = int(self.dur * SR)
        st = np.stack([self.L[:n], self.R[:n]], 1)
        pk = np.max(np.abs(st)) + 1e-9
        st = np.tanh(st / pk * self.drive) / np.tanh(self.drive)  # soft limiter
        st *= 10 ** (peak_db / 20) / (np.max(np.abs(st)) + 1e-9)
        fade = int(0.03 * SR)
        st[-fade:] *= np.linspace(1, 0, fade)[:, None]
        wavfile.write(path, SR, (st * 32767).astype(np.int16))


# ---------------------------------------------------------------- sounds
def room(dur, level=0.012):
    n = int(dur * SR) + SR
    b = np.cumsum(rng.normal(0, 1, n))
    b = hp(b, 20)
    b = lp(b, 260)
    b /= np.max(np.abs(b)) + 1e-9
    hiss = hp(rng.normal(0, 1, n), 4000) * 0.04
    return (b + hiss) * level


def clack(pitch=1.0, weight=1.0):
    n = int(0.16 * SR)
    t = tsec(n)
    click = bp(rng.normal(0, 1, n), 1800 * pitch, 6000 * pitch) * env_exp(n, 0.008)
    body = np.sin(2 * np.pi * 1050 * pitch * t + rng.uniform(0, 6)) * env_exp(n, 0.022) * 0.5
    body += np.sin(2 * np.pi * 1690 * pitch * t) * env_exp(n, 0.012) * 0.25
    thud = np.sin(2 * np.pi * 130 * pitch * t) * env_exp(n, 0.045) * 0.6 * weight
    s = click * 0.9 + body + thud
    return s / (np.max(np.abs(s)) + 1e-9)


def boom():
    n = int(1.4 * SR)
    t = tsec(n)
    f = 58 * (1 + 0.25 * np.exp(-t / 0.08))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * env_exp(n, 0.45)
    s += lp(rng.normal(0, 1, n), 180) * env_exp(n, 0.2) * 0.6
    a = np.minimum(1, t / 0.004)
    return s * a / (np.max(np.abs(s)) + 1e-9)


def tick():
    n = int(0.012 * SR)
    s = bp(rng.normal(0, 1, n), 2500, 7000) * env_exp(n, 0.0025)
    return s / (np.max(np.abs(s)) + 1e-9)


def scrape(dur=0.22):
    n = int(dur * SR)
    t = tsec(n)
    s = bp(rng.normal(0, 1, n), 500, 2600)
    am = 0.6 + 0.4 * np.sin(2 * np.pi * 37 * t + rng.uniform(0, 6)) * rng.uniform(0.6, 1)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.7
    s = s * am * e
    return s / (np.max(np.abs(s)) + 1e-9)


def step(soft=1.0):
    n = int(0.09 * SR)
    t = tsec(n)
    s = lp(rng.normal(0, 1, n), 1400) * env_exp(n, 0.012) * 0.8
    s += np.sin(2 * np.pi * rng.uniform(140, 175) * t) * env_exp(n, 0.025) * 0.7
    return s / (np.max(np.abs(s)) + 1e-9) * soft


def cloth(dur=0.25):
    n = int(dur * SR)
    t = tsec(n)
    s = bp(rng.normal(0, 1, n), 700, 4000) * np.sin(np.pi * t / dur) ** 2
    s += np.sin(2 * np.pi * 110 * t) * env_exp(n, 0.05) * 0.5 * (t > dur * 0.6)
    return s / (np.max(np.abs(s)) + 1e-9)


def whoosh(dur, f0=300, f1=1800):
    n = int(dur * SR)
    t = tsec(n)
    x = rng.normal(0, 1, n)
    out = np.zeros(n)
    blk = int(0.02 * SR)
    for i in range(0, n, blk):
        u = i / n
        fc = f0 * (f1 / f0) ** u
        seg = bp(x[max(0, i - 2 * blk):i + blk], fc * 0.7, min(fc * 1.4, 20000))
        out[i:i + blk] = seg[-min(blk, n - i):]
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5 * (0.4 + 0.6 * t / dur)
    s = out * e
    return s / (np.max(np.abs(s)) + 1e-9)


def splash_snd(size=1.0):
    dur = 1.6 * size + 0.4
    n = int(dur * SR)
    t = tsec(n)
    s = lp(rng.normal(0, 1, n), 3500) * env_exp(n, 0.18 * size) * 1.0
    s += hp(rng.normal(0, 1, n), 2500) * env_exp(n, 0.35 * size) * 0.35
    s += np.sin(2 * np.pi * 70 * t) * env_exp(n, 0.07) * 0.9 * size
    for _ in range(int(40 * size)):
        st = rng.uniform(0.03, dur * 0.7)
        ln = rng.uniform(0.015, 0.05)
        f = rng.uniform(450, 1600)
        m = int(ln * SR)
        tt = tsec(m)
        bub = np.sin(2 * np.pi * (f * tt + f * 2.5 * tt * tt / ln)) * np.sin(np.pi * tt / ln)
        i = int(st * SR)
        s[i:i + m] += bub[:max(0, min(m, n - i))] * rng.uniform(0.05, 0.22) * math.exp(-st / (0.6 * size))
    a = np.minimum(1, t / 0.003)
    s *= a
    return s / (np.max(np.abs(s)) + 1e-9)


def thwang():
    n = int(0.9 * SR)
    t = tsec(n)
    f = 92 * (1 + 0.05 * np.sin(2 * np.pi * 9 * t))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.22)
    s += bp(rng.normal(0, 1, n), 300, 1500) * env_exp(n, 0.02) * 1.2
    s += np.sin(2 * np.pi * 184 * t) * env_exp(n, 0.1) * 0.3
    return s / (np.max(np.abs(s)) + 1e-9)


def rumble(dur):
    n = int(dur * SR)
    t = tsec(n)
    s = lp(rng.normal(0, 1, n), 120) * 3
    s *= 0.7 + 0.3 * np.sin(2 * np.pi * 11 * t)
    cr_f = 260 + 40 * np.sin(2 * np.pi * 1.3 * t) + 25 * np.sin(2 * np.pi * 7.7 * t)
    creak = np.sin(2 * np.pi * np.cumsum(cr_f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 23 * t)) ** 3 * 0.35
    s = s / (np.max(np.abs(s)) + 1e-9) + bp(creak, 150, 1200)
    e = np.minimum(1, t / 0.15) * np.minimum(1, (dur - t) / 0.25)
    s *= e
    return s / (np.max(np.abs(s)) + 1e-9)


def rattle(dur):
    n = int(dur * SR)
    out = np.zeros(n + SR // 4)
    t = 0.0
    while t < dur:
        amp = min(1, t / (dur * 0.4))
        c = clack(rng.uniform(0.7, 1.3), 0.3) * rng.uniform(0.25, 0.6) * amp
        i = int(t * SR)
        out[i:i + len(c)] += c[:len(out) - i]
        t += rng.uniform(0.025, 0.06)
    grind = lp(rng.normal(0, 1, len(out)), 220)
    grind = grind / (np.max(np.abs(grind)) + 1e-9) * np.minimum(1, np.arange(len(out)) / (dur * 0.5 * SR)) * 0.5
    grind[n:] *= np.linspace(1, 0, len(out) - n)
    s = out + grind
    return s / (np.max(np.abs(s)) + 1e-9)


def swell(dur=1.6):
    n = int(dur * SR)
    t = tsec(n)
    s = lp(rng.normal(0, 1, n), 600)
    s += np.sin(2 * np.pi * 49 * t) * 0.8
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return s * e / (np.max(np.abs(s * e)) + 1e-9)


def water_bed(dur, level=1.0):
    n = int(dur * SR) + SR
    t = tsec(n)
    s = lp(rng.normal(0, 1, n), 700)
    am = 0.55 + 0.25 * np.sin(2 * np.pi * 0.31 * t) + 0.2 * np.sin(2 * np.pi * 0.73 * t + 1)
    s = s * am
    return s / (np.max(np.abs(s)) + 1e-9) * level


# ---------------------------------------------------------------- builds
def build_v2():
    sys.path.insert(0, '.')
    import v2_steady as v
    ev = json.load(open('out/v2_events.json'))
    m = Mix(v.DUR)
    rt = room(v.DUR)
    m.add(rt, 0, 1.0)
    # day-counter ticks (rate limited), quiet
    last, prev_d = -1, 1
    for k in range(int(v.DUR * 1000)):
        t = k / 1000
        if t > 10.9:
            break
        d = v.day_at(t)
        if d != prev_d and t - last > 0.045:
            m.add(tick(), t, 0.05, 0.0)
            last = t
        prev_d = d
    # placements (right side)
    for t, n in ev['place'][:-1]:
        for q in range(n):
            m.add(clack(rng.uniform(0.9, 1.15)), t + q * 0.03, 0.42 if q == 0 else 0.2, 0.35)
    for cy in v.CYCLES:
        m.add(scrape(0.12), cy['s'] + 0.28 * cy['d'], 0.1 if cy['d'] > 0.5 else 0.05, 0.25)
    tr = ev['red']
    m.add(clack(0.85, 1.6), tr, 0.7, 0.35)
    m.add(boom(), tr, 0.4, 0.1)
    # right figure steps back at the end
    for q in range(3):
        m.add(step(), tr + 0.45 + q * 0.22, 0.18, 0.3)
    # left figure: sits, then keeps getting up and sitting back down
    m.add(cloth(0.3), ev['sit1'], 0.2, -0.4)
    for t0 in ev['tries']:
        m.add(cloth(0.25), t0 + 0.02, 0.18, -0.4)
        m.add(step(0.7), t0 + 0.3, 0.14, -0.4)
        m.add(cloth(0.3), t0 + 1.7, 0.18, -0.4)
    # end card
    m.add(swell(2.2), ev['end_card'] - 0.4, 0.22, 0)
    m.write('out/v2_audio.wav')


def build_v3():
    ev = json.load(open('out/v3_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    wb = water_bed(D)
    # water bed louder after the splash
    gain = np.full(len(wb), 0.05)
    ie = int(ev['entry'] * SR)
    gain[ie:] = 0.05 + 0.12 * np.exp(-np.arange(len(wb) - ie) / (2.2 * SR))
    m.add(wb * gain, 0, 1.0)
    # right figure: prayer movements, walk, jump, splash, surface
    for t in (0.6, 1.45, 2.05, 2.45, 2.75, 3.05, 3.4, 3.7):
        m.add(cloth(0.22), t, 0.13, 0.4)
    w0, w1 = ev['r_walk']
    t = w0 + 0.1
    while t < w1:
        m.add(step(), t, 0.22, 0.35)
        t += 0.3
    m.add(thwang(), ev['jump'], 0.4, 0.25)
    m.add(whoosh(ev['entry'] - ev['jump'] - 0.05, 250, 1400), ev['jump'] + 0.05, 0.22, 0.05)
    m.add(lp(np.tanh(splash_snd(1.0) * 2.5), 9000), ev['entry'], 1.1, 0.0)
    m.add(splash_snd(0.35), ev['surface'] + 0.1, 0.35, 0.05)
    # left figure: steps, recoils, tower rises
    for a, b in ev['l_walks']:
        t = a + 0.12
        while t < b - 0.05:
            m.add(step(0.8), t, 0.2, -0.4)
            t += 0.34
    for t in ev['recoils']:
        m.add(step(), t + 0.03, 0.22, -0.4)
        m.add(step(), t + 0.17, 0.16, -0.4)
    rises = [(3.0, 3.7), (6.9, 7.7), (10.1, 11.0)]
    for i, (a, b) in enumerate(rises):
        m.add(rumble(b - a + 0.2), a, 0.17 + 0.05 * i, -0.45)
    m.add(swell(2.2), ev['end_card'] - 0.4, 0.22, 0)
    m.drive = 2.2
    m.write('out/v3_audio.wav', peak_db=-3.0)

def beep_pattern(dur):
    n = int(dur * SR)
    out = np.zeros(n)
    t = 0.0
    k = 0
    while t < dur:
        f = 1320 if k % 2 else 990
        m = int(0.075 * SR)
        tt = tsec(m)
        b = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt)) * np.minimum(1, tt / 0.004) * np.minimum(1, (0.075 - tt) / 0.006)
        i = int(t * SR)
        out[i:i + m] += b[:max(0, n - i)]
        t += 0.11 if k % 4 != 3 else 0.32
        k += 1
    return out / (np.max(np.abs(out)) + 1e-9)


def pluck(f=620):
    n = int(0.5 * SR)
    t = tsec(n)
    s = np.sin(2 * np.pi * f * t) * env_exp(n, 0.09) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t) * env_exp(n, 0.05)
    s += bp(rng.normal(0, 1, n), 2000, 7000) * env_exp(n, 0.004) * 0.8
    return s / (np.max(np.abs(s)) + 1e-9)


def water_run(dur):
    n = int(dur * SR)
    t = tsec(n)
    s = bp(rng.normal(0, 1, n), 700, 5200) * (0.8 + 0.2 * np.sin(2 * np.pi * 13 * t))
    e = np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.12)
    return s * e / (np.max(np.abs(s)) + 1e-9)


def chirp():
    n = int(rng.uniform(0.06, 0.14) * SR)
    t = tsec(n)
    f0 = rng.uniform(2800, 4200)
    f = f0 + rng.uniform(-900, 900) * t / t[-1] + 300 * np.sin(2 * np.pi * rng.uniform(25, 45) * t)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / t[-1])
    return s


def crickets(dur):
    n = int(dur * SR)
    t = tsec(n)
    car = np.sin(2 * np.pi * 4300 * t)
    gate = (np.sin(2 * np.pi * 28 * t) > 0.3) * (np.sin(2 * np.pi * 1.6 * t) > -0.2)
    s = car * lp(gate.astype(float), 300)
    return s / (np.max(np.abs(s)) + 1e-9)


def city(dur):
    n = int(dur * SR)
    s = lp(rng.normal(0, 1, n), 400) + 0.3 * bp(rng.normal(0, 1, n), 800, 2500)
    return s / (np.max(np.abs(s)) + 1e-9)


def wind(dur, level=1.0):
    n = int(dur * SR)
    t = tsec(n)
    x = rng.normal(0, 1, n)
    a = bp(x, 200, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.17 * t) * np.sin(2 * np.pi * 0.41 * t + 1))
    b = bp(x, 1200, 3000) * 0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.23 * t + 2))
    s = a + b
    return s / (np.max(np.abs(s)) + 1e-9) * level


def flutter(dur):
    n = int(dur * SR)
    t = tsec(n)
    s = bp(rng.normal(0, 1, n), 300, 2400) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 9 * t + 3 * np.sin(2 * np.pi * 0.7 * t))))
    s = lp(s, 2000)
    return s / (np.max(np.abs(s)) + 1e-9)


def build_v1():
    ev = json.load(open('out/v1_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    cr = crickets(9.0) * np.minimum(1, np.arange(int(9.0 * SR)) / (0.5 * SR))
    cr[-int(1.0 * SR):] *= np.linspace(1, 0, int(1.0 * SR))
    m.add(cr, 0, 0.025, 0)
    for a, b in ev['ring_top']:
        m.add(beep_pattern(b - a), a, 0.07, -0.3)
        m.add(step(), b, 0.25, -0.3)
    for i, (a, b) in enumerate(ev['ring_bot']):
        m.add(beep_pattern(b - a), a + 0.01, 0.07, 0.3)
        if i < 3:
            m.add(step(), b, 0.28, 0.3)
    m.add(cloth(0.4), 8.18, 0.25, 0.3)
    # top: sit up, scoot, stand, walk, wudu, walk, pray
    for t in (1.7, 2.7, 3.05):
        m.add(cloth(0.3), t, 0.16, -0.3)
    for t in (3.4, 3.62, 3.82, 5.12, 5.3, 5.47):
        m.add(step(0.8), t, 0.18, -0.3)
    a, b = ev['water']
    m.add(water_run(b - a), a, 0.14, -0.2)
    for t in (5.75, 6.55, 7.15, 7.42, 7.66, 7.92, 8.4):
        m.add(cloth(0.22), t - 0.1, 0.12, -0.25)
    for t in (7.15, 7.66):
        m.add(step(0.6), t, 0.12, -0.25)
    for k, t in enumerate(ev['knots']):
        m.add(pluck(560 + 120 * k), t, 0.35, -0.2)
    # dawn birds (top room, later)
    t = 6.3
    while t < 8.8:
        m.add(chirp(), t, 0.03, -0.4)
        t += rng.uniform(0.12, 0.5)
    # street
    x0 = ev['xfade'][0]
    cty = city(D - x0)
    cty *= np.minimum(1, np.arange(len(cty)) / (0.8 * SR))
    m.add(cty, x0, 0.06, 0)
    t = x0 + 0.3
    while t < D:
        m.add(step(0.9), t, 0.15, -0.3)
        t += 0.36
    t = x0 + 0.4
    while t < D:
        m.add(scrape(0.35), t, 0.06, 0.3)
        t += 0.95
    m.add(swell(2.2), ev['end_card'] - 0.4, 0.2, 0)
    m.drive = 2.0
    m.write('out/v1_audio.wav', peak_db=-2.0)


def build_v4():
    ev = json.load(open('out/v4_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    wd = wind(D)
    lvl = np.full(len(wd), 0.06)
    z0 = int(ev['zoom'][0] * SR)
    lvl[z0:] = np.minimum(0.14, 0.06 + np.arange(len(wd) - z0) / SR * 0.05)
    m.add(wd * lvl, 0, 1.0)
    a, b = ev['walk']
    t = a + 0.1
    while t < b:
        m.add(step(0.8), t, 0.2, -0.2)
        t += 0.28
    for (t0, t1, t2) in ev['segs'] + [(ev['last'][0], ev['last'][1], ev['ondome'])]:
        for i in range(3):
            tt = t0 + (i + 0.5) / 3 * (t1 - t0)
            m.add(scrape(0.14), tt, 0.16, -0.1)
            m.add(step(0.6), tt + 0.02, 0.1, -0.1)
        m.add(step(1.0), t2 - 0.05, 0.24, -0.1)
    t = ev['ondome']
    while t < ev['crest']:
        m.add(step(0.8), t, 0.18, 0)
        t += 0.3
    m.add(cloth(0.3), ev['crest'] + 0.1, 0.18, 0)
    m.add(clack(0.6, 2.0), ev['stab'], 0.4, 0.05)
    m.add(flutter(D - ev['stab']), ev['stab'], 0.035, 0.1)
    m.add(boom(), ev['zoom'][0] + 0.25, 0.3, 0)
    m.add(swell(2.4), ev['end_card'] - 0.4, 0.22, 0)
    m.drive = 1.8
    m.write('out/v4_audio.wav', peak_db=-2.5)

def applause(dur):
    n = int(dur * SR)
    out = np.zeros(n + SR // 5)
    t = 0.0
    while t < dur:
        m = int(0.03 * SR)
        cl = bp(rng.normal(0, 1, m), rng.uniform(900, 1500), rng.uniform(3000, 5000)) * env_exp(m, 0.006)
        i = int(t * SR)
        out[i:i + m] += cl * rng.uniform(0.3, 1.0)
        t += rng.exponential(0.0045)
    out = out[:n]
    tt = tsec(n)
    out *= np.minimum(1, tt / 0.25) * np.minimum(1, (dur - tt) / 0.4)
    return out / (np.max(np.abs(out)) + 1e-9)


def tape_rewind(dur):
    n = int(dur * SR)
    t = tsec(n)
    f = 2400 * (1 - 0.7 * t / dur)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + bp(rng.normal(0, 1, n), 1500, 6000)
    s *= np.sin(np.pi * t / dur) * (0.6 + 0.4 * np.sin(2 * np.pi * 31 * t))
    return s / (np.max(np.abs(s)) + 1e-9)


def knock():
    n = int(0.12 * SR)
    t = tsec(n)
    s = np.sin(2 * np.pi * 420 * t) * env_exp(n, 0.02) + bp(rng.normal(0, 1, n), 1000, 4000) * env_exp(n, 0.004)
    return s / (np.max(np.abs(s)) + 1e-9)


def page():
    n = int(0.25 * SR)
    t = tsec(n)
    s = bp(rng.normal(0, 1, n), 1500, 7000) * np.sin(np.pi * t / 0.25) ** 3
    return s / (np.max(np.abs(s)) + 1e-9)


def sparkle(dur):
    n = int(dur * SR)
    out = np.zeros(n + SR // 4)
    t = 0.0
    while t < dur:
        m = int(0.18 * SR)
        tt = tsec(m)
        fr = rng.uniform(3200, 5200)
        ping = np.sin(2 * np.pi * fr * tt) * env_exp(m, 0.04)
        i = int(t * SR)
        out[i:i + m] += ping * rng.uniform(0.3, 1.0)
        t += rng.uniform(0.15, 0.5)
    return out[:n] / (np.max(np.abs(out)) + 1e-9)


def build_v5():
    ev = json.load(open('out/v5_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    m.add(wind(D) * 0.07, 0, 1.0)
    sp = sparkle(ev['last_fall'] + 0.8)
    m.add(sp, 0, 0.035, 0.35)
    falls = ev['falls']
    # running feet: a stream per runner until they go over the edge
    for k, tf in enumerate(falls + [ev['stop']]):
        t = 0.05 + k * 0.07
        while t < tf - 0.05:
            m.add(step(0.9), t, 0.07, -0.2 + 0.05 * k)
            t += 0.43 + rng.uniform(-0.02, 0.02)
    for tf in falls:
        m.add(whoosh(0.7, 1400, 250), tf + 0.05, 0.16, 0.4)
    m.add(cloth(0.3), ev['stop'] + 0.3, 0.16, -0.3)
    m.add(cloth(0.35), ev['sit'] - 0.3, 0.18, -0.3)
    m.add(page(), ev['book'], 0.22, -0.3)
    t = ev['book'] + 2.5
    while t < D - 1:
        m.add(page(), t, 0.08, -0.3)
        t += rng.uniform(2.5, 3.5)
    m.add(swell(2.4), ev['end_card'] - 0.4, 0.22, 0)
    m.drive = 2.0
    m.write('out/v5_audio.wav', peak_db=-2.0)


def hall(dur):
    n = int(dur * SR)
    s = lp(rng.normal(0, 1, n), 300) + 0.15 * bp(rng.normal(0, 1, n), 400, 1600)
    return s / (np.max(np.abs(s)) + 1e-9)


def rows_move(t, m, n=6, gain=0.12):
    for k in range(n):
        m.add(cloth(rng.uniform(0.25, 0.4)), t + 0.22 + k * 0.03 + rng.uniform(0, 0.05), gain, rng.uniform(-0.5, 0.3))


def build_v6():
    ev = json.load(open('out/v6_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    r0, r1 = ev['rewind']
    m.add(hall(r0 + 0.1) * np.minimum(1, np.arange(int((r0 + 0.1) * SR)) / (0.3 * SR)), 0.0, 0.05, 0)
    rows_move(1.05, m)
    rows_move(2.05, m)
    m.add(tape_rewind(r1 - r0 + 0.1), r0, 0.35, 0)
    last = -1
    for i, t in enumerate(ev['inc']):
        if t - last > 0.055:
            m.add(knock(), t, 0.22 if i < 6 else 0.12, 0.25)
            last = t
    t = r1 + 0.6
    while t < ev['back']:
        m.add(page(), t, 0.06, -0.1)
        t += rng.uniform(0.6, 1.4)
    b = ev['back']
    m.add(hall(D - b), b, 0.05, 0)
    rows_move(b + 0.6, m)
    rows_move(b + 1.6, m)
    rows_move(b + 2.3, m, gain=0.16)
    m.add(swell(2.4), ev['end_card'] - 0.4, 0.2, 0)
    m.drive = 2.0
    m.write('out/v6_audio.wav', peak_db=-2.0)




def build_v7():
    ev = json.load(open('out/v7_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    last = -1
    for i, t in enumerate(ev['earth']):
        if t - last > 0.07:
            m.add(clack(rng.uniform(0.9, 1.15)), t, 0.3 if i < 10 else 0.18, -0.4)
            last = t
    last = -1
    for i, t in enumerate(ev['sky']):
        if t - last > 0.09:
            m.add(pluck(rng.uniform(1300, 1900)), t, 0.07, 0.4)
            last = t
    t = ev['t0'] + 0.3
    while t < ev['t1']:
        m.add(cloth(0.22), t, 0.06, 0.4)
        t += rng.uniform(0.5, 0.9)
    d0, d1 = ev['die']
    m.add(swell(1.8), d0 - 0.2, 0.18, 0)
    o0, o1 = ev['owner']
    t = o0 + 0.15
    while t < o1:
        m.add(step(0.8), t, 0.16, -0.5)
        t += 0.33
    m.add(scrape(0.4), o1 - 0.2, 0.12, -0.4)
    m.add(clack(0.6, 2.0), o1 + 0.38, 0.35, -0.4)
    m.add(swell(2.4), ev['end_card'] - 0.4, 0.2, 0)
    m.drive = 2.0
    m.write('out/v7_audio.wav', peak_db=-2.0)


def build_v8():
    ev = json.load(open('out/v8_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    cr = crickets(ev['fajr'] + 0.6)
    m.add(cr, 0, 0.022, 0)
    t = 0.5
    while t < ev['fajr']:
        m.add(tick(), t, 0.035, 0)
        t += 0.5
    # top: walk, wudu, back to bed, lie down
    for t in (0.6, 0.85, 1.08):
        m.add(step(0.8), t, 0.16, -0.25)
    a, b = ev['water']
    m.add(water_run(b - a), a, 0.13, -0.2)
    for t in (2.6, 2.85, 3.1):
        m.add(step(0.8), t, 0.14, -0.25)
    m.add(cloth(0.35), 3.35, 0.16, -0.25)
    m.add(cloth(0.45), 4.6, 0.16, -0.25)
    m.add(cloth(0.4), 5.0, 0.12, -0.25)
    for k, t in enumerate(ev['check']):
        m.add(pluck(560 + 120 * k), t, 0.28, -0.2)
    # bottom: scrolling taps, phone drop
    t = 0.6
    while t < ev['t3']:
        m.add(tick(), t, 0.05, 0.3)
        t += rng.uniform(0.25, 0.9)
    m.add(step(0.6), ev['t3'] + 0.3, 0.2, 0.3)
    # fajr
    for a, b in ev['ring_top']:
        m.add(beep_pattern(b - a), a, 0.07, -0.3)
    m.add(cloth(0.4), ev['fajr'] + 0.35, 0.18, -0.3)
    for a, b in ev['ring_bot']:
        m.add(beep_pattern(b - a), a + 0.01, 0.07, 0.3)
        m.add(step(), b, 0.26, 0.3)
    t = ev['fajr'] + 0.4
    while t < D - 0.5:
        m.add(chirp(), t, 0.025, -0.3)
        t += rng.uniform(0.15, 0.6)
    m.add(swell(2.4), ev['end_card'] - 0.4, 0.2, 0)
    m.drive = 2.0
    m.write('out/v8_audio.wav', peak_db=-2.0)

def simmer(dur):
    n = int(dur * SR)
    s = lp(rng.normal(0, 1, n), 500) * 0.4
    out = s.copy()
    t = 0.0
    while t < dur:
        m = int(rng.uniform(0.02, 0.05) * SR)
        tt = tsec(m)
        fr = rng.uniform(250, 700)
        b = np.sin(2 * np.pi * (fr * tt + fr * 3 * tt * tt / tt[-1])) * np.sin(np.pi * tt / tt[-1])
        i = int(t * SR)
        out[i:i + m] += b[:max(0, n - i)] * rng.uniform(0.2, 0.6)
        t += rng.uniform(0.04, 0.2)
    return out / (np.max(np.abs(out)) + 1e-9)


def power_down():
    n = int(0.9 * SR)
    t = tsec(n)
    f = 700 * np.exp(-t * 2.2) + 80
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.35)
    return s / (np.max(np.abs(s)) + 1e-9)


def build_v9():
    ev = json.load(open('out/v9_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    m.add(simmer(D), 0, 0.03, 0)
    t = 0.3
    while t < D:
        m.add(tick(), t, 0.03, rng.choice([-0.6, 0.6]))
        t += rng.uniform(0.3, 1.1)
    for side, key, pan in (('L', 'gifts_l', -0.4), ('R', 'gifts_r', 0.4)):
        for g in ev[key]:
            m.add(pluck(rng.uniform(1700, 2100)), g, 0.08, pan)
            m.add(clack(1.25, 0.4), g, 0.18, pan)
            m.add(cloth(0.2), g - 0.6, 0.07, pan)
    for g in ev['gifts_r']:
        m.add(pluck(rng.uniform(900, 1200)), g + 1.3, 0.06, 0.3)
    m.add(power_down(), ev['drained'] - 0.1, 0.18, -0.4)
    m.add(cloth(0.45), ev['drained'] + 0.2, 0.2, -0.4)
    m.add(swell(2.4), ev['end_card'] - 0.4, 0.2, 0)
    m.drive = 2.0
    m.write('out/v9_audio.wav', peak_db=-2.0)

def thump(f0=110, dec=0.06, click=0.4):
    n = int(0.25 * SR)
    t = tsec(n)
    s = np.sin(2 * np.pi * f0 * t * (1 + 0.3 * np.exp(-t / 0.02))) * env_exp(n, dec)
    s += bp(rng.normal(0, 1, n), 800, 3000) * env_exp(n, 0.005) * click
    return s / (np.max(np.abs(s)) + 1e-9)


def build_v10():
    ev = json.load(open('out/v10_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    m.add(whoosh(1.5, 300, 1600), 0.05, 0.12, -0.2)
    for k, t in enumerate(ev['top']):
        m.add(thump(95, 0.09 - 0.015 * k, 0.5), t, [0.6, 0.3, 0.16, 0.08][k], -0.25)
    for t in ev['bot']:
        m.add(thump(150, 0.035, 0.6), t, 0.3, 0.25)
    for t in ev['months']:
        m.add(tick(), t, 0.14, 0)
    m.add(pluck(660), ev['arrive'], 0.35, 0.2)
    m.add(pluck(990), ev['arrive'] + 0.12, 0.22, 0.2)
    m.add(swell(2.4), ev['end_card'] - 0.4, 0.2, 0)
    m.drive = 2.8
    m.write('out/v10_audio.wav', peak_db=-2.0)

def twang():
    n = int(0.5 * SR)
    t = tsec(n)
    s = np.sin(2 * np.pi * 180 * t * (1 - 0.15 * t)) * env_exp(n, 0.12) + bp(rng.normal(0, 1, n), 200, 1200) * env_exp(n, 0.02)
    return s / (np.max(np.abs(s)) + 1e-9)


def thunk():
    n = int(0.3 * SR)
    t = tsec(n)
    s = np.sin(2 * np.pi * 140 * t) * env_exp(n, 0.05) + bp(rng.normal(0, 1, n), 300, 2500) * env_exp(n, 0.012) * 1.2
    return s / (np.max(np.abs(s)) + 1e-9)


def build_v11():
    ev = json.load(open('out/v11_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    m.add(twang(), 0.3, 0.3, -0.3)
    m.add(thunk(), ev['top_hit'], 0.45, -0.1)
    m.add(twang(), ev['shot'], 0.3, 0.1)
    for t in ev['hits']:
        m.add(clack(rng.uniform(0.6, 0.8), 1.2), t, 0.32, 0.15)
        m.add(scrape(0.18), t + 0.1, 0.1, 0.15)
    m.add(thunk(), ev['land'], 0.55, 0.15)
    m.add(swell(2.4), ev['end_card'] - 0.4, 0.2, 0)
    m.drive = 2.5
    m.write('out/v11_audio.wav', peak_db=-2.0)

def bang(pitch=1.0):
    n = int(0.35 * SR)
    t = tsec(n)
    s = np.sin(2 * np.pi * 1900 * pitch * t) * env_exp(n, 0.05) * 0.5 + np.sin(2 * np.pi * 2870 * pitch * t) * env_exp(n, 0.03) * 0.3
    s += bp(rng.normal(0, 1, n), 1500, 7000) * env_exp(n, 0.006) * 1.2
    s += np.sin(2 * np.pi * 120 * t) * env_exp(n, 0.04) * 0.8
    return s / (np.max(np.abs(s)) + 1e-9)


def creak_pull(dur=0.35):
    n = int(dur * SR)
    t = tsec(n)
    f = 400 + 900 * t / dur
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 45 * t))) * np.sin(np.pi * t / dur)
    s = bp(s + 0.3 * rng.normal(0, 1, n), 300, 3000)
    return s / (np.max(np.abs(s)) + 1e-9)


def build_v12():
    ev = json.load(open('out/v12_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    for i, t in enumerate(ev['top_hits']):
        m.add(bang(rng.uniform(0.85, 0.95)), t, 0.32, -0.3)
        if i % 4 >= 1:
            m.add(clack(0.5, 1.5), t + 0.01, 0.18, -0.3)
    for t in ev['bot_lifts']:
        m.add(creak_pull(0.3), t, 0.2, 0.3)
    for t in ev['bot_sets']:
        m.add(tick(), t, 0.15, 0.3)
    for t in ev['bot_hits']:
        m.add(bang(rng.uniform(1.05, 1.15)), t, 0.3, 0.3)
    m.add(swell(2.4), ev['end_card'] - 0.4, 0.2, 0)
    m.drive = 2.0
    m.write('out/v12_audio.wav', peak_db=-2.0)

def build_v13():
    ev = json.load(open('out/v13_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.008), 0, 1.0)
    n = int(D * SR)
    t = tsec(n)
    height = np.zeros(n)
    breath = np.zeros(n)
    for (a, b, kind) in ev['sched']:
        i0, i1 = int(a * SR), int(b * SR)
        u = np.linspace(0, 1, max(1, i1 - i0))
        uu = u * u * (3 - 2 * u)
        if kind == 'in':
            height[i0:i1] = uu
            breath[i0:i1] = np.sin(np.pi * u) ** 0.8
        elif kind == 'hold':
            height[i0:i1] = 1.0
        elif kind == 'out':
            height[i0:i1] = 1 - uu
            breath[i0:i1] = np.sin(np.pi * u) ** 0.8
    last = int(ev['sched'][-1][1] * SR)
    height[last:] = 0
    f0 = 220 * (2 ** (height * 7 / 12))
    ph = 2 * np.pi * np.cumsum(f0) / SR
    tone = (np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph))
    on = np.zeros(n)
    s0 = int(ev['sched'][0][0] * SR)
    on[s0:last] = 1
    on = lp(on, 4)
    tone *= on
    m.add(tone, 0, 0.05, 0)
    air = bp(rng.normal(0, 1, n), 400, 2400) * breath
    m.add(air, 0, 0.09, 0)
    for (a, b, kind) in ev['sched']:
        if kind in ('in', 'out'):
            m.add(pluck(660 if kind == 'in' else 495), a, 0.12, 0)
    m.add(swell(2.4), ev['end_card'] - 0.4, 0.18, 0)
    m.drive = 1.8
    m.write('out/v13_audio.wav', peak_db=-11.0)


def build_v14():
    ev = json.load(open('out/v14_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.008), 0, 1.0)
    notes = [440, 554, 659, 880]
    for k, t in enumerate(ev['sides']):
        m.add(pluck(notes[k]), t, 0.4, 0)
        m.add(pluck(notes[k] * 1.5), t + 0.03, 0.12, 0)
    n = int(D * SR)
    tt = tsec(n)
    pad = np.zeros(n)
    for f0 in (220, 330, 440):
        pad += np.sin(2 * np.pi * f0 * tt + rng.uniform(0, 6))
    env = np.clip((tt - ev['sides'][0]) / 1.0, 0, 1) * np.clip((ev['done'] + 0.8 - tt) / 1.0, 0, 1)
    m.add(lp(pad * env, 800), 0, 0.025, 0)
    m.add(pluck(1320), ev['done'], 0.25, 0)
    m.add(swell(2.4), ev['end_card'] - 0.4, 0.2, 0)
    m.drive = 2.0
    m.write('out/v14_audio.wav', peak_db=-2.0)




def build_v15():
    ev = json.load(open('out/v15_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    a, b = ev['wrap']
    m.add(cloth(0.45), a, 0.3, 0.3)
    m.add(whoosh(0.4, 600, 2400), a + 0.1, 0.12, 0.3)
    last = -1
    for i, t in enumerate(ev['bricks']):
        if t - last > 0.06:
            m.add(pluck(rng.choice([880, 990, 1175, 1320])), t, 0.16 if i < 10 else 0.09, 0.35)
            m.add(thump(90, 0.05, 0.3), t, 0.18 if i < 10 else 0.11, -0.35)
            last = t
    for t in ev['hesitate']:
        m.add(cloth(0.35), t, 0.14, -0.3)
    m.add(swell(2.0), ev['end_card'] - 0.4, 0.15, 0)
    m.drive = 2.0
    m.write('out/v15_audio.wav', peak_db=-2.0)


def spray():
    n = int(0.22 * SR)
    t = tsec(n)
    s = bp(rng.normal(0, 1, n), 3500, 11000)
    e = np.minimum(1, t / 0.008) * np.exp(-np.maximum(0, t - 0.05) / 0.06)
    return s * e / (np.max(np.abs(s * e)) + 1e-9)


def fire_bed(dur):
    n = int(dur * SR)
    roar = lp(rng.normal(0, 1, n), 380) * 0.7
    roar += bp(rng.normal(0, 1, n), 600, 2200) * 0.12
    out = roar
    t = 0.0
    while t < dur:
        i = int(t * SR)
        m = int(0.006 * SR)
        c = bp(rng.normal(0, 1, m), 1500, 7000) * env_exp(m, 0.0015)
        out[i:i + m] += c[:max(0, n - i)] * rng.uniform(0.6, 2.2)
        t += rng.exponential(0.05)
    return out / (np.max(np.abs(out)) + 1e-9)


def puff():
    n = int(0.38 * SR)
    t = tsec(n)
    s = lp(rng.normal(0, 1, n), 520)
    s += bp(rng.normal(0, 1, n), 500, 1400) * 0.25
    e = np.sin(np.pi * np.clip(t / 0.38, 0, 1)) ** 1.6
    return s * e / (np.max(np.abs(s * e)) + 1e-9)


def sizzle():
    n = int(0.2 * SR)
    t = tsec(n)
    s = bp(rng.normal(0, 1, n), 2500, 8000) * env_exp(n, 0.06)
    s += np.sin(2 * np.pi * 180 * t) * env_exp(n, 0.02) * 0.4
    return s / (np.max(np.abs(s)) + 1e-9)


def cough():
    out = np.zeros(int(0.5 * SR))
    for k, (t0, g) in enumerate([(0.0, 1.0), (0.2, 0.7)]):
        n = int(0.13 * SR)
        t = tsec(n)
        s = bp(rng.normal(0, 1, n), 350, 1900, 3) * np.minimum(1, t / 0.006) * env_exp(n, 0.04)
        s += np.sin(2 * np.pi * 150 * t) * env_exp(n, 0.03) * 0.3
        i = int(t0 * SR)
        out[i:i + n] += s * g
    return out / (np.max(np.abs(out)) + 1e-9)


def build_v16():
    ev = json.load(open('out/v16_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    m.add(fire_bed(D), 0, 0.07, 0.25)
    for p in ev['pumps']:
        m.add(puff(), p - 0.18, 0.16, 0.35)
    for s_ in ev['sprays']:
        m.add(spray(), s_, 0.22, 0.15)
        m.add(pluck(1760), s_ + ev['mist'] + 0.05, 0.07, -0.2)
        m.add(pluck(2349), s_ + ev['mist'] + 0.16, 0.05, -0.2)
    a, b = ev['toss']
    m.add(whoosh(b - a + 0.1, 500, 2200), a, 0.12, 0)
    m.add(cloth(0.2), b - 0.05, 0.25, -0.3)
    m.add(tick(), b, 0.18, -0.3)
    m.add(sparkle(0.6), 3.95, 0.05, -0.2)
    for t in ev['burns']:
        m.add(sizzle(), t, 0.16, -0.25)
    for k in range(4):
        m.add(thump(130, 0.03, 0.2), ev['pats'][0] + 0.03 + k * 0.165, 0.16, -0.3)
    m.add(cloth(0.5), ev['wave'][0], 0.18, -0.3)
    m.add(cloth(0.4), ev['wave'][0] + 0.35, 0.12, -0.3)
    for t in ev['flinch']:
        m.add(cloth(0.2), t, 0.16, -0.3)
    m.add(cough(), ev['cough'][0] + 0.05, 0.26, -0.3)
    m.add(cough(), ev['cough'][0] + 0.36, 0.18, -0.3)
    m.add(cloth(0.35), ev['stand'], 0.2, -0.2)
    w0, w1 = ev['walk']
    t = w0 + 0.1
    k = 0
    while t < w1:
        m.add(step(0.8), t, 0.14, -0.4 - 0.1 * (k % 2))
        m.add(step(0.7), t + 0.04, 0.10, -0.4)
        t += 0.31
        k += 1
    m.add(swell(2.0), ev['end_card'] - 0.4, 0.15, 0)
    m.drive = 2.0
    m.write('out/v16_audio.wav', peak_db=-5.0)


def build_v17():
    ev = json.load(open('out/v17_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    for t in ev['steps_child']:
        m.add(step(0.6), t, 0.10, 0.1)
    for k, t in enumerate(ev['steps_parents']):
        m.add(step(0.7), t, 0.12, -0.2)
        if t > 4.2 and k % 2 == 0:
            m.add(knock(), t + 0.02, 0.05, 0.25)
    a, b = ev['swing']
    m.add(whoosh(b - a, 400, 1600), a, 0.14, 0)
    m.add(cloth(0.3), a, 0.15, 0)
    m.add(cloth(0.25), ev['let_go'], 0.15, 0.2)
    t = ev['let_go'] + 0.5
    while t < ev['stop'] - 0.2:
        m.add(tick(), t, 0.05, 0.4)
        t += rng.uniform(0.18, 0.45)
    m.add(cloth(0.3), ev['stop'], 0.18, 0.4)
    m.add(cloth(0.35), ev['turn'], 0.16, 0.4)
    m.add(cloth(0.4), ev['join'] - 0.2, 0.2, 0)
    m.add(swell(2.0), ev['end_card'] - 0.4, 0.15, 0)
    m.drive = 2.0
    m.write('out/v17_audio.wav', peak_db=-4.0)


def build_v18():
    ev = json.load(open('out/v18_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    for k, t in enumerate(ev['rise']):
        f = [784, 988, 1175][k]
        m.add(whoosh(ev['rise_d'], 300, 1400), t, 0.08, -0.3 + 0.3 * k)
        m.add(pluck(f), t + ev['rise_d'] - 0.04, 0.2, -0.3 + 0.3 * k)
        m.add(pluck(f * 2), t + ev['rise_d'] + 0.06, 0.07, -0.3 + 0.3 * k)
    a, b = ev['dad_in']
    t = a + 0.12
    while t < b:
        m.add(step(0.8), t, 0.16, 0.5)
        t += 0.32
    m.add(cloth(0.3), ev['look'], 0.12, 0.5)
    for k in range(4):
        m.add(scrape(0.08), ev['scratch'] + 0.15 + k * 0.13, 0.06, 0.5)
    m.add(whoosh(0.22, 1500, 400), ev['drop'] - 0.22, 0.1, 0.5)
    m.add(clack(0.7, 1.4), ev['drop'], 0.32, 0.5)
    h0, h1 = ev['hop']
    m.add(cloth(0.2), h0, 0.14, 0.5)
    m.add(thump(120, 0.05, 0.3), h1, 0.22, 0.5)
    m.add(pluck(523), ev['win'], 0.14, 0.4)
    m.add(pluck(659), ev['win'] + 0.1, 0.14, 0.4)
    m.add(pluck(784), ev['win'] + 0.2, 0.16, 0.4)
    m.add(applause(D - ev['win']), ev['win'] + 0.05, 0.05, -0.1)
    m.add(swell(1.6), ev['end_card'] - 0.3, 0.13, 0)
    m.drive = 2.0
    m.write('out/v18_audio.wav', peak_db=-1.5)


def breath(dur=0.45, inhale=True):
    n = int(dur * SR)
    t = tsec(n)
    s = bp(rng.normal(0, 1, n), 500 if inhale else 300, 2600 if inhale else 1600)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** (1.2 if inhale else 0.8)
    return s * e / (np.max(np.abs(s * e)) + 1e-9)


def build_v19():
    ev = json.load(open('out/v19_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    for a, b in ev['reps']:
        mid = (a + b) / 2
        m.add(whoosh(mid - a, 250, 900), a, 0.08, -0.2)
        m.add(clack(0.55, 0.6), b, 0.12, -0.2)
    for a, b in ev['sips']:
        m.add(cloth(0.15), a, 0.06, -0.2)
    a, b = ev['pass_in']
    t = a + 0.1
    while t < b:
        m.add(step(0.7), t, 0.12, 0.4)
        t += 0.31
    bump = ev['bump']
    m.add(thump(95, 0.06, 0.5), bump, 0.3, 0.1)
    m.add(cloth(0.25), bump, 0.2, 0.1)
    m.add(clack(1.7, 0.4), bump + 0.3, 0.16, 0)
    m.add(splash_snd(0.25), bump + 0.05, 0.08, 0)
    r0, r1 = ev['rage']
    m.add(rumble(1.3), r0, 0.22, -0.2)
    d0, d1 = ev['drop']
    m.add(bang(0.6), d1, 0.42, -0.1)
    m.add(clack(0.5, 1.2), d1 + 0.12, 0.18, -0.1)
    s0, s1 = ev['shove']
    m.add(whoosh(s1 - s0 + 0.05, 300, 1400), s0, 0.18, 0.2)
    m.add(thump(80, 0.08, 0.6), ev['fall'][1], 0.36, 0.3)
    m.add(power_down(), 3.0, 0.12, -0.3)
    for k, b in enumerate(ev['breaths']):
        m.add(breath(0.24, True), b, 0.16, -0.1)
        m.add(breath(0.36, False), b + 0.24, 0.14, -0.1)
    for k, f in enumerate([523, 659, 784, 1047]):
        m.add(pluck(f), 3.55 + k * 0.28, 0.12, 0.1)
    m.add(cloth(0.3), ev['forgive'][0] + 0.2, 0.12, 0)
    m.add(swell(1.8), ev['end_card'] - 0.35, 0.14, 0)
    m.drive = 2.0
    m.write('out/v19_audio.wav', peak_db=-1.8)


def rain_bed(dur):
    n = int(dur * SR)
    s = bp(rng.normal(0, 1, n), 900, 9000) * 0.8 + lp(rng.normal(0, 1, n), 400) * 0.5
    out = s.copy()
    t = 0.0
    while t < dur:
        i = int(t * SR)
        m = int(0.01 * SR)
        d = bp(rng.normal(0, 1, m), 2000, 8000) * env_exp(m, 0.002)
        out[i:i + m] += d[:max(0, n - i)] * rng.uniform(0.5, 1.6)
        t += rng.exponential(0.012)
    return out / (np.max(np.abs(out)) + 1e-9)


def coin():
    n = int(0.35 * SR)
    t = tsec(n)
    f0 = rng.uniform(3200, 4200)
    s = sum(np.sin(2 * np.pi * f0 * r * t + rng.uniform(0, 6)) * env_exp(n, d) * g
            for r, d, g in ((1.0, 0.09, 1.0), (1.47, 0.06, 0.6), (2.09, 0.04, 0.4)))
    s += bp(rng.normal(0, 1, n), 3000, 9000) * env_exp(n, 0.003) * 0.8
    return s / (np.max(np.abs(s)) + 1e-9)


def build_v20():
    ev = json.load(open('out/v20_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.016), 0, 1.0)
    m.add(wind(D, 0.8), 0, 0.09, 0)
    m.add(crickets(1.6), 0.0, 0.05, 0)
    m.add(pluck(1047), 0.05, 0.12, 0.3)
    m.add(pluck(1319), 0.17, 0.1, 0.3)
    m.add(pluck(1568), 0.29, 0.08, 0.3)
    m.add(rumble(1.2), ev['flash2'], 0.22, 0.4)
    a, b = ev['cloud']
    m.add(rumble(1.6), a, 0.25, 0)
    m.add(boom(), ev['flash'] + 0.12, 0.42, -0.2)
    r0, r1 = ev['rain']
    bed = rain_bed(r1 - r0 + 0.8)
    nb = len(bed)
    env = np.minimum(1, np.arange(nb) / (0.3 * SR)) * np.clip((nb - np.arange(nb)) / (0.9 * SR), 0, 1)
    m.add(bed * env, r0, 0.32, 0)
    g0, g1 = ev['grow']
    t = g0
    k = 0
    notes = [784, 880, 988, 1175, 1319, 1568, 1760]
    while t < g1:
        m.add(pluck(notes[k % len(notes)]), t, 0.08, -0.4 + 0.8 * (k % 3) / 2)
        t += 0.32
        k += 1
    m.add(swell(2.0), ev['part'][0], 0.14, 0)
    m.add(cloth(0.4), ev['sujud'][0], 0.14, 0)
    m.drive = 2.0
    m.write('out/v20_audio.wav', peak_db=-2.0)


def build_v21():
    ev = json.load(open('out/v21_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    for (t, side) in ev['throws']:
        pan = -0.45 if side == 0 else 0.45
        m.add(whoosh(0.2, 500, 1800), t - 0.06, 0.07, pan)
        m.add(thump(100, 0.05, 0.5), t + ev['flight'], 0.24, 0)
        m.add(clack(0.6, 1.0), t + ev['flight'], 0.12, 0)
    m.add(simmer(ev['arg_end'] + 0.6), 0.3, 0.06, 0)
    n0 = ev['nights'][0]
    m.add(crickets(3.2), n0 - 0.2, 0.08, 0)
    a0, a1 = ev['pull']
    m.add(scrape(a1 - a0), a0, 0.2, -0.2)
    m.add(thump(120, 0.04, 0.4), a1 + 0.25, 0.18, -0.3)
    f = ev['fall']
    for k in range(14):
        m.add(clack(rng.uniform(0.5, 0.8), 1.0), f + 0.12 + k * 0.045, 0.1, rng.uniform(-0.5, 0.5))
    m.add(thump(80, 0.08, 0.5), f + 0.6, 0.2, 0)
    for up in (ev['a_up'], ev['b_up']):
        m.add(cloth(0.3), up[0], 0.12, 0)
    b0, b1 = ev['b_pull']
    m.add(scrape(b1 - b0), b0, 0.16, 0.2)
    s0, s1 = ev['step']
    m.add(step(0.7), s0 + 0.08, 0.1, -0.2)
    m.add(step(0.7), s0 + 0.12, 0.1, 0.2)
    m.add(cloth(0.5), ev['hug'] - 0.2, 0.2, 0)
    m.add(swell(2.2), ev['hug'] - 0.6, 0.18, 0)
    m.drive = 2.0
    m.write('out/v21_audio.wav', peak_db=-3.9)


def build_v22():
    ev = json.load(open('out/v22_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    for (a, b, r) in ev['gives']:
        m.add(rattle(0.22), a + (b - a) * 0.35, 0.14, -0.3)
        m.add(whoosh(ev['flight'], 600, 2400), b, 0.06, 0.2)
        for q in range(4):
            m.add(coin(), b + ev['flight'] + q * 0.03, 0.08, 0.5)
    p0, p1 = ev['peer']
    m.add(cloth(0.3), p0, 0.1, -0.3)
    m.add(step(0.6), ev['back'][0] + 0.05, 0.1, -0.3)
    m.add(step(0.6), ev['back'][0] + 0.25, 0.1, -0.3)
    f0, f1 = ev['fill']
    m.add(swell(2.2), f0 - 0.5, 0.2, 0)
    t = f0
    while t < f1 + 0.1:
        m.add(coin(), t, 0.05 + 0.04 * min(1, (t - f0) / 0.4), rng.uniform(-0.3, 0.3))
        t += rng.uniform(0.018, 0.045)
    m.add(cloth(0.35), ev['dua'][0], 0.12, -0.3)
    m.drive = 2.0
    m.write('out/v22_audio.wav', peak_db=-5.6)


def build_v23():
    ev = json.load(open('out/v23_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    for k, t in enumerate(ev['bricks']):
        late = k / len(ev['bricks'])
        m.add(thump(rng.uniform(90, 120), 0.05, 0.5), t, 0.26 - 0.1 * late, rng.uniform(-0.1, 0.25))
        m.add(clack(rng.uniform(0.55, 0.75), 1.0), t, 0.1 - 0.04 * late, 0.1)
    m.add(cloth(0.35), ev['look'][0], 0.12, -0.3)
    m.add(cloth(0.5), ev['sit'][0], 0.18, -0.3)
    w0 = ev['sit'][0]
    wd = wind(ev['vanish'][1] - w0 + 0.6, 1.0)
    wd *= np.minimum(1, np.arange(len(wd)) / (0.6 * SR))
    wd[-int(0.6 * SR):] *= np.linspace(1, 0, int(0.6 * SR))
    m.add(wd, w0, 0.05, 0)
    m.add(cloth(0.45), ev['up'][0], 0.16, -0.3)
    m.add(cloth(0.35), ev['kneel'][0], 0.14, -0.3)
    m.add(cloth(0.4), ev['suj'][0], 0.16, -0.3)
    v0, v1 = ev['vanish']
    m.add(swell(2.4), v0 - 0.3, 0.22, 0)
    m.add(sparkle(1.6), v0 + 0.05, 0.1, 0.2)
    m.drive = 2.0
    m.write('out/v23_audio.wav', peak_db=-3.0)


def build_v24():
    ev = json.load(open('out/v24_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    for (a, b) in ev['pours']:
        m.add(water_run(b - a - 0.1), a + 0.1, 0.12, 0.1)
        m.add(clack(1.6, 0.4), b + 0.05, 0.05, 0.2)
    for w in ev['walks'] + [ev['back']]:
        if not w:
            continue
        t = w[0] + 0.05
        while t < w[1]:
            m.add(step(0.7), t, 0.12, -0.1)
            t += 0.21
    t = 0.3
    while t < D:
        m.add(tick(), t, 0.03, rng.uniform(0.2, 0.6))
        t += rng.uniform(0.35, 0.9)
    m.add(cloth(0.4), ev['sit'][0], 0.14, -0.4)
    f0, f1 = ev['fill']
    m.add(swell(2.4), f0 - 0.4, 0.2, -0.3)
    m.add(sparkle(1.4), f0, 0.08, -0.3)
    m.add(water_run(f1 - f0), f0 + 0.05, 0.08, -0.4)
    m.drive = 2.0
    m.write('out/v24_audio.wav', peak_db=-3.0)


def build_v25():
    ev = json.load(open('out/v25_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    a2 = ev['a2']
    r0, r1 = ev['rew']
    cr = crickets(ev['late'][0] + 0.3)
    cr[-int(0.4 * SR):] *= np.linspace(1, 0, int(0.4 * SR))
    m.add(cr, 0, 0.02, 0)
    for (ring, slap) in ev['snooze']:
        m.add(beep_pattern(slap - ring), ring, 0.07, -0.3)
        m.add(thump(140, 0.04, 0.6), slap, 0.2, -0.3)
        m.add(creak_pull(0.3), slap + 0.05, 0.05, 0)
    l0, l1 = ev['late']
    m.add(whoosh(l1 - l0, 1800, 300), l0, 0.06, 0)
    m.add(city(r0 - l1 + 0.2), l1, 0.04, 0)
    m.add(beep_pattern(0.35), ev['jolt'] - 0.3, 0.08, -0.3)
    m.add(cloth(0.5), ev['jolt'] + 0.05, 0.16, 0)
    m.add(creak_pull(0.45), ev['jolt'] + 0.1, 0.07, 0)
    m.add(tape_rewind(r1 - r0), r0, 0.09, 0)
    # act 2
    m.add(crickets(1.6), a2, 0.015, 0)
    m.add(beep_pattern(0.26), a2, 0.07, -0.3)
    m.add(thump(140, 0.04, 0.6), a2 + 0.26, 0.15, -0.3)
    m.add(cloth(0.4), a2 + 0.4, 0.14, 0)
    for k, tk in enumerate(ev['knots']):
        m.add(thwang(), tk, 0.16, -0.1 + 0.2 * k)
        m.add(pluck(560 + 120 * k), tk + 0.02, 0.2, 0)
    m.add(water_run(0.5), a2 + 1.95, 0.12, 0.1)
    for t in (a2 + 1.55, a2 + 1.7, a2 + 1.82, a2 + 2.55, a2 + 2.68):
        m.add(step(0.8), t, 0.14, 0)
    m.add(cloth(0.5), a2 + 3.2, 0.14, 0.2)
    t = a2 + 1.6
    while t < D - 0.5:
        m.add(chirp(), t, 0.025, -0.4)
        t += rng.uniform(0.2, 0.6)
    m.add(swell(2.2), ev['card'] - 0.5, 0.18, 0)
    m.drive = 2.0
    m.write('out/v25_audio.wav', peak_db=-3.0)


def build_v26():
    ev = json.load(open('out/v26_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    s0, s1 = ev['storm']
    cr = crickets(s1 + 0.4)
    cr[-int(0.8 * SR):] *= np.linspace(1, 0, int(0.8 * SR))
    m.add(cr, 0, 0.03, 0)
    p0, p1 = ev['part']
    wd = wind(p1 - s0 + 0.5, 1.0)
    n = len(wd)
    env = np.minimum(1, np.arange(n) / (1.0 * SR)) * np.minimum(1, (n - np.arange(n)) / (1.2 * SR))
    m.add(wd * env, s0, 0.1, 0)
    r0, r1 = ev['rain']
    rb = rain_bed(r1 - r0 + 0.6)
    n = len(rb)
    rb *= (np.minimum(1, np.arange(n) / (0.8 * SR)) * np.minimum(1, (n - np.arange(n)) / (1.0 * SR)))[:, None] if rb.ndim == 2 else np.minimum(1, np.arange(n) / (0.8 * SR)) * np.minimum(1, (n - np.arange(n)) / (1.0 * SR))
    m.add(rb, r0, 0.16, 0)
    m.add(boom(), ev['flash'], 0.3, 0.2)
    m.add(boom(), ev['flash'] + 1.9, 0.14, -0.3)
    m.add(puff(), ev['out'] - 0.05, 0.18, 0.35)
    m.add(cloth(0.4), ev['shield'][0], 0.12, 0.35)
    m.add(cloth(0.45), ev['rise'][0], 0.12, -0.3)
    m.add(clack(0.9, 0.5), ev['pick'][0] + 0.3, 0.08, -0.4)
    w0, w1 = ev['walk']
    t = w0 + 0.08
    while t < w1:
        m.add(step(0.9), t, 0.16, -0.2 + 0.4 * (t - w0) / (w1 - w0))
        m.add(splash_snd(0.3), t + 0.01, 0.03, 0)
        t += 0.34
    m.add(cloth(0.4), ev['kneel'][0], 0.12, 0.1)
    m.add(sparkle(0.6), ev['light'] - 0.05, 0.1, 0.2)
    m.add(pluck(660), ev['light'], 0.2, 0.2)
    m.add(swell(2.2), ev['light'] - 0.4, 0.14, 0)
    cr2 = crickets(D - p1)
    cr2 *= np.minimum(1, np.arange(len(cr2)) / (0.8 * SR))
    m.add(cr2, p1, 0.025, 0)
    m.add(pluck(880), ev['tick'], 0.18, 0.3)
    m.add(swell(2.0), ev['card'] - 0.4, 0.14, 0)
    m.drive = 2.0
    m.write('out/v26_audio.wav', peak_db=-3.0)


def build_v27():
    ev = json.load(open('out/v27_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    for a, b in (ev['place_a'], ev['place_b']):
        m.add(cloth(0.3), a, 0.1, 0)
        m.add(clack(0.8, 1.0), b - 0.05, 0.14, 0)
    for (t0, kind) in ev['throws']:
        m.add(whoosh(0.3, 600, 2000), t0, 0.06, 0.6)
        hit = t0 + ev['tfly']
        if kind == 'wall':
            m.add(thump(90, 0.04, 0.8), hit, 0.2, 0.3)
            m.add(clack(0.5, 1.0), hit, 0.12, 0.3)
            m.add(rattle(0.3), hit + 0.02, 0.05, 0.3)
        elif kind == 'her':
            m.add(thump(120, 0.04, 0.5), hit, 0.18, 0.2)
        else:
            m.add(clack(0.6, 1.0), hit, 0.12, 0.25)
            m.add(rattle(0.25), hit + 0.02, 0.04, 0.25)
    for k, tk in ev['knock'].items():
        m.add(clack(0.9, 1.0), tk + 0.1, 0.12, 0.35)
        m.add(clack(0.7, 1.0), tk + 0.45, 0.1, 0.4)
    h0, h1 = ev['hands']
    m.add(cloth(0.5), h0, 0.12, 0.1)
    w0, w1 = ev['walk']
    t = w0 + 0.1
    while t < w1:
        m.add(step(0.8), t, 0.14, -0.2)
        t += 0.3
    m.add(cloth(0.4), ev['lower'][0], 0.12, 0)
    for g in ev['give']:
        m.add(clack(rng.uniform(0.9, 1.2), 0.8), g, 0.07, 0.3)
    m.add(swell(2.2), ev['stand'][0] - 0.4, 0.16, 0)
    m.add(pluck(880), ev['tick'], 0.18, 0.2)
    m.add(pluck(660), ev['tick'] + 0.06, 0.12, -0.2)
    m.drive = 2.0
    m.write('out/v27_audio.wav', peak_db=-3.0)


def ringtone(dur):
    n = int(dur * SR)
    out = np.zeros(n)
    t = 0.0
    while t < dur:
        for k, f in enumerate((880, 1175, 1480)):
            m = int(0.09 * SR)
            tt = tsec(m)
            b = np.sin(2 * np.pi * f * tt) * np.minimum(1, tt / 0.004) * env_exp(m, 0.06)
            i = int((t + k * 0.1) * SR)
            if i + m < n:
                out[i:i + m] += b
        t += 0.55
    return out / (np.max(np.abs(out)) + 1e-9)


def build_v28():
    ev = json.load(open('out/v28_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    x0, x1 = ev['x']
    cr = crickets(x1 + 0.2)
    cr[-int(0.5 * SR):] *= np.linspace(1, 0, int(0.5 * SR))
    m.add(cr, 0, 0.02, 0)
    for which, pan in (('top', -0.3), ('bot', 0.3)):
        rings = ev['rings'][which]
        for k, (a, b) in enumerate(rings):
            if which == 'bot' and k == 2:
                m.add(ringtone(b - a), a, 0.1, pan)
            else:
                m.add(beep_pattern(b - a), a, 0.07, pan)
                m.add(thump(140, 0.04, 0.6), b, 0.16, pan)
        for k, tk in enumerate(ev['knots'][which]):
            m.add(thwang(), tk, 0.14, pan)
            m.add(pluck(560 + 120 * k), tk + 0.02, 0.18, pan)
    off = ev['off_b']
    for base, pan in ((0.0, -0.3), (off, 0.3)):
        m.add(cloth(0.4), base + 0.4, 0.12, pan)
        m.add(water_run(0.5), base + 1.95, 0.1, pan)
        for t in (base + 1.55, base + 1.7, base + 1.82):
            m.add(step(0.8), t, 0.1, pan)
    for (a, b), pan in ((ev['leave_a'], -0.3), (ev['leave_b'], 0.3)):
        t = a + 0.05
        while t < b:
            m.add(step(0.8), t, 0.1, pan)
            t += 0.3
    w0, w1 = ev['walk']
    m.add(city(D - x0), x0, 0.04, 0)
    t = w0
    while t < w1:
        m.add(step(0.9), t, 0.14, -0.1)
        m.add(step(0.85), t + 0.17, 0.12, 0.1)
        t += 0.36
    m.add(thwang(), ev['salah'], 0.14, 0.2)
    m.add(pluck(800), ev['salah'] + 0.02, 0.2, 0.2)
    m.add(swell(2.2), ev['salah'] - 0.2, 0.16, 0.2)
    m.add(pluck(880), ev['tick'], 0.16, 0.25)
    m.add(swell(2.0), ev['card'] - 0.3, 0.12, 0)
    m.drive = 2.0
    m.write('out/v28_audio.wav', peak_db=-3.0)


def build_v29():
    ev = json.load(open('out/v29_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    wb = water_bed(D, 1.0)
    m.add(wb, 0, 0.07, 0.05)
    notes = [523, 587, 659, 698, 784]
    for k, (a, b) in enumerate(ev['cycles']):
        m.add(pluck(notes[k]), max(0.02, a - 0.04), 0.13, 0)
    # right man: into the river and out, five times
    for k in range(5):
        w0, w1 = ev['r_walks'][k]
        t = w0 + 0.06
        n = 0
        while t < w1 - 0.05:
            u = (t - w0) / (w1 - w0)
            if u < 0.45:
                m.add(step(0.8), t, 0.12, 0.4)
            else:
                m.add(splash_snd(0.12), t, 0.05, 0.25)
            t += 0.17
        m.add(lp(splash_snd(0.55), 6000), ev['dip_down'][k] - 0.04, 0.26, 0.1)
        m.add(splash_snd(0.3), ev['dip_up'][k], 0.14, 0.15)
        m.add(sparkle(0.5), ev['dip_up'][k] + 0.05, 0.03, 0.2)
        o0, o1 = ev['r_outs'][k]
        t = o0 + 0.05
        while t < o1 - 0.04:
            u = (t - o0) / (o1 - o0)
            if u < 0.55:
                m.add(splash_snd(0.12), t, 0.05, 0.3)
            else:
                m.add(step(0.75), t, 0.11, 0.4)
            t += 0.17
    # dirt landing on both, same moments
    for t in ev['lands']:
        m.add(thump(rng.uniform(70, 90), 0.035, 0.25), t, 0.16, -0.35)
        m.add(thump(rng.uniform(70, 90), 0.035, 0.25), t + 0.005, 0.16, 0.35)
    # left man: scrubbing
    for a, b in ev['scrubs']:
        t = a
        while t < b:
            m.add(scrape(0.16), t, 0.06, -0.4)
            t += rng.uniform(0.17, 0.23)
    mg = ev['mag']
    w0, w1 = mg['walk']
    for t in (w0 + 0.06, w0 + 0.2, w0 + 0.33):
        m.add(step(0.8), t, 0.13, -0.3)
    m.add(cloth(0.3), mg['hands'][0], 0.1, -0.3)
    r0, r1 = mg['recoil']
    m.add(step(1.0), r0 + 0.02, 0.18, -0.3)
    b0, b1 = mg['back']
    for t in (b0 + 0.08, b0 + 0.24, b0 + 0.4):
        m.add(step(0.7), t, 0.1, -0.35)
    s0, s1 = ev['sit']
    m.add(cloth(0.45), s0, 0.16, -0.4)
    m.add(thump(75, 0.05, 0.2), s1 - 0.05, 0.12, -0.4)
    m.add(swell(2.2), ev['e1'] - 0.35, 0.18, 0)
    m.add(pluck(880), ev['e2'], 0.1, 0)
    m.drive = 2.0
    m.write('out/v29_audio.wav', peak_db=-3.0)


def build_v30():
    ev = json.load(open('out/v30_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    per = ev['rung_period'] / 2
    for i, (a, b) in enumerate(ev['climbs']):
        t = a + 0.05
        while t < b - 0.03:
            m.add(clack(rng.uniform(1.15, 1.35), 0.5), t, 0.07, 0.35)
            m.add(clack(rng.uniform(0.8, 0.95), 0.4), t + per * 0.5, 0.04, 0.35)
            if i == 0:
                m.add(clack(rng.uniform(1.15, 1.35), 0.5), t + 0.01, 0.07, -0.35)
                m.add(clack(rng.uniform(0.8, 0.95), 0.4), t + per * 0.5 + 0.01, 0.04, -0.35)
            t += per
    for k, (s0, c0) in enumerate(zip(ev['slips'], ev['catches'])):
        pans = (0.35, -0.35) if k == 0 else (0.35,)
        for pan in pans:
            m.add(scrape(0.22), s0, 0.16, pan)
            m.add(whoosh(0.22, 900, 300), s0, 0.07, pan)
            m.add(thump(120, 0.05, 0.6), c0, 0.24, pan)
            m.add(clack(0.9, 1.0), c0 + 0.01, 0.12, pan)
    for (a, b) in ev['bows']:
        m.add(cloth(0.35), a + 0.02, 0.09, 0.35)
    m.add(cloth(0.25), ev['a_let'] - 0.05, 0.1, -0.35)
    m.add(whoosh(ev['a_land'] - ev['a_let'], 500, 160), ev['a_let'], 0.12, -0.35)
    m.add(thump(70, 0.09, 0.8), ev['a_land'], 0.42, -0.3)
    m.add(boom(), ev['a_land'], 0.08, -0.3)
    m.add(cloth(0.45), ev['a_sit'][0], 0.15, -0.35)
    for r0, r1 in ev['reaches']:
        m.add(cloth(0.3), r0, 0.08, -0.35)
        m.add(cloth(0.35), r1, 0.1, -0.35)
    m.add(swell(2.4), ev['top'] - 1.2, 0.14, 0.3)
    m.add(sparkle(1.2), ev['top'] - 0.3, 0.05, 0.3)
    m.add(swell(2.0), ev['e1'] - 0.3, 0.14, 0)
    m.add(pluck(880), ev['e2'], 0.1, 0)
    m.drive = 2.0
    m.write('out/v30_audio.wav', peak_db=-3.0)


def leaves(dur):
    n = int(dur * SR)
    t = tsec(n)
    s = bp(rng.normal(0, 1, n), 1800, 6500)
    am = 0.5 + 0.3 * np.sin(2 * np.pi * 0.7 * t) + 0.2 * np.sin(2 * np.pi * 1.9 * t + 1.3)
    return s * am / (np.max(np.abs(s * am)) + 1e-9)


def build_v31():
    ev = json.load(open('out/v31_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    w0, w1 = ev['water']
    for pan in (-0.35, 0.35):
        m.add(water_run(w1 - w0 - 0.3), w0 + 0.25, 0.1, pan)
    g = ev['grab']
    m.add(clack(0.8, 1.0), g + 0.26, 0.14, -0.35)
    m.add(thump(110, 0.04, 0.5), g + 0.26, 0.14, -0.35)
    m.add(cloth(0.3), g + 0.05, 0.12, -0.35)
    p0, p1 = ev['place']
    m.add(clack(0.9, 0.5), (p0 + p1) / 2, 0.08, 0.35)
    m.add(cloth(0.4), ev['dua'][0], 0.08, 0.35)
    m.add(cloth(0.45), ev['sit'][0], 0.12, 0.35)
    g0, g1 = ev['grow']
    lv = leaves(D - g0)
    lv *= np.minimum(1, np.arange(len(lv)) / ((g1 - g0) * SR)) ** 1.5
    m.add(lv, g0, 0.035, 0)
    m.add(wind(D - g0, 1.0), g0, 0.025, 0)
    t = g0 + 1.6
    k = 0
    while t < D - 1.2:
        m.add(creak_pull(0.3), t, 0.05 + 0.012 * k, -0.4)
        t += 0.85
        k += 1
    f0, f1 = ev['fruit']
    n = ev['n_fruit']
    notes = [784, 880, 988, 1047, 1175, 1319, 1397]
    for i in range(n):
        tt = f0 + (f1 - f0) * i / (n - 1)
        m.add(pluck(notes[i % len(notes)]), tt, 0.06, -0.3)
        m.add(pluck(notes[i % len(notes)]), tt + 0.004, 0.06, 0.3)
    m.add(whoosh(0.3, 900, 400), ev['drop'], 0.05, 0.3)
    m.add(whoosh(0.4, 900, 300), ev['drop'], 0.05, -0.3)
    m.add(thump(150, 0.03, 0.5), ev['catch'], 0.16, 0.35)
    m.add(cloth(0.2), ev['catch'], 0.08, 0.35)
    ll = ev['land_l']
    m.add(thump(95, 0.05, 0.7), ll, 0.26, -0.35)
    m.add(thump(120, 0.03, 0.5), ll + 0.32, 0.1, -0.35)
    m.add(thump(140, 0.02, 0.4), ll + 0.5, 0.05, -0.35)
    m.add(swell(2.2), ev['e1'] - 0.35, 0.16, 0)
    m.add(pluck(880), ev['e2'], 0.09, 0)
    m.drive = 2.0
    m.write('out/v31_audio.wav', peak_db=-3.0)


def build_v33():
    ev = json.load(open('out/v33_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(wind(D, 1.0), 0, 0.03, 0)
    # the left archer's held draw: the bow keeps creaking, worse as he tires
    t = 0.3
    k = 0
    fail = ev['fail']
    while t < fail:
        fat = min(1.0, max(0.0, (t - 8.0) / (fail - 8.0)))
        m.add(creak_pull(0.28 + 0.1 * fat), t, 0.035 + 0.07 * fat, -0.4)
        t += 1.1 - 0.5 * fat
        k += 1
    m.add(rattle(1.2), fail - 1.3, 0.05, -0.4)
    # right archer
    h0, h1 = ev['heart']
    m.add(cloth(0.35), h0 + 0.05, 0.08, 0.4)
    for (n0, n1), (d0, d1), rel in ((ev['nock1'], ev['draw1'], ev['rel1']), (ev['nock2'], ev['draw2'], ev['rel2'])):
        m.add(whoosh(0.25, 500, 1400), n0 + 0.1, 0.05, 0.4)
        m.add(clack(1.6, 0.4), n1 - 0.05, 0.08, 0.4)
        m.add(creak_pull(0.6), d0 + 0.2, 0.09, 0.4)
        m.add(thwang(), rel, 0.32, 0.45)
        m.add(whoosh(0.35, 1800, 600), rel + 0.02, 0.16, 0.7)
    m.add(cloth(0.4), ev['raise_'][0], 0.07, 0.4)
    # somewhere off-screen, the first arrow lands
    th = lp(thump(160, 0.04, 0.9), 900)
    m.add(th, ev['thock'], 0.07, 0.8)
    # the left archer's arrow drops, never fired
    m.add(scrape(0.15), fail + 0.05, 0.08, -0.4)
    m.add(clack(1.2, 0.8), ev['land'], 0.18, -0.5)
    m.add(clack(1.4, 0.5), ev['land'] + 0.14, 0.08, -0.5)
    m.add(cloth(0.5), fail + 0.3, 0.12, -0.4)
    m.add(swell(2.2), ev['title'] - 0.6, 0.12, 0)
    m.drive = 2.0
    m.write('out/v33_audio.wav', peak_db=-3.0)


def build_v34():
    ev = json.load(open('out/v34_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(wind(D, 1.0), 0, 0.02, 0)
    for t in ev['steps_c']:
        m.add(step(0.8), t, 0.11, 0.35)
    for t, n in ev['steps_a']:
        m.add(step(1.0), t, 0.12 + 0.015 * n, -0.35)
        m.add(thump(70, 0.04, 0.2), t, 0.02 * n, -0.35)
    items = ev['items']
    # calm man: real boxes handled, what-ifs dissolve as he reaches them
    for g in ev['calm']:
        if g[0] == 'handle':
            a, b = g[1], g[2]
            m.add(cloth(0.25), a + 0.15, 0.1, 0.35)
            m.add(clack(0.85, 0.7), a + 0.8 * (b - a), 0.12, 0.35)
    for t in ev['ghost_fades']:
        m.add(sparkle(0.5), t, 0.025, 0.45)
        m.add(whoosh(0.3, 2500, 4500), t, 0.025, 0.45)
    # anxious man: real boxes, and every what-if he pulls onto his back
    for a, b, i in ev['a_handles']:
        m.add(cloth(0.3), a + 0.15, 0.1, -0.35)
        m.add(clack(0.85, 0.7), a + 0.8 * (b - a), 0.12, -0.35)
    fly = ev['fly']
    for k, (tp, j) in enumerate(ev['pulls']):
        m.add(whoosh(fly, 400, 1600), tp, 0.07, -0.2)
        m.add(thump(95 - 3 * k, 0.05 + 0.006 * k, 0.6), tp + fly, 0.2 + 0.03 * k, -0.35)
        m.add(creak_pull(0.3), tp + fly + 0.03, 0.05 + 0.012 * k, -0.35)
    bk = ev['buckle']
    m.add(thump(60, 0.12, 0.9), bk + 0.45, 0.42, -0.35)
    m.add(boom(), bk + 0.45, 0.1, -0.3)
    m.add(rattle(1.0), bk + 0.3, 0.06, -0.35)
    m.add(swell(2.2), ev['e'] - 0.35, 0.16, 0)
    m.drive = 2.0
    m.write('out/v34_audio.wav', peak_db=-3.0)


def hum(dur, f=110, bright=0.3):
    n = int(dur * SR)
    t = tsec(n)
    s = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t + 0.3) + bright * np.sin(2 * np.pi * 3 * f * t)
    s *= 0.85 + 0.15 * np.sin(2 * np.pi * 0.4 * t)
    e = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.6)
    return s * e / (np.max(np.abs(s)) + 1e-9)


def buzz(dur):
    n = int(dur * SR)
    t = tsec(n)
    s = np.sign(np.sin(2 * np.pi * 120 * t)) * 0.3 + np.sin(2 * np.pi * 240 * t) * 0.4
    s = bp(s, 100, 3000)
    e = np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.05)
    return s * e / (np.max(np.abs(s)) + 1e-9)


def build_v35():
    ev = json.load(open('out/v35_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    # the door's warmth: there at the start, fading as he walks away
    m.add(hum(5.5, 98, 0.2), 0, 0.05, -0.3)
    # the tug, the walk, the thread winding round him
    m.add(creak_pull(0.4), ev['tug'][0], 0.12, 0.3)
    m.add(cloth(0.3), ev['tug'][0] + 0.05, 0.08, 0.2)
    for t in ev['steps']:
        m.add(step(0.8), t, 0.12, 0)
    for t in ev['loops']:
        m.add(creak_pull(0.25), t, 0.06, 0.1)
        m.add(scrape(0.2), t + 0.05, 0.03, 0.1)
    # the cold spotlight: click, buzz, flicker, out
    on = ev['spot_on']
    f0, f1 = ev['flick']
    m.add(tick(), on, 0.3, 0.1)
    m.add(thump(160, 0.02, 0.8), on, 0.18, 0.1)
    m.add(buzz(f0 - on), on, 0.025, 0.1)
    k = 0
    t = f0
    while t < f1:
        m.add(tick(), t, 0.12 + 0.08 * (k % 2), 0.1)
        m.add(buzz(0.04), t, 0.03, 0.1)
        t += 0.045 + 0.05 * ((k * 7) % 3)
        k += 1
    m.add(tick(), f1, 0.3, 0.1)
    m.add(thump(130, 0.03, 0.8), f1, 0.16, 0.1)
    m.add(cloth(0.45), ev['sink'][0], 0.08, 0)
    m.add(cloth(0.5), ev['sit'][0], 0.12, 0)
    # the line of warm light creeping to his feet
    l0, l1 = ev['line']
    m.add(hum(l1 - l0 + 6.0, 98, 0.2), l0, 0.05, -0.3)
    m.add(sparkle(1.4), l1 - 0.6, 0.04, 0)
    m.add(cloth(0.4), ev['rise'][0], 0.1, 0)
    r0, r1 = ev['ret']
    t = r0 + 0.4
    while t < r1:
        m.add(creak_pull(0.3), t, 0.05, 0.3)
        t += 1.1
    # two soft knocks
    for kt in ev['knocks']:
        m.add(knock(), kt, 0.18, -0.2)
    # opened at once
    o0 = ev['open'][0]
    m.add(creak_pull(0.5), o0, 0.12, -0.2)
    m.add(whoosh(0.9, 200, 900), o0 + 0.05, 0.12, -0.1)
    m.add(swell(3.0), o0, 0.24, 0)
    m.add(hum(D - o0, 98, 0.35), o0, 0.07, 0)
    m.add(sparkle(2.0), o0 + 0.2, 0.06, 0)
    for t in ev['fall']:
        m.add(tick(), t + 0.32, 0.06, 0)
        m.add(cloth(0.15), t + 0.3, 0.03, 0)
    m.add(swell(2.4), ev['end'] - 0.3, 0.14, 0)
    m.drive = 2.0
    m.write('out/v35_audio.wav', peak_db=-3.0)


def build_v36():
    ev = json.load(open('out/v36_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(wind(D, 1.0), 0, 0.02, 0)
    st, rt, rc = ev['sting'], ev['reach_t'], ev['rec_t']
    notes = [784, 740, 698, 659, 622, 587, 554]
    for k, r in enumerate(ev['reach']):
        late = k / 6
        m.add(cloth(0.25), r + 0.02, 0.08, -0.35)
        m.add(rattle(0.18), r + st - 0.12, 0.05, -0.4)
        m.add(tick(), r + st, 0.32, -0.35)
        m.add(thump(190, 0.02, 0.9), r + st, 0.2, -0.35)
        m.add(whoosh(0.18, 1400, 500), r + rt, 0.06 * (1 - 0.5 * late), -0.3)
        m.add(cloth(0.2), r + rt + 0.05, 0.07, -0.3)
        if k > 0:
            m.add(pluck(notes[k]), r - 0.02, 0.11, 0)
    r = ev['r_reach']
    m.add(cloth(0.25), r + 0.02, 0.08, 0.35)
    m.add(rattle(0.18), r + st - 0.12, 0.05, 0.4)
    m.add(tick(), r + st, 0.32, 0.35)
    m.add(thump(190, 0.02, 0.9), r + st, 0.2, 0.35)
    m.add(cloth(0.3), r + rt + 0.1, 0.07, 0.35)
    t0, t1 = ev['take']
    m.add(scrape(0.25), t0 + 0.25, 0.08, 0.4)
    p0, p1 = ev['place']
    m.add(thump(85, 0.06, 0.6), p1 - 0.05, 0.22, 0.4)
    m.add(clack(0.7, 0.8), p1 - 0.04, 0.1, 0.4)
    m.add(cloth(0.4), ev['heart'][0], 0.07, 0.35)
    m.add(cloth(0.5), ev['sit'][0], 0.1, 0.35)
    last = ev['reach'][-1] + rt + rc
    m.add(thump(70, 0.08, 0.6), last + 0.5, 0.22, -0.35)
    m.add(swell(2.2), ev['e1'] - 0.35, 0.16, 0)
    m.add(pluck(880), ev['e2'], 0.09, 0)
    m.drive = 2.0
    m.write('out/v36_audio.wav', peak_db=-3.0)


def build_v37():
    ev = json.load(open('out/v37_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    m.add(water_bed(D, 1.0), 0, 0.06, 0)
    m.add(wind(D, 1.0), 0, 0.025, 0)
    t = 0.7
    while t < D - 1:
        m.add(creak_pull(0.4), t, 0.03, rng.uniform(-0.4, 0.4))
        t += rng.uniform(1.1, 1.8)
    # drilling: both boats until the bottom one is stopped, the top one until it goes through
    d0 = ev['drill']
    punch = ev['punch']
    stop = ev['b_stop'][0]
    t = d0
    while t < punch:
        m.add(scrape(0.12), t, 0.07, -0.25)
        if t < stop:
            m.add(scrape(0.12), t + 0.02, 0.06, 0.25)
        t += 0.11
    m.add(cloth(0.3), ev['a_wave'][0], 0.08, -0.3)
    m.add(cloth(0.4), ev['a_sit'][0], 0.08, -0.3)
    # the hole goes through
    m.add(clack(0.6, 1.0), punch, 0.26, -0.3)
    m.add(thump(90, 0.05, 0.9), punch, 0.24, -0.3)
    f0, f1 = ev['flood']
    m.add(water_run(f1 - f0), f0 + 0.02, 0.16, -0.3)
    m.add(splash_snd(0.5), f0 + 0.05, 0.12, -0.3)
    s0, s1 = ev['sink']
    m.add(rumble(s1 - s0), s0, 0.12, -0.3)
    m.add(splash_snd(1.0), 6.2, 0.22, -0.2)
    for k in range(8):
        m.add(pluck(rng.choice([1200, 1400, 1600])), 6.8 + 0.22 * k, 0.03, -0.2)
    # the bottom boat: down the ladder, hand on the drill, the water handed over
    b0, b1 = ev['b_down']
    t = b0 + 0.05
    while t < b1:
        m.add(clack(1.3, 0.4), t, 0.07, 0.3)
        t += 0.16
    m.add(cloth(0.35), stop, 0.1, 0.3)
    m.add(clack(1.0, 0.5), ev['b_give'][1] - 0.1, 0.08, 0.3)
    dr0, dr1 = ev['d_drink']
    m.add(water_run(dr1 - dr0 - 0.2), dr0 + 0.15, 0.06, 0.3)
    m.add(swell(2.2), ev['e1'] - 0.35, 0.16, 0)
    m.add(pluck(880), ev['e2'], 0.09, 0)
    m.drive = 2.0
    m.write('out/v37_audio.wav', peak_db=-3.0)


def bloop(f0=420, f1=150, dur=0.16):
    n = int(dur * SR)
    t = tsec(n)
    f = f1 + (f0 - f1) * np.exp(-t / 0.035)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.05)
    s += lp(rng.normal(0, 1, n), 1800) * env_exp(n, 0.012) * 0.5
    s *= np.minimum(1, t / 0.002)
    return s / (np.max(np.abs(s)) + 1e-9)


def build_v38():
    ev = json.load(open('out/v38_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(water_bed(D, 1.0), 0, 0.06, 0.0)
    # the same prayer, both men
    for t in (0.34, 0.68, 1.0, 1.25):
        m.add(cloth(0.22), t, 0.11, -0.15)
        m.add(cloth(0.22), t + 0.01, 0.11, 0.15)
    w0, w1 = ev['walk']
    t = w0 + 0.1
    while t < w1 - 0.05:
        m.add(step(0.8), t, 0.14, -0.15)
        m.add(step(0.8), t + 0.01, 0.14, 0.15)
        t += 0.28
    # the stepper: a stone rises under every step
    notes = [392, 440, 494, 523, 587, 659, 698, 784, 784, 784]
    for k, (r0, r1) in enumerate(ev['rise']):
        if ev['stones_x'][k] > 1120:
            continue
        tb = r0 + 0.45 * (r1 - r0)
        m.add(bloop(rng.uniform(380, 460), rng.uniform(130, 170)), tb, 0.2, 0.15)
        m.add(splash_snd(0.14), tb + 0.01, 0.07, 0.15)
        m.add(pluck(notes[k]), tb + 0.02, 0.06, 0.1)
        ld = ev['land'][k]
        m.add(clack(0.5, 1.0), ld, 0.1, 0.15)
        m.add(step(0.7), ld + 0.005, 0.09, 0.15)
    # the waiter: toe in, nothing there, back off (twice)
    for tr in ev['tries']:
        m.add(cloth(0.25), tr['out'][0], 0.07, -0.2)
        td = tr['dip'][1] - 0.05
        m.add(splash_snd(0.1), td, 0.11, -0.2)
        m.add(step(1.0), tr['recoil'][0] + 0.03, 0.15, -0.2)
        m.add(cloth(0.2), tr['recoil'][0], 0.08, -0.2)
        b0, b1 = tr['back']
        for t in (b0 + 0.08, b0 + 0.24, b0 + 0.4):
            m.add(step(0.65), t, 0.1, -0.2)
    w0, w1 = ev['walk2']
    for t in (w0 + 0.08, w0 + 0.24, w0 + 0.4):
        m.add(step(0.75), t, 0.11, -0.2)
    s0, s1 = ev['sit']
    m.add(cloth(0.4), s0, 0.12, -0.2)
    m.add(thump(75, 0.05, 0.2), s1 - 0.06, 0.1, -0.2)
    m.add(swell(2.2), ev['e1'] - 0.35, 0.17, 0)
    m.add(pluck(880), ev['e2'], 0.09, 0)
    m.drive = 2.0
    m.write('out/v38_audio.wav', peak_db=-3.0)


def build_v39():
    sys.path.insert(0, '.')
    import importlib
    L = importlib.import_module('v39_load')
    ev = json.load(open('out/v39_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(wind(D, 1.0), 0, 0.025, 0.0)
    TT, PHA, PHB = L.TT, L.PHA, L.PHB
    sitt = ev['sit'][0]
    # footfalls from the walk phase of each lane
    for ph, pan, lane in ((PHA, -0.2, 'A'), (PHB, 0.2, 'B')):
        k = np.floor(ph * 2)
        idx = np.nonzero(np.diff(k) > 0)[0]
        for i in idx:
            t = TT[i]
            if t > D - 0.1 or (lane == 'A' and t > sitt):
                continue
            if lane == 'A':
                heavy = min(1.0, t / 8.0)
                m.add(step(0.75 + 0.25 * heavy), t, 0.1 + 0.07 * heavy, pan)
                m.add(thump(lerp(70, 52, heavy), 0.05, 0.1), t, 0.04 + 0.08 * heavy, pan)
            else:
                m.add(step(0.75), t, 0.1, pan)
    notes = [523, 587, 659, 698, 784]
    for k, (a, b) in enumerate(ev['win']):
        Dk = b - a
        # the mat unrolls in both lanes
        m.add(cloth(0.28), a - 0.34, 0.06, -0.2)
        m.add(cloth(0.28), a - 0.33, 0.06, 0.2)
        m.add(pluck(notes[k]), a - 0.3, 0.1, 0)
        # bottom: load down, prayer, load back on
        m.add(thump(68, 0.07, 0.3), a + 0.2 * Dk - 0.02, 0.2, 0.25)
        m.add(cloth(0.2), a + 0.2 * Dk - 0.1, 0.07, 0.25)
        v0 = a + 0.2 * Dk
        pd = 0.6 * Dk
        m.add(cloth(0.22), v0 + 0.16 * pd, 0.09, 0.2)
        m.add(cloth(0.22), v0 + 0.36 * pd, 0.1, 0.2)
        m.add(cloth(0.22), v0 + 0.68 * pd, 0.09, 0.2)
        m.add(cloth(0.3), a + 0.8 * Dk, 0.1, 0.2)
        m.add(thump(90, 0.04, 0.3), a + 0.9 * Dk, 0.09, 0.2)
        # top: stops on it, reaches for the strap, shakes it off, slumps lower
        h0, h1 = ev['hes'][k]
        m.add(cloth(0.25), h0 + 0.3 * (h1 - h0), 0.06, -0.2)
        m.add(thump(lerp(62, 48, k / 4), 0.09, 0.15), h1 + 0.05, 0.08 + 0.03 * k, -0.2)
    s0, s1 = ev['sit']
    m.add(cloth(0.45), s0, 0.12, -0.2)
    m.add(thump(58, 0.08, 0.2), s1 - 0.08, 0.16, -0.2)
    m.add(swell(2.2), ev['e1'] - 0.35, 0.17, 0)
    m.add(pluck(880), ev['e2'], 0.09, 0)
    m.drive = 2.0
    m.write('out/v39_audio.wav', peak_db=-3.0)


def build_v40():
    ev = json.load(open('out/v40_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.01), 0, 1.0)
    a, b = ev['wrap']
    m.add(cloth(0.45), a, 0.3, 0.3)
    m.add(whoosh(0.4, 600, 2400), a + 0.1, 0.12, 0.3)
    last = -1
    for i, t in enumerate(ev['bricks']):
        if t - last > 0.06:
            m.add(pluck(rng.choice([880, 990, 1175, 1320])), t, 0.16 if i < 10 else 0.09, 0.35)
            m.add(thump(90, 0.05, 0.3), t, 0.18 if i < 10 else 0.11, -0.35)
            last = t
    a1, a2, a3 = ev['hesitate']
    m.add(cloth(0.3), a1, 0.16, -0.3)
    m.add(cloth(0.3), a1 + 0.55, 0.12, -0.3)
    m.add(cloth(0.3), a2, 0.16, -0.3)
    m.add(whoosh(0.3, 600, 2200), a2 + 0.3, 0.1, -0.3)
    m.add(cloth(0.35), a2 + 0.8, 0.18, -0.3)
    m.add(cloth(0.25), a3, 0.12, -0.3)
    m.add(swell(2.0), ev['end_card'] - 0.4, 0.15, 0)
    m.drive = 2.0
    m.write('out/v40_audio.wav', peak_db=-2.0)


def build_v41():
    ev = json.load(open('out/v41_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    for lane, pan in (('a_bricks', -0.25), ('b_bricks', 0.25)):
        for k, t in enumerate(ev[lane]):
            m.add(thump(rng.uniform(90, 120), 0.05, 0.5), t, 0.18, pan)
            m.add(clack(rng.uniform(0.55, 0.75), 1.0), t, 0.07, pan)
    # bottom: down into sujood, the wall turns to light, up and a step forward
    for k, (d0, d1) in zip(ev['kneel'], ev['dissolve']):
        m.add(cloth(0.3), k, 0.12, 0.25)
        m.add(cloth(0.35), k + 0.2, 0.12, 0.25)
        m.add(swell(1.4), d0 - 0.1, 0.16, 0.2)
        m.add(sparkle(1.0), d0 + 0.05, 0.08, 0.25)
        m.add(cloth(0.3), k + 1.0, 0.1, 0.25)
    w0, w1 = ev['walk_in']
    t = w0 + 0.1
    while t < w1 - 0.2:
        m.add(step(0.7), t, 0.1, 0.25)
        t += 0.3
    # top: walks up, pulls two bricks out, drops them, looks up, backs off, sits
    a0, a1 = ev['a_walk1']
    for t in (a0 + 0.08, a0 + 0.22, a0 + 0.36):
        m.add(step(0.8), t, 0.12, -0.25)
    for pl in ev['pulls']:
        m.add(scrape(0.2), pl['pull'][0], 0.12, -0.25)
        m.add(thump(80, 0.05, 0.4), pl['drop'][1] - 0.02, 0.18, -0.3)
        m.add(clack(0.6, 1.0), pl['drop'][1] - 0.02, 0.08, -0.3)
    m.add(step(1.0), ev['a_recoil'][0] + 0.03, 0.16, -0.25)
    b0, b1 = ev['a_back']
    for t in (b0 + 0.08, b0 + 0.26, b0 + 0.44):
        m.add(step(0.65), t, 0.1, -0.25)
    s0, s1 = ev['a_sit']
    m.add(cloth(0.5), s0, 0.14, -0.3)
    wd = wind(D - s0, 1.0)
    wd *= np.minimum(1, np.arange(len(wd)) / (0.6 * SR))
    m.add(wd, s0, 0.04, -0.2)
    m.add(swell(2.2), ev['e1'] - 0.35, 0.16, 0)
    m.drive = 2.0
    m.write('out/v41_audio.wav', peak_db=-2.0)


def build_v42():
    ev = json.load(open('out/v42_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.016), 0, 1.0)
    m.add(wind(D, 0.8), 0, 0.07, 0)
    m.add(crickets(1.6), 0.0, 0.05, 0)
    m.add(pluck(1047), 0.05, 0.1, 0.3)
    m.add(pluck(1319), 0.17, 0.08, 0.3)
    a, b = ev['cloud']
    m.add(rumble(1.6), a, 0.25, 0)
    m.add(boom(), ev['flash'] + 0.12, 0.42, -0.2)
    m.add(rumble(1.2), ev['flash2'], 0.2, 0.4)
    r0, r1 = ev['rain']
    bed = rain_bed(r1 - r0 + 0.8)
    nb = len(bed)
    env = np.minimum(1, np.arange(nb) / (0.3 * SR)) * np.clip((nb - np.arange(nb)) / (0.9 * SR), 0, 1)
    m.add(bed * env, r0, 0.32, 0)
    L = ev['left']
    m.add(cloth(0.35), L['cover'][0], 0.12, -0.35)
    m.add(cloth(0.3), L['half'][0], 0.08, -0.35)
    m.add(cloth(0.3), L['drop'][0], 0.08, -0.35)
    m.add(cloth(0.4), L['stand'][0], 0.12, -0.35)
    w0, w1 = L['walk']
    t = w0 + 0.1
    while t < w1:
        m.add(step(0.8), t, 0.12, -0.45)
        m.add(splash_snd(0.25), t + 0.01, 0.03, -0.45)
        t += 0.32
    m.add(cloth(0.5), L['sit'][0], 0.12, -0.5)
    m.add(cloth(0.4), 3.6, 0.12, 0.35)      # right man down into sujood
    m.add(swell(2.0), ev['part'][0], 0.14, 0)
    notes = [784, 880, 988, 1175, 1319, 1568, 1760]
    k = 0
    for g0, pan in ((ev['grow_r'], 0.35), (ev['grow_l'], -0.35)):
        t = g0 + 0.3
        for _ in range(5):
            m.add(pluck(notes[k % len(notes)]), t, 0.07, pan)
            t += 0.28
            k += 1
    m.add(swell(2.2), ev['e1'] - 0.35, 0.12, 0)
    m.drive = 2.0
    m.write('out/v42_audio.wav', peak_db=-2.0)


def build_v43():
    ev = json.load(open('out/v43_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    s0, s1 = ev['storm']
    cr = crickets(s1 + 0.4)
    cr[-int(0.8 * SR):] *= np.linspace(1, 0, int(0.8 * SR))
    m.add(cr, 0, 0.03, 0)
    wd = wind(D - s0, 1.0)
    n = len(wd)
    wd *= np.minimum(1, np.arange(n) / (0.8 * SR))
    m.add(wd, s0, 0.12, 0)
    r0, r1 = ev['rain']
    rb = rain_bed(min(D, r1) - r0 + 0.6)
    n = len(rb)
    rb *= np.minimum(1, np.arange(n) / (0.8 * SR))
    m.add(rb, r0, 0.16, 0)
    m.add(boom(), ev['flash'], 0.3, -0.3)
    # right man: prayer movements; each time he rises his flame grows
    for c0 in ev['cycles_r']:
        for dt in (0.85, 1.4, 1.8, 2.45, 2.95, 3.4):
            m.add(cloth(0.22), c0 + dt, 0.09, 0.3)
    for i, tt in enumerate((0.2 + 2.45, 0.2 + 3.75, 0.2 + 3.95)):
        m.add(pluck([660, 784, 988][i]), tt, 0.1, 0.35)
    m.add(sparkle(0.7), 0.2 + 3.95, 0.07, 0.35)
    # left man: starts to kneel, stops; relaxes; reaches, stops; then the storm takes his candle
    L = ev['left']
    m.add(cloth(0.3), L['kneel'][0], 0.1, -0.35)
    m.add(cloth(0.3), L['up'][0], 0.08, -0.35)
    m.add(cloth(0.3), L['relax'][0], 0.07, -0.35)
    m.add(cloth(0.3), L['reach'][0], 0.08, -0.35)
    m.add(step(1.0), L['alarm'][0] + 0.05, 0.14, -0.35)
    m.add(cloth(0.45), L['drop'][0], 0.12, -0.35)
    m.add(puff(), ev['out'] - 0.05, 0.2, -0.3)
    m.add(swell(2.2), ev['e1'] - 0.35, 0.15, 0)
    m.drive = 2.0
    m.write('out/v43_audio.wav', peak_db=-3.0)


def build_v44():
    ev = json.load(open('out/v44_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(wind(D, 1.0), 0, 0.02, 0)
    for t in ev['steps_c']:
        m.add(step(0.8), t, 0.11, 0.35)
    for t, n in ev['steps_a']:
        m.add(step(1.0), t, 0.12 + 0.015 * n, -0.35)
        m.add(thump(70, 0.04, 0.2), t, 0.02 * n, -0.35)
    for a, b in ev['calm_handles']:
        m.add(cloth(0.25), a + 0.15, 0.1, 0.35)
        m.add(clack(0.85, 0.7), a + 0.8 * (b - a), 0.12, 0.35)
    # calm man: hands up, the what-ifs rise and go
    for k, (a, b) in enumerate(ev['gives']):
        m.add(cloth(0.25), a, 0.08, 0.35)
        m.add(whoosh(0.5, 900, 4200), a + 0.12, 0.05, 0.4)
        m.add(sparkle(0.7), a + 0.2, 0.04, 0.45)
        m.add(pluck([784, 880, 988][k % 3]), a + 0.18, 0.06, 0.4)
    for a, b in ev['a_handles']:
        m.add(cloth(0.3), a + 0.15, 0.1, -0.35)
        m.add(clack(0.85, 0.7), a + 0.8 * (b - a), 0.12, -0.35)
    for a, b in ev['picks']:
        m.add(cloth(0.25), a, 0.07, -0.35)
    fly = ev['fly']
    for k, (tp, j) in enumerate(ev['pulls']):
        m.add(whoosh(fly, 400, 1600), tp, 0.07, -0.2)
        m.add(thump(95 - 3 * k, 0.05 + 0.006 * k, 0.6), tp + fly, 0.2 + 0.03 * k, -0.35)
        m.add(creak_pull(0.3), tp + fly + 0.03, 0.05 + 0.012 * k, -0.35)
    bk = ev['buckle']
    m.add(thump(60, 0.12, 0.9), bk + 0.45, 0.42, -0.35)
    m.add(boom(), bk + 0.45, 0.1, -0.3)
    m.add(rattle(1.0), bk + 0.3, 0.06, -0.35)
    m.add(swell(2.2), ev['e'] - 0.35, 0.16, 0)
    r0, r1 = ev['reveal']
    m.add(sparkle(1.0), r0, 0.06, -0.3)
    m.drive = 2.0
    m.write('out/v44_audio.wav', peak_db=-3.0)


def build_v45():
    ev = json.load(open('out/v45_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.016), 0, 1.0)
    cave = lp(wind(D, 1.0), 500)
    m.add(cave / (np.max(np.abs(cave)) + 1e-9), 0, 0.05, 0)
    for t in (0.6, 2.9, 4.7, 6.8):
        m.add(bloop(1500, 700, 0.09), t, 0.04, rng.uniform(-0.5, 0.5))      # cave drips
    # both: walk up, push, step back
    w0, w1 = ev['walk_in']
    for t in (w0 + 0.05, w0 + 0.22, w0 + 0.39):
        m.add(step(0.8), t, 0.12, 0)
    p0, p1 = ev['push']
    m.add(breath(0.4, True), p0 - 0.1, 0.06, 0)
    m.add(scrape(0.5), p0 + 0.05, 0.07, 0.2)
    m.add(breath(0.5, False), p1 - 0.1, 0.08, 0)
    b0, b1 = ev['back']
    for t in (b0 + 0.05, b0 + 0.2):
        m.add(step(0.6), t, 0.1, 0)
    # B: kneels, asks; the rock shifts; asks again; sujood; it rolls away
    m.add(cloth(0.35), ev['b_kneel'][0], 0.1, 0.2)
    m.add(cloth(0.3), ev['b_dua1'][0], 0.1, 0.2)
    for (a, b), g in ((ev['shift1'], 0.55), (ev['shift2'], 0.8)):
        m.add(rumble(0.6), a - 0.05, 0.3 * g, 0.35)
        m.add(scrape(0.35), a, 0.2 * g, 0.4)
        m.add(rattle(0.5), a + 0.1, 0.06 * g, 0.4)
        m.add(swell(0.9), a, 0.08 * g, 0.4)
    m.add(cloth(0.3), ev['b_bow'][0], 0.07, 0.2)
    m.add(cloth(0.3), ev['b_dua2'][0], 0.1, 0.2)
    m.add(cloth(0.45), ev['b_suj'][0], 0.12, 0.2)
    r0, r1 = ev['roll']
    m.add(rumble(r1 - r0 + 0.4), r0 - 0.05, 0.45, 0.45)
    m.add(scrape(0.6), r0, 0.22, 0.45)
    m.add(rattle(0.8), r0 + 0.1, 0.1, 0.5)
    m.add(thump(55, 0.15, 0.5), r1 - 0.1, 0.25, 0.8)
    m.add(swell(2.0), r0 + 0.2, 0.16, 0.3)
    birds = Mix(3.5)
    t = 0.0
    while t < 3.2:
        birds.add(chirp(), t, rng.uniform(0.3, 0.7), rng.uniform(0.3, 0.8))
        t += rng.uniform(0.15, 0.5)
    m.add(birds.L[:int(3.5 * SR)] * 0.5 + birds.R[:int(3.5 * SR)] * 0.5, r1 - 0.3, 0.03, 0.5)
    m.add(cloth(0.4), ev['b_rise'][0], 0.1, 0.2)
    o0, o1 = ev['b_out']
    t = o0 + 0.1
    while t < o1 - 0.2:
        m.add(step(0.8), t, 0.11, 0.3 + 0.5 * (t - o0) / (o1 - o0))
        t += 0.3
    # A: looks it up and down, hands, half-raise, drop, head shake, shoulder push, turns, sits
    m.add(cloth(0.3), ev['a_hands'][0], 0.07, -0.2)
    m.add(cloth(0.3), ev['a_half'][0], 0.07, -0.2)
    m.add(cloth(0.3), ev['a_drop'][0], 0.08, -0.2)
    m.add(breath(0.45, False), ev['a_shake'][0], 0.05, -0.2)
    a0, a1 = ev['a_walk2']
    for t in (a0 + 0.05, a0 + 0.2):
        m.add(step(0.7), t, 0.1, -0.2)
    p0, p1 = ev['a_push2']
    m.add(thump(80, 0.06, 0.4), p0, 0.12, 0)
    m.add(scrape(0.45), p0 + 0.05, 0.06, 0)
    m.add(breath(0.5, False), p1 - 0.1, 0.08, -0.2)
    t0, t1 = ev['a_turn']
    for t in (t0 + 0.1, t0 + 0.28):
        m.add(step(0.6), t, 0.09, -0.2)
    m.add(cloth(0.5), ev['a_sit'][0], 0.12, -0.2)
    m.add(swell(2.2), ev['e1'] - 0.35, 0.14, 0)
    m.drive = 2.0
    m.write('out/v45_audio.wav', peak_db=-2.0)


def build_v46():
    ev = json.load(open('out/v46_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.014), 0, 1.0)
    m.add(wind(D, 1.0), 0, 0.05, 0)
    # right: du'a, walks up, grips, shakes three times
    m.add(cloth(0.3), ev['r_dua'][0], 0.1, 0.35)
    w0, w1 = ev['r_walk']
    for t in (w0 + 0.05, w0 + 0.22):
        m.add(step(0.8), t, 0.12, 0.35)
    for k, (a, b) in enumerate(ev['shakes']):
        g = [0.5, 0.75, 1.0][k]
        lv = leaves(b - a + 0.5)
        lv *= np.minimum(1, np.arange(len(lv)) / (0.1 * SR)) * np.clip((len(lv) - np.arange(len(lv))) / (0.4 * SR), 0, 1)
        m.add(lv, a, 0.12 * g, 0.4)
        f = [5.0, 6.0, 6.5][k]
        t = a
        while t < b:
            m.add(thump(70, 0.05, 0.2), t, 0.06 * g, 0.35)
            m.add(cloth(0.12), t, 0.025 * g, 0.35)
            t += 1 / f
    m.add(breath(0.4, False), ev['shakes'][2][1] - 0.2, 0.06, 0.35)
    for k, t in enumerate(ev['lands_r']):
        m.add(thump(rng.uniform(170, 240), 0.03, 0.7), t, 0.16 if k < 4 else 0.1, 0.4)
    for i, t in enumerate((ev['falls_r'][4] + 0.1, ev['falls_r'][4] + 0.35, ev['falls_r'][4] + 0.6)):
        m.add(pluck([784, 988, 1175][i]), t, 0.07, 0.4)
    m.add(cloth(0.35), ev['r_kneel'][0], 0.1, 0.35)
    m.add(cloth(0.2), ev['r_reach'][0], 0.06, 0.35)
    # left: backs up, looks at his hands, walks up, one weak push, head shake, turns, sits
    b0, b1 = ev['l_back']
    for t in (b0 + 0.05, b0 + 0.25, b0 + 0.45):
        m.add(step(0.6), t, 0.09, -0.4)
    m.add(cloth(0.25), ev['l_hands'][0], 0.06, -0.4)
    w0, w1 = ev['l_walk']
    for t in (w0 + 0.05, w0 + 0.22, w0 + 0.39):
        m.add(step(0.8), t, 0.11, -0.4)
    p0, p1 = ev['l_push']
    m.add(thump(70, 0.05, 0.2), p0 + 0.2, 0.04, -0.4)
    m.add(leaves(0.4) * np.hanning(int(0.4 * SR)), p0 + 0.15, 0.02, -0.4)
    m.add(breath(0.45, False), ev['l_shake'][0], 0.05, -0.4)
    t0, t1 = ev['l_turn']
    for t in (t0 + 0.08, t0 + 0.26):
        m.add(step(0.6), t, 0.09, -0.4)
    m.add(cloth(0.5), ev['l_sit'][0], 0.12, -0.4)
    for t in ev['lands_l']:
        m.add(thump(210, 0.03, 0.7), t, 0.09, -0.3)
    m.add(swell(2.2), ev['e1'] - 0.35, 0.14, 0)
    m.drive = 2.0
    m.write('out/v46_audio.wav', peak_db=-2.0)


def build_v47(v='v47'):
    ev = json.load(open(f'out/{v}_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.014), 0, 1.0)
    m.add(wind(D, 1.0), 0, 0.03, 0)
    k0, k1 = ev['kid_in']
    t = k0 + 0.05
    while t < k1 - 0.05:
        m.add(step(0.5), t, 0.07, 0.4)
        t += 0.16
    # the jab from the ex's house, both lanes
    for k, (a, b) in enumerate(ev['jabs']):
        g = 1.0 if k < 2 else 0.8
        m.add(whoosh(b - a + 0.05, 700, 2600), a, 0.1 * g, 0.5)
        m.add(clack(1.5, 0.4), b - 0.01, 0.16 * g, -0.2)
        m.add(thump(260, 0.03, 0.9), b - 0.01, 0.14 * g, -0.2)
    # top: fires back; it flies over his kid's head and hits the other house
    for k, (a, b) in enumerate(ev['rj']):
        m.add(cloth(0.15), a - 0.08, 0.08, -0.3)
        m.add(whoosh(b - a + 0.05, 2600, 700), a, 0.1, 0.0)
        m.add(clack(1.3, 0.5), b - 0.01, 0.13, 0.6)
        m.add(thump(200, 0.04, 0.6), b - 0.01, 0.1, 0.6)
        m.add(cloth(0.25), ev['rj_over'][k] - 0.05, 0.08 + 0.02 * k, 0.1)
    m.add(cloth(0.45), ev['rj_over'][2] + 0.15, 0.1, 0.1)
    # bottom: hand on heart, a soft answer; his kid steps close and takes his hand
    for k, (a, b) in enumerate(ev['b_heart']):
        m.add(cloth(0.25), a, 0.07, -0.3)
    notes = [(659, 784), (698, 880)]
    for k, (a, b) in enumerate(ev['wb']):
        m.add(pluck(notes[k][0]), a + 0.05, 0.08, 0.1)
        m.add(pluck(notes[k][1]), a + 0.2, 0.06, 0.2)
    s0, s1 = ev['b_step']
    for t in (s0 + 0.08, s0 + 0.24, s0 + 0.4):
        m.add(step(0.5), t, 0.06, -0.1)
    h0, h1 = ev['b_hand']
    m.add(cloth(0.2), h0, 0.06, -0.2)
    m.add(pluck(784), h1 - 0.15, 0.08, -0.2)
    m.add(pluck(988), h1, 0.06, -0.2)
    m.add(swell(2.2), ev['e1'] - 0.35, 0.14, 0)
    m.drive = 2.0
    m.write(f'out/{v}_audio.wav', peak_db=-2.0)


def build_v48():
    ev = json.load(open('out/v48_events.json'))
    D = ev['dur']
    m = Mix(D)
    m.add(room(D, 0.014), 0, 1.0)
    m.add(wind(D, 1.0), 0, 0.03, 0)
    w0, w1 = ev['walk_out']
    for t in (w0 + 0.05, w0 + 0.22, w0 + 0.39):
        m.add(step(0.8), t, 0.11, -0.3)
    s0, s1 = ev['slam']
    m.add(boom(), s1 - 0.01, 0.3, -0.5)
    m.add(thump(70, 0.08, 0.8), s1 - 0.01, 0.4, -0.5)
    m.add(clack(0.7, 1.0), s1, 0.12, -0.5)
    m.add(rattle(0.25), s1 + 0.02, 0.04, -0.5)
    # the new door: an outline, light under it, then it opens (both lanes at once)
    o0, o1 = ev['outline']
    m.add(swell(1.2), o0 - 0.1, 0.08, 0.5)
    c0, c1 = ev['crack']
    m.add(sparkle(0.8), c0, 0.05, 0.5)
    p0, p1 = ev['open']
    m.add(creak_pull(0.5), p0, 0.07, 0.5)
    m.add(swell(1.6), p0, 0.16, 0.5)
    birds = Mix(3.0)
    t = 0.0
    while t < 2.7:
        birds.add(chirp(), t, rng.uniform(0.3, 0.7), rng.uniform(0.3, 0.8))
        t += rng.uniform(0.15, 0.5)
    m.add(birds.L[:int(3.0 * SR)] * 0.5 + birds.R[:int(3.0 * SR)] * 0.5, p1 - 0.2, 0.03, 0.6)
    # bottom: du'a three times, then walks through
    for a, b in ev['b_dua']:
        m.add(cloth(0.3), a, 0.09, 0.2)
    b0, b1 = ev['b_walk']
    t = b0 + 0.08
    while t < b1 - 0.2:
        m.add(step(0.75), t, 0.1, 0.2 + 0.5 * (t - b0) / (b1 - b0))
        t += 0.3
    # top: brick by brick
    a0, a1 = ev['a_to_wall']
    for t in (a0 + 0.05, a0 + 0.2):
        m.add(step(0.6), t, 0.08, -0.2)
    for k, tb in enumerate(ev['bricks']):
        m.add(clack(rng.uniform(0.55, 0.7), 1.0), tb + 0.08, 0.1, -0.15)
        m.add(thump(rng.uniform(90, 120), 0.05, 0.5), tb + 0.08, 0.14, -0.15)
        m.add(scrape(0.12), tb - 0.05, 0.03, -0.15)
    m.add(cloth(0.3), ev['a_half'][0], 0.07, -0.2)
    m.add(cloth(0.3), ev['a_drop'][0], 0.07, -0.2)
    m.add(cloth(0.5), ev['a_sit'][0], 0.12, -0.3)
    m.add(swell(2.2), ev['e1'] - 0.35, 0.14, 0)
    m.drive = 2.0
    m.write('out/v48_audio.wav', peak_db=-2.0)


if __name__ == '__main__':
    which = sys.argv[1]
    {'v1': build_v1, 'v2': build_v2, 'v3': build_v3, 'v4': build_v4, 'v5': build_v5, 'v6': build_v6, 'v7': build_v7, 'v8': build_v8, 'v9': build_v9, 'v10': build_v10, 'v11': build_v11, 'v12': build_v12, 'v13': build_v13, 'v14': build_v14, 'v15': build_v15, 'v16': build_v16, 'v17': build_v17, 'v18': build_v18, 'v19': build_v19, 'v20': build_v20, 'v21': build_v21, 'v22': build_v22, 'v23': build_v23, 'v24': build_v24, 'v25': build_v25, 'v26': build_v26, 'v27': build_v27, 'v28': build_v28, 'v29': build_v29, 'v30': build_v30, 'v31': build_v31, 'v33': build_v33, 'v34': build_v34, 'v35': build_v35, 'v36': build_v36, 'v37': build_v37, 'v38': build_v38, 'v39': build_v39, 'v40': build_v40, 'v41': build_v41, 'v42': build_v42, 'v43': build_v43, 'v44': build_v44, 'v45': build_v45, 'v46': build_v46, 'v47': build_v47, 'v48': build_v48, 'v49': lambda: build_v47('v49')}[which]()
    print('ok', which)
