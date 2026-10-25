"""Lay an Alafasy recitation over the end of a Qur'an reel, duck the SFX under it, and mux to out/<name>.mp4.
Add a CFG entry per reel: name (output file stem), file (SSSAAA in audio_src/hq), seg (start, end seconds of the
relevant words inside that mp3), start (when the recitation starts in the reel), optional fo (fade-out), duck,
keep_video_len (never shorten the video). Run: python3 quran_mix.py vXX. Needs out/vXX_silent.mp4 + out/vXX_audio.wav."""
import json, subprocess, sys
import numpy as np
from scipy.io import wavfile

SR = 48000
CFG = {
    'v10': dict(name='The_Bounce', file='015099', seg=(0.0, 7.59), start=3.3),
    'v11': dict(name='The_Arrow', file='053040', seg=(0.0, 4.48), start=3.2),
    'v12': dict(name='The_Nails', file='003135', seg=(33.0, 40.3), start=3.3),
    'v13': dict(name='The_Zigzag', file='013028', seg=(10.6, 18.35), start=4.6),
    'v14': dict(name='The_Loop', file='033041', seg=(0.05, 7.34), start=3.5),
    'v15': dict(name='Right_Reasons', file='024031', seg=(16.6, 23.68), start=3.2),
    'v41': dict(name='Every_Sin_Another_Brick_v2', file='039053', seg=(15.42, 21.37), start=5.25),
    'v42': dict(name='Flowers_v2', file='002216', seg=(4.62, 11.95), start=3.3),
    'v45': dict(name='The_Rock', file='027062', seg=(0.0, 9.07), start=0.9, fo=0.06, duck=0.6),
    'v46': dict(name='The_Palm', file='019025', seg=(0.0, 6.12), start=2.48, fo=0.08),
    'v47': dict(name='Fair', file='002237', seg=(28.25, 32.05), start=4.6, fo=0.1),
    'v49': dict(name='Fair_Women', file='002237', seg=(28.25, 32.05), start=4.6, fo=0.1),
    'v52': dict(name='The_Rope', file='024022', seg=(21.86, 27.94), start=2.37, fo=0.08),
    'v53': dict(name='Small_Things', file='014007', seg=(0.0, 8.05), start=0.45, fo=0.08, duck=0.65),
    'v54': dict(name='Ready', file='024032', seg=(11.4, 20.5), start=0.15, fo=0.08, duck=0.65),
    'v55': dict(name='Rest', file='013028', seg=(10.6, 18.35), start=0.8, duck=0.65),
    'v56': dict(name='Everything_But_Him', file='017024', seg=(5.29, 11.05), start=2.69),
    'v48': dict(name='Both_of_Them', file='004130', seg=(0.0, 7.3), start=0.9, fo=0.08, duck=0.65),
    'v40': dict(name='Right_Reasons_v2', file='024031', seg=(16.6, 23.68), start=2.2),
    'v17': dict(name='They_Held_Your_Hand', file='017024', seg=(5.29, 11.05), start=3.6),
    'v20': dict(name='The_Rain', file='002216', seg=(4.62, 11.95), start=3.2),
    'v9': dict(name='Waiting_for_a_Thank_You', file='076009', seg=(0.0, 11.7), start=2.0),
    'v23': dict(name='Too_Far_Gone', file='039053', seg=(15.42, 21.37), start=6.15),
    'v24': dict(name='Running_on_Empty', file='055060', seg=(0.0, 8.4), start=4.3),
    'v62': dict(name='The_Fire', file='021069', seg=(0.0, 10.9), start=0.1, fo=0.1, duck=0.65),
    'v63': dict(name='Same_Word', file='036082', seg=(9.12, 16.75), start=1.82, fo=0.15, duck=0.65),
    'v67': dict(name='Twenty_One', file='017023', seg=(27.2, 34.15), start=1.7, fo=0.15, duck=0.65, keep_video_len=True),
    'v5': dict(name='No_Time_for_Quran', parts=[('087016', (0.0, 4.3)), ('087017', (0.0, 4.65))], gap=0.25, start=4.3),
}
TAIL = 0.45


def load_rec(f, a, b, fo_s=0.25):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(a), '-to', str(b), '-i', f'audio_src/hq/{f}.mp3',
                          '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = len(x)
    fi = int(0.06 * SR)
    fo = int(fo_s * SR)
    x[:fi] *= np.linspace(0, 1, fi)[:, None]
    x[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return x


def load_cfg_rec(c):
    """one ayah cut (file + seg), or several cuts in a row (parts) with a short gap between them."""
    if 'parts' not in c:
        return load_rec(c['file'], *c['seg'], c.get('fo', 0.25))
    gap = np.zeros((int(c.get('gap', 0.25) * SR), 2), np.float32)
    out = []
    for k, (f, (a, b)) in enumerate(c['parts']):
        if k:
            out.append(gap)
        out.append(load_rec(f, a, b))
    return np.vstack(out)


def rec_dur(v):
    c = CFG[v]
    if 'parts' in c:
        return sum(b - a for _, (a, b) in c['parts']) + c.get('gap', 0.25) * (len(c['parts']) - 1)
    a, b = c['seg']
    return b - a


def new_dur(v):
    return round(CFG[v]['start'] + rec_dur(v) + TAIL, 2)


def mix(v):
    c = CFG[v]
    D = new_dur(v)
    if c.get('keep_video_len'):
        vd0 = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                    f'out/{v}_silent.mp4'], capture_output=True, text=True).stdout)
        D = max(D, round(vd0, 2))
    sr, sfx = wavfile.read(f'out/{v}_audio.wav')
    sfx = sfx.astype(np.float32) / 32767
    n = int(D * SR)
    if len(sfx) < n:
        sfx = np.vstack([sfx, np.zeros((n - len(sfx), 2), np.float32)])
    sfx = sfx[:n]
    t = np.arange(n) / SR
    duck = 1 - c.get('duck', 0.8) * np.clip((t - (c['start'] - 0.3)) / 0.3, 0, 1)
    out = sfx * 0.42 * duck[:, None]
    rec = load_cfg_rec(c)
    i = int(c['start'] * SR)
    m = min(len(rec), n - i)
    out[i:i + m] += rec[:m] * 1.6
    fo = int(0.2 * SR)
    out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    out = np.tanh(out * 1.3) / np.tanh(1.3)
    out = out / (np.abs(out).max() + 1e-9) * 10 ** (-1.5 / 20)
    wavfile.write(f'out/{v}_final.wav', SR, (out * 32767).astype(np.int16))
    vd = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                               f'out/{v}_silent.mp4'], capture_output=True, text=True).stdout)
    vf = f'tpad=stop_mode=clone:stop_duration={max(0.0, D - vd) + 0.1:.2f}'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f'out/{v}_silent.mp4', '-i', f'out/{v}_final.wav',
                    '-vf', vf, '-t', str(D), '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', f"out/{c['name']}.mp4"], check=True)
    return D


if __name__ == '__main__':
    which = sys.argv[1:] or list(CFG)
    if which[0] == 'durs':
        for v in CFG:
            print(v, new_dur(v))
    else:
        for v in which:
            print(CFG[v]['name'], mix(v))
