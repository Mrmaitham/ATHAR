#!/usr/bin/env python3
# usage: morphcheck.py CLIP.mp4  -> flags in-shot morphs: frame-to-frame residual after best global shift+zoom
# (camera moves are compensated; a background that suddenly transforms leaves a high residual spike).
import sys, subprocess, numpy as np
from PIL import Image
W, H = 192, 108
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
F = []
while True:
    b = p.stdout.read(W * H)
    if len(b) < W * H: break
    F.append(np.frombuffer(b, np.uint8).reshape(H, W).astype(float))
def resid(a, b):
    best = 1e9; m = 12
    A = a[m:H - m, m:W - m]
    for s in (0.97, 0.985, 1.0, 1.015, 1.03):
        bs = np.asarray(Image.fromarray(b.astype(np.uint8)).resize((int(W * s), int(H * s)))).astype(float)
        ox, oy = (bs.shape[1] - W) // 2, (bs.shape[0] - H) // 2
        for dy in range(-6, 7, 2):
            for dx in range(-8, 9, 2):
                y0, x0 = m + oy + dy, m + ox + dx
                if y0 < 0 or x0 < 0 or y0 + A.shape[0] > bs.shape[0] or x0 + A.shape[1] > bs.shape[1]: continue
                best = min(best, abs(bs[y0:y0 + A.shape[0], x0:x0 + A.shape[1]] - A).mean())
    return best
R = np.array([resid(F[i - 1], F[i]) for i in range(1, len(F))])
med = np.median(R); bad = [(round(i / 24, 2), round(r, 1)) for i, r in enumerate(R, 1) if r > max(6, 2.5 * med)]
print(sys.argv[1], 'median', round(med, 2), 'MORPH?' if bad else 'clean', bad[:12])
