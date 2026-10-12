#!/usr/bin/env python3
# usage: pushbridge.py A.mp4 B_FIRST.png OUT.mp4 [secs=1.0]
# Finds the zoom/offset that maps A's last frame onto B's first frame (B framed closer), then re-renders the
# last `secs` of A with an eased digital push-in ending exactly on that framing -> A->B join becomes a camera move.
import sys, subprocess, numpy as np
from PIL import Image
a, bf, out = sys.argv[1:4]; secs = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
W, H, fps = 1280, 720, 24
dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",a],capture_output=True,text=True).stdout)
dec = subprocess.Popen(["ffmpeg","-v","error","-i",a,"-vf","scale=1280:720,fps=24","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE); F=[]
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    F.append(Image.frombytes("RGB",(W,H),b))
last = F[-1]; B = Image.open(bf).convert("RGB").resize((W,H))
sw, sh = 320, 180; bs = np.asarray(B.resize((sw,sh))).astype(float); best=None
for s in np.arange(1.0, 1.6, 0.01):
    cw, ch = W/s, H/s
    for cx in np.arange(cw/2, W-cw/2+1, 16):
        for cy in np.arange(ch/2, H-ch/2+1, 12):
            c = np.asarray(last.crop((int(cx-cw/2),int(cy-ch/2),int(cx+cw/2),int(cy+ch/2))).resize((sw,sh))).astype(float)
            d = abs(c-bs).mean()
            if best is None or d < best[0]: best = (d, s, cx, cy)
d, s, cx, cy = best
# refine
for s2 in np.arange(s-0.01, s+0.011, 0.0025):
    cw, ch = W/s2, H/s2
    for cx2 in np.arange(cx-16, cx+17, 4):
        for cy2 in np.arange(cy-12, cy+13, 4):
            x0, y0 = cx2-cw/2, cy2-ch/2
            if x0 < 0 or y0 < 0 or x0+cw > W or y0+ch > H: continue
            c = np.asarray(last.crop((int(x0),int(y0),int(x0+cw),int(y0+ch))).resize((sw,sh))).astype(float)
            dd = abs(c-bs).mean()
            if dd < d: d, s, cx, cy = dd, s2, cx2, cy2
print(f"push s={s:.3f} centre=({cx:.0f},{cy:.0f}) residual={d:.1f} (raw {abs(np.asarray(last.resize((sw,sh))).astype(float)-bs).mean():.1f})")
n = int(secs*fps); ease = lambda u: 0.5-0.5*np.cos(np.pi*u)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",a,"-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-ar","48000","-shortest",out],stdin=subprocess.PIPE)
for i, fr in enumerate(F):
    k = i-(len(F)-n)
    if k >= 0:
        u = ease((k+1)/n); si = 1+(s-1)*u; cxi = W/2+(cx-W/2)*u; cyi = H/2+(cy-H/2)*u
        cw, ch = W/si, H/si; x0 = min(max(cxi-cw/2,0),W-cw); y0 = min(max(cyi-ch/2,0),H-ch)
        fr = fr.crop((int(round(x0)),int(round(y0)),int(round(x0+cw)),int(round(y0+ch)))).resize((W,H),Image.LANCZOS)
    enc.stdin.write(fr.tobytes())
enc.stdin.close(); enc.wait(); print("ok", out)
