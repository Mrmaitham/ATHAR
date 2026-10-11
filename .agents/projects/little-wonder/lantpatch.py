#!/usr/bin/env python3
# usage: lantpatch.py IN.mp4 OUT.mp4 REF.png refx refy "t:x:y,..."
# Replaces the (lit) wall lantern by a clean unlit lantern sprite built from REF.png
# (lantern dark pixels over clean panel texture taken from below the glow), tracked per frame.
import sys, subprocess, numpy as np
from PIL import Image
inp, out, ref, rx, ry, kp = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
KP = sorted(tuple(map(float, k.split(":"))) for k in kp.split(","))
W, H = 1280, 720; PW, PH = 40, 54        # sprite half sizes
R = np.asarray(Image.open(ref).convert("RGB")).astype(np.float32)
lan = R[ry-PH:ry+PH, rx-PW:rx+PW]
bg = R[ry-PH+80:ry+PH+80, rx-PW:rx+PW]   # clean panel below
lum = lan.mean(2); dark = (lum < 85).astype(np.float32)
def blur(a, s):
    r = int(3*s); k = np.exp(-0.5*(np.arange(-r, r+1)/s)**2); k /= k.sum()
    a = np.pad(a.astype(np.float32), r, mode="edge")
    a = np.apply_along_axis(lambda v: np.convolve(v, k, "valid"), 0, a)
    return np.apply_along_axis(lambda v: np.convolve(v, k, "valid"), 1, a)
am = np.clip(blur(dark, 1.2)*1.6, 0, 1)[..., None]
sprite = lan*am + bg*(1-am)
yy, xx = np.mgrid[-PH:PH, -PW:PW]
edge = np.clip(np.minimum((PW-np.abs(xx))/14, (PH-np.abs(yy))/14), 0, 1)[..., None]
edge = edge*edge*(3-2*edge)
tmpl = dark  # match on lantern silhouette
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
def est(t):
    if t <= KP[0][0]: return KP[0][1:]
    for a, b in zip(KP, KP[1:]):
        if t <= b[0]:
            f = (t-a[0])/(b[0]-a[0]); return (a[1]+f*(b[1]-a[1]), a[2]+f*(b[2]-a[2]))
    return KP[-1][1:]
def track(fr, t):
    ex, ey = map(int, map(round, est(t))); best = None
    for dy in range(-10, 11):
        for dx in range(-10, 11):
            cx, cy = ex+dx, ey+dy
            w = fr[cy-PH:cy+PH, cx-PW:cx+PW].astype(np.float32).mean(2)
            d = (w < 85).astype(np.float32)
            sc = (d*tmpl).sum()/(np.sqrt(d.sum()*tmpl.sum())+1)
            if best is None or sc > best[0]: best = (sc, cx, cy)
    return best[1], best[2]
def fix(fr, cx, cy):
    reg = fr[cy-PH:cy+PH, cx-PW:cx+PW].astype(np.float32)
    # match sprite brightness/colour to this frame's clean panel (below the glow)
    lo = fr[cy-PH+80:cy+PH+80, cx-PW:cx+PW].astype(np.float32).reshape(-1, 3).mean(0)
    g = lo/ bg.reshape(-1, 3).mean(0)
    fr[cy-PH:cy+PH, cx-PW:cx+PW] = np.clip(reg*(1-edge) + sprite*g*edge, 0, 255).astype(np.uint8)
    return fr
def frames():
    d = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
    while True:
        b = d.stdout.read(W*H*3)
        if len(b) < W*H*3: return
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
P = np.array([track(f, i/fps) for i, f in enumerate(frames())], np.float32)
k = 7; Ps = np.stack([np.convolve(np.pad(P[:, j], k, mode="edge"), np.ones(2*k+1)/(2*k+1), "valid") for j in range(2)], 1)
Ps = np.round(Ps).astype(int)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
n = 0
for fr in frames():
    enc.stdin.write(fix(fr, *Ps[min(n, len(Ps)-1)]).tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "raw track", P[0], P[n//2], P[-1], "max step", np.abs(np.diff(Ps, axis=0)).max())
