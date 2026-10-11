#!/usr/bin/env python3
# usage: wallfill.py IN.mp4 OUT.mp4 cx cy rx ry   - fixed-camera: removes a small lamp glow on a wall by row-wise
# interpolation of the wall colour from left/right of the ellipse; keeps dark pixels (lamp body, people)
import sys, os, subprocess, numpy as np
T0 = float(os.environ.get('T0', '-1e9')); T1 = float(os.environ.get('T1', '1e9'))
inp, out = sys.argv[1], sys.argv[2]; cx, cy, rx, ry = map(int, sys.argv[3:7])
W, H = 1280, 720
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
y0, y1, x0, x1 = cy-ry-6, cy+ry+6, cx-rx-14, cx+rx+14
yy, xx = np.mgrid[y0:y1, x0:x1]
r = np.sqrt(((xx-cx)/rx)**2+((yy-cy)/ry)**2); m = np.clip((1.3-r)/0.4, 0, 1); m = (m*m*(3-2*m))[..., None]
t = ((xx-x0)/(x1-1-x0))[..., None]
fi = -1
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(); fi += 1; tt = fi/fps
    TW = float(np.clip(min((tt-T0)/0.3, (T1-tt)/0.3), 0, 1))
    if TW <= 0: enc.stdin.write(fr.tobytes()); continue
    orig = fr[y0:y1, x0:x1].astype(np.float32)
    reg = fr[y0:y1, x0:x1].astype(np.float32)
    L = reg[:, :6].mean(1, keepdims=True); R = reg[:, -6:].mean(1, keepdims=True)
    lum = reg.mean(2, keepdims=True)
    Lok = L.mean(2, keepdims=True) > 100; Rok = R.mean(2, keepdims=True) > 100
    fill = np.where(Lok & Rok, L*(1-t)+R*t, np.where(Rok, R, L))     # one side hidden (e.g. hijab) -> use the other
    ok = Lok | Rok
    keep = np.clip((lum-95)/30, 0, 1)
    a = m*keep*ok
    fr[y0:y1, x0:x1] = np.clip(orig*(1-TW)+(reg*(1-a)+fill*a)*TW, 0, 255).astype(np.uint8)
    enc.stdin.write(fr.tobytes())
enc.stdin.close(); enc.wait(); print("ok")
