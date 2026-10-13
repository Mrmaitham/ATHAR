#!/usr/bin/env python3
# usage: starcomp.py GEN.mp4 OUT.mp4 BEFORE.png AFTER.png T7_FRAME SX SY
# Locked-camera star-board composite: the generated clip supplies the people (and Grandma's hand), the board
# region comes from stills - BEFORE (n stars) until frame T7, AFTER (n+1 stars) from T7 on - so the star count is exact.
# Anything in front of the board in the generated clip (hand, sleeve, the star she holds) is kept via a mask:
# pixels that differ from the generated board's own clean look (median of hand-free frames, before/after T7).
# At T7 a small star flies from the brightest point of her hand to the new slot (SX,SY) with a soft flash.
import sys, subprocess, numpy as np
from PIL import Image, ImageFilter
GEN, OUT, BEF, AFT, T7, SX, SY = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
W, H = 1280, 720
X0, Y0, X1, Y1 = 1040, 282, 1258, 468          # board region (whole board + margin)
raw = subprocess.run(["ffmpeg","-v","error","-i",GEN,"-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3); N = len(F)
B6 = np.asarray(Image.open(BEF).convert('RGB'), np.float32)[Y0:Y1, X0:X1]
B7 = np.asarray(Image.open(AFT).convert('RGB'), np.float32)[Y0:Y1, X0:X1]
R = F[:, Y0:Y1, X0:X1].astype(np.float32)
pre = np.median(R[:40], 0); post = np.median(R[N-18:], 0)
lum = lambda a: a[..., 0]*0.299 + a[..., 1]*0.587 + a[..., 2]*0.114
yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32)
# star sprite = new slot cut from AFTER, for the flying star
r = 13; spr = np.asarray(Image.open(AFT).convert('RGB'), np.float32)[SY-r:SY+r, SX-r:SX+r]
sm = np.clip((r - np.sqrt(((np.mgrid[-r:r, -r:r])**2).sum(0))) / 4, 0, 1)[..., None]
# take-off point: brightest pixel of the frame just before T7 inside the board area (the star in her hand)
g0 = R[T7-2]; L = lum(g0)*(np.abs(g0-pre).mean(2) > 30)*(g0[..., 1] > 0.8*g0[..., 0])
iy, ix = np.unravel_index(np.argmax(L), L.shape); P0 = (X0+ix, Y0+iy)
print("hand star at", P0, "-> slot", (SX, SY))
FLY = 9
out = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s","1280x720","-r","24","-i","-","-i",GEN,
                        "-map","0:v","-map","1:a?","-c:v","libx264","-crf","16","-pix_fmt","yuv420p","-c:a","copy","-shortest",OUT],stdin=subprocess.PIPE)
for f in range(N):
    g = R[f]
    if f < T7:                                   # before the press: anything unlike the clean board (hand, held star)
        m = np.abs(g - pre).mean(2) > 30
    else:                                        # after: board in any state (unlit, lit, glowing) counts as board
        glow = (lum(g) > 195) & (g[..., 1] > 0.8*g[..., 0])
        m = (np.abs(g - pre).mean(2) > 30) & (np.abs(g - post).mean(2) > 30) & ~glow
        if f >= T7+3:                            # hand has moved off to the left: right part = board only (kills generated glow rings)
            m[:, (P0[0]-X0)-20:] &= (lum(g)[:, (P0[0]-X0)-20:] < 60)
    mi = Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(1.5))
    a = np.asarray(mi, np.float32)[..., None]/255
    if f < T7: board = B6
    elif f < T7+FLY: board = B6.copy()           # new star not there yet - it is flying in
    else: board = B7
    if T7+FLY <= f < T7+FLY+4:                    # short cross-fade so the star "settles"
        k = (f-(T7+FLY)+1)/5; board = B6*(1-k) + B7*k
    comp = g*a + board*(1-a)
    o = F[f].copy(); o[Y0:Y1, X0:X1] = np.clip(comp, 0, 255).astype(np.uint8)
    of = o.astype(np.float32)
    if T7 <= f < T7+FLY:                          # flying star with a fading trail
        for j in range(4):
            t = max(0.0, (f-T7+1-j*0.6)/FLY); e = 1-(1-t)**2
            cx = P0[0]+(SX-P0[0])*e; cy = P0[1]+(SY-P0[1])*e - 22*np.sin(np.pi*e)
            x0, y0 = int(round(cx))-r, int(round(cy))-r
            if 0 <= x0 and x0+2*r < W and 0 <= y0 and y0+2*r < H:
                al = sm*(1.0 if j == 0 else 0.35/j)
                of[y0:y0+2*r, x0:x0+2*r] = np.maximum(of[y0:y0+2*r, x0:x0+2*r]*(1-al) + spr*al, of[y0:y0+2*r, x0:x0+2*r])
    if T7+FLY-1 <= f < T7+FLY+10:                 # soft flash at the slot when it lands
        k = f-(T7+FLY-1); amp = 0.9*np.exp(-k/3.5); rad = 10+3*k
        Y, X = np.mgrid[0:H, 0:W]
        gl = amp*np.exp(-((X-SX)**2+(Y-SY)**2)/(2*rad**2))[..., None]
        of = of + gl*np.array([255, 225, 120])*0.9
    out.stdin.write(np.clip(of, 0, 255).astype(np.uint8).tobytes())
out.stdin.close(); out.wait(); print("ok", OUT, N)
