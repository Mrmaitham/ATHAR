#!/usr/bin/env python3
# usage: pushcard.py FRAME.png OUT.mp4 "text" [secs=7] [zoom=1.18] [cx cy]
# Day-card made only from the real frame: slow eased push-in toward (cx,cy), card text fades in/out over a soft
# darkened band, then eased pull-back to the exact frame (so the next shot starts on the identical image).
# No new scenery is invented. Audio: birdsong from v01.mp4.
import sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
fr, out, txt = sys.argv[1], sys.argv[2], sys.argv[3]
T = float(sys.argv[4]) if len(sys.argv) > 4 else 7.0; Z = float(sys.argv[5]) if len(sys.argv) > 5 else 1.18
W, H, fps = 1280, 720, 24
cx = float(sys.argv[6]) if len(sys.argv) > 6 else W*0.35; cy = float(sys.argv[7]) if len(sys.argv) > 7 else H*0.25
F = Image.open(fr).convert('RGB').resize((W, H))
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 64)
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
w, h = d.textbbox((0, 0), txt, font=font)[2:]; pos = ((W-w)//2, (H-h)//2-40)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pos[0]+3, pos[1]+4), txt, font=font, fill=(30, 40, 70, 160))
sh = sh.filter(ImageFilter.GaussianBlur(4)); d.text(pos, txt, font=font, fill=(255, 255, 255, 255))
textl = Image.alpha_composite(sh, lay)
ease = lambda u: 0.5-0.5*np.cos(np.pi*np.clip(u, 0, 1))
N = int(round(T*fps))
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s","1280x720","-r",str(fps),"-i","-",
    "-stream_loop","-1","-i","/home/user/lw_v3/v01.mp4","-map","0:v","-map","1:a","-t",str(T),
    "-af","aresample=48000,afade=t=in:d=0.3,afade=t=out:st=%.2f:d=0.4,volume=0.8" % (T-0.4),
    "-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
a1, a2 = T*0.36, T*0.64           # push-in until a1, hold, pull-back from a2
for i in range(N):
    t = i/fps
    z = 1+(Z-1)*(ease(t/a1) if t < a1 else (1.0 if t < a2 else 1-ease((t-a2)/(T-a2))))
    if i == N-1: z = 1.0
    cw, ch = W/z, H/z; x0 = cx-(cx)/z; y0 = cy-(cy)/z
    img = F.transform((W, H), Image.EXTENT, (x0, y0, x0+cw, y0+ch), Image.BICUBIC).convert("RGBA")
    al = np.clip(min((t-a1*0.55)/0.6, (a2+0.35-t)/0.6), 0, 1)
    if al > 0:
        band = Image.new("RGBA", (W, H), (0, 0, 0, int(55*al)))
        img = Image.alpha_composite(img, band)
        tl = textl.copy(); tl.putalpha(tl.getchannel("A").point(lambda v: int(v*al)))
        img = Image.alpha_composite(img, tl)
    enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("ok", out, N)
