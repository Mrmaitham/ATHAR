#!/usr/bin/env python3
# rmshards.py IN OUT — paint out the 2 stray vase shards on the floor in 39b (locked camera):
# shard mask from frame 0 (bright low-sat blobs > 1000px in floor box), closed + filled + dilated, minus shoes per frame;
# filled with a clean plate (inpaint of frame 0), feathered; rest of the frame untouched.
import sys,subprocess,numpy as np,cv2
IN,OUT=sys.argv[1:3]
b=subprocess.run(['ffmpeg','-v','error','-i',IN,'-f','rawvideo','-pix_fmt','bgr24','-'],capture_output=True).stdout
F=np.frombuffer(b,np.uint8).reshape(-1,720,1280,3).copy(); N=len(F)
h=cv2.cvtColor(F[0],cv2.COLOR_BGR2HSV)
m=((h[...,2]>150)&(h[...,1]<70)).astype(np.uint8); box=np.zeros_like(m); box[540:700,600:1000]=1; m*=box
n,lab,st,_=cv2.connectedComponentsWithStats(m); sh=np.zeros_like(m)
for k in range(1,n):
    if st[k,4]>1000:
        x,y,w,hh=st[k,:4]; sh[y-4:y+hh+6,x-6:x+w+6]|=((lab[y-4:y+hh+6,x-6:x+w+6]==k)).astype(np.uint8)
        # fill the shard body (darker shaded inside/edges) using its convex hull
        pts=np.column_stack(np.where(lab==k))[:,::-1]; hull=cv2.convexHull(pts); cv2.fillConvexPoly(sh,hull,1)
sh=cv2.dilate(sh,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
def shoes(f):
    hv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV); dark=(hv[...,2]<70).astype(np.uint8)
    dark[:560]=0; dark[:, :820]=0
    return cv2.dilate(dark,np.ones((9,9),np.uint8))
plate=cv2.inpaint(F[0],(sh*(1-shoes(F[0]))).astype(np.uint8)*255,9,cv2.INPAINT_TELEA)
enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s','1280x720','-r','24','-i','-','-i',IN,'-map','0:v','-map','1:a?','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-c:a','copy',OUT],stdin=subprocess.PIPE)
for i in range(N):
    f=F[i]; mk=(sh*(1-shoes(f))).astype(np.float32)
    mk=cv2.GaussianBlur(mk,(0,0),3)[...,None]
    enc.stdin.write(np.clip(f*(1-mk)+plate*mk,0,255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); print('frames',N,'mask px',int(sh.sum()))
