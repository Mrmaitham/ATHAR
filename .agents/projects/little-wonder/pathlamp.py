#!/usr/bin/env python3
# usage: TRACK=IN.mp4.track.npy pathlamp.py IN.mp4 OUT.mp4 x y r [x y r ...]
# Lamps given in REF-frame coords (the frame camtrack.py used as REF); per frame position = p + track[i].
# Lit glass / bulbs (bright pixels inside r) are pulled down to the surrounding level (unlit look); dark pixels untouched.
import sys, os, subprocess, numpy as np
inp, out = sys.argv[1], sys.argv[2]; a = list(map(int, sys.argv[3:])); P = [a[i:i+3] for i in range(0, len(a), 3)]
T = np.load(os.environ['TRACK']); W, H = 1280, 720
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
n = 0
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    dx, dy = T[min(n, len(T)-1)]
    for (x, y, r) in P:
        cx, cy = int(round(x+dx)), int(round(y+dy)); R = int(r*1.6)
        a0, a1, b0, b1 = max(cx-R, 0), min(cx+R+1, W), max(cy-R, 0), min(cy+R+1, H)
        if a1-a0 < 4 or b1-b0 < 4: continue
        reg = fr[b0:b1, a0:a1].astype(np.float32); Y, X = np.mgrid[b0:b1, a0:a1]
        d = np.sqrt((X-cx)**2+(Y-cy)**2)/r; lum = reg.mean(2)
        ring = (d > 1.15) & (d < 1.6)
        if ring.sum() < 8: continue
        bg = np.median(reg[ring], 0); bl = bg.mean()
        m = np.clip((1.2-d)/0.4, 0, 1) * np.clip((lum-bl-8)/30, 0, 1)
        tgt = np.minimum(reg, bg*0.85 + reg*0.15)   # unlit: glass/bulb takes surrounding tone, slightly darker
        reg = reg*(1-m[..., None]) + tgt*m[..., None]
        fr[b0:b1, a0:a1] = np.clip(reg, 0, 255).astype(np.uint8)
    enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n)
