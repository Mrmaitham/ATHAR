#!/usr/bin/env python3
# usage: clonefill.py IN.mp4 OUT.mp4 x0 y0 x1 y1 dx dy   - replace box with feathered copy of the box shifted by (dx,dy) (same frame)
import sys, subprocess, numpy as np
inp, out = sys.argv[1], sys.argv[2]; x0, y0, x1, y1, dx, dy = map(int, sys.argv[3:9])
W, H = 1280, 720; F = 10
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
yy, xx = np.mgrid[y0:y1, x0:x1]
m = np.minimum(np.minimum((xx-x0)/F, (x1-1-xx)/F), np.minimum((yy-y0)/F, (y1-1-yy)/F)).clip(0, 1)
m = (m*m*(3-2*m))[..., None]
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    reg = fr[y0:y1, x0:x1].astype(np.float32); src = fr[y0+dy:y1+dy, x0+dx:x1+dx].astype(np.float32)
    fr[y0:y1, x0:x1] = np.clip(reg*(1-m)+src*m, 0, 255).astype(np.uint8)
    enc.stdin.write(fr.tobytes())
enc.stdin.close(); enc.wait(); print("ok")
