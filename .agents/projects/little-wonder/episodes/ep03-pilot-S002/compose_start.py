import sys; sys.path.insert(0,'.')
from comp4 import sprite
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
im=Image.open('USER_house.png').convert('RGB')   # 2336x1744 approved
W,H=im.size; sc=W/2000
d=ImageDraw.Draw(im)
# door opening (display coords -> original)
x0,x1,y0,y1=[round(v*sc) for v in (947,1050,775,970)]
print('door',x0,x1,y0,y1)
# hallway interior (dark, depth cues like S001 last frame)
w=x1-x0; h0=y1-y0
a=np.zeros((h0,w,3),np.uint8)
for j in range(h0):
    t=j/h0; a[j,:]=(70-20*t,58-16*t,48-12*t)       # back wall, darker toward bottom
fl=int(h0*0.80); a[fl:,:]=(128,110,92)                 # floor
bx0,bx1=int(w*0.28),int(w*0.72); a[int(h0*0.14):fl,bx0:bx1]=(26,19,15)   # inner dark doorway at the back
a[int(h0*0.14):int(h0*0.17),bx0:bx1]=(60,48,40)
hall=Image.fromarray(a).filter(ImageFilter.GaussianBlur(1.5)); im.paste(hall,(x0,y0))
# door leaf swung inward on the right + handle
d.polygon([(x1-16,y0+4),(x1-3,y0-2),(x1-3,y1),(x1-16,y1-10)],fill=(82,50,32)); d.rectangle((x1-13,y0+int(h0*0.45),x1-11,y0+int(h0*0.62)),fill=(190,190,190))
# Zoozoo sprite (side view facing right) standing on threshold
s=sprite('zoozoo','side').transpose(Image.FLIP_LEFT_RIGHT)
door_h=y1-y0; h=round(door_h*1.45/2.2)
s=s.resize((round(s.width*h/s.height),h),Image.LANCZOS)
cx=(x0+x1)//2-6; base=y1-4
im2=im.convert('RGBA'); lay=Image.new('RGBA',im.size,(0,0,0,0)); lay.paste(s,(cx-s.width//2,base-h),s)
im2=Image.alpha_composite(im2,lay).convert('RGB')
# 16:9 crop around door + steps
cw=1000; ch=round(cw*9/16); cx0=(x0+x1)//2-cw//2; cy0=y0-120
im2.crop((cx0,cy0,cx0+cw,cy0+ch)).resize((1920,1080),Image.LANCZOS).save('S002_start.png')
print('zoozoo h',h,'door h',door_h)
