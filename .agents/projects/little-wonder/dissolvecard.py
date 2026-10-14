#!/usr/bin/env python3
# usage: dissolvecard.py A.png B.png OUT.mp4 "text" [secs=5]
# Day card between two real frames: starts exactly on A (end of previous shot), dissolves to B under a soft dark band
# card text shown over A, then a dissolve to B; ends exactly on B (first frame of next shot). No new image is invented.
import sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
A, B, out, txt = sys.argv[1:5]; T = float(sys.argv[5]) if len(sys.argv) > 5 else 5.0
W, H, fps = 1280, 720, 24
fa = np.asarray(Image.open(A).convert('RGB').resize((W, H)), np.float32); fb = np.asarray(Image.open(B).convert('RGB').resize((W, H)), np.float32)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 64)
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
w, h = d.textbbox((0, 0), txt, font=font)[2:]; pos = ((W-w)//2, (H-h)//2-40)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pos[0]+3, pos[1]+4), txt, font=font, fill=(30, 40, 70, 160))
sh = sh.filter(ImageFilter.GaussianBlur(4)); d.text(pos, txt, font=font, fill=(255, 255, 255, 255))
tl = np.asarray(Image.alpha_composite(sh, lay), np.float32); ta = tl[..., 3:] / 255
ease = lambda u: 0.5-0.5*np.cos(np.pi*np.clip(u, 0, 1))
N = int(round(T*fps))
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s","1280x720","-r",str(fps),"-i","-",
    "-stream_loop","-1","-i","/home/user/lw_v3/v01.mp4","-map","0:v","-map","1:a","-t",str(T),
    "-af","aresample=48000,afade=t=in:d=0.3,afade=t=out:st=%.2f:d=0.4,volume=0.8" % (T-0.4),
    "-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
for i in range(N):
    t = i/fps
    x = ease((t-0.58*T)/(0.32*T))                      # A -> B dissolve after the text
    al = np.clip(min((t-0.08*T)/0.5, (0.58*T-t)/0.5), 0, 1)   # band + text over A only
    if i == 0: x, al = 0, 0
    if i == N-1: x, al = 1, 0
    img = fa*(1-x) + fb*x
    img = img*(1-0.22*al)
    img = img*(1-ta*al) + tl[..., :3]*ta*al
    enc.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); print("ok", out, N)
