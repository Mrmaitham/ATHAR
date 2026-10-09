#!/usr/bin/env python3
# usage: flickqc.py ORIG NEW OUT.png [frame] — 5 consecutive frames zoomed on the changed area (orig row / new row)
# + prints temporal flicker in that area: mean |frame-to-frame change| orig vs new (new ≈ orig = no flicker)
import sys,subprocess,numpy as np,cv2
def frames(f):
    b=subprocess.run(['ffmpeg','-v','error','-i',f,'-f','rawvideo','-pix_fmt','bgr24','-'],capture_output=True).stdout
    return np.frombuffer(b,np.uint8).reshape(-1,720,1280,3)
A,Bv=frames(sys.argv[1]),frames(sys.argv[2]); N=min(len(A),len(Bv)); i0=int(sys.argv[4]) if len(sys.argv)>4 else N//2
d=(np.abs(A[:N].astype(np.int16)-Bv[:N].astype(np.int16)).sum(3)>40).any(0); ys,xs=np.where(d)
if len(xs)==0: print('no change'); sys.exit()
cx,cy=int(np.median(xs)),int(np.median(ys)); r=100; x0,y0=int(np.clip(cx-r,0,1280-2*r)),int(np.clip(cy-r,0,720-2*r))
ra=[cv2.resize(A[i][y0:y0+2*r,x0:x0+2*r],(240,240)) for i in range(i0,i0+5)]
rb=[cv2.resize(Bv[i][y0:y0+2*r,x0:x0+2*r],(240,240)) for i in range(i0,i0+5)]
cv2.imwrite(sys.argv[3],np.vstack([np.hstack(ra),np.hstack(rb)]))
reg=lambda X:X[:N,y0:y0+2*r,x0:x0+2*r].astype(np.float32)
fa=np.abs(np.diff(reg(A),axis=0)).mean(); fb=np.abs(np.diff(reg(Bv),axis=0)).mean()
print(f'flicker orig {fa:.2f} new {fb:.2f} ratio {fb/fa:.2f}')
