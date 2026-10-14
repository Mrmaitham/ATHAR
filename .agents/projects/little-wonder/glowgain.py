#!/usr/bin/env python3
# usage: glowgain.py IN.mp4 OUT.mp4 x0 y0 x1 y1   (fixed camera)
# Removes a soft lamp wash on a textured wall without blurring the texture: from the median frame, the low-frequency
# brightness inside the box (per colour) is compared with the wall level at the top/bottom box edges; a smooth gain map (<=1) is multiplied
# into every frame, so the pattern (mosaic) keeps its detail and only the glow is taken away.
import sys, subprocess, numpy as np
from PIL import Image, ImageFilter
inp, out = sys.argv[1], sys.argv[2]; x0, y0, x1, y1 = map(int, sys.argv[3:7]); W, H = 1280, 720
raw = subprocess.run(["ffmpeg","-v","error","-i",inp,"-vf","scale=1280:720","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
med = np.median(fr[::6, y0:y1, x0:x1].astype(np.float32), axis=0)
G = []
for c in range(3):
    low = np.asarray(Image.fromarray(np.clip(med[..., c],0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(12)), np.float32)
    # wall level: column-wise interpolation between the TOP and BOTTOM rows of the box (the wash spreads up/down)
    base = np.linspace(low[:6].mean(0), low[-6:].mean(0), y1 - y0, axis=0)
    g = np.clip(base / np.maximum(low, 1), 0.55, 1.0)
    G.append(np.asarray(Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255)
g = np.stack(G, 2)
yy, xx = np.mgrid[0:y1-y0, 0:x1-x0]; ex = np.minimum.reduce([xx, yy, x1-x0-1-xx, y1-y0-1-yy]).astype(np.float32)
f = np.clip(ex / 8, 0, 1)[..., None]; g = 1 - (1 - g) * f
fps = subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip()
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",fps,"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","copy",out], stdin=subprocess.PIPE)
for a in fr:
    b = a.copy().astype(np.float32); b[y0:y1, x0:x1] *= g
    enc.stdin.write(np.clip(b, 0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); print("ok min gain", round(float(g.min()), 2))
