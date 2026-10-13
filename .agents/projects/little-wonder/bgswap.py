#!/usr/bin/env python3
# usage: bgswap.py START.png EDIT.png OUT.png [far_q=0.45]
# Keep START's foreground (characters, cat, bench, pots, lawn) pixel-identical and take only the far background
# (house, sky, trees behind) from EDIT. EDIT is first aligned to START on the lower (foreground) half, then a
# depth mask (Depth-Anything-V2) from START decides near/far, softened and feathered.
import sys, numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, '/home/user/lw_tools'); from bgblur import depth
S = Image.open(sys.argv[1]).convert('RGB'); W, H = S.size
E0 = Image.open(sys.argv[2]).convert('RGB').resize((W, H), Image.LANCZOS)
Q = float(sys.argv[4]) if len(sys.argv) > 4 else 0.45
g = lambda im: np.asarray(im.resize((W//4, H//4)), np.float32).mean(2)
def warp(img, sc, tx, ty):
    return img.transform((W, H), Image.AFFINE, (1/sc, 0, (W/2)*(1-1/sc) - tx/sc, 0, 1/sc, (H/2)*(1-1/sc) - ty/sc), Image.BICUBIC)
s4 = g(S); lo = slice(int(H*0.45)//4, H//4); best = None; e4 = E0.resize((W//4, H//4))
def warp4(img, sc, tx, ty):
    w, h = img.size; tx, ty = tx/4, ty/4
    return np.asarray(img.transform((w, h), Image.AFFINE, (1/sc, 0, (w/2)*(1-1/sc) - tx/sc, 0, 1/sc, (h/2)*(1-1/sc) - ty/sc), Image.BILINEAR), np.float32).mean(2)
for sc in np.arange(0.94, 1.061, 0.01):
    for tx in range(-32, 33, 4):
        for ty in range(-32, 33, 4):
            e = np.abs(warp4(e4, sc, tx, ty) - s4)[lo].mean()
            if best is None or e < best[0]: best = (e, sc, tx, ty)
_, sc, tx, ty = best; E = np.asarray(warp(E0, sc, tx, ty), np.float32); s = np.asarray(S, np.float32)
d = depth(S); t = np.quantile(d, Q)
m = np.clip((d - t) / 0.08, 0, 1)                       # 1 = near (keep START)
m[int(H*0.80):] = 1                                      # lowest band is always foreground lawn
M = np.asarray(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(3)), np.float32)[..., None]/255
out = s*M + E*(1-M)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(sys.argv[3])
Image.fromarray((M[..., 0]*255).astype(np.uint8)).save(sys.argv[3].replace('.png', '_mask.png'))
print('align', round(sc, 3), tx, ty, 'err %.1f' % best[0], 'background share %.1f%%' % (100*(1-M.mean())))
