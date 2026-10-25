"""Sound for each reel: one build_vXX() per reel, reading out/vXX_events.json written by the render.
Run: python3 sfx_reels.py vXX  ->  out/vXX_audio.wav. Add new reels as build_vXX functions; dispatch is automatic.
The build_v60..build_v75 functions are worked examples (two-lane reels 60-69, formula reels 70-75)."""
import json, sys
import numpy as np
from sfx import *


def ev(v):
    return json.load(open(f'out/{v}_events.json'))


def beep(f, dur=0.09):
    n = int(dur * SR)
    t = tsec(n)
    s = np.sin(2 * np.pi * f * t) * np.minimum(1, t / 0.004) * np.minimum(1, (dur - t) / 0.02)
    return s


def low_battery():
    out = np.zeros(int(0.42 * SR))
    for d, f in ((0.0, 880), (0.16, 587)):
        s = beep(f, 0.12)
        i = int(d * SR)
        out[i:i + len(s)] += s
    return lp(out, 3000)


def full_chime(base=523):
    out = np.zeros(int(0.9 * SR))
    for k, f in enumerate((base, base * 1.25, base * 1.5, base * 2)):
        s = pluck(f)
        i = int(0.06 * k * SR)
        out[i:i + len(s)] += s[:len(out) - i] * (0.8 if k < 3 else 0.6)
    return out / (np.max(np.abs(out)) + 1e-9)


def build_v60():
    e = ev('v60')
    D = e['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(wind(D, 0.8), 0, 0.03, 0)
    # walking away: footsteps, a little softer every year
    t = e['walk1'][0] + 0.12
    k = 0
    while t < e['walk2'][1]:
        m.add(step(0.9), t, 0.16 * (1 - 0.35 * k / 9), -0.15)
        m.add(step(0.9), t + 0.012, 0.13 * (1 - 0.35 * k / 9), 0.15)
        t += 0.3
        k += 1
    for y in range(1, 8):
        m.add(tick(), 0.3 + 0.27 * y, 0.05, 0)
    for b in e['births']:
        m.add(thump(70, 0.05, 0.08), b, 0.12, 0)
    m.add(cloth(0.3), e['look'][0], 0.07, 0)
    m.add(cloth(0.3), e['turn'][0], 0.07, 0)
    # B prays where he is; every part of the prayer, the door comes closer
    for tp in e['b_pray'][1::2]:
        m.add(cloth(0.22), tp - 0.12, 0.05, 0.2)
    for k, (a, b) in enumerate(e['b_rush']):
        m.add(whoosh(b - a + 0.1, 220 + 40 * k, 1400 + 200 * k), a, 0.2, 0.25)
        m.add(pluck([392, 494, 587][k]), b - 0.08, 0.1, 0.25)
    m.add(cloth(0.4), e['b_suj'][0], 0.08, 0.2)
    for k, c in enumerate(e['clean']):
        m.add(pluck([659, 784, 880, 1047, 1175, 1319, 1568, 1760, 2093][k % 9]), c, 0.035, 0.2)
    m.add(cloth(0.3), e['b_up'][0], 0.06, 0.2)
    # A stays where he is
    m.add(cloth(0.3), e['a_hands'][0], 0.06, -0.2)
    m.add(cloth(0.35), e['a_shake'][0], 0.05, -0.2)
    m.add(cloth(0.45), e['a_sink'][0], 0.09, -0.2)
    m.add(thump(60, 0.07, 0.1), e['a_sink'][1] - 0.05, 0.12, -0.2)
    m.add(cloth(0.3), e['a_almost'][0] + 0.05, 0.05, -0.2)
    m.add(breath(0.5, inhale=False), e['a_head'][0], 0.05, -0.2)
    m.add(swell(2.2), e['e1'] - 0.35, 0.14, 0)
    m.drive = 2.0
    m.write('out/v60_audio.wav', peak_db=-2.0)


def build_v61():
    e = ev('v61')
    D = e['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(city(D), 0, 0.02, 0)
    # tired footsteps in
    t = e['walk_in'][0] + 0.1
    while t < e['walk_in'][1]:
        m.add(step(1.0), t, 0.17, -0.1)
        m.add(step(1.0), t + 0.015, 0.15, 0.1)
        t += 0.38
    # both batteries blink low once, together
    m.add(low_battery(), 0.35, 0.05, 0)
    # A flops onto the couch
    m.add(cloth(0.35), e['a_sit'][0], 0.08, -0.25)
    m.add(thump(55, 0.09, 0.12), e['a_sit'][1] - 0.04, 0.26, -0.25)
    m.add(clack(2.6, 0.3), e['phone_in'][1] - 0.08, 0.06, -0.25)
    m.add(beep(1046, 0.07), e['phone_in'][1] + 0.02, 0.05, -0.25)
    t = e['phone_in'][1] + 0.25
    while t < e['a_nod'][0]:
        busy = e['a_almost1'][0] <= t < e['a_almost1'][1] or e['a_almost2'][0] <= t < e['a_almost2'][1]
        if not busy:
            m.add(tick(), t, 0.03, -0.3)
        t += 0.31
    m.add(cloth(0.3), e['a_almost1'][0] + 0.1, 0.06, -0.25)
    m.add(thump(55, 0.07, 0.08), e['a_almost1'][1] - 0.15, 0.12, -0.25)
    m.add(cloth(0.35), e['a_almost2'][0], 0.07, -0.25)
    m.add(creak_pull(0.3), e['a_almost2'][0] + 0.3, 0.05, -0.25)
    m.add(thump(55, 0.08, 0.1), e['a_almost2'][1] - 0.12, 0.16, -0.25)
    m.add(cloth(0.5), e['a_nod'][0], 0.06, -0.25)
    # B: past the couch to the sink
    t = e['b_walk'][0] + 0.1
    while t < e['b_walk'][1]:
        m.add(step(0.9), t, 0.15, 0.25)
        t += 0.32
    w0, w1 = e['wash'][0][0] - 0.1, e['wash'][-1][1]
    m.add(water_run(w1 - w0 + 0.1), w0, 0.07, 0.3)
    m.add(splash_snd(0.6), e['wash'][1][0] + 0.2, 0.09, 0.3)
    for k, (a, b) in enumerate(e['wash']):
        m.add(pluck([523, 587, 659][k]), b - 0.05, 0.08, 0.3)
    for k, tp in enumerate(e['pray'][1:]):
        if k % 2 == 0:
            m.add(cloth(0.22), tp - 0.1, 0.045, 0.3)
    m.add(full_chime(523), e['pray'][-1] - 0.25, 0.1, 0.3)
    t = e['b_home'][0] + 0.1
    while t < e['b_home'][1]:
        m.add(step(0.8), t, 0.12, 0.25)
        t += 0.3
    m.add(cloth(0.35), e['b_sit'][0], 0.07, 0.25)
    # the clock races; his phone fills
    r0, r1 = e['race']
    t = r0
    dt = 0.12
    while t < r1:
        m.add(tick(), t, 0.05, 0)
        t += dt
        dt = max(0.035, dt * 0.85)
    m.add(whoosh(r1 - r0 + 0.1, 400, 2600), r0, 0.06, 0)
    m.add(full_chime(784), r1 - 0.02, 0.07, -0.25)
    # he wakes up at 5%
    m.add(cloth(0.3), e['a_wake'][0], 0.07, -0.25)
    m.add(low_battery(), e['a_look'][0] + 0.05, 0.08, -0.25)
    m.add(swell(2.2), e['e1'] - 0.35, 0.14, 0)
    m.drive = 2.0
    m.write('out/v61_audio.wav', peak_db=-2.0)


def build_v62():
    e = ev('v62')
    D = e['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(wind(D, 1.0), 0, 0.05, 0)
    # cold breath
    for k in range(6):
        ts = 0.15 + 0.62 * k
        if ts < e['warm_in'][1] + 0.4:
            m.add(breath(0.45, inhale=False), ts, 0.05, 0)
    # striking a light
    for k in range(4):
        m.add(scrape(0.12), e['strike'][0] + 0.1 + 0.09 * k, 0.05, 0)
    m.add(clack(3.0, 0.2), e['strike'][1] - 0.06, 0.08, 0)
    m.add(puff(), e['catch'][0], 0.16, 0)
    c0 = e['catch'][0]
    m.add(fire_bed(D - c0), c0, 0.07, 0)
    # B: sujood each time, and a note as each word lands
    for k, a in enumerate(e['ev']):
        m.add(cloth(0.3), a, 0.07, 0.25)
        m.add(cloth(0.25), a + 0.5, 0.05, 0.25)
        m.add(pluck([523, 659, 784][k]), a + e['suj_len'] - 0.12, 0.09, 0.25)
        m.add(pluck(196), a + e['suj_len'] - 0.12, 0.035, -0.25)
    # A: hands up to the sky
    m.add(cloth(0.35), e['a_dua'][0], 0.06, -0.25)
    # warming up
    m.add(cloth(0.35), e['warm_in'][0], 0.05, 0)
    # the pot
    m.add(cloth(0.4), e['pot_lift'][0] - 0.1, 0.05, 0)
    m.add(clack(1.6, 0.6), e['pot_lift'][1] - 0.04, 0.09, 0)
    m.add(simmer(D - e['steam0']), e['steam0'], 0.05, 0)
    m.add(cloth(0.3), e['a_almost'][0] + 0.1, 0.05, -0.25)
    m.add(swell(2.2), e['e1'] - 0.35, 0.14, 0)
    m.drive = 2.0
    m.write('out/v62_audio.wav', peak_db=-2.0)


def build_v63():
    e = ev('v63')
    D = e['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(wind(D, 0.6), 0, 0.03, 0)
    kun = e['kun'] + [e['final_kun']]
    for k, t in enumerate(kun):
        m.add(thump(48, 0.18, 0.05), t, 0.22, 0)
        m.add(swell(1.2), t - 0.1, 0.05, 0)
    r = e['ring']
    # 1. fire catches in both; below, the log crackles and burns down
    m.add(puff(), kun[0] + r, 0.16, 0)
    m.add(fire_bed(D - kun[0] - r), kun[0] + r, 0.05, 0)
    for k in range(6):
        m.add(clack(2.4 + 0.3 * k, 0.15), kun[0] + r + 0.4 + 0.18 * k, 0.03, 0.2)
    # 2. water: the sea rises into walls / rain falls
    m.add(rumble(1.0), kun[1] + r, 0.09, -0.2)
    m.add(whoosh(0.8, 160, 900), kun[1] + r, 0.1, -0.2)
    m.add(rain_bed(1.9), kun[1] + r + 0.3, 0.06, 0.2)
    # 3. the moon rises; on top it splits
    m.add(swell(1.4), kun[2] + r, 0.07, 0)
    m.add(thwang(), kun[2] + r + 1.0, 0.06, -0.2)
    m.add(swell(2.2), e['e1'] - 0.35, 0.12, 0)
    m.drive = 2.0
    m.write('out/v63_audio.wav', peak_db=-2.0)


def build_v64():
    e = ev('v64')
    D = e['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    for r, t0 in enumerate(e['rounds']):
        # the argument: sharp crackles
        for k in range(4):
            m.add(clack(2.2 + 0.3 * k, 0.4), t0 + 0.08 + 0.12 * k, 0.07, 0)
        for i in range(e['per']):
            tb = t0 + e['form'] + 0.07 * i
            m.add(thunk(), tb + 0.4, 0.05, -0.25)               # top: bricks land in the wall
            if r * e['per'] + i < e['n_house']:
                m.add(clack(1.4, 0.8), tb + 0.42, 0.04, 0.25)    # bottom: bricks land in the house
        m.add(cloth(0.3), t0 + e['argue'], 0.05, 0.25)
    t0 = e['rounds'][2] + e['form']
    m.add(thunk(), t0 + 0.55, 0.1, 0.25)                         # the roof goes on
    m.add(pluck(523), t0 + 0.7, 0.08, 0.25)
    m.add(pluck(659), t0 + 0.82, 0.07, 0.25)
    w0, w1 = e['b_wife_walk']
    t = w0 + 0.1
    while t < w1:
        m.add(step(0.6), t, 0.08, 0.25)
        t += 0.3
    m.add(swell(2.2), e['e1'] - 0.35, 0.14, 0)
    m.drive = 2.0
    m.write('out/v64_audio.wav', peak_db=-2.0)


def build_v65():
    e = ev('v65')
    D = e['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(city(D), 0, 0.015, 0)
    for t0 in e['rounds']:
        m.add(whoosh(e['jab'] + 0.05, 600, 2400), t0, 0.08, 0)
        m.add(thump(90, 0.05, 0.4), t0 + e['jab'], 0.16, 0)
    for t0 in e['vent_at']:
        t = t0
        while t < t0 + 0.9:
            m.add(tick(), t, 0.03, -0.25)                        # typing
            t += 0.09
    for k, tf in enumerate(e['flights']):
        m.add(pluck(1047 - 40 * k), tf, 0.05, -0.25)
        m.add(pluck(523), tf + e['fly'], 0.04, 0.3)
    m.add(cloth(0.25), e['almost'][0], 0.05, -0.25)
    for ta in e['b_add']:
        m.add(pluck(784), ta, 0.07, 0.25)
    m.add(swell(2.2), e['e1'] - 0.35, 0.14, 0)
    m.drive = 2.0
    m.write('out/v65_audio.wav', peak_db=-2.0)


def build_v66():
    e = ev('v66')
    D = e['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(wind(D, 0.6), 0, 0.02, 0)
    for d0 in e['days']:
        for k in range(3):
            m.add(chirp(), d0 + 0.05 + 0.13 * k, 0.05, 0.3)    # hungry chicks
        m.add(flutter(0.5), d0 + 0.1, 0.06, 0.3)
        m.add(flutter(0.45), d0 + 1.15, 0.06, 0.3)
        m.add(chirp(), d0 + 1.62, 0.06, 0.3)
        m.add(chirp(), d0 + 1.72, 0.05, 0.3)
        # bottom: du'a, out the door, back
        m.add(cloth(0.3), d0 + 0.2, 0.05, 0.2)
        for k in range(3):
            m.add(step(0.8), d0 + 0.6 + 0.15 * k, 0.1, 0.2)
        m.add(creak_pull(0.3), d0 + 0.8, 0.04, 0.2)
        m.add(creak_pull(0.3), d0 + 1.3, 0.04, 0.2)
        for k in range(3):
            m.add(step(0.8), d0 + 1.32 + 0.14 * k, 0.1, 0.2)
        m.add(cloth(0.3), d0 + 1.8, 0.05, 0.2)
    # top: paper, the door he doesn't open
    for d0 in e['days'][:2]:
        m.add(cloth(0.3), d0 + 0.05, 0.05, -0.2)
        m.add(knock(), d0 + 0.85, 0.04, -0.2)
        m.add(page(), d0 + 1.6, 0.05, -0.2)
    m.add(page(), e['days'][2] + 0.4, 0.05, -0.2)
    m.add(swell(2.2), e['e1'] - 0.35, 0.14, 0)
    m.drive = 2.0
    m.write('out/v66_audio.wav', peak_db=-2.0)


def build_v67():
    e = ev('v67')
    D = e['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    for t in np.arange(0.2, D, 1.0):
        m.add(tick(), t, 0.015, 0.4)                             # a clock in the room
    t = 0.2
    while t < e['asks'][3]:
        m.add(tick(), t, 0.02, 0.3)                              # typing
        t += 0.13
    for k, a in enumerate(e['asks']):
        m.add(pluck(440), a + 0.05, 0.05, -0.3)                  # his question
        m.add(pluck(330 if k < 3 else 294), a + 0.45, 0.04, 0.3) # an answer
    m.add(thump(70, 0.08, 0.3), e['asks'][3] + 0.4, 0.14, 0.3)    # uff
    m.add(cloth(0.3), e['asks'][4] + 0.15, 0.05, 0.3)
    w0, w1 = e['b_walk']
    for k in range(3):
        m.add(step(0.6), w0 + 0.2 + 0.14 * k, 0.07, 0.1)
    m.add(swell(2.0), e['mem'][0] - 0.1, 0.06, 0)
    for k, ta in enumerate(e['kid_asks']):
        m.add(pluck(880 + 20 * (k % 5)), ta, 0.018, 0)
    m.add(swell(2.2), e['e1'] - 0.35, 0.12, 0)
    m.drive = 2.0
    m.write('out/v67_audio.wav', peak_db=-2.0)


def build_v68():
    e = ev('v68')
    D = e['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    for k, r in enumerate(e['rounds']):
        m.add(pluck(1175), r + 0.05, 0.06, 0.3)                  # a notification
        m.add(pluck(1568), r + 0.12, 0.04, 0.3)
        m.add(cloth(0.3), r + 0.4, 0.05, 0.2)
        m.add(pluck([392, 440, 494][k]), r + 0.75, 0.06, 0.2)    # bottom: alhamdulillah
        for j in range(3):
            m.add(step(0.4), r + 0.65 + 0.15 * j, 0.05, -0.1)
    r = e['rounds'][2]
    for j in range(5):
        m.add(step(0.6), r + 0.5 + 0.22 * j, 0.06, -0.2)
    m.add(creak_pull(0.3), r + 1.05, 0.05, -0.3)
    m.add(thunk(), r + 1.75, 0.08, -0.3)                         # the door closes
    m.add(swell(2.2), e['e1'] - 0.35, 0.14, 0)
    m.drive = 2.0
    m.write('out/v68_audio.wav', peak_db=-2.0)


def build_v69(name='v69'):
    e = ev(name)
    D = e['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(wind(D, 0.7), 0, 0.03, 0)
    for k, y in enumerate(e['years']):
        m.add(cloth(0.25), y + 0.1, 0.04, 0)
        # bottom: the phone rings over there
        for j in range(3):
            m.add(beep(880, 0.08), y + 0.32 + 0.22 * j, 0.03, 0.4)
            m.add(beep(988, 0.08), y + 0.42 + 0.22 * j, 0.03, 0.4)
        m.add(clack(1.5, 0.6), y + 1.3, 0.06, -0.1)                # a plank lands
    c0, c1 = e['cross']
    m.add(clack(1.5, 0.6), e['years'][2] + 1.25, 0.06, 0.2)
    t = c0 + 0.2
    while t < c1:
        m.add(step(0.7), t, 0.07, 0)
        t += 0.2
    m.add(cloth(0.5), c1, 0.08, 0)
    m.add(pluck(523), c1 + 0.05, 0.07, 0)
    m.add(pluck(659), c1 + 0.17, 0.06, 0)
    m.add(swell(2.2), e['e1'] - 0.35, 0.14, 0)
    m.drive = 2.0
    m.write(f'out/{name}_audio.wav', peak_db=-2.0)


def build_v69e():
    """the Ember/lanes.py version of Call First (examples/v69_callfirst_ember.py): same sound."""
    build_v69('v69e')


def formula_beats(m, e):
    """the shared beat sounds of the formula reels: a soft whoosh in on each value, a small tick on each open loop."""
    b = e['beats']
    for k in ('v1', 'v2', 'v3'):
        m.add(whoosh(0.35, 400, 2200), b[k][0] - 0.08, 0.05, 0)
    for k in ('l1', 'l2'):
        m.add(tick(), b[k][0] + 0.02, 0.06, 0)
        m.add(pluck(1047), b[k][0] + 0.04, 0.025, 0)


def build_v70():
    e = ev('v70')
    D = e['dur']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    formula_beats(m, e)
    # wudu: the tap runs, water on hands, face, feet
    w0, w1 = e['wash'][0][0], e['wash'][-1][1]
    m.add(water_run(w1 - w0 + 0.3), w0 - 0.1, 0.05, 0.2)
    for a, b in e['wash']:
        m.add(splash_snd(0.5), a + 0.1, 0.05, 0.2)
        m.add(splash_snd(0.4), (a + b) / 2, 0.04, 0.2)
    for g in sorted(e['gone']):
        if g < 6.0:
            m.add(pluck(1568 + 60 * (int(g * 10) % 4)), g, 0.02, 0.2)   # a drop falls
    # walking: steps, and every other step rises with a note
    t = e['beats']['l1'][0] + 0.15
    while t < e['steps'][0]:
        m.add(step(0.8), t, 0.07, 0)
        t += 0.42
    for k, ts in enumerate(e['steps']):
        m.add(step(0.8), ts, 0.08, 0.1)
        if k % 2 == 0:
            m.add(pluck(1175), ts + 0.15, 0.025, 0.1)                    # a sin erased
        else:
            m.add(pluck([392, 440, 523, 587][k // 2]), ts + 0.05, 0.05, 0.1)  # raised
    # the foam of the sea, fizzing away while he counts
    f0, f1 = e['foam']
    m.add(water_bed(f1 - f0 + 0.6, 0.6), f0 - 0.3, 0.035, -0.4)
    for k in range(40):
        tk = f0 + (f1 - f0) * (k / 40) ** 0.85
        m.add(tick(), tk, 0.025, 0.3)                                    # the tasbih
    m.add(swell(2.2), e['beats']['cta'][0] - 0.35, 0.12, 0)
    m.drive = 2.0
    m.write('out/v70_audio.wav', peak_db=-2.0)


def build_v71():
    e = ev('v71')
    D = e['dur']
    b = e['beats']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    formula_beats(m, e)
    t = 0.15
    while t < b['v1'][0] + 0.6:
        m.add(tick(), t, 0.022, 0.2)                              # thumb on the screen
        t += 0.28
    a0, a1 = e['adhan']
    m.add(swell(2.4), a0 - 0.1, 0.06, 0.35)                        # the adhan, from the minaret
    m.add(pluck(392), a0, 0.03, 0.4)
    m.add(thunk(), b['v1'][0] + 0.72, 0.05, 0.2)                   # phone face down
    for d0 in (e['dua1'][0] + 0.45, e['suj'][0] + 0.25, e['dua3'][0] + 0.45):
        for k, f in enumerate((523, 659, 784)):
            m.add(pluck(f), d0 + 0.2 * k, 0.045, 0)                # the du'a rises
        m.add(swell(1.8), d0 + 0.9, 0.07, 0)                       # and comes back
    for tp in e['pray'][1::2]:
        m.add(cloth(0.22), tp - 0.1, 0.05, 0.1)
    s0 = e['sleep'][0]
    m.add(cloth(0.4), s0 + 0.1, 0.06, 0)
    m.add(crickets(D - s0), s0, 0.006, 0.5)
    for tc in np.arange(s0 + 0.4, b['v3'][0] + 1.2, 0.5):
        m.add(tick(), tc, 0.02, -0.3)                              # a clock at night
    m.add(cloth(0.45), e['wake'][0], 0.07, 0)
    m.add(swell(2.2), b['cta'][0] - 0.35, 0.12, 0)
    m.drive = 2.0
    m.write('out/v71_audio.wav', peak_db=-2.0)


def build_v72():
    e = ev('v72')
    D = e['dur']
    b = e['beats']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(wind(D, 0.6), 0, 0.025, 0)
    formula_beats(m, e)
    for k in range(6):
        m.add(pluck(1047 + 80 * (k % 3)), 0.05 + 0.18 * k, 0.02, 0.3)   # his deeds, while he lives
    m.add(thump(60, 0.12, 0.2), e['fade'][0] + 0.2, 0.12, 0.3)
    m.add(scrape(0.5), e['mound'][0], 0.05, 0.3)
    for d in e['drinks']:
        m.add(creak_pull(0.35), d - 0.6, 0.04, -0.4)
        m.add(splash_snd(0.3), d - 0.1, 0.03, -0.4)
    m.add(cloth(0.8), e['tree'][0], 0.04, -0.6)
    scale = [523, 587, 659, 784, 880, 1047]
    for k, a in enumerate(e['arrive']):
        m.add(pluck(scale[k % 6]), a, 0.022, 0.3)                    # a light reaches the grave
    for s0, s1 in (e['spark1'], e['spark2']):
        m.add(pluck(659), s0, 0.04, 0)
        m.add(pluck(988), s1, 0.04, 0)
    m.add(cloth(0.3), e['b_stand'][0], 0.05, 0)
    k0, k1 = e['kid_walk']
    t = k0 + 0.1
    while t < k1:
        m.add(step(0.5), t, 0.05, 0.4)
        t += 0.26
    m.add(swell(3.0), e['kid_dua'][0], 0.08, 0.3)
    m.add(sparkle(D - e['kid_dua'][0] - 0.3), e['kid_dua'][0] + 0.3, 0.012, 0.3)
    m.add(swell(2.2), b['cta'][0] - 0.35, 0.12, 0)
    m.drive = 2.0
    m.write('out/v72_audio.wav', peak_db=-2.0)


def build_v73():
    e = ev('v73')
    D = e['dur']
    b = e['beats']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    formula_beats(m, e)
    for k, (a, z) in enumerate(e['say']):
        m.add(whoosh(z - a, 300, 1200), a, 0.03, -0.3)            # the word drifts over
        m.add(pluck([523, 659, 784][k]), a + 0.05, 0.04, -0.4)
    for k, ti in enumerate(e['impacts']):
        w = [0.10, 0.16, 0.16, 0.24][k]
        m.add(thump([70, 52, 52, 44][k], 0.12, 0.4), ti, w, -0.1)  # lands in his pan
        m.add(creak_pull(0.3), ti + 0.05, 0.03, 0.1)               # the beam swings
    m.add(swell(1.0), e['fill'][0], 0.05, -0.2)
    mi = e['msg_in']
    m.add(beep(1250, 0.07), mi, 0.05, -0.5)                        # the rude message
    m.add(beep(1250, 0.07), mi + 0.11, 0.05, -0.5)
    t = e['type'][0]
    while t < e['type'][1]:
        m.add(tick(), t, 0.03, -0.5)                               # typing back
        t += 0.07
    m.add(cloth(0.4), e['calm'][0], 0.06, -0.4)                    # hand on his chest
    m.add(pluck(880), e['reply'], 0.05, -0.5)                      # sent something kind
    m.add(whoosh(0.4, 200, 900), e['block'][0], 0.06, -0.2)
    m.add(rattle(0.5), e['block'][1] + 0.03, 0.05, 0.4)            # the stones jump
    m.add(swell(2.2), b['cta'][0] - 0.35, 0.12, 0)
    m.drive = 2.0
    m.write('out/v73_audio.wav', peak_db=-2.0)


def build_v74():
    e = ev('v74')
    D = e['dur']
    b = e['beats']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(crickets(D), 0, 0.005, 0.5)
    formula_beats(m, e)
    for tc in np.arange(0.3, D, 1.0):
        m.add(tick(), tc, 0.016, 0.5)                              # the clock
    t = 0.1
    while t < e['phone_down'][0]:
        m.add(tick(), t, 0.02, -0.2)                               # scrolling
        t += 0.3
    m.add(wind(e['dome1'][0] + 0.4, 1.0), 0, 0.03, 0)              # the worries
    m.add(thunk(), e['phone_down'][1], 0.04, 0.4)                  # phone down
    m.add(cloth(0.4), e['sit1'][0], 0.06, 0)
    m.add(swell(1.6), e['dome1'][0], 0.08, 0)
    m.add(pluck(523), e['dome1'][0] + 0.3, 0.05, 0)
    m.add(pluck(659), e['dome1'][0] + 0.45, 0.04, 0)
    for k, h in enumerate(e['hits']):
        m.add(puff(), h, 0.04, -0.4 if k % 2 == 0 else 0.4)        # a worry breaks on it
    m.add(swell(1.6), e['dome2'][0], 0.09, 0)
    for k, f in enumerate((523, 659, 784)):
        m.add(pluck(f), e['dome2'][0] + 0.3 + 0.12 * k, 0.04, 0)
    m.add(cloth(0.5), e['lie_back'][0], 0.06, 0)
    c0, c1 = e['count']
    for k in range(34):
        m.add(tick(), c0 + (c1 - c0) * k / 34, 0.018, 0.1)         # counting
    for k, f in enumerate((392, 440, 494)):
        m.add(pluck(f), c0 + (c1 - c0) * (k + 1) / 3, 0.04, 0)     # 33, 66, 100
    m.add(swell(2.4), e['sleeps'][0], 0.07, 0)
    m.add(swell(2.2), b['cta'][0] - 0.35, 0.10, 0)
    m.drive = 2.0
    m.write('out/v74_audio.wav', peak_db=-2.0)


def build_v75():
    e = ev('v75')
    D = e['dur']
    b = e['beats']
    m = Mix(D)
    m.add(room(D, 0.012), 0, 1.0)
    m.add(wind(D, 0.8), 0, 0.035, 0)
    formula_beats(m, e)
    w0, w1 = e['walk_in']
    t = w0 + 0.1
    while t < w1:
        m.add(step(0.8), t, 0.07, 0)
        m.add(step(0.8), t + 0.16, 0.06, 0.1)
        t += 0.32
    m.add(rumble(w1 - w0), w0, 0.025, -0.3)                        # the cart rolls after him
    l0, l1 = e['lower']
    m.add(cloth(0.6), l0, 0.07, 0.3)
    m.add(thump(60, 0.12, 0.3), l1 - 0.05, 0.12, 0.3)
    m.add(scrape(0.6), e['mound'][0], 0.06, 0.3)
    h0, h1 = e['walk_home']
    t = h0 + 0.05
    while t < h1 + 0.3:
        m.add(step(0.7), t, 0.06, -0.2)
        t += 0.34
    for d0, d1 in (e['door1'], e['door2']):
        m.add(creak_pull(0.35), d0, 0.04, -0.6)
        m.add(thunk(), d1 - 0.1, 0.06, -0.6)
    c0, c1 = e['cart_home']
    m.add(rumble(c1 - c0), c0, 0.03, -0.3)
    s0, s1 = e['sink']
    for k, f in enumerate((784, 659, 523)):
        m.add(pluck(f), s0 + 0.25 * k, 0.05, 0.3)                  # the three that stay
    m.add(swell(2.0), s1 - 0.4, 0.07, 0.3)
    m.add(swell(2.2), b['cta'][0] - 0.35, 0.10, 0)
    m.drive = 2.0
    m.write('out/v75_audio.wav', peak_db=-2.0)


if __name__ == '__main__':
    globals()['build_' + sys.argv[1]]()
    print('ok', sys.argv[1])
