#!/usr/bin/env python3
# usage: daycard.py OUT.mp4 "Day 2" FROM_FRAME.png FROM_OUTPAINT.png TO_FRAME.png TO_OUTPAINT.png
# 7s camera-move transition: tilt up from FROM_FRAME into its outpainted top, card over the top, crossfade top->top,
# tilt down into TO_FRAME (ends exactly on TO_FRAME). Audio: birdsong from v01.mp4.
import sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
out, txt, fa, oa, fb, ob = sys.argv[1:7]
W, H, fps = 1280, 720, 24
def tall(frame, outp):
    F = Image.open(frame).convert('RGB').resize((W, H)); O = Image.open(outp).convert('RGB')
    O = O.resize((W, int(round(O.height * W / O.width))), Image.LANCZOS)
    fs = np.asarray(F.resize((320, 180))).astype(float); best = None
    for oy in range(0, O.height - H + 1, 2):
        c = np.asarray(O.crop((0, oy, W, oy + H)).resize((320, 180))).astype(float)
        d = abs(c - fs).mean()
        if best is None or d < best[0]: best = (d, oy)
    d, oy = best; T = O.copy()
    # paste real frame with soft top edge so the tilt ends exactly on it
    m = Image.new('L', (W, H), 255); md = np.ones((H, W)) ; ramp = 40
    md[:ramp] = np.linspace(0, 1, ramp)[:, None]
    m = Image.fromarray((md * 255).astype(np.uint8))
    T.paste(F, (0, oy), m)
    print(frame, 'offset', oy, 'diff', round(d, 1))
    return T, oy
A, oya = tall(fa, oa); B, oyb = tall(fb, ob)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 64)
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
w, h = d.textbbox((0, 0), txt, font=font)[2:]; pos = ((W - w) // 2, (H - h) // 2 - 140)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pos[0] + 3, pos[1] + 4), txt, font=font, fill=(30, 40, 70, 150)); sh = sh.filter(ImageFilter.GaussianBlur(4))
d.text(pos, txt, font=font, fill=(255, 255, 255, 255)); textl = Image.alpha_composite(sh, lay)
ease = lambda u: 0.5 - 0.5 * np.cos(np.pi * np.clip(u, 0, 1))
N = 7 * fps
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-stream_loop", "-1", "-i", "v01.mp4", "-map", "0:v", "-map", "1:a", "-t", "7",
    "-af", "aresample=48000,afade=t=in:d=0.3,afade=t=out:st=6.6:d=0.4,volume=0.8", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart", "-c:a", "aac", "-ar", "48000", out], stdin=subprocess.PIPE)
for i in range(N):
    t = i / fps
    ya = int(round(oya * (1 - ease(t / 2.5)))); yb = int(round(oyb * ease((t - 4.5) / 2.5)))
    fra = A.crop((0, ya, W, ya + H)); frb = B.crop((0, yb, W, yb + H))
    x = np.clip((t - 2.8) / 1.2, 0, 1)
    fr = Image.blend(fra, frb, float(ease(x))).convert("RGBA")
    a = np.clip(min((t - 1.8) / 0.6, (4.4 - t) / 0.6), 0, 1)
    if a > 0:
        tl = textl.copy(); al = np.asarray(tl.split()[3]).astype(np.float32) * a; tl.putalpha(Image.fromarray(al.astype(np.uint8)))
        fr = Image.alpha_composite(fr, tl)
    enc.stdin.write(fr.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("ok", out)
