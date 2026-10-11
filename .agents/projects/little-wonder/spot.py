#!/usr/bin/env python3
# usage: spot.py IN.mp4 OUT.mp4 seed_x seed_y [seed=last|first]
# Removes a lit ceiling downlight (small bright ellipse ~18x9) and its soft wash: tracks the blob
# frame-to-frame from the seed frame, fills it from its surrounding ring, softens the warm pool below.
import sys, subprocess, numpy as np
inp, out, sx, sy = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
seed = sys.argv[5] if len(sys.argv) > 5 else "last"
W, H = 1280, 720
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
def frames():
    d = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
    while True:
        b = d.stdout.read(W*H*3)
        if len(b) < W*H*3: return
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
F = list(frames()); n = len(F)
yy, xx = np.mgrid[-20:21, -30:31]
core = ((xx/9)**2+(yy/4.5)**2) <= 1; ring = (((xx/16)**2+(yy/9)**2) <= 1) & ~(((xx/11)**2+(yy/6)**2) <= 1)
def score(L, cx, cy):
    w = L[cy-20:cy+21, cx-30:cx+31]
    return w[core].mean()-w[ring].mean(), w[core].mean()
order = range(n-1, -1, -1) if seed == "last" else range(n)
pos = {}; cx, cy = sx, sy
for i in order:
    L = F[i].astype(np.float32).mean(2); best = None
    for dy in range(-3, 4):
        for dx in range(-5, 6):
            s, lum = score(L, cx+dx, cy+dy)
            if best is None or s > best[0]: best = (s, cx+dx, cy+dy, lum)
    _, cx, cy, lum = best; pos[i] = (cx, cy, best[0], lum)
P = np.array([pos[i][:2] for i in range(n)], np.float32); S = np.array([pos[i][2] for i in range(n)]); LU = np.array([pos[i][3] for i in range(n)])
if '--dbg' in sys.argv: print([ (i, round(S[i]), round(LU[i])) for i in range(0, n, 6)])
TH = float(next((a.split('=')[1] for a in sys.argv if a.startswith('--th=')), 18))
k = 5; P = np.stack([np.convolve(np.pad(P[:, j], k, mode="edge"), np.ones(2*k+1)/(2*k+1), "valid") for j in range(2)], 1)
Y2, X2 = np.mgrid[-26:27, -40:41]
r = np.sqrt((X2/13)**2+(Y2/7)**2); m = np.clip((1.6-r)/0.6, 0, 1); m = (m*m*(3-2*m))[..., None]
pool = np.clip(1-np.sqrt((X2/26)**2+((Y2-14)/13)**2), 0, 1)[..., None]  # warm wash under the light
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
ST = np.clip((S-TH)/10, 0, 1); ST = np.convolve(np.pad(ST, 4, mode='edge'), np.ones(9)/9, 'valid')
for i, fr in enumerate(F):
    cx, cy = map(int, np.round(P[i]))
    if ST[i] > 0.02:   # only where a lit blob is actually present
        reg = fr[cy-26:cy+27, cx-40:cx+41].astype(np.float32)
        lum = reg.mean(2)
        keep = np.clip((lum-110)/40, 0, 1)[..., None]          # protect dark subjects (hijab etc.)
        from_bg = (r > 1.7) & (r < 2.6) & (lum > 150)
        if from_bg.sum() < 20: enc.stdin.write(fr.tobytes()); continue
        fill = np.median(reg[from_bg], 0)
        mm = m*keep*ST[i]
        reg = reg*(1-mm) + fill*mm
        base = np.median(reg[(r > 2.2) & (lum > 150)], 0)
        reg = reg - pool*keep*0.6*ST[i]*np.clip(reg-base, 0, None)
        fr[cy-26:cy+27, cx-40:cx+41] = np.clip(reg, 0, 255).astype(np.uint8)
    enc.stdin.write(fr.tobytes())
enc.stdin.close(); enc.wait()
print("frames", n, "track first/mid/last", P[0], P[n//2], P[-1], "score min/max", round(S.min()), round(S.max()))
