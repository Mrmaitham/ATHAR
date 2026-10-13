#!/usr/bin/env python3
# usage: necklacekill.py IN.(mp4|png) OUT [K=11] [x0 y0 x1 y1]
# Removes Grandma's thin silver chain / cross pendant from her black abaya in every frame.
# Grey-level opening (min then max filter, size K) wipes bright structures thinner than K px; it is applied only
# where the opened result is dark (the abaya), the original is clearly brighter and grey (no skin, no hair colour).
import sys, subprocess, numpy as np
from PIL import Image, ImageFilter
inp, out = sys.argv[1], sys.argv[2]
K = int(sys.argv[3]) if len(sys.argv) > 3 else 11
BOX = list(map(int, sys.argv[4:8])) if len(sys.argv) > 7 else [0, 0, 1280, 720]
W, H = 1280, 720
def clean(fr):
    x0, y0, x1, y1 = BOX; reg = fr[y0:y1, x0:x1]
    im = Image.fromarray(reg)
    op = np.asarray(im.filter(ImageFilter.MinFilter(K)).filter(ImageFilter.MaxFilter(K)), np.float32)
    big = np.asarray(im.filter(ImageFilter.MinFilter(K + 10)).filter(ImageFilter.MaxFilter(K + 10)), np.float32)
    r = reg.astype(np.float32); lum = r.mean(2); ol = op.mean(2); bl = big.mean(2)
    ch = r.max(2) - r.min(2); grey = ch < 30; neutral = (ch < 22) & (np.abs(r[..., 0] - r[..., 2]) < 16)   # silver is neutral, hair is brown
    dk = np.asarray(Image.fromarray(((lum < 60) * 255).astype(np.uint8)).resize((lum.shape[1]//4, lum.shape[0]//4), Image.BILINEAR).filter(ImageFilter.BoxBlur(5)).resize((lum.shape[1], lum.shape[0]), Image.BILINEAR), np.float32) / 255
    loose = (ol < 75) & (bl < 80) & ((lum - ol) > 25) & (lum > 60) & grey
    seed = (ol < 70) & (bl < 70) & ((lum - ol) > 40) & (lum > 75) & neutral & (dk > 0.62)   # deep inside the dark abaya chest
    # the chain is a cluster of seeds: keep seeds with >=25 others within ~40 px, then clean 'loose' pixels around them
    q = np.asarray(Image.fromarray((seed * 255).astype(np.uint8)).resize((seed.shape[1]//4, seed.shape[0]//4), Image.BOX), np.float32) / 255 * 16   # seeds per 4x4 cell
    c = np.pad(q, 6).cumsum(0).cumsum(1); dens = c[11:-1, 11:-1] - c[:-12, 11:-1] - c[11:-1, :-12] + c[:-12, :-12]       # seeds in 11x11 cells (~44 px)
    core = dens > 25
    reg_ = Image.fromarray((core * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).resize((seed.shape[1], seed.shape[0]), Image.NEAREST)
    m = loose & (np.asarray(reg_) > 128)
    mm = np.clip(1.4 * np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.5)), np.float32)[..., None] / 255, 0, 1)
    src = np.asarray(Image.fromarray(op.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)), np.float32)
    fr[y0:y1, x0:x1] = np.clip(r * (1 - mm) + src * mm, 0, 255).astype(np.uint8)
    return int(m.sum())
if inp.endswith('.png'):
    fr = np.asarray(Image.open(inp).convert('RGB').resize((W, H))).copy(); print('px', clean(fr)); Image.fromarray(fr).save(out); sys.exit()
fps = subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",inp],capture_output=True,text=True).stdout.strip()
dec = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-vf","scale=1280:720","-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",fps,"-i","-","-i",inp,
    "-map","0:v","-map","1:a?","-c:v","libx264","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-ar","48000",out], stdin=subprocess.PIPE)
n = tot = 0
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(); tot += clean(fr); enc.stdin.write(fr.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print('frames', n, 'px', tot)
