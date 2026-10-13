#!/usr/bin/env python3
# usage: sproutkill.py IN.mp4 OUT.mp4 x0 y0 x1 y1 [...]   (boxes around pot soil, full-res 1280x720 coords)
# "Nothing green before Day 7": removes green leaves/sprouts inside the boxes: green pixels (G clearly above R and B)
# plus a 2 px margin are filled from the surrounding non-green pixels (normalized convolution), every frame.
import sys, subprocess, numpy as np
from PIL import Image, ImageFilter
inp, out = sys.argv[1], sys.argv[2]; v = list(map(int, sys.argv[3:])); B = [v[i:i+4] for i in range(0, len(v), 4)]
W, H = 1280, 720
fps = subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip()
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-vf","scale=1280:720","-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",fps,"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
def blur(a, r):
    a = np.pad(a.astype(np.float64), r+1, mode='edge'); c = a.cumsum(0).cumsum(1); k = 2*r+1
    s = c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]
    return (s / (k*k))[:a.shape[0]-2*r-2, :a.shape[1]-2*r-2].astype(np.float32)
n = tot = 0
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    for x0, y0, x1, y1 in B:
        reg = fr[y0:y1, x0:x1].astype(np.float32); R, G, Bc = reg[..., 0], reg[..., 1], reg[..., 2]
        g = (G >= R - 2) & (G > Bc + 10) & (G > 30)
        if not g.any(): continue
        m = np.asarray(Image.fromarray((g*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)), np.float32)/255
        keep = 1 - m; den = blur(keep, 7) + 1e-4
        clean = np.stack([blur(reg[..., c]*keep, 7)/den for c in range(3)], 2)
        mm = np.asarray(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)), np.float32)[..., None]/255
        fr[y0:y1, x0:x1] = np.clip(reg*(1-mm) + clean*mm, 0, 255).astype(np.uint8); tot += int(g.sum())
    enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "green pixels removed", tot)
