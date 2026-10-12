#!/usr/bin/env python3
# usage: tracklamp.py IN.mp4 OUT.mp4 x y [x y ...]   (lamp glass centres in frame 0; works with a moving/zooming camera)
# Each lamp: tracked frame-to-frame (warm-bright blob in a small search window). Around it, the warm glow wash is pulled
# down to the surrounding wall level and the glass is darkened (unlit). Skips frames where the blob is lost (occluded).
import sys, os, subprocess, numpy as np
F1 = int(os.environ.get('F1', 10**9))  # stop after this frame
inp, out = sys.argv[1], sys.argv[2]; pts = list(map(int, sys.argv[3:])); L = [[pts[i], pts[i+1]] for i in range(0, len(pts), 2)]
W, H = 1280, 720
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
R0 = int(os.environ.get('R0', 34))  # glow radius at frame 0
n = 0; log = []; V = [[0.0, 0.0] for _ in L]
def warm(fr):
    f = fr.astype(np.float32); return f.mean(2) + 0.6*(f[..., 0]-f[..., 2])
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(); Wm = warm(fr)
    for k, (cx, cy) in (enumerate(L) if n < F1 else []):
        vx, vy = V[k]; px, py = int(round(cx+vx)), int(round(cy+vy))   # predicted position (constant velocity)
        sx = 4 if n > 6 else 10; x0, x1, y0, y1 = max(px-sx, 0), min(px+sx+1, W), max(py-sx, 0), min(py+sx+1, H)
        if x1 - x0 < 5 or y1 - y0 < 5: continue
        win = Wm[y0:y1, x0:x1]; yy, xx = np.unravel_index(win.argmax(), win.shape)
        peak = win.max(); nx, ny = x0+xx, y0+yy
        fw = fr[y0:y1, x0:x1].astype(np.float32); warmok = (fw[yy, xx, 0] - fw[yy, xx, 2]) > 25
        if peak < 190 or not warmok:
            L[k] = [px, py]; log.append((n, k, 'lost')); continue   # occluded / gone: coast
        V[k] = [0.7*vx + 0.3*(nx-cx), 0.7*vy + 0.3*(ny-cy)]
        L[k] = [nx, ny]
        R = int(R0*(1+0.5*n/max(1, fps*5)))
        a0, a1, b0, b1 = max(nx-R, 0), min(nx+R+1, W), max(ny-R, 0), min(ny+R+1, H)
        reg = fr[b0:b1, a0:a1].astype(np.float32); Y, X = np.mgrid[b0:b1, a0:a1]
        d = np.sqrt(((X-nx)/R)**2 + ((Y-ny)/R)**2)
        ring = (d > 0.85) & (d < 1.0)
        lum = reg.mean(2)
        if ring.sum() < 10: continue
        if (lum[d < 1.0] < 60).mean() > float(os.environ.get('OCC', 0.25)): continue   # hair/person in front: leave untouched
        wall = np.median(reg[ring], 0); wl = wall.mean()
        excess = np.clip(lum - wl, 0, None)[..., None]
        fall = np.clip((1-d)/0.35, 0, 1)[..., None]
        notdark = np.clip((lum-70)/30, 0, 1)[..., None]   # never touch hair/dark metal
        reg = reg - fall*notdark*excess*(reg/np.maximum(lum[..., None], 1))*0.95
        glass = (d < 0.22)[..., None] & (lum[..., None] > wl)
        if not os.environ.get('NOGLASS'): reg = np.where(glass, reg*0.55, reg)
        fr[b0:b1, a0:a1] = np.clip(reg, 0, 255).astype(np.uint8)
    enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n, "lost", len(log), "final", L)
