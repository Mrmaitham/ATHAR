import numpy as np
from PIL import Image, ImageDraw, ImageFont
AR9='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
EN='/usr/share/fonts/opentype/inter/Inter-Bold.otf'
NAVY=(11,31,75); GOLD=(255,196,0); W=(255,255,255); N=1254
logo=Image.open('/home/user/ATHAR/car-wash/brand/logo/big-bubbles-logo-4096-transparent.png').convert('RGBA')
mas=Image.open('/home/user/ATHAR/car-wash/brand/mascot/big-bubbles-mascot-transparent.png').convert('RGBA')
wa=Image.open('icon_wa_gold.png').resize((50,50),Image.LANCZOS)
ig=Image.open('icon_ig_gold.png').resize((50,50),Image.LANCZOS)
AR_ITEMS=['غسيل خارجي مع طبقة واكس','تنظيف داخلي','تلميع التابلوه','تلميع الإطارات والرنقات','تلبيس الدواسات']
def recolor(ic,rgb):
    a=np.array(ic.convert('RGBA')); a[...,0],a[...,1],a[...,2]=rgb; return Image.fromarray(a,'RGBA')
def icon(p,rgb):
    ic=Image.open(p).convert('RGBA'); return recolor(ic.crop((0,12,ic.width,ic.height)),rgb)
def rtl(d,t,right,cy,f,col):
    bb=f.getbbox(t,direction='rtl'); w=f.getlength(t,direction='rtl')
    d.text((right-w-bb[0],cy-(bb[3]+bb[1])/2),t,font=f,fill=col,direction='rtl')
def ctr(d,t,cx,cy,f,col,rtl_=False,stroke=0,sc=None):
    if rtl_:
        w=f.getlength(t,direction='rtl'); bb=f.getbbox(t,direction='rtl')
        d.text((cx-w/2-bb[0],cy-(bb[3]+bb[1])/2),t,font=f,fill=col,direction='rtl',stroke_width=stroke,stroke_fill=sc)
    else:
        bb=f.getbbox(t); w=bb[2]-bb[0]
        d.text((cx-w/2-bb[0],cy-(bb[3]+bb[1])/2),t,font=f,fill=col,stroke_width=stroke,stroke_fill=sc)
def bubbles(img,n,seed,col):
    rng=np.random.default_rng(seed); L=Image.new('RGBA',img.size,(0,0,0,0)); d=ImageDraw.Draw(L)
    for _ in range(n):
        x,y=rng.integers(0,N),rng.integers(0,N); r=int(rng.integers(8,44))
        d.ellipse((x-r,y-r,x+r,y+r),outline=col+(110,),width=3)
    img.alpha_composite(L)
yy=np.arange(N)[:,None]/N
dark=np.array([3,12,40])*(1-yy)+np.array([12,50,130])*yy
D=Image.fromarray(np.broadcast_to(dark[:,None,:],(N,N,3)).clip(0,255).astype('uint8')).convert('RGBA')
bubbles(D,60,1,(150,210,255))
D.alpha_composite(logo.resize((230,int(230*logo.height/logo.width)),Image.LANCZOS),(N//2-115,25))
d=ImageDraw.Draw(D)
ctr(d,'دبل ببلز',N//2,405,ImageFont.truetype(AR9,96),GOLD,True,stroke=4,sc=NAVY)
ctr(d,'DOUBLE BUBBLES',N//2,478,ImageFont.truetype(EN,30),W)
D.alpha_composite(mas.resize((int(560*mas.width/mas.height),560),Image.LANCZOS),(0,470))
X0,X1,Y0,Y1=530,N-45,535,915
d=ImageDraw.Draw(D); d.rounded_rectangle((X0,Y0,X1,Y1),radius=26,fill=(6,22,70,240),outline=GOLD,width=3)
fa=ImageFont.truetype(AR9,40)
for i,a in enumerate(AR_ITEMS):
    y=Y0+56+i*66
    rtl(d,a,X1-34,y,fa,W); d.ellipse((X1-24,y-6,X1-12,y+6),fill=GOLD)
# price boxes: left = label on top + car icon below; right = gold price
BY0,BY1=1035,1165
for x0,x1,p,lab,pr in [(60,N//2-10,'icon_saloon.png','صالون','9'),(N//2+10,N-60,'icon_jeep.png','جيب','10')]:
    d=ImageDraw.Draw(D); d.rounded_rectangle((x0,BY0,x1,BY1),radius=26,fill=W)
    cx=x0+135
    d=ImageDraw.Draw(D)
    ctr(d,lab,cx,BY0+34,ImageFont.truetype(AR9,34),NAVY,True)
    ic=icon(p,NAVY); w=170; h=int(w*ic.height/ic.width)
    D.alpha_composite(ic.resize((w,h),Image.LANCZOS),(cx-w//2,BY0+68-h//2+8))
    d=ImageDraw.Draw(D)
    fpz=ImageFont.truetype(EN,58); t=pr+' K.D'
    bb=fpz.getbbox(t); tw=bb[2]-bb[0]
    d.text((x1-30-tw-bb[0],(BY0+BY1)//2-(bb[1]+bb[3])/2),t,font=fpz,fill=GOLD,stroke_width=3,stroke_fill=NAVY)
d=ImageDraw.Draw(D)
fp=ImageFont.truetype(EN,40); ph='98894114'; hd='@big_bubbless'
wp=fp.getlength(ph); wh=fp.getlength(hd)
total=50+14+wp+60+2+60+50+14+wh
x=(N-total)/2; cy=1212
D.alpha_composite(wa,(int(x),cy-25)); x+=64
d.text((x,cy-(fp.getbbox(ph)[1]+fp.getbbox(ph)[3])/2),ph,font=fp,fill=GOLD); x+=wp+60
d.line((x,cy-28,x,cy+28),fill=GOLD,width=2); x+=62
D.alpha_composite(ig,(int(x),cy-25)); x+=64
d.text((x,cy-(fp.getbbox(hd)[1]+fp.getbbox(hd)[3])/2),hd,font=fp,fill=GOLD)
D.convert('RGB').save('final-double2.jpg',quality=95)
print('ok')
