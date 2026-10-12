#!/usr/bin/env python3
# usage: whipjoin.py A.mp4 B.mp4 OUT.mp4 [B_start_sec=0] [blur_frames=8]
# Joins A then B (from B_start) with a whip-pan: horizontal motion blur ramps up over A's last frames and
# down over B's first frames, crossfading at the peak blur -> a fast camera move, not a cut. Audio crossfades.
import sys, subprocess, numpy as np
from PIL import Image, ImageFilter
a, b, out = sys.argv[1:4]; bs = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0; n = int(sys.argv[5]) if len(sys.argv) > 5 else 8
W, H, fps = 1280, 720, 24
def frames(p, ss=0.0):
    d = subprocess.Popen(["ffmpeg","-v","error","-ss",str(ss),"-i",p,"-vf","scale=1280:720,fps=24","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE); L=[]
    while True:
        x = d.stdout.read(W*H*3)
        if len(x) < W*H*3: return L
        L.append(np.frombuffer(x,np.uint8).reshape(H,W,3))
A = frames(a); B = frames(b, bs)
def hblur(f, k):
    if k < 2: return f
    acc = np.zeros_like(f, dtype=np.float32)
    for s in range(-k//2, k//2+1): acc += np.roll(f, s, axis=1)
    return (acc/(len(range(-k//2, k//2+1)))).astype(np.uint8)
K = 90
outF = A[:-n]
for i in range(n):  # ramp up on A
    u = (i+1)/n; outF.append(hblur(A[len(A)-n+i], int(K*u*u)))
mid = (hblur(A[-1], K).astype(np.float32)*0.5 + hblur(B[0], K).astype(np.float32)*0.5).astype(np.uint8); outF.append(mid)
for i in range(n):  # ramp down on B
    u = 1-(i+1)/n; outF.append(hblur(B[i], int(K*u*u)))
outF += B[n:]
ta = len(A)/fps; T = len(outF)/fps
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-",
    "-i",a,"-ss",str(bs),"-i",b,"-filter_complex",
    f"[1:a]aresample=48000,aformat=channel_layouts=stereo[x];[2:a]aresample=48000,aformat=channel_layouts=stereo[y];[x][y]acrossfade=d={(2*n+1)/fps:.3f}[aa]",
    "-map","0:v","-map","[aa]","-t",f"{T:.3f}","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-ar","48000",out],stdin=subprocess.PIPE)
for f in outF: enc.stdin.write(np.ascontiguousarray(f).tobytes())
enc.stdin.close(); enc.wait(); print("ok", out, round(T,2), "s; join at", round(ta,2))
