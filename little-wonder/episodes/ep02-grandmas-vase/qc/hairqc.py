#!/usr/bin/env python3
# usage: hairqc.py ORIG NEW OUT.png — 4 moments: new frame (scaled) | changed pixels in red | zoom on the changed area
import sys,subprocess,numpy as np,cv2
o,n,out=sys.argv[1:4]
def frames(f):
    b=subprocess.run(['ffmpeg','-v','error','-i',f,'-f','rawvideo','-pix_fmt','bgr24','-'],capture_output=True).stdout
    return np.frombuffer(b,np.uint8).reshape(-1,720,1280,3)
A,Bv=frames(o),frames(n); N=min(len(A),len(Bv)); rows=[]
for i in np.linspace(0,N-1,4).astype(int):
    d=np.abs(A[i].astype(int)-Bv[i].astype(int)).sum(2)>45
    ov=Bv[i].copy(); ov[d]=(0,0,255)
    ys,xs=np.where(d)
    if len(xs): cx,cy=int(np.median(xs)),int(np.median(ys))
    else: cx,cy=640,360
    x0,y0=int(np.clip(cx-150,0,980)),int(np.clip(cy-150,0,420))
    z=np.hstack([A[i][y0:y0+300,x0:x0+300],Bv[i][y0:y0+300,x0:x0+300]])
    z=cv2.resize(z,(480,240))
    r=np.hstack([cv2.resize(Bv[i],(427,240)),cv2.resize(ov,(427,240)),z])
    cv2.putText(r,f'f{i}',(6,24),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,255),2); rows.append(r)
cv2.imwrite(out,np.vstack(rows))
