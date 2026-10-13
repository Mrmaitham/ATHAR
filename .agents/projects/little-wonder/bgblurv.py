#!/usr/bin/env python3
# usage: bgblurv.py IN.mp4 OUT.mp4 [far_pct=0.35] [sigma=14]
# Depth-based background blur for a clip: per-frame depth (Depth-Anything-V2 small), threshold fixed per clip
# (median of per-frame quantiles, so the cut-off does not pump), temporally smoothed mask (EMA), audio copied.
import sys, subprocess, numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, '/home/user/lw_tools'); from bgblur import depth
IN, OUT = sys.argv[1], sys.argv[2]; FP = float(sys.argv[3]) if len(sys.argv) > 3 else 0.35; SG = float(sys.argv[4]) if len(sys.argv) > 4 else 14
W, H = 1280, 720; SOFT = 0.12
raw = subprocess.run(["ffmpeg","-v","error","-i",IN,"-vf","scale=1280:720","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3); N = len(F)
D = [depth(Image.fromarray(f)) for f in F]
T = float(np.median([np.quantile(d, FP) for d in D]))
out = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s","1280x720","-r","24","-i","-","-i",IN,
                        "-map","0:v","-map","1:a?","-c:v","libx264","-crf","16","-pix_fmt","yuv420p","-c:a","copy","-shortest",OUT],stdin=subprocess.PIPE)
M = None
for f in range(N):
    m = np.clip((T + SOFT - D[f]) / SOFT, 0, 1)
    M = m if M is None else 0.6*M + 0.4*m                     # temporal smoothing against edge flicker
    mm = np.asarray(Image.fromarray((M*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4)), np.float32)[..., None]/255
    im = Image.fromarray(F[f]); b = np.asarray(im.filter(ImageFilter.GaussianBlur(SG)), np.float32)
    o = F[f].astype(np.float32)*(1-mm) + b*mm
    out.stdin.write(np.clip(o, 0, 255).astype(np.uint8).tobytes())
out.stdin.close(); out.wait(); print("ok", OUT, N, "threshold", round(T, 3))
