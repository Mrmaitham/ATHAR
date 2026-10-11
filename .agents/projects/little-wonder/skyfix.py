#!/usr/bin/env python3
# usage: skyfix.py IN.mp4 OUT.mp4 MASTER.png [ymax=300]
# Maps the colour of SKY pixels (blue-dominant, upper part only) to the master frame's sky
# (per-channel mean/std match, temporally smoothed), soft mask; characters below ymax untouched.
import sys, subprocess, numpy as np
from PIL import Image
inp, out, master = sys.argv[1], sys.argv[2], sys.argv[3]
YM = int(sys.argv[4]) if len(sys.argv) > 4 else 300
W, H = 1280, 720
def skymask(f):
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    m = np.clip((b-r-25)/30, 0, 1)*np.clip((b-110)/40, 0, 1)
    ramp = np.clip((YM+30-np.arange(H))/60, 0, 1)[:, None]
    return m*ramp
M = np.asarray(Image.open(master).convert("RGB")).astype(np.float32); mm = skymask(M) > 0.6
mu_t, sd_t = M[mm].mean(0), M[mm].std(0)
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
def frames():
    d = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
    while True:
        b = d.stdout.read(W*H*3)
        if len(b) < W*H*3: return
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
st = []
for fr in frames():
    f = fr.astype(np.float32); m = skymask(f) > 0.6
    st.append(np.concatenate([f[m].mean(0), f[m].std(0)]) if m.sum() > 300 else np.concatenate([mu_t, sd_t]))
st = np.array(st); k = 6
st = np.stack([np.convolve(np.pad(st[:, j], k, mode="edge"), np.ones(2*k+1)/(2*k+1), "valid") for j in range(6)], 1)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
for i, fr in enumerate(frames()):
    f = fr.astype(np.float32); mu, sd = st[i, :3], st[i, 3:]
    ratio = np.clip(sd_t/np.maximum(sd, 1), 0.7, 1.4)
    g = (f-mu)*ratio+mu_t
    a = skymask(f)[..., None]
    enc.stdin.write(np.clip(f*(1-a)+g*a, 0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait()
print("sky in first/last", st[0, :3].round(), st[-1, :3].round(), "-> target", mu_t.round())
