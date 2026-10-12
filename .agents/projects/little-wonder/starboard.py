# usage: starboard.py IN OUT NSTARS  -> repaint board star row on anchor A4 (a4b.png geometry): 7 squares, first N with gold stars
import sys, math
from PIL import Image, ImageDraw, ImageFilter
src, out, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
im = Image.open(src).convert('RGB')
X0, X1, Y0, Y1 = 1058, 1262, 294, 372          # band to repaint
H = Y1 - Y0
patch = im.crop((X0, 398, X1, 398 + H))          # plank texture from lower board
mask = Image.new('L', (X1 - X0, H), 0)
ImageDraw.Draw(mask).rounded_rectangle((4, 2, X1 - X0 - 4, H - 2), 8, fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(3))
im.paste(patch, (X0, Y0), mask)
S = 4
W = (X1 - X0) * S; HH = H * S
lay = Image.new('RGBA', (W, HH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
pitch = (W - 20 * S) / 7; sq = pitch * 0.78; cy = HH / 2
for i in range(7):
    cx = 10 * S + pitch * (i + 0.5)
    d.rounded_rectangle((cx - sq / 2, cy - sq / 2, cx + sq / 2, cy + sq / 2), 3 * S, outline=(92, 62, 38, 230), width=int(2.2 * S))
glow = Image.new('RGBA', (W, HH), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
stars = Image.new('RGBA', (W, HH), (0, 0, 0, 0)); s = ImageDraw.Draw(stars)
def pts(cx, cy, R, r):
    return [(cx + (R if k % 2 == 0 else r) * math.sin(k * math.pi / 5), cy - (R if k % 2 == 0 else r) * math.cos(k * math.pi / 5)) for k in range(10)]
for i in range(n):
    cx = 10 * S + pitch * (i + 0.5); R = pitch * 0.62
    g.ellipse((cx - R * 1.3, cy - R * 1.3, cx + R * 1.3, cy + R * 1.3), fill=(255, 220, 90, 120))
    s.polygon(pts(cx, cy + R * 0.08, R, R * 0.45), fill=(255, 205, 40, 255), outline=(225, 150, 20, 255))
    s.polygon(pts(cx - R * 0.08, cy, R * 0.55, R * 0.25), fill=(255, 240, 150, 200))
glow = glow.filter(ImageFilter.GaussianBlur(5 * S))
lay = Image.alpha_composite(Image.alpha_composite(lay, glow), stars).resize((X1 - X0, H), Image.LANCZOS)
base = im.convert('RGBA'); base.alpha_composite(lay, (X0, Y0)); base.convert('RGB').save(out)
