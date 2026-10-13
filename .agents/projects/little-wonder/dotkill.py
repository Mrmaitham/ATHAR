#!/usr/bin/env python3
# usage: dotkill.py IN.mp4 OUT.mp4 x0 y0 x1 y1 [x0 y0 x1 y1 ...]
# Removes small lit ceiling downlights (tiny bright dots + their soft glow) inside the given boxes, every frame.
# A pixel is a "lamp dot" only if it is much brighter than its local mean, belongs to a SMALL blob, sits on a light
# surface (no dark pixel within ~6 px) and is FAR (depth) - so people, eyes, hair and clothes are never touched.
# Dots are filled by normalized convolution (blur of the surroundings without the dot).
import sys, subprocess, numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, '/home/user/lw_tools'); from bgblur import depth
inp, out = sys.argv[1], sys.argv[2]; v = list(map(int, sys.argv[3:])); B = [v[i:i+4] for i in range(0, len(v), 4)]
W, H = 1280, 720
fps = subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip()
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-vf","scale=1280:720","-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",fps,"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
def blur(a, r):    # box mean (2r+1)^2 via integral image
    a = np.pad(a.astype(np.float64), r+1, mode='edge'); c = a.cumsum(0).cumsum(1); k = 2*r+1
    s = c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]
    return (s / (k*k))[:a.shape[0]-2*r-2, :a.shape[1]-2*r-2].astype(np.float32)
def minf(l8, k):   # min filter on a half-size image (fast), scaled back
    h, w = l8.shape; s = Image.fromarray(l8).resize((w//2, h//2), Image.BILINEAR).filter(ImageFilter.MinFilter(k))
    return np.asarray(s.resize((w, h), Image.NEAREST), np.float32)
n = 0; tot = 0; FAR = None
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    if n % 6 == 0:
        d = depth(Image.fromarray(fr)); t = np.quantile(d, 0.40)
        near = ((d > t + 0.04) * 255).astype(np.uint8)
        FAR = np.asarray(Image.fromarray(near).filter(ImageFilter.MaxFilter(31)), np.float32) < 128
    for x0, y0, x1, y1 in B:
        reg = fr[y0:y1, x0:x1].astype(np.float32); lum = reg.mean(2)
        cand = lum > 200
        if not cand.any(): continue
        P = np.pad(lum, 8, mode='edge'); hh, ww = lum.shape
        NB = np.stack([P[8+dy:8+dy+hh, 8+dx:8+dx+ww] for dy, dx in ((7,0),(-7,0),(0,7),(0,-7),(5,5),(-5,-5),(5,-5),(-5,5))])
        nb = NB.max(0); smooth = (nb - NB.min(0)) < np.maximum(28, 0.5*(lum - nb))   # ring smooth relative to dot strength
        m = cand & ((lum - nb) > 18) & smooth                        # brighter than ALL 8 neighbours 7 px away = isolated dot
        if not m.any(): continue
        small = blur(m.astype(np.float32), 6) < 0.35                 # blob covers < 35% of its 13x13 neighbourhood
        light = minf(lum.astype(np.uint8), 7) > 70                    # no dark pixel (eye, hair, hijab) nearby
        mr, mg, mb = blur(reg[..., 0], 8), blur(reg[..., 1], 8), blur(reg[..., 2], 8)
        warm = (mr >= mg - 4) & (mr > mb + 6)                           # beige/stone surroundings, not sky or leaves
        m = m & small & light & warm & FAR[y0:y1, x0:x1]
        if not m.any(): continue
        mm = np.asarray(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2.5)), np.float32)/255
        mm = np.clip(mm*1.6, 0, 1)
        keep = (mm < 0.02).astype(np.float32); den = blur(keep, 8) + 1e-4
        clean = np.stack([blur(reg[..., c]*keep, 8)/den for c in range(3)], 2)
        mm = mm[..., None]
        fr[y0:y1, x0:x1] = np.clip(reg*(1-mm) + clean*mm, 0, 255).astype(np.uint8); tot += int(m.sum())
    enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "dot pixels removed", tot)
