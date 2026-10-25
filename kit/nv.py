"""Minimal renderer for neuronvisuals-style reels: black void, faceless white
pictogram figures, glossy reflections, spaced mono labels, one red accent."""
import math, os, subprocess
import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
TF_MED = skia.Typeface.MakeFromFile(os.path.join(HERE, 'fonts', 'IBMPlexMono-Medium.ttf'))
TF_REG = skia.Typeface.MakeFromFile(os.path.join(HERE, 'fonts', 'IBMPlexMono-Regular.ttf'))

BG_IN = (25, 27, 31)
BG_OUT = (6, 7, 9)
WHITE = (238, 238, 235)
FAR = (128, 131, 136)
LABEL = (205, 206, 208)
DIM = (120, 122, 126)
RED = (200, 42, 48)


def C(rgb, a=1.0):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(round(255 * max(0, min(1, a)))))


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, u):
    return a + (b - a) * u


def ease(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = clamp(u)
    return 1 - (1 - u) ** 3


def ease_in(u):
    u = clamp(u)
    return u ** 3


def seg(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))


# ---------------------------------------------------------------- poses
KEYS = ['t', 'hd', 'Lth', 'Lkn', 'Rth', 'Rkn', 'Lua', 'Lel', 'Rua', 'Rel']


def P(**kw):
    d = dict(t=0, hd=0, Lth=-4, Lkn=0, Rth=4, Rkn=0, Lua=-7, Lel=6, Rua=7, Rel=6)
    d.update(kw)
    return d


def mix(a, b, u):
    return {k: lerp(a[k], b[k], u) for k in KEYS}


def chain(t, keys):
    """keys: list of (time, pose). Eased interpolation between neighbours."""
    if t <= keys[0][0]:
        return dict(keys[0][1])
    for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
        if t <= t1:
            return mix(p0, p1, ease(seg(t, t0, t1)))
    return dict(keys[-1][1])


def walk(phase, stride=26, back=False):
    """Walk cycle pose at phase (cycles)."""
    s = math.sin(2 * math.pi * phase)
    c = math.cos(2 * math.pi * phase)
    sign = -1 if back else 1
    return P(t=3 * sign, hd=2,
             Lth=stride * s, Lkn=max(0, 30 * c) + 4,
             Rth=-stride * s, Rkn=max(0, -30 * c) + 4,
             Lua=-20 * s, Lel=14, Rua=20 * s, Rel=14)


# library (facing right, degrees). angles measured from straight down,
# positive = toward facing direction.
STAND = P(Lua=-4, Lel=5, Rua=5, Rel=5)
STAND_TALL = P(t=-3, hd=-4)
LOOK_UP = P(t=-9, hd=-14, Lua=-12, Rua=-6)
HAND_HEAD = P(t=-4, hd=10, Rua=128, Rel=112, Lua=-6, Lel=8)
BOTH_HEAD = P(t=-2, hd=12, Rua=155, Rel=150, Lua=150, Lel=150)
BEND = P(t=78, hd=14, Lth=12, Lkn=22, Rth=16, Rkn=26, Lua=-4, Lel=2, Rua=2, Rel=2)
CARRY = P(t=4, hd=6, Lua=34, Lel=62, Rua=40, Rel=62)
SIT = P(t=22, hd=32, Lth=104, Lkn=128, Rth=112, Rkn=134, Lua=62, Lel=48, Rua=68, Rel=48)
SIT_UP = P(t=2, hd=-10, Lth=104, Lkn=128, Rth=112, Rkn=134, Lua=50, Lel=40, Rua=56, Rel=40)
LOOK_DOWN = P(t=24, hd=30, Lua=-22, Lel=6, Rua=-14, Rel=6)
RECOIL = P(t=-14, hd=-6, Lth=-12, Lkn=6, Rth=10, Rkn=4, Lua=-40, Lel=30, Rua=40, Rel=60)
THINK = P(t=-2, hd=10, Rua=70, Rel=125, Lua=20, Lel=95)
CROUCH = P(t=42, hd=10, Lth=58, Lkn=104, Rth=66, Rkn=110, Lua=-58, Lel=6, Rua=-50, Rel=6)
TAKBIR = P(hd=6, Lua=66, Lel=108, Rua=72, Rel=108)
QIYAM = P(hd=14, Lua=-6, Lel=96, Rua=-2, Rel=96)
RUKU = P(t=88, hd=0, Lth=-6, Lkn=0, Rth=-2, Rkn=0, Lua=-6, Lel=0, Rua=-2, Rel=0)
SUJUD = P(t=100, hd=40, Lth=8, Lkn=98, Rth=12, Rkn=102, Lua=40, Lel=50, Rua=44, Rel=50)
JULUS = P(t=2, hd=12, Lth=86, Lkn=174, Rth=90, Rkn=176, Lua=26, Lel=44, Rua=30, Rel=44)


class Figure:
    def __init__(self, h, near=WHITE, far=FAR):
        self.h = h
        self.r = 0.085 * h
        self.torso = 0.30 * h
        self.thigh = 0.235 * h
        self.shin = 0.235 * h
        self.uarm = 0.165 * h
        self.farm = 0.155 * h
        self.lw = 0.074 * h
        self.tw = 0.12 * h
        self.gap = 0.03 * h
        self.near = near
        self.far = far

    @staticmethod
    def _down(f, ang):
        a = math.radians(ang)
        return np.array([f * math.sin(a), math.cos(a)])

    @staticmethod
    def _up(f, ang):
        a = math.radians(ang)
        return np.array([f * math.sin(a), -math.cos(a)])

    def joints(self, p, x, y, f):
        hip = np.array([x, y], float)
        up = self._up(f, p['t'])
        sh = hip + up * self.torso
        ash = hip + up * self.torso * 0.86
        head = sh + self._up(f, p['t'] + p['hd']) * (self.tw / 2 + self.gap + self.r)
        j = dict(hip=hip, sh=sh, ash=ash, head=head, f=f)
        for s in 'LR':
            k = hip + self._down(f, p[s + 'th']) * self.thigh
            ft = k + self._down(f, p[s + 'th'] - p[s + 'kn']) * self.shin
            e = ash + self._down(f, p[s + 'ua']) * self.uarm
            hd = e + self._down(f, p[s + 'ua'] + p[s + 'el']) * self.farm
            j[s + 'k'], j[s + 'f'], j[s + 'e'], j[s + 'h'] = k, ft, e, hd
        return j

    def solve(self, p, x, f, ground=None, y=0.0):
        j = self.joints(p, x, y, f)
        if ground is not None:
            r = self.lw / 2
            low = max(j['Lf'][1] + r, j['Rf'][1] + r, j['Lk'][1] + r, j['Rk'][1] + r,
                      j['hip'][1] + self.tw / 2, j['head'][1] + self.r,
                      j['Lh'][1] + r, j['Rh'][1] + r)
            j = self.joints(p, x, y + ground - low, f)
        return j

    def _limb(self, c, pts, color, a, w):
        path = skia.Path()
        path.moveTo(*pts[0])
        for q in pts[1:]:
            path.lineTo(*q)
        c.drawPath(path, skia.Paint(AntiAlias=True, Color=C(color, a), Style=skia.Paint.kStroke_Style,
                                    StrokeWidth=w, StrokeCap=skia.Paint.kRound_Cap,
                                    StrokeJoin=skia.Paint.kRound_Join))

    def draw(self, c, j, a=1.0, near=None, far=None, held=None):
        near = near or self.near
        far = far or self.far
        self._limb(c, [j['ash'], j['Le'], j['Lh']], far, a, self.lw)
        self._limb(c, [j['hip'], j['Lk'], j['Lf']], far, a, self.lw)
        self._limb(c, [j['hip'], j['sh']], near, a, self.tw)
        self._limb(c, [j['hip'], j['Rk'], j['Rf']], near, a, self.lw)
        self._limb(c, [j['ash'], j['Re'], j['Rh']], near, a, self.lw)
        if held:
            held()
        c.drawCircle(j['head'][0], j['head'][1], self.r, skia.Paint(AntiAlias=True, Color=C(near, a)))


# ---------------------------------------------------------------- drawing helpers
def rect(c, x, y, w, h, color, a=1.0, r=0):
    p = skia.Paint(AntiAlias=True, Color=C(color, a))
    if r:
        c.drawRoundRect(skia.Rect(x, y, x + w, y + h), r, r, p)
    else:
        c.drawRect(skia.Rect(x, y, x + w, y + h), p)


def line(c, x0, y0, x1, y1, color, w=2, a=1.0, cap=True):
    c.drawLine(x0, y0, x1, y1, skia.Paint(AntiAlias=True, Color=C(color, a), StrokeWidth=w,
                                          Style=skia.Paint.kStroke_Style,
                                          StrokeCap=skia.Paint.kRound_Cap if cap else skia.Paint.kButt_Cap))


def brick(c, x, y, w, h, color=(206, 202, 195), a=1.0, rot=0.0):
    c.save()
    if rot:
        c.translate(x + w / 2, y + h / 2)
        c.rotate(rot)
        c.translate(-(x + w / 2), -(y + h / 2))
    sh = skia.GradientShader.MakeLinear(points=[(0, y), (0, y + h)],
                                        colors=[C(tuple(min(255, v + 22) for v in color), a), C(color, a),
                                                C(tuple(v * 0.62 for v in color), a)],
                                        positions=[0, 0.35, 1])
    c.drawRoundRect(skia.Rect(x, y, x + w, y + h), 2.2, 2.2, skia.Paint(AntiAlias=True, Shader=sh))
    c.restore()


def text(c, s, x, y, size, color=LABEL, a=1.0, spacing=0.22, tf=None, align='center'):
    if a <= 0:
        return
    font = skia.Font(tf or TF_MED, size)
    font.setSubpixel(True)
    adv = [font.measureText(ch) for ch in s]
    sp = size * spacing
    total = sum(adv) + sp * (len(s) - 1)
    if align == 'center':
        x -= total / 2
    elif align == 'right':
        x -= total
    p = skia.Paint(AntiAlias=True, Color=C(color, a))
    for ch, ad in zip(s, adv):
        c.drawString(ch, x, y, font, p)
        x += ad + sp
    return total


def background(c):
    sh = skia.GradientShader.MakeRadial(center=(W / 2, H * 0.52), radius=H * 0.62,
                                        colors=[C(BG_IN), C(BG_OUT)])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=sh))


def vignette(c, strength=0.55):
    sh = skia.GradientShader.MakeRadial(center=(W / 2, H * 0.5), radius=H * 0.72,
                                        colors=[C((0, 0, 0), 0), C((0, 0, 0), 0), C((0, 0, 0), strength)],
                                        positions=[0, 0.55, 1])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=sh))


def record(fn):
    rec = skia.PictureRecorder()
    rc = rec.beginRecording(skia.Rect(0, 0, W, H))
    fn(rc)
    return rec.finishRecordingAsPicture()


def draw_world(c, pic, bloom=0.32, sigma=13):
    if bloom > 0:
        c.saveLayer(None, skia.Paint(Alphaf=bloom, ImageFilter=skia.ImageFilters.Blur(sigma, sigma)))
        c.drawPicture(pic)
        c.restore()
    c.drawPicture(pic)


def reflection(c, pic, floor_y, strength=0.26, fade=320, ripple=None, t=0.0, blur=1.5):
    c.save()
    c.clipRect(skia.Rect(0, floor_y, W, H))
    lp = skia.Paint(Alphaf=strength)
    if blur:
        lp.setImageFilter(skia.ImageFilters.Blur(blur, blur * 2.5))
    c.saveLayer(None, lp)
    if ripple is None:
        c.save()
        c.translate(0, 2 * floor_y)
        c.scale(1, -1)
        c.drawPicture(pic)
        c.restore()
    else:
        amp, k, speed, strip = ripple
        y = floor_y
        while y < min(H, floor_y + fade + 10):
            d = (y - floor_y) / fade
            dx = amp * (0.4 + d) * math.sin(y * k + t * speed) + amp * 0.5 * d * math.sin(y * k * 2.3 - t * speed * 1.4)
            c.save()
            c.clipRect(skia.Rect(0, y, W, y + strip))
            c.translate(dx, 2 * floor_y)
            c.scale(1, -1)
            c.drawPicture(pic)
            c.restore()
            y += strip
    mask = skia.GradientShader.MakeLinear(points=[(0, floor_y), (0, floor_y + fade)],
                                          colors=[C((0, 0, 0), 1), C((0, 0, 0), 0)])
    c.drawRect(skia.Rect(0, floor_y, W, H), skia.Paint(Shader=mask, BlendMode=skia.BlendMode.kDstIn))
    c.restore()
    c.restore()


_GRAIN = []


def grain(c, i, a=0.07):
    if not _GRAIN:
        rng = np.random.default_rng(7)
        for _ in range(8):
            n = np.clip(rng.normal(128, 46, (H // 2, W // 2)), 0, 255).astype(np.uint8)
            rgba = np.dstack([n, n, n, np.full_like(n, 255)])
            _GRAIN.append(skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType))
    img = _GRAIN[i % len(_GRAIN)]
    c.drawImageRect(img, skia.Rect(0, 0, W, H), skia.SamplingOptions(skia.FilterMode.kLinear),
                    skia.Paint(Alphaf=a, BlendMode=skia.BlendMode.kOverlay))


def black(c, a):
    if a > 0:
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=C((0, 0, 0), a)))


# ---------------------------------------------------------------- output
class Writer:
    def __init__(self, path, fps=FPS):
        self.p = subprocess.Popen(
            ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra',
             '-s', f'{W}x{H}', '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'medium',
             '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path],
            stdin=subprocess.PIPE)

    def write(self, surface):
        self.p.stdin.write(surface.makeImageSnapshot().toarray().tobytes())

    def close(self):
        self.p.stdin.close()
        self.p.wait()


def render(draw_frame, n_frames, out_path, stills=None, still_dir=None):
    surface = skia.Surface(W, H)
    wr = Writer(out_path) if out_path else None
    for i in range(n_frames):
        c = surface.getCanvas()
        c.clear(skia.ColorBLACK)
        draw_frame(c, i / FPS, i)
        if wr:
            wr.write(surface)
        if stills and i in stills:
            surface.makeImageSnapshot().save(os.path.join(still_dir, f'f{i:04d}.png'), skia.kPNG)
    if wr:
        wr.close()


# ---------------------------------------------------------------- Arabic (HarfBuzz-shaped)
_AR = {}


def _ar_font(bold=False):
    key = 'b' if bold else 'r'
    if key not in _AR:
        import uharfbuzz as hb
        path = os.path.join(HERE, 'fonts', 'Amiri-Bold.ttf' if bold else 'Amiri-Regular.ttf')
        blob = hb.Blob.from_file_path(path)
        face = hb.Face(blob)
        font = hb.Font(face)
        upem = face.upem
        font.scale = (upem, upem)
        _AR[key] = (font, upem, skia.Typeface.MakeFromFile(path))
    return _AR[key]


def arabic(c, s, x, y, size, color=WHITE, a=1.0, align='center', bold=False):
    """Draw shaped Arabic text with baseline at y."""
    if a <= 0:
        return 0
    import uharfbuzz as hb
    font, upem, tf = _ar_font(bold)
    buf = hb.Buffer()
    buf.add_str(s)
    buf.guess_segment_properties()
    hb.shape(font, buf, {'kern': True, 'liga': True})
    k = size / upem
    glyphs, pts = [], []
    pen = 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        glyphs.append(info.codepoint)
        pts.append(skia.Point(pen + pos.x_offset * k, -pos.y_offset * k))
        pen += pos.x_advance * k
    width = pen
    if align == 'center':
        x -= width / 2
    elif align == 'right':
        x -= width
    sk = skia.Font(tf, size)
    sk.setSubpixel(True)
    builder = skia.TextBlobBuilder()
    builder.allocRunPos(sk, glyphs, pts)
    blob = builder.make()
    c.drawTextBlob(blob, x, y, skia.Paint(AntiAlias=True, Color=C(color, a)))
    return width
