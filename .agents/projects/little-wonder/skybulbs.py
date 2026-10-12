#!/usr/bin/env python3
# usage: skybulbs.py IN.mp4 OUT.mp4 [YMAX] [--dbg]  - lit string-light bulbs / lantern glass against the SKY -> unlit glass.
# warm-bright pixels whose neighbourhood is mostly sky are pulled to the local sky tone (frosted unlit glass). Skin/walls untouched.
import sys, subprocess, numpy as np
def uniform_filter(x, k):
    p = k // 2; c = np.pad(x, p, mode='edge').cumsum(0).cumsum(1); c = np.pad(c, ((1, 0), (1, 0)))
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)
def binary_dilation(m, iterations=1):
    return uniform_filter(m.astype(np.float32), 2 * iterations + 1) > 0
inp, out = sys.argv[1], sys.argv[2]; YM = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 360
DBG = '--dbg' in sys.argv; W, H = 1280, 720
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
n = 0
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(); a = fr[:YM].astype(np.float32); r, g, bl = a[..., 0], a[..., 1], a[..., 2]
    sky = ((bl > r + 25) & (bl > 150)).astype(np.float32)
    frac = uniform_filter(sky, 41)
    warm = (r > 200) & (r - bl > 35) & (g > 165)
    wf = warm.astype(np.float32); w41 = uniform_filter(wf, 41); w81 = uniform_filter(wf, 81); s81 = uniform_filter(sky, 81)
    m = warm & (frac > 0.30) & ((w41 < 0.05) | ((w81 < 0.10) & (s81 > 0.45)))
    m = binary_dilation(m, iterations=3) & (r - bl > 10) & ((r + g + bl) / 3 > 120)
    if m.any():
        skyc = np.stack([uniform_filter(a[..., c] * sky, 41) / np.maximum(uniform_filter(sky, 41), 1e-3) for c in range(3)], -1)
        tgt = np.minimum(a, skyc * 0.92)
        mm = uniform_filter(m.astype(np.float32), 3)[..., None]
        a = a * (1 - mm) + (np.array([255, 0, 255]) if DBG else tgt) * mm
        fr[:YM] = np.clip(a, 0, 255).astype(np.uint8)
    enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n)
