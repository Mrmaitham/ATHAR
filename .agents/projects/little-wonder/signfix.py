#!/usr/bin/env python3
# usage: signfix.py IN.mp4 OUT.mp4 REF_FRAME OLD_REF.png NEW_REF.png RX RY BX0 BY0 BX1 BY1
# Replaces the lettering on a moving sign. OLD_REF/NEW_REF = same crop of frame REF_FRAME (crop origin RX,RY in the frame),
# NEW_REF has the corrected word. Board face box (frame coords) BX0..BY1 is tracked in every frame with a
# scale+translation model (coarse 1/4-res search, then full-res subpixel refine), forward and backward from REF_FRAME.
# Only pixels where NEW differs from OLD (the lettering, dilated + feathered) are replaced; anything passing in
# front of the sign (hands, trowel) is kept via an occlusion test against the warped OLD board. Colour gain and
# blur are matched per frame. Audio is copied.
import sys, subprocess, numpy as np
from PIL import Image, ImageFilter
a = sys.argv[1:]
IN, OUT, RF = a[0], a[1], int(a[2])
OLD = np.asarray(Image.open(a[3]).convert('RGB'), np.float32)
NEWim = Image.open(a[4]).convert('RGB').resize((OLD.shape[1], OLD.shape[0]), Image.LANCZOS)
NEW = np.asarray(NEWim, np.float32)
RX, RY = int(a[5]), int(a[6]); BX0, BY0, BX1, BY1 = map(int, a[7:11])
W, H = 1280, 720
import os; NOOCC = os.environ.get('NOOCC') == '1'; START = int(os.environ.get('START', '0')); END = int(os.environ.get('END', '100000'))   # frames >= END untouched, 8-frame fade before END   # frames before START are left untouched   # set when nothing passes in front of the sign (avoids old-letter ghosts)
raw = subprocess.run(["ffmpeg","-v","error","-i",IN,"-vf","scale=1280:720","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3); N = len(F)
gray = lambda x: x[..., 0]*0.299 + x[..., 1]*0.587 + x[..., 2]*0.114

# align NEW to OLD (the image edit can shift the crop a little): best integer shift on the board area
bo = (BX0-RX, BY0-RY, BX1-RX, BY1-RY)
go, gn = gray(OLD), gray(NEW); best = (1e18, 0, 0)
for dy in range(-12, 13):
    for dx in range(-12, 13):
        x0, y0, x1, y1 = bo[0]+12, bo[1]+12, bo[2]-12, bo[3]-12
        e = np.abs(go[y0:y1, x0:x1] - gn[y0+dy:y1+dy, x0+dx:x1+dx]).mean()
        if e < best[0]: best = (e, dx, dy)
_, sdx, sdy = best
NEW = np.roll(np.roll(NEW, -sdy, 0), -sdx, 1)
print("new->old shift", sdx, sdy, "err", round(best[0], 2))
# colour-match NEW to OLD on the board outside the lettering
d0 = np.abs(NEW - OLD).mean(2)
board = np.zeros(d0.shape, bool); board[bo[1]:bo[3], bo[0]:bo[2]] = True
calm = board & (d0 < 12)
g = np.array([np.median(OLD[..., c][calm]) / max(1, np.median(NEW[..., c][calm])) for c in range(3)])
NEW = np.clip(NEW * g, 0, 255)
# change mask = lettering difference, inside board, dilated + feathered
ch = (np.abs(NEW - OLD).mean(2) > 22) & board
cm = Image.fromarray((ch*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3))
CM = np.asarray(cm, np.float32) / 255 * board
face = np.zeros(d0.shape, np.uint8); face[bo[1]+10:bo[3]-10, bo[0]+10:bo[2]-10] = 255
face = np.asarray(Image.fromarray(face).filter(ImageFilter.GaussianBlur(5)), np.float32)/255
CM = np.maximum(CM, face)
print("change pixels", int(ch.sum()))

# template (board) in ref frame
cx, cy = (BX0+BX1)/2, (BY0+BY1)/2
TPL = gray(F[RF][BY0:BY1, BX0:BX1].astype(np.float32))
def score(fr_g, s, tx, ty, th=0.0, q=1):
    # sample frame at ref-board grid mapped by p' = s*R(th)(p-c)+c+t  (q = subsample step)
    ys, xs = np.mgrid[BY0:BY1:q, BX0:BX1:q].astype(np.float32)
    cs, sn = np.cos(th), np.sin(th); u, v_ = xs-cx, ys-cy
    X = s*(cs*u-sn*v_)+cx+tx; Y = s*(sn*u+cs*v_)+cy+ty
    ok = (X >= 0) & (X < W-1) & (Y >= 0) & (Y < H-1)
    if ok.mean() < 0.35: return 1e9
    Xi, Yi = np.clip(X, 0, W-2), np.clip(Y, 0, H-2)
    x0, y0 = Xi.astype(int), Yi.astype(int); fx, fy = Xi-x0, Yi-y0
    v = (fr_g[y0, x0]*(1-fx)*(1-fy) + fr_g[y0, x0+1]*fx*(1-fy) + fr_g[y0+1, x0]*(1-fx)*fy + fr_g[y0+1, x0+1]*fx*fy)
    t = TPL[::q, ::q]
    e = np.abs(v - t)
    return np.median(e[ok]) + 0.3*e[ok].mean()   # robust to occluders
def track(f, p):
    fr = gray(F[f].astype(np.float32)); s, tx, ty, th = p
    best = (score(fr, s, tx, ty, th, 4), s, tx, ty, th)
    for step in (8, 4, 2, 1, 0.5, 0.25):
        q = 4 if step >= 4 else (2 if step >= 1 else 1)
        best = (score(fr, *best[1:], q),) + best[1:]
        improved = True
        while improved:
            improved = False
            for ds in ((0.985, 1.0, 1.015) if step >= 2 else (0.996, 1.0, 1.004)):
                for dth in ((-0.012, 0, 0.012) if step >= 2 else (-0.003, 0, 0.003)):
                    for dx in (-step, 0, step):
                        for dy in (-step, 0, step):
                            c = (best[1]*ds, best[2]+dx, best[3]+dy, best[4]+dth)
                            e = score(fr, *c, q)
                            if e < best[0] - 1e-6: best = (e,) + c; improved = True
    return best[1:], best[0]
P = [None]*N; P[RF] = (1.0, 0.0, 0.0, 0.0)
for f in range(RF+1, min(N, END)): P[f], e = track(f, P[f-1])
for f in range(RF-1, START-1, -1): P[f], e = track(f, P[f+1])

# composite
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
out = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s","1280x720","-r","24","-i","-","-i",IN,
                        "-map","0:v","-map","1:a?","-c:v","libx264","-crf","16","-pix_fmt","yuv420p","-c:a","copy","-shortest",OUT],stdin=subprocess.PIPE)
def warp(img, s, tx, ty, th=0.0):
    # inverse map frame pixel -> crop coords: p = R(-th)(p'-c-t)/s + c ; crop coords = p - (RX,RY)
    cs, sn = np.cos(th), np.sin(th); u, v_ = (xx-cx-tx)/s, (yy-cy-ty)/s
    X = (cs*u+sn*v_)+cx-RX; Y = (-sn*u+cs*v_)+cy-RY
    h, w = img.shape[:2]; ok = (X >= 0) & (X < w-1) & (Y >= 0) & (Y < h-1)
    Xi, Yi = np.clip(X, 0, w-2), np.clip(Y, 0, h-2); x0, y0 = Xi.astype(int), Yi.astype(int); fx, fy = Xi-x0, Yi-y0
    if img.ndim == 3: fx, fy = fx[..., None], fy[..., None]
    v = img[y0, x0]*(1-fx)*(1-fy) + img[y0, x0+1]*fx*(1-fy) + img[y0+1, x0]*(1-fx)*fy + img[y0+1, x0+1]*fx*fy
    return v, ok
log = []
for f in range(N):
    if f < START or f >= END: out.stdin.write(F[f].tobytes()); continue
    s, tx, ty, th = P[f]; fr = F[f].astype(np.float32)
    m, ok = warp(CM, s, tx, ty, th); m = m*ok
    if m.max() < 0.05: out.stdin.write(F[f].tobytes()); continue
    wo, _ = warp(OLD, s, tx, ty, th); wn, _ = warp(NEW, s, tx, ty, th)
    sel = m > 0.5
    # blur match: pick the softening that makes warped OLD closest to the frame on the board
    bb = np.argwhere(m > 0.01); y0, x0 = bb.min(0); y1, x1 = bb.max(0)+1
    y0, x0 = max(0, y0-6), max(0, x0-6); y1, x1 = min(H, y1+6), min(W, x1+6)
    best = None
    for r in (0, 0.7, 1.2, 1.8, 2.6, 3.6):
        bo_ = np.asarray(Image.fromarray(wo[y0:y1, x0:x1].astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), np.float32) if r else wo[y0:y1, x0:x1]
        e = np.abs(bo_ - fr[y0:y1, x0:x1]).mean(2)[sel[y0:y1, x0:x1]]
        e = np.median(e) if e.size else 1e9
        if best is None or e < best[0]: best = (e, r)
    r = best[1]
    blur = lambda im: np.asarray(Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), np.float32) if r else im
    wo_c, wn_c = blur(wo[y0:y1, x0:x1]), blur(wn[y0:y1, x0:x1]); frc = fr[y0:y1, x0:x1]; mc = m[y0:y1, x0:x1]
    # colour gain from unoccluded board pixels
    diff = np.abs(wo_c - frc).mean(2)
    clean = (mc > 0.3) & (diff < 30)
    gain = np.array([np.median(frc[..., c][clean]) / max(1, np.median(wo_c[..., c][clean])) for c in range(3)]) if clean.sum() > 30 else np.ones(3)
    gain = np.clip(gain, 0.75, 1.3)
    # occlusion: where the frame does not look like the (gain-matched) old board, keep the frame
    occ = np.minimum(np.abs(wo_c*gain - frc).mean(2), np.abs(wn_c*gain - frc).mean(2)) > 42
    occ = np.asarray(Image.fromarray((occ*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2)), np.float32)/255
    if NOOCC: occ = occ*0
    al = (mc*(1-occ))[..., None] * min(1.0, (END-f)/8.0)
    frc2 = frc*(1-al) + np.clip(wn_c*gain, 0, 255)*al
    o = F[f].copy(); o[y0:y1, x0:x1] = np.clip(frc2, 0, 255).astype(np.uint8)
    out.stdin.write(o.tobytes())
    log.append((f, round(s, 3), round(tx, 1), round(ty, 1), round(th, 3), r, round(float(occ.mean()), 2)))
out.stdin.close(); out.wait()
for l in log[::12]: print(l)
print("ok", OUT, N)
