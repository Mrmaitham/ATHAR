from PIL import Image, ImageFilter, ImageDraw
import numpy as np, cv2, json, sys
def flood(bgl):
    cur=np.zeros_like(bgl); cur[0]=bgl[0]; cur[-1]=bgl[-1]; cur[:,0]=bgl[:,0]; cur[:,-1]=bgl[:,-1]
    while True:
        n=cur.copy(); n[1:]|=cur[:-1]; n[:-1]|=cur[1:]; n[:,1:]|=cur[:,:-1]; n[:,:-1]|=cur[:,1:]; n&=bgl
        if (n==cur).all(): return cur
        cur=n
def sprite(k):
    im=Image.open(f'/home/user/lw_ep3/new/turn/t_{k}.png').convert('RGB'); W,H=im.size
    sub=im.crop((int(W*0.34),0,int(W*0.66),H)); a=np.asarray(sub).astype(int)
    edge=np.concatenate([a[:,:10],a[:,-10:]],axis=1); rowbg=np.median(edge,axis=1)
    d=np.abs(a-rowbg[:,None,:]).sum(2); fg=~flood(d<12)
    fg[int(H*0.93):]&=(d[int(H*0.93):]>=30)   # drop ground shadow under feet
    n,lab,st,_=cv2.connectedComponentsWithStats(fg.astype(np.uint8),connectivity=8)
    big=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); fg=(lab==big)
    ys=np.where(fg.any(1))[0]; xs=np.where(fg.any(0))[0]
    box=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
    al=Image.fromarray((fg*255).astype('uint8')).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))
    r=sub.copy(); r.putalpha(al); return r.crop(box).transpose(Image.FLIP_LEFT_RIGHT)
SP={k:sprite(k) for k in ['zoozoo','noonoo','nadyah','hoor']}
# heights in px for Zoozoo=640 (Zoozoo 90, Noonoo 84, Nadyah 55, Hoor 49)
Z=500; HT={'zoozoo':Z,'noonoo':round(Z*84/90),'nadyah':round(Z*55/90),'hoor':round(Z*49/90)}
def build(plate,placements,out,ground=1100):
    bg=Image.open(plate).convert('RGB').resize((2688,1520)); c=bg.copy().convert('RGBA')
    for k,x in placements:
        s=SP[k]; h=HT[k]; s=s.resize((round(s.width*h/s.height),h),Image.LANCZOS)
        # contact shadow
        sh=Image.new('RGBA',c.size,(0,0,0,0)); d=ImageDraw.Draw(sh)
        w=s.width; d.ellipse((x-int(w*0.15),ground-int(h*0.02),x+int(w*0.85),ground+int(h*0.035)),fill=(20,50,20,120))
        sh=sh.filter(ImageFilter.GaussianBlur(10)); c=Image.alpha_composite(c,sh)
        lay=Image.new('RGBA',c.size,(0,0,0,0)); lay.paste(s,(x,ground-h),s); c=Image.alpha_composite(c,lay)
    c.convert('RGB').save(out)
    print(out,HT)

import numpy as np
from PIL import ImageDraw
def prep(src,out):
    im=Image.open(src).convert('RGB').resize((2688,1520)); a=np.asarray(im).copy()
    a[1085:1140]=a[1145:1200]            # erase old chalk line (clone grass)
    im=Image.fromarray(a); d=ImageDraw.Draw(im)
    d.line((0,1362,1500,1362),fill=(238,240,236),width=7)
    im=im.filter(ImageFilter.GaussianBlur(0.6)); im.save(out)
prep('lawn_a.png','plate_lawn.png')
GR=1362
build('plate_lawn.png',[('hoor',560),('nadyah',800),('noonoo',1040),('zoozoo',1290)],'S007_end_lawn.png',ground=GR)
build('plate_lawn.png',[('hoor',40),('nadyah',270),('noonoo',500),('zoozoo',1220)],'S007_start_lawn.png',ground=GR)
