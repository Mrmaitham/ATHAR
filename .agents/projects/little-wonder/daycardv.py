#!/usr/bin/env python3
# usage: daycardv.py OUT.mp4 "Day 5" FROM_TILT.mp4 TO_FRAME.png TO_OUTPAINT.png
# Like daycard.py but the tilt-up is a real generated camera move (FROM_TILT.mp4, starts on the previous shot's last frame,
# ends on pure sky). Plays it, card over the sky, crossfade sky->TO top, tilt down into TO_FRAME (ends exactly on it).
import sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
out, txt, va, fb, ob = sys.argv[1:6]
W, H, fps = 1280, 720, 24
dec = subprocess.Popen(["ffmpeg","-v","error","-i",va,"-vf","scale=1280:720,fps=24","-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
A = []
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    A.append(Image.frombytes("RGB", (W, H), b))
F = Image.open(fb).convert('RGB').resize((W, H)); O = Image.open(ob).convert('RGB'); O = O.resize((W, int(round(O.height * W / O.width))), Image.LANCZOS)
fs = np.asarray(F.resize((320, 180))).astype(float); best = None
for oy in range(0, O.height - H + 1, 2):
    d = abs(np.asarray(O.crop((0, oy, W, oy + H)).resize((320, 180))).astype(float) - fs).mean()
    if best is None or d < best[0]: best = (d, oy)
d, oyb = best; B = O.copy(); md = np.ones((H, W)); md[:40] = np.linspace(0, 1, 40)[:, None]
B.paste(F, (0, oyb), Image.fromarray((md * 255).astype(np.uint8))); print('to offset', oyb, 'diff', round(d, 1), 'tilt frames', len(A))
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 64)
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
w, h = dr.textbbox((0, 0), txt, font=font)[2:]; pos = ((W - w) // 2, (H - h) // 2 - 140)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pos[0] + 3, pos[1] + 4), txt, font=font, fill=(30, 40, 70, 150)); sh = sh.filter(ImageFilter.GaussianBlur(4))
dr.text(pos, txt, font=font, fill=(255, 255, 255, 255)); textl = Image.alpha_composite(sh, lay)
ease = lambda u: 0.5 - 0.5 * np.cos(np.pi * np.clip(u, 0, 1))
TA = len(A) / fps; X0, X1 = TA - 0.2, TA + 1.0; C0, C1 = TA - 1.4, TA + 1.4; D0 = TA + 1.5; T = D0 + 2.5
N = int(round(T * fps))
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-stream_loop", "-1", "-i", "v01.mp4", "-map", "0:v", "-map", "1:a", "-t", f"{T:.3f}",
    "-af", f"aresample=48000,afade=t=in:d=0.3,afade=t=out:st={T-0.4:.3f}:d=0.4,volume=0.8", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart", "-c:a", "aac", "-ar", "48000", out], stdin=subprocess.PIPE)
for i in range(N):
    t = i / fps
    fra = A[min(i, len(A) - 1)]
    yb = int(round(oyb * ease((t - D0) / 2.5))); frb = B.crop((0, yb, W, yb + H))
    fr = Image.blend(fra, frb, float(ease((t - X0) / (X1 - X0)))).convert("RGBA")
    a = np.clip(min((t - C0) / 0.6, (C1 - t) / 0.6), 0, 1)
    if a > 0:
        tl = textl.copy(); al = np.asarray(tl.split()[3]).astype(np.float32) * a; tl.putalpha(Image.fromarray(al.astype(np.uint8))); fr = Image.alpha_composite(fr, tl)
    enc.stdin.write(fr.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("ok", out, round(T, 2), "s")
