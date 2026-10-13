#!/usr/bin/env python3
# usage: keylock.py START.png EDIT.png OUT.png [thr=28]
# Make an end keyframe that keeps the background (house, garden) pixel-identical to START:
# 1) align EDIT to START with a scale+translation search on the top band (house), undoing the image model's drift/zoom;
# 2) take EDIT only where it really differs from START (characters/poses), dilated + feathered;
# 3) everywhere else use START. Prints alignment and the share of pixels taken from EDIT.
import sys, numpy as np
from PIL import Image, ImageFilter
S = Image.open(sys.argv[1]).convert('RGB'); W, H = S.size
E0 = Image.open(sys.argv[2]).convert('RGB').resize((W, H), Image.LANCZOS)
THR = float(sys.argv[4]) if len(sys.argv) > 4 else 28
s = np.asarray(S, np.float32); g = lambda a: a.mean(2)
band = (slice(0, int(H*0.30)), slice(0, W))
def warp(img, sc, tx, ty):
    # output pixel p -> source (p - c - t)/sc + c
    return img.transform((W, H), Image.AFFINE, (1/sc, 0, (W/2)*(1-1/sc) - tx/sc, 0, 1/sc, (H/2)*(1-1/sc) - ty/sc), Image.BICUBIC)
best = None
for sc in np.arange(0.90, 1.121, 0.01):
    for tx in range(-40, 41, 8):
        for ty in range(-40, 41, 8):
            e = np.abs(g(np.asarray(warp(E0, sc, tx, ty).resize((W//4, H//4)), np.float32)) - g(np.asarray(S.resize((W//4, H//4)), np.float32)))[:int(H*0.30)//4].mean()
            if best is None or e < best[0]: best = (e, sc, tx, ty)
_, sc, tx, ty = best
for d_sc in (-0.005, 0, 0.005):
    for dx in range(-6, 7, 2):
        for dy in range(-6, 7, 2):
            c = (sc+d_sc, tx+dx, ty+dy)
            e = np.abs(g(np.asarray(warp(E0, *c), np.float32)) - g(s))[band].mean()
            if e < best[0] or best[1:] == (sc, tx, ty): best = (e, *c) if e < best[0] else best
_, sc, tx, ty = best
E = np.asarray(warp(E0, sc, tx, ty), np.float32)
d = np.abs(E - s).mean(2)
m = Image.fromarray(((d > THR)*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(5))
M = np.asarray(m, np.float32)[..., None]/255
out = E*M + s*(1-M)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(sys.argv[3])
Image.fromarray((M[..., 0]*255).astype(np.uint8)).save(sys.argv[3].replace('.png', '_mask.png'))
print("align scale %.3f tx %d ty %d  band err %.1f  edit share %.1f%%  house-band edit share %.1f%%" %
      (sc, tx, ty, best[0], 100*M.mean(), 100*M[band].mean()))
