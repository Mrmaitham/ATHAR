#!/usr/bin/env python3
# usage: goldkill.py IN.(mp4|png) OUT x0 y0 x1 y1 [t0=0]
# Removes a small thin gold item (earring hoop) inside a box: gold/yellow pixels that form a thin structure
# (removed by a 7px grey opening) are filled from their surroundings (normalized convolution). From time t0 on.
import sys, subprocess, numpy as np
from PIL import Image, ImageFilter
inp, out = sys.argv[1], sys.argv[2]; x0, y0, x1, y1 = map(int, sys.argv[3:7]); t0 = float(sys.argv[7]) if len(sys.argv) > 7 else 0
W, H = 1280, 720
def blur(a, r):
    a = np.pad(a.astype(np.float64), r+1, mode='edge'); c = a.cumsum(0).cumsum(1); k = 2*r+1
    s = c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]
    return (s / (k*k))[:a.shape[0]-2*r-2, :a.shape[1]-2*r-2].astype(np.float32)
def fix(fr):
    reg = fr[y0:y1, x0:x1].astype(np.float32); R, G, B = reg[..., 0], reg[..., 1], reg[..., 2]
    gold = (R > 120) & (G > 90) & (R - B > 45) & (G - B > 25) & (R - G < 70)
    op = np.asarray(Image.fromarray(reg.astype(np.uint8)).filter(ImageFilter.MinFilter(7)).filter(ImageFilter.MaxFilter(7)), np.float32)
    thin = (reg.mean(2) - op.mean(2)) > 12
    m = gold & thin
    if m.sum() < 3: return 0
    mm = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1)), np.float32)[..., None] / 255
    keep = (mm[..., 0] < 0.05).astype(np.float32); den = blur(keep, 5) + 1e-4
    clean = np.stack([blur(reg[..., c] * keep, 5) / den for c in range(3)], 2)
    fr[y0:y1, x0:x1] = np.clip(reg * (1 - mm) + clean * mm, 0, 255).astype(np.uint8); return int(m.sum())
if inp.endswith('.png'):
    fr = np.asarray(Image.open(inp).convert('RGB').resize((W, H))).copy(); print('px', fix(fr)); Image.fromarray(fr).save(out); sys.exit()
fps = subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip()
num, den_ = map(int, fps.split('/')); f = num / den_
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-vf","scale=1280:720","-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",fps,"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","copy",out], stdin=subprocess.PIPE)
n = tot = 0
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    if n / f >= t0: tot += fix(fr)
    enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print('frames', n, 'px', tot)
