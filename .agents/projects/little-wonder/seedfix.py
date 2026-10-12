#!/usr/bin/env python3
# usage: X0=..X1=..Y0=..Y1=..F0=.. seedfix.py IN.mp4 OUT.mp4  - olive/green seed pixels inside the box -> cream bean colour (keeps shading)
import sys, os, subprocess, numpy as np
inp, out = sys.argv[1], sys.argv[2]; W, H = 1280, 720
X0, X1, Y0, Y1 = (int(os.environ[k]) for k in ("X0", "X1", "Y0", "Y1")); F0 = int(os.environ.get("F0", 0)); F1 = int(os.environ.get("F1", 10**9))
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","copy",out], stdin=subprocess.PIPE)
cream = np.array([240, 226, 190], np.float32); n = 0
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    if F0 <= n < F1:
        reg = fr[Y0:Y1, X0:X1].astype(np.float32); r, g, bl = reg[..., 0], reg[..., 1], reg[..., 2]
        m = np.clip((g - bl - 20) / 15, 0, 1) * np.clip((g - r + 22) / 12, 0, 1)
        lum = reg.mean(2, keepdims=True) / 140.0
        tgt = np.clip(cream * np.clip(lum * 1.5, 0.72, 1.08), 0, 255)
        reg = reg * (1 - m[..., None]) + tgt * m[..., None]
        fr[Y0:Y1, X0:X1] = reg.astype(np.uint8)
    enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n)
