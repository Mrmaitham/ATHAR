#!/usr/bin/env python3
# usage: unglow.py IN.mp4 OUT.mp4 "t:x:y,t:x:y,..."   (lantern centre keypoints, 1280x720 coords)
# Removes the warm wall-wash of a lit wall lantern: tracks the dark lantern, flattens the
# smooth illumination on its panel to the unlit panel level, keeps texture. Audio copied.
import sys, subprocess, numpy as np
from PIL import Image, ImageFilter
inp, out, kp = sys.argv[1], sys.argv[2], sys.argv[3]
KP = sorted(tuple(map(float, k.split(":"))) for k in kp.split(","))
HW, HH, FE, REF = 70, 140, 10, 118   # region half-width, half-height, pad, ref offset below lantern
RX, RY, RYOFF = 46, 88, 12          # elliptical mask radii, vertical offset
W, H = 1280, 720
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
def est(t):
    if t <= KP[0][0]: return KP[0][1:]
    for a, b in zip(KP, KP[1:]):
        if t <= b[0]:
            f = (t-a[0])/(b[0]-a[0]); return (a[1]+f*(b[1]-a[1]), a[2]+f*(b[2]-a[2]))
    return KP[-1][1:]
def blur(a, s):
    r = int(3*s); k = np.exp(-0.5*(np.arange(-r, r+1)/s)**2); k /= k.sum()
    a = np.pad(a.astype(np.float32), r, mode="edge")
    a = np.apply_along_axis(lambda v: np.convolve(v, k, "valid"), 0, a)
    return np.apply_along_axis(lambda v: np.convolve(v, k, "valid"), 1, a)
def fix(fr, t):
    ex, ey = est(t)
    x0, y0 = int(ex-30), int(ey-30)
    win = fr[max(0,y0):y0+60, max(0,x0):x0+60].astype(np.float32)
    lum = win.mean(2); ys, xs = np.nonzero(lum < 75)
    if len(xs) > 40: ex, ey = x0+xs.mean(), max(0,y0)+ys.mean()
    cx, cy = int(round(ex)), int(round(ey))
    bx0, bx1 = max(0, cx-HW-FE-10), min(W, cx+HW+FE+10)
    by0, by1 = max(0, cy-HH-FE-10), min(H, cy+HH+FE+10)
    reg = fr[by0:by1, bx0:bx1].astype(np.float32)
    l = reg.mean(2); w = (l > 95).astype(np.float32)
    wb = blur(w, 14) + 1e-3
    field = np.stack([blur(reg[..., c]*w, 14)/wb for c in range(3)], 2)
    ry = min(cy+REF-by0, field.shape[0]-1); rx = cx-bx0
    ref = field[ry, max(0,rx-20):rx+20].mean(0)
    F = np.clip(ref/np.maximum(field, 1), 0.55, 1.0)
    yy, xx = np.mgrid[by0:by1, bx0:bx1]
    r = np.sqrt(((xx-cx)/RX)**2 + ((yy-cy-RYOFF)/RY)**2)
    m = np.clip((1.25-r)/0.55, 0, 1)[..., None]
    m = m*m*(3-2*m)
    fr[by0:by1, bx0:bx1] = np.clip(reg*(1-m+m*F), 0, 255).astype(np.uint8)
    return fr
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
n = 0
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    enc.stdin.write(fix(fr, n/fps).tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n)
