#!/usr/bin/env python3
# usage: dotkill.py IN.mp4 OUT.mp4 x0 y0 x1 y1 [x0 y0 x1 y1 ...]
# Removes small lit ceiling downlights (tiny bright dots + their soft glow) inside the given boxes, every frame.
# A pixel is a "lamp dot" only if it is much brighter than its surroundings, belongs to a SMALL blob, and sits on a light
# surface (no dark pixel within 6 px) - so eye highlights, hair shine and clothes are never touched.
import sys, subprocess, numpy as np
from PIL import Image, ImageFilter
inp, out = sys.argv[1], sys.argv[2]; v = list(map(int, sys.argv[3:])); B = [v[i:i+4] for i in range(0, len(v), 4)]
W, H = 1280, 720
fps = subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip()
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-vf","scale=1280:720","-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",fps,"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
f = lambda a, flt: np.asarray(Image.fromarray(a).filter(flt), np.float32)
n = 0; tot = 0
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    for x0, y0, x1, y1 in B:
        reg = fr[y0:y1, x0:x1]; lum = reg.astype(np.float32).mean(2); l8 = lum.astype(np.uint8)
        bg = f(l8, ImageFilter.MedianFilter(15))
        m = ((lum - bg) > 22) & (lum > 200)
        m8 = (m*255).astype(np.uint8)
        small = f(m8, ImageFilter.BoxBlur(6)) < 255*0.35          # blob covers < 35% of its 13x13 neighbourhood
        light = f(l8, ImageFilter.MinFilter(13)) > 70             # no dark pixel (eye, hair, hijab) nearby
        m = m & small & light
        if not m.any(): continue
        mm = f((m*255).astype(np.uint8), ImageFilter.MaxFilter(5)); mm = np.asarray(Image.fromarray(mm.astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.5)), np.float32)/255
        mm = np.clip(mm*1.6, 0, 1)[..., None]
        clean = np.stack([f(reg[..., c], ImageFilter.MedianFilter(15)) for c in range(3)], 2)
        fr[y0:y1, x0:x1] = np.clip(reg*(1-mm) + clean*mm, 0, 255).astype(np.uint8); tot += int(m.sum())
    enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "dot pixels removed", tot)
