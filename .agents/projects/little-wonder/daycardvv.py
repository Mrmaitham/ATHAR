#!/usr/bin/env python3
# usage: daycardvv.py OUT.mp4 "Day 2" FROM_TILT.mp4 TO_TILTUP.mp4 TO_FRAME.png
# Day card from two real generated camera moves: FROM_TILT (prev shot last frame -> sky) plays forward,
# card over the sky, sky->sky crossfade, then TO_TILTUP (generated from the anchor -> sky) plays REVERSED as a tilt-down,
# last frames eased onto TO_FRAME so it ends exactly on the anchor. Run in /home/user/lw_v3 (birdsong from v01.mp4).
import sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
out, txt, va, vb, fb = sys.argv[1:6]
W, H, fps = 1280, 720, 24
def frames(p):
    dec = subprocess.Popen(["ffmpeg","-v","error","-i",p,"-vf","scale=1280:720,fps=24","-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE); L = []
    while True:
        b = dec.stdout.read(W*H*3)
        if len(b) < W*H*3: return L
        L.append(Image.frombytes("RGB", (W, H), b))
A = frames(va); B = frames(vb)[::-1][12:]; F = Image.open(fb).convert('RGB').resize((W, H))
print('tilt up', len(A), 'tilt down', len(B), 'B end vs anchor', round(abs(np.asarray(B[-1]).astype(float) - np.asarray(F).astype(float)).mean(), 1))
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 64)
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
w, h = dr.textbbox((0, 0), txt, font=font)[2:]; pos = ((W - w) // 2, (H - h) // 2 - 140)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((pos[0] + 3, pos[1] + 4), txt, font=font, fill=(30, 40, 70, 150)); sh = sh.filter(ImageFilter.GaussianBlur(4))
dr.text(pos, txt, font=font, fill=(255, 255, 255, 255)); textl = Image.alpha_composite(sh, lay)
ease = lambda u: float(0.5 - 0.5 * np.cos(np.pi * np.clip(u, 0, 1)))
HOLD, XF = 0.4, 1.2                      # hold on A's sky, crossfade into B's sky (both pure sky)
TA = len(A) / fps; X0 = TA + HOLD; X1 = X0 + XF; TB = X1; T = TB + len(B) / fps
C0, C1 = TA - 0.8, X1 + 0.2; N = int(round(T * fps)); EZ = 8
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-stream_loop", "-1", "-i", "v01.mp4", "-map", "0:v", "-map", "1:a", "-t", f"{T:.3f}",
    "-af", f"aresample=48000,afade=t=in:d=0.3,afade=t=out:st={T-0.4:.3f}:d=0.4,volume=0.8", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart", "-c:a", "aac", "-ar", "48000", out], stdin=subprocess.PIPE)
for i in range(N):
    t = i / fps
    if t < X0: fr = A[min(i, len(A) - 1)]
    elif t < X1: fr = Image.blend(A[-1], B[0], ease((t - X0) / XF))
    else:
        j = min(int(round((t - TB) * fps)), len(B) - 1); fr = B[j]
        k = j - (len(B) - EZ)
        if k >= 0: fr = Image.blend(fr, F, ease((k + 1) / EZ))
    fr = fr.convert("RGBA"); a = np.clip(min((t - C0) / 0.6, (C1 - t) / 0.6), 0, 1)
    if a > 0:
        tl = textl.copy(); al = np.asarray(tl.split()[3]).astype(np.float32) * a; tl.putalpha(Image.fromarray(al.astype(np.uint8))); fr = Image.alpha_composite(fr, tl)
    enc.stdin.write(fr.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("ok", out, round(T, 2), "s")
