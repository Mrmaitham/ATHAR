#!/usr/bin/env python3
# usage: hairfix.py IN.(mp4|png) OUT [STRENGTH=0.42]
# Darkens Nadyah's brown hair to the reference near-black brown in every frame.
# Nadyah is found by her royal-blue vest (the only blue clothes); her head box sits on top of it.
# Hair = brown pixels (R>G>B, moderate warmth, mid/low luminance) inside that box; skin, pots and wood are excluded
# by luminance / warmth limits and by staying above the vest's shoulder line (except the ponytail column).
import sys, subprocess, numpy as np
sys.path.insert(0, '/home/user/lw_tools'); from bgblur import depth
from PIL import Image, ImageFilter
inp, out = sys.argv[1], sys.argv[2]
K = float(sys.argv[3]) if len(sys.argv) > 3 else 0.6
W, H = 1280, 720
prev = None; NEAR = None; NI = 0
def fix(fr):
    global prev, NEAR, NI
    if NI % 3 == 0:
        d = depth(Image.fromarray(fr)); t = 0.22                                  # normalised depth: house ~0.05, people ~0.35+
        NEAR = np.asarray(Image.fromarray(((d > t) * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5)), np.float32) > 128
    NI += 1
    a = fr.astype(np.float32); R, G, B = a[..., 0], a[..., 1], a[..., 2]
    vest = (B > 140) & (B - R > 110) & (B - G > 45)            # saturated royal blue, not sky or glass
    vest[:260] = False
    ys, xs = np.nonzero(vest)
    if len(xs) < 300:
        if prev is None: return 0
        cx, top = prev
    else:
        cx = int(np.median(xs)); top = int(np.percentile(ys, 2))
        if prev: cx, top = int(0.6 * cx + 0.4 * prev[0]), int(0.6 * top + 0.4 * prev[1])
    prev = (cx, top)
    x0, x1, y0, y1 = max(cx - 150, 0), min(cx + 170, W), max(top - 190, 0), min(top + 90, H)
    r = a[y0:y1, x0:x1]; R, G, B = r[..., 0], r[..., 1], r[..., 2]
    lum = r.mean(2); warm = R - B
    hair = (R >= G - 2) & (G >= B - 4) & (warm > 12) & (warm < 95) & (lum > 12) & (lum < 118) & ((R - G) < 55) & (warm > 0.25 * R)   # dark saturated brown only (skin is lighter)
    Y = np.arange(y0, y1)[:, None] + np.zeros((1, x1 - x0))
    hair &= NEAR[y0:y1, x0:x1]                                                       # people only, never the house / palms
    X = np.arange(x0, x1)[None, :] + np.zeros((y1 - y0, 1))
    hair &= ~((Y > top + 10) & (np.abs(X - cx) < 70))                               # nothing on the chest / arms
    Y = np.arange(y0, y1)[:, None] + np.zeros((1, x1 - x0)); X = np.arange(x0, x1)[None, :] + np.zeros((y1 - y0, 1))
    skin = (lum > 105) & (R - B > 35) & (R > 150) & (R - G > 25)
    face = np.asarray(Image.fromarray((skin * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(25)).filter(ImageFilter.MinFilter(19)), np.float32) > 128
    hair &= ~face                                                                      # never inside the face / neck (shadows, eyes, mouth)
    m = Image.fromarray((hair * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.MinFilter(7))   # erode: breaks thin fringe links to the eyebrows
    # keep only the hair blob connected to the head: flood-fill from seeds on the crown
    from PIL import ImageDraw
    ma = np.asarray(m); hy, hx = np.nonzero(ma[max(0, top - 175 - y0):max(1, top - 60 - y0), max(0, cx - 80 - x0):cx + 80 - x0] > 128)
    seeds = [(int(hx[k] + max(0, cx - 80 - x0)), int(hy[k] + max(0, top - 175 - y0))) for k in range(0, len(hy), max(1, len(hy) // 25))]
    # ponytail seeds: dark hair column beside the head (either side), from ear level down to the shoulders
    for side in (-1, 1):
        qx0, qx1 = (cx + 30, cx + 140) if side > 0 else (cx - 140, cx - 30)
        qx0, qx1, qy0, qy1 = max(qx0 - x0, 0), max(qx1 - x0, 1), max(top - 120 - y0, 0), max(top + 40 - y0, 1)
        py, px = np.nonzero((ma[qy0:qy1, qx0:qx1] > 128) & (lum[qy0:qy1, qx0:qx1] < 70))
        if len(py) > 150: seeds += [(int(px[k] + qx0), int(py[k] + qy0)) for k in range(0, len(py), max(1, len(py) // 15))]
    for sx, sy in seeds:
        if m.getpixel((sx, sy)) == 255: ImageDraw.floodfill(m, (sx, sy), 128)
    reg = Image.fromarray(((np.asarray(m) == 128) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))   # the connected hair area (undo the erosion)
    m = Image.fromarray((((np.asarray(reg) > 128) & hair) * 255).astype(np.uint8))                          # but only true hair pixels inside it
    # keep only blobs connected to the head area: dilate-erode closing, then a soft edge
    m = m.filter(ImageFilter.GaussianBlur(0.8))
    mm = np.asarray(m, np.float32)[..., None] / 255
    tgt = r * K * np.array([1.0, 1.02, 1.12])                                          # same texture, darker and less red = near-black brown
    fr[y0:y1, x0:x1] = np.clip(r * (1 - mm) + tgt * mm, 0, 255).astype(np.uint8)
    return int((mm > 0.5).sum())
if inp.endswith('.png'):
    fr = np.asarray(Image.open(inp).convert('RGB').resize((W, H))).copy(); print('px', fix(fr)); Image.fromarray(fr).save(out); sys.exit()
fps = subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip()
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-vf","scale=1280:720","-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",fps,"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","copy",out], stdin=subprocess.PIPE)
n = 0
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(); fix(fr); enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print('frames', n)
