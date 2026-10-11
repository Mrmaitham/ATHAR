#!/usr/bin/env python3
# usage: unlitpost.py IN.mp4 OUT.mp4 x0 y0 x1 y1  - in the box, warm bright (lit) lamp-glass pixels -> frosted cool grey glass
import sys, subprocess, numpy as np
inp, out = sys.argv[1], sys.argv[2]; x0, y0, x1, y1 = map(int, sys.argv[3:7])
W, H = 1280, 720
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
n = 0
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    g = fr[y0:y1, x0:x1].astype(np.float32); warm = g[..., 0]-g[..., 2]; lum = g.mean(2)
    a = (np.clip((lum-140)/35, 0, 1)*np.maximum(np.clip((warm+5)/20, 0, 1), np.clip((lum-215)/20, 0, 1)))[..., None]
    grey = np.stack([lum*0.36+38, lum*0.38+42, lum*0.40+50], 2)       # frosted, cool, darker = unlit glass
    fr[y0:y1, x0:x1] = np.clip(g*(1-a)+grey*a, 0, 255).astype(np.uint8)
    enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n)
