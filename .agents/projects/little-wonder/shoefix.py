#!/usr/bin/env python3
# usage: X0=.. X1=.. Y0=.. F1=.. shoefix.py IN.mp4 OUT.mp4  - pink pixels inside box (frames < F1) -> white (keeps shading)
import sys, os, subprocess, numpy as np
inp, out = sys.argv[1], sys.argv[2]; W, H = 1280, 720
X0, X1, Y0, Y1 = (int(os.environ.get(k, d)) for k, d in (('X0', 0), ('X1', W), ('Y0', 0), ('Y1', H)))
F0, F1 = int(os.environ.get('F0', 0)), int(os.environ.get('F1', 10**9))
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
n = 0; tot = 0
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    if F0 <= n < F1:
        reg = fr[Y0:Y1, X0:X1].astype(np.float32); r, g, bl = reg[..., 0], reg[..., 1], reg[..., 2]
        pink = np.clip(((r - g) - float(os.environ.get("RG", 20))) / 25, 0, 1) * np.clip(((bl - g) + 6) / 10, 0, 1) * (bl > 55)
        lum = (0.3*r + 0.59*g + 0.11*bl)
        lum = np.maximum(lum*1.25, 0); white = np.stack([lum, lum, lum*1.03], -1)
        m = pink[..., None]; tot += int((pink > 0.5).sum())
        fr[Y0:Y1, X0:X1] = np.clip(reg*(1-m) + white*m, 0, 255).astype(np.uint8)
    enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "px", tot)
