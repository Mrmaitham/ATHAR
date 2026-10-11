#!/usr/bin/env python3
# usage: propfill.py IN.mp4 OUT.mp4 x0 y0 x1 y1 dx dy  - inside box, pixels that look like the yellow trowel (blade+handle)
# are replaced (soft mask, dilated) by the same frame shifted by (dx,dy); shoes/skin/other untouched.
import sys, subprocess, numpy as np
inp, out = sys.argv[1], sys.argv[2]; x0, y0, x1, y1, dx, dy = map(int, sys.argv[3:9])
W, H = 1280, 720
import os
from PIL import Image
PL = np.asarray(Image.open(os.environ['PLATE']).convert('RGB')).astype(np.float32) if os.environ.get('PLATE') else None
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
def blur(a, s):
    r = int(3*s); k = np.exp(-0.5*(np.arange(-r, r+1)/s)**2); k /= k.sum()
    a = np.pad(a.astype(np.float32), r, mode="edge")
    a = np.apply_along_axis(lambda v: np.convolve(v, k, "valid"), 0, a)
    return np.apply_along_axis(lambda v: np.convolve(v, k, "valid"), 1, a)
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    reg = fr[y0:y1, x0:x1].astype(np.float32); r, g, bl = reg[..., 0], reg[..., 1], reg[..., 2]
    LOOSE = len(sys.argv) > 9
    yellow = ((r > 170) & (g > 140) & (bl < 120) & (r - bl > 80)) | (LOOSE & (r > 120) & (g > 110) & (r - bl > 25) & (g - bl > 15))
    handle = (r > 95) & (r < 190) & (g > 50) & (g < 120) & (bl < 85) & (r - bl > 45) & (r - g > 25)
    m = (yellow | handle).astype(np.float32)
    m = np.clip(blur(m, 2.5) * 3, 0, 1)[..., None]
    src = PL[y0:y1, x0:x1] if PL is not None else fr[y0+dy:y1+dy, x0+dx:x1+dx].astype(np.float32)
    fr[y0:y1, x0:x1] = np.clip(reg*(1-m)+src*m, 0, 255).astype(np.uint8)
    enc.stdin.write(fr.tobytes())
enc.stdin.close(); enc.wait(); print("ok")
