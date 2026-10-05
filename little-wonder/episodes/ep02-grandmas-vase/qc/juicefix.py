#!/usr/bin/env python3
# usage: juicefix.py IN OUT — paste the orange-juice glasses from shot 50's last frame (locked camera, same spot)
# over a pale-juice frame; skips grey fur / anything not warm so the cat's ear stays on top
import sys,numpy as np
from PIL import Image,ImageFilter
src=np.array(Image.open('qc/shot50_last.png').convert('RGB')).astype(float)
dst=np.array(Image.open(sys.argv[1]).convert('RGB')).astype(float)
m=np.zeros(dst.shape[:2]);x0,x1,y0,y1=1100,1250,388,452
box=dst[y0:y1,x0:x1];warm=((box[...,0]-box[...,2])>45)&(box[...,0]>140)
m[y0:y1,x0:x1]=warm
m=np.array(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))).astype(float)[...,None]/255
Image.fromarray((src*m+dst*(1-m)).clip(0,255).astype(np.uint8)).save(sys.argv[2])
