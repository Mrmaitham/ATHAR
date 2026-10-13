#!/usr/bin/env python3
# usage: housealign.py TARGET.png MASTER.png OUT_WARPED.png  -> scale+shift MASTER onto TARGET's house (upper-middle band)
import sys, numpy as np
from PIL import Image
T=Image.open(sys.argv[1]).convert('RGB'); M=Image.open(sys.argv[2]).convert('RGB')
W,H=T.size; f=8; w8,h8=W//f,H//f
t8=np.asarray(T.resize((w8,h8)),np.float32).mean(2); m8=M.resize((w8,h8))
ys,ye,xs,xe=1,int(0.42*h8),int(0.40*w8),int(0.80*w8)
def warp(img,sc,tx,ty,w,h): return img.transform((w,h),Image.AFFINE,(1/sc,0,-tx/sc,0,1/sc,-ty/sc),Image.BILINEAR)
best=None
for sc in np.arange(1.0,2.41,0.04):
    for tx in np.arange(-200,51,4):
        for ty in np.arange(-110,26,4):
            e=np.abs(np.asarray(warp(m8,sc,tx,ty,w8,h8),np.float32).mean(2)[ys:ye,xs:xe]-t8[ys:ye,xs:xe]).mean()
            if best is None or e<best[0]: best=(e,sc,tx,ty)
print('coarse',best)
e,sc,tx,ty=best; tx*=f; ty*=f
tf=np.asarray(T.resize((W//2,H//2)),np.float32).mean(2); best=(1e9,)
for s2 in np.arange(sc-0.03,sc+0.031,0.01):
    for x2 in range(int(tx)-24,int(tx)+25,6):
        for y2 in range(int(ty)-24,int(ty)+25,6):
            w=np.asarray(warp(M,s2,x2,y2,W,H).resize((W//2,H//2)),np.float32).mean(2)
            e=np.abs(w[ys*f//2:ye*f//2,xs*f//2:xe*f//2]-tf[ys*f//2:ye*f//2,xs*f//2:xe*f//2]).mean()
            if e<best[0]: best=(e,s2,x2,y2)
print('fine',best)
e,s2,x2,y2=best; warp(M,s2,x2,y2,W,H).save(sys.argv[3])
