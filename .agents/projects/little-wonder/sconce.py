#!/usr/bin/env python3
# usage: sconce.py IN.mp4 OUT.mp4 gx gy [grx gry]   (glass centre; fixed camera)
# 1) halo on the wall around the glass -> wall colour interpolated from left/right (one side if the other is hidden)
# 2) bright glass -> dark smoked glass (unlit). Dark pixels (people, lamp metal) are never touched.
import sys, os, subprocess, numpy as np
T0 = float(os.environ.get('T0', '-1e9')); T1 = float(os.environ.get('T1', '1e9'))
inp, out = sys.argv[1], sys.argv[2]; gx, gy = int(sys.argv[3]), int(sys.argv[4])
grx, gry = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (7, 10)
W, H = 1280, 720; HX, HY = 26, 34
fps = eval(subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip())
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-profile:v","high","-movflags","+faststart","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
y0, y1, x0, x1 = gy-HY-4, gy+HY+4, gx-HX-8, gx+HX+8
yy, xx = np.mgrid[y0:y1, x0:x1]
rh = np.sqrt(((xx-gx)/HX)**2+((yy-gy)/HY)**2); mh = np.clip((1.15-rh)/0.35, 0, 1); mh = (mh*mh*(3-2*mh))[..., None]
rg = np.sqrt(((xx-gx)/grx)**2+((yy-gy)/gry)**2); mg = np.clip((1.25-rg)/0.35, 0, 1); mg = (mg*mg*(3-2*mg))[..., None]
t = ((xx-x0)/(x1-1-x0))[..., None]
fi = -1
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(); fi += 1; tt = fi/fps
    TW = float(np.clip(min((tt-T0)/0.3, (T1-tt)/0.3), 0, 1))
    if TW <= 0: enc.stdin.write(fr.tobytes()); continue
    orig = fr[y0:y1, x0:x1].astype(np.float32)
    reg = fr[y0:y1, x0:x1].astype(np.float32); lum = reg.mean(2, keepdims=True)
    L = reg[:, :5].mean(1, keepdims=True); R = reg[:, -5:].mean(1, keepdims=True)
    Lok = L.mean(2, keepdims=True) > 110; Rok = R.mean(2, keepdims=True) > 110
    fill = np.where(Lok & Rok, L*(1-t)+R*t, np.where(Rok, R, L))
    wall = np.clip((lum-110)/30, 0, 1) * (Lok | Rok)
    a = mh*wall*(1-mg)
    reg = reg*(1-a)+fill*a
    GL = float(os.environ.get('GL', '150')); glass = np.clip((lum-GL)/40, 0, 1)
    if os.environ.get('GLASSBOX'):
        warm = (reg[..., :1]-reg[..., 2:3])
        box = ((np.abs(xx-gx) < grx*1.7) & (np.abs(yy-gy) < gry*1.5))[..., None]
        glass = np.clip((lum-160)/30, 0, 1)*np.clip((warm-15)/20, 0, 1)*box
        mg_use = np.ones_like(mg)
    else:
        mg_use = mg
    dark = np.array([62, 56, 50], np.float32) + (lum-150).clip(0)*0.08
    ag = mg_use*glass
    reg = reg*(1-ag)+dark*ag
    fr[y0:y1, x0:x1] = np.clip(orig*(1-TW)+reg*TW, 0, 255).astype(np.uint8)
    enc.stdin.write(fr.tobytes())
enc.stdin.close(); enc.wait(); print("ok")
