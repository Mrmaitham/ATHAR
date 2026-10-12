#!/usr/bin/env python3
# usage: kenburns.py IMG OUT.mp4 secs zoom cx cy [audio_src.mp4]  -> eased push-in from full frame to zoom x centred (cx,cy)
import sys, subprocess, numpy as np
from PIL import Image
img, out, secs, z, cx, cy = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
au = sys.argv[7] if len(sys.argv) > 7 else "v01.mp4"
W, H, fps = 1280, 720, 24
I = Image.open(img).convert("RGB"); I = I.resize((W*2, H*2), Image.LANCZOS)  # supersample for smoother crop
n = int(secs*fps); ease = lambda u: 0.5-0.5*np.cos(np.pi*u)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(fps),"-i","-","-stream_loop","-1","-i",au,"-map","0:v","-map","1:a","-t",f"{secs:.3f}",
    "-af",f"aresample=48000,afade=t=in:d=0.3,afade=t=out:st={secs-0.4:.3f}:d=0.4,volume=0.8","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-ar","48000",out],stdin=subprocess.PIPE)
for i in range(n):
    u = ease(i/(n-1)); s = 1+(z-1)*u
    x = W/2+(cx-W/2)*u; y = H/2+(cy-H/2)*u; cw, ch = W/s, H/s
    x0 = min(max(x-cw/2,0),W-cw); y0 = min(max(y-ch/2,0),H-ch)
    enc.stdin.write(I.crop((int(x0*2),int(y0*2),int((x0+cw)*2),int((y0+ch)*2))).resize((W,H),Image.LANCZOS).tobytes())
enc.stdin.close(); enc.wait(); print("ok", out)
