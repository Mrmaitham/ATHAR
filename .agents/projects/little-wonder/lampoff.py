#!/usr/bin/env python3
# usage: [FWD=1 | MID=frame] lampoff.py IN.mp4 OUT.mp4 x y r [x y r ...]   (positions in the LAST frame, or the FIRST with FWD=1)
# Switches lit lamps off without camera tracking: each lamp is followed by itself, frame by frame from the last frame
# backwards (a lamp moves at most 4 px per frame; if it is hidden the estimate is kept). In every frame the compact
# bright warm/white blob at the lamp is filled with the colour of the ring around it (slightly darker = unlit glass).
# Faces/clothes are never touched unless they are a small bright blob exactly on a lamp's tracked position.
import sys, subprocess, numpy as np
from PIL import Image, ImageFilter
inp, out = sys.argv[1], sys.argv[2]; v = list(map(int, sys.argv[3:])); L = [v[i:i+3] for i in range(0, len(v), 3)]
W, H = 1280, 720
fps = subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip()
raw = subprocess.run(["ffmpeg","-v","error","-i",inp,"-vf","scale=1280:720","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).copy(); N = len(F)
def blob(fr, x, y, r, S):
    x0, x1, y0, y1 = max(x-S-2*r, 0), min(x+S+2*r, W), max(y-S-2*r, 0), min(y+S+2*r, H)
    reg = fr[y0:y1, x0:x1].astype(np.float32); lum = reg.mean(2)
    bl = np.asarray(Image.fromarray(lum.astype(np.uint8)).filter(ImageFilter.BoxBlur(10)), np.float32)
    w = (lum - bl) * (reg[..., 0] > 190) * (reg[..., 1] > 160)
    Y, X = np.mgrid[y0:y1, x0:x1]; w[(np.abs(X-x) > S) | (np.abs(Y-y) > S)] = 0
    if w.max() < 22: return None
    yy, xx = np.unravel_index(np.argmax(w), w.shape); return int(X[yy, xx]), int(Y[yy, xx])
# 1) follow each lamp from a seed frame: the last (default), the first (FWD=1) or any frame (MID=index), both ways
import os
i0 = int(os.environ['MID']) if 'MID' in os.environ else (0 if os.environ.get('FWD') == '1' else N-1)
P = np.zeros((N, len(L), 2), int)
for order in (range(i0, N), range(i0, -1, -1)):
    cur = [(x, y) for x, y, r in L]
    for i in order:
        for k, (x, y, r) in enumerate(L):
            b = blob(F[i], cur[k][0], cur[k][1], r, 4 if i != i0 else 8)
            if b: cur[k] = b
            P[i, k] = cur[k]
# 2) unlight
for i in range(N):
    fr = F[i]
    for k, (x0_, y0_, r) in enumerate(L):
        cx, cy = P[i, k]; R = int(r*1.7)
        a0, a1, b0, b1 = max(cx-R, 0), min(cx+R+1, W), max(cy-R, 0), min(cy+R+1, H)
        reg = fr[b0:b1, a0:a1].astype(np.float32); Y, X = np.mgrid[b0:b1, a0:a1]
        d = np.sqrt((X-cx)**2 + (Y-cy)**2) / r; lum = reg.mean(2)
        ring = (d > 1.2) & (d < 1.7)
        if ring.sum() < 8: continue
        bg = np.median(reg[ring], 0); bl = bg.mean()
        m = np.clip((1.25-d)/0.35, 0, 1) * np.clip((lum-bl-6)/25, 0, 1)
        tgt = np.minimum(reg, bg*0.88 + reg*0.12)
        fr[b0:b1, a0:a1] = np.clip(reg*(1-m[..., None]) + tgt*m[..., None], 0, 255).astype(np.uint8)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",fps,"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
enc.stdin.write(F.tobytes()); enc.stdin.close(); enc.wait()
print("frames", N, "lamp paths (first->last):", [(tuple(P[0, k]), tuple(P[-1, k])) for k in range(len(L))])
