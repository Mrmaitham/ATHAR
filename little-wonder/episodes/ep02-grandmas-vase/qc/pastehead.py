#!/usr/bin/env python3
# pastehead.py BASE EDIT OUT cx cy r — align EDIT (gpt) to BASE (ORB+affine on the area around the head), paste only a
# feathered disk of radius r around (cx,cy) from the aligned edit → everything else stays pixel-identical to BASE
import sys,cv2,numpy as np
base=cv2.imread(sys.argv[1]); ed=cv2.imread(sys.argv[2]); out=sys.argv[3]; cx,cy,r=map(int,sys.argv[4:7])
H,W=base.shape[:2]; ed=cv2.resize(ed,(W,H),interpolation=cv2.INTER_AREA)
g1,g2=[cv2.cvtColor(x,cv2.COLOR_BGR2GRAY) for x in (base,ed)]
m=np.zeros((H,W),np.uint8); cv2.circle(m,(cx,cy),int(r*2.2),255,-1); cv2.circle(m,(cx,cy),int(r*1.1),0,-1)   # ring around head (unchanged area)
orb=cv2.ORB_create(4000); k1,d1=orb.detectAndCompute(g1,m); k2,d2=orb.detectAndCompute(g2,m)
mt=sorted(cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True).match(d2,d1),key=lambda x:x.distance)[:400]
A,inl=cv2.estimateAffinePartial2D(np.float32([k2[x.queryIdx].pt for x in mt]),np.float32([k1[x.trainIdx].pt for x in mt]),method=cv2.RANSAC,ransacReprojThreshold=2)
al=cv2.warpAffine(ed,A,(W,H),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REFLECT)
mask=np.zeros((H,W),np.float32); cv2.circle(mask,(cx,cy),r,1,-1); mask=cv2.GaussianBlur(mask,(0,0),r*0.12)[...,None]
res=(al*mask+base*(1-mask)).astype(np.uint8); cv2.imwrite(out,res)
print('inliers',int(inl.sum()),'scale',round(float(np.hypot(A[0,0],A[1,0])),4),'shift',A[:,2].round(1))
