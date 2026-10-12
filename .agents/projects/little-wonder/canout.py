#!/usr/bin/env python3
# usage: canout.py IN.mp4 OUT.mp4 PLATE.png x0 y0 x1 y1 F_FULL F_END
# Inside the box, green watering-can pixels are replaced by the plate (offset-matched) for frames < F_FULL,
# then the replacement fades out linearly until F_END (the can is revealed under Grandma's hand).
import sys, subprocess, numpy as np
from PIL import Image
inp, out, plate = sys.argv[1:4]; x0, y0, x1, y1, FF, FE = map(int, sys.argv[4:10])
W, H = 1280, 720
PL = np.asarray(Image.open(plate).convert('RGB')).astype(np.float32)[y0:y1, x0:x1]
def blur(a, s):
    r = int(3*s); k = np.exp(-0.5*(np.arange(-r, r+1)/s)**2); k /= k.sum()
    a = np.pad(a.astype(np.float32), r, mode="edge")
    a = np.apply_along_axis(lambda v: np.convolve(v, k, "valid"), 0, a)
    return np.apply_along_axis(lambda v: np.convolve(v, k, "valid"), 1, a)
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
n = 0; off = None
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    if n < FE:
        reg = fr[y0:y1, x0:x1].astype(np.float32); r, g, bl = reg[..., 0], reg[..., 1], reg[..., 2]
        key = (g > 100) & (g - r > 20) & (g - bl > 10)
        m = np.clip(blur(blur(key.astype(np.float32), 3) > 0.05, 1.5) * 1.0, 0, 1)
        if off is None:  # colour-match plate to this clip using pixels outside the key
            ring = (m < 0.01)
            off = (reg[ring].mean(0) - PL[ring].mean(0))
        src = np.clip(PL + off, 0, 255)
        a = 1.0 if n < FF else max(0.0, 1 - (n - FF + 1) / (FE - FF + 1))
        m = (m * a)[..., None]
        fr[y0:y1, x0:x1] = np.clip(reg*(1-m)+src*m, 0, 255).astype(np.uint8)
    enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("ok", n, off)
