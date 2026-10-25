import sys, glob
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]
crop = None
if len(sys.argv) > 3:
    crop = tuple(int(v) for v in sys.argv[3].split(','))
fs = sorted(glob.glob(d + '/t*.png'))
ims = []
for f in fs:
    im = Image.open(f).convert('RGB')
    if crop: im = im.crop(crop)
    ims.append((f, im))
w, h = ims[0][1].size
s = 360 / w
tw, th = int(w * s), int(h * s)
cols = min(5, len(ims))
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * tw, rows * (th + 18)), (0, 0, 0))
dr = ImageDraw.Draw(sheet)
for k, (f, im) in enumerate(ims):
    x, y = (k % cols) * tw, (k // cols) * (th + 18)
    sheet.paste(im.resize((tw, th)), (x, y + 18))
    dr.text((x + 4, y + 2), f.split('/')[-1], fill=(255, 255, 0))
sheet.save(out)
