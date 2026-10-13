#!/usr/bin/env python3
# usage: findlamps.py FRAME.png S x y r [x y r ...]  -> prints "x y r ..." with each lamp re-located in FRAME
# (brightest compact warm/white blob within +-S px of the given guess; guess kept, r=0 if no lit blob found).
import sys, numpy as np
from PIL import Image, ImageFilter
im = Image.open(sys.argv[1]).convert('RGB').resize((1280, 720)); S = int(sys.argv[2])
a = np.asarray(im, np.float32); lum = a.mean(2)
bl = np.asarray(im.convert('L').filter(ImageFilter.BoxBlur(10)), np.float32)
d = lum - bl
v = list(map(int, sys.argv[3:])); out = []
for i in range(0, len(v), 3):
    x, y, r = v[i:i+3]
    x0, x1, y0, y1 = max(x-S, 0), min(x+S, 1279), max(y-S, 0), min(y+S, 719)
    w = d[y0:y1, x0:x1] * (a[y0:y1, x0:x1, 0] > 190) * (a[y0:y1, x0:x1, 1] > 160)
    if w.max() < 22: out += [x, y, 0]; continue
    yy, xx = np.unravel_index(np.argmax(w), w.shape)
    m = w > 0.6 * w.max(); Y, X = np.mgrid[y0:y1, x0:x1]
    near = m & ((X - (x0+xx))**2 + (Y - (y0+yy))**2 < (2*r)**2)
    out += [int(X[near].mean()), int(Y[near].mean()), r]
print(' '.join(map(str, out)))
