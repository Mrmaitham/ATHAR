#!/usr/bin/env python3
# usage: camtrack.py IN.mp4 REF_FRAME x0 y0 x1 y1  -> prints per-frame (dx,dy) of the background patch vs REF_FRAME
# (phase correlation, chained frame-to-frame for robustness). Writes IN.track.npy (n,2): position of a REF point = p + track[i].
import sys, subprocess, numpy as np
inp = sys.argv[1]; ref = int(sys.argv[2]); x0, y0, x1, y1 = map(int, sys.argv[3:7])
W, H = 1280, 720
d = subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-f","rawvideo","-pix_fmt","gray","-"], stdout=subprocess.PIPE)
F = []
while True:
    b = d.stdout.read(W*H)
    if len(b) < W*H: break
    F.append(np.frombuffer(b, np.uint8).reshape(H, W)[y0:y1, x0:x1].astype(np.float32))
win = np.outer(np.hanning(y1-y0), np.hanning(x1-x0))
def pc(a, b):
    A = np.fft.fft2((a-a.mean())*win); B = np.fft.fft2((b-b.mean())*win)
    R = A*np.conj(B); R /= np.abs(R)+1e-6; r = np.fft.ifft2(R).real
    y, x = np.unravel_index(r.argmax(), r.shape)
    # subpixel
    def sp(c, n, axis):
        cm = r[(y if axis else (c-1) % n), ((c-1) % n if axis else x)]; c0 = r[y, x]; cp = r[(y if axis else (c+1) % n), ((c+1) % n if axis else x)]
        den = cm - 2*c0 + cp; return c + (0.5*(cm-cp)/den if abs(den) > 1e-9 else 0)
    fy = sp(y, r.shape[0], 0); fx = sp(x, r.shape[1], 1)
    if fy > r.shape[0]/2: fy -= r.shape[0]
    if fx > r.shape[1]/2: fx -= r.shape[1]
    return fx, fy   # shift of a relative to b
n = len(F); T = np.zeros((n, 2))
for i in range(ref+1, n): T[i] = T[i-1] + pc(F[i], F[i-1])
for i in range(ref-1, -1, -1): T[i] = T[i+1] + pc(F[i], F[i+1])
np.save(inp + ".track.npy", T)
print(n, [tuple(np.round(T[i], 1)) for i in range(0, n, 12)])
