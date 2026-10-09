#!/usr/bin/env python3
# abayafix.py IN OUT [x0 y0 x1 y1] — pull Grandma's drifted brown abaya/hijab back to black (reference) inside her box.
# skin is protected: only dark, low-chroma brown pixels are touched, and the face ellipse is skipped.
import sys,numpy as np
from PIL import Image,ImageFilter
im=np.array(Image.open(sys.argv[1]).convert('RGB')).astype(float)
x0,y0,x1,y1=[int(v) for v in sys.argv[3:7]] if len(sys.argv)>6 else (860,120,1115,700)
H,W,_=im.shape;m=np.zeros((H,W))
b=im[y0:y1,x0:x1];L=b.mean(2);mx=b.max(2);mn=b.min(2);sat=(mx-mn)/np.maximum(mx,1)
brown=(b[...,0]>=b[...,1])&(b[...,1]>=b[...,2]-4)
cloth=brown&(L<125)&(sat<0.62)
m[y0:y1,x0:x1]=cloth
# protect face: find the brightest skin blob in the top third of the box
top=im[y0:y0+(y1-y0)//3,x0:x1];sk=(top[...,0]>150)&(top[...,0]-top[...,2]>40)
if sk.sum()>50:
    ys,xs=np.nonzero(sk);cy,cx=ys.mean()+y0,xs.mean()+x0;ry,rx=ys.std()*2.6+8,xs.std()*2.6+8
    Y,X=np.ogrid[:H,:W];m[((Y-cy)/ry)**2+((X-cx)/rx)**2<1]=0
m=np.array(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(float)[...,None]/255
L3=im.mean(2,keepdims=True)
black=np.concatenate([L3*0.42+3,L3*0.40+2,L3*0.40+2],2)   # near-neutral, keeps fold shading
Image.fromarray((black*m+im*(1-m)).clip(0,255).astype(np.uint8)).save(sys.argv[2])
