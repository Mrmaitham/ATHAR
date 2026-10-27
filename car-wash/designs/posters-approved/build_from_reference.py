import numpy as np
from PIL import Image, ImageDraw, ImageFont
SRC='/root/.claude/uploads/bd7e1a97-04b9-59d5-af43-4aac24edca24/346a8afd-image.jpg'
OUT='/tmp/claude-0/-home-user-ATHAR/bd7e1a97-04b9-59d5-af43-4aac24edca24/scratchpad/pk/ref/'
AR='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
EN='/usr/share/fonts/opentype/inter/Inter-Bold.otf'
MASCOT='/home/user/ATHAR/car-wash/brand/mascot/big-bubbles-mascot-transparent.png'
Y=(255,196,0); W=(255,255,255); NAVY=(11,31,75)

def fill_interp(a,x0,y0,x1,y1,lx0,lx1,rx0,rx1):
    for y in range(y0,y1+1):
        L=np.median(a[y,lx0:lx1],axis=0); R=np.median(a[y,rx0:rx1],axis=0)
        for x in range(x0,x1+1):
            t=(x-x0)/max(1,(x1-x0)); a[y,x]=L*(1-t)+R*t
    return a

def tw(txt,f):
    return f.getlength(txt,direction='rtl'), f.getbbox(txt,direction='rtl')
def draw_rtl(img,txt,right,cy,f,col):
    w,bb=tw(txt,f); h=bb[3]-bb[1]
    ImageDraw.Draw(img).text((right-w-bb[0],cy-h/2-bb[1]),txt,font=f,fill=col,direction='rtl')
def draw_ltr(img,txt,left,cy,f,col):
    d=ImageDraw.Draw(img); bb=d.textbbox((0,0),txt,font=f); h=bb[3]-bb[1]
    d.text((left-bb[0],cy-h/2-bb[1]),txt,font=f,fill=col)
def draw_center(img,txt,cx,cy,f,col):
    d=ImageDraw.Draw(img); bb=d.textbbox((0,0),txt,font=f); w=bb[2]-bb[0]; h=bb[3]-bb[1]
    d.text((cx-w/2-bb[0],cy-h/2-bb[1]),txt,font=f,fill=col)
def fit(path,txt,maxw,start):
    s=start
    while s>16:
        f=ImageFont.truetype(path,s)
        if tw(txt,f)[0]<=maxw: return f
        s-=1
    return ImageFont.truetype(path,s)

BASE=np.array(Image.open(SRC).convert('RGB')).astype(float)

def base_fixed():
    a=BASE.copy()
    return a

def fill_rows(a,x0,y0,x1,y1,rx0,rx1):
    for y in range(y0,y1+1):
        a[y,x0:x1+1]=np.median(a[y,rx0:rx1],axis=0)
    return a

def fill_vert(a,x0,y0,x1,y1):
    """smooth vertical fill: blend the clean rows above and below the box, per column"""
    top=a[y0-4].copy(); bot=a[y1+4].copy()
    for y in range(y0,y1+1):
        t=(y-y0)/max(1,(y1-y0))
        a[y,x0:x1+1]=(top*(1-t)+bot*t)[x0:x1+1]
    return a

def prices(a,lcy,rcy,left_txt,right_txt):
    # erase both price groups inside their boxes (keep the mascot bubble), then redraw "N K.d" centred
    a=fill_rows(a,214,1036,500,1132,470,490)
    a=fill_rows(a,725,1036,1105,1132,716,724)
    img=Image.fromarray(a.clip(0,255).astype('uint8'))
    big=ImageFont.truetype(AR,104); small=ImageFont.truetype(AR,58)
    for txt,cx in [(left_txt,372),(right_txt,938)]:
        num,unit=txt.split(' ',1)
        wn,bbn=tw(num,big); wu,bbu=tw(unit,small); gap=18
        total=wn+gap+wu; x=cx-total/2+12
        d=ImageDraw.Draw(img)
        hn=bbn[3]-bbn[1]
        d.text((x-bbn[0],1083-hn/2-bbn[1]),num,font=big,fill=W,direction='rtl')
        hu=bbu[3]-bbu[1]
        d.text((x+wn+gap-bbu[0],1083-hu/2-bbu[1]),unit,font=small,fill=Y,direction='rtl')
    return img

def shrink_logo(a,scale=0.45,top=20):
    from PIL import ImageFilter
    orig=Image.open(SRC).convert('RGB')
    X0,Y0,X1,Y1=22,4,468,300
    for y in range(Y0,Y1+1):
        a[y,X0:X1+1]=np.median(a[y,4:14],axis=0)
    c=np.array(orig.crop((X0,Y0,X1+1,Y1+1))).astype(float)
    bg=np.median(c[:, :8],axis=1)[:,None,:]
    dist=np.sqrt(((c-bg)**2).sum(axis=2))
    m=Image.fromarray(((dist>55)*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
    rgba=Image.fromarray(c.clip(0,255).astype('uint8')).convert('RGBA'); rgba.putalpha(m)
    rgba=rgba.resize((int(rgba.width*scale),int(rgba.height*scale)),Image.LANCZOS)
    base=Image.fromarray(a.clip(0,255).astype('uint8')).convert('RGBA')
    base.alpha_composite(rgba,(int(245-rgba.width/2),top))
    return np.array(base.convert('RGB')).astype(float)

def package(name_ar,name_en,items_ar,items_en,left,right,fix_list=True,ar_size=21):
    items_ar=[(t,True) if isinstance(t,str) else t for t in items_ar]
    a=base_fixed()
    a=shrink_logo(a)
    a=fill_rows(a,26,302,440,446,8,16)
    img=prices(a,0,0,left,right)
    a=np.array(img).astype(float)
    if fix_list:
        a=fill_rows(a,32,470,470,628,456,462)
        a=fill_rows(a,32,652,470,822,40,46)
    img=Image.fromarray(a.clip(0,255).astype('uint8'))
    d=ImageDraw.Draw(img)
    ft=fit(AR,name_ar,400,84)
    draw_center(img,name_ar,245,205,ft,W)
    fe=fit(EN,name_en,400,44)
    draw_center(img,name_en,245,268,fe,W)
    sizes=[]
    for t,_ in items_ar:
        s_=ar_size
        while s_>15 and tw(t,ImageFont.truetype(AR,s_))[0]>372: s_-=1
        sizes.append(s_)
    fa=ImageFont.truetype(AR,min(sizes))
    stepa=min(37,(636-494)/max(1,len(items_ar)-1))
    for i,(t,bul) in enumerate(items_ar):
        cy=494+i*stepa
        draw_rtl(img,t,430,cy,fa,W)
        if bul: ImageDraw.Draw(img).ellipse((440,cy-5,450,cy+5),fill=Y)
    fen=fit(EN,max(items_en,key=len),380,26)
    stepe=min(36,(806-676)/max(1,len(items_en)-1))
    for i,t in enumerate(items_en):
        cy=676+i*stepe
        draw_ltr(img,'•',52,cy,ImageFont.truetype(EN,26),Y)
        draw_ltr(img,t,76,cy,fen,W)
    return img

if __name__=='__main__':
    pk={}
    pk['3-super']=package('سوبر ببلز','Super bubbles',
        ['غسيل خارجي مع طبقة واكس','غسيل داخلي مع تلميع كامل من الداخل','تلميع الاطارات والرنقات والابواب والارضيات','تلميع جميع ربلات السيارة'],
        ['Exterior wash','Internal cleaning with wax','Tyres & rings shine, Doors & pads','All car Bubbles shine.'],'15 K.d','20 K.d')
    pk['1-dbl']=package('دبل ببلز','Double bubbles',
        ['غسيل خارجي مع طبقة واكس','تنظيف داخلي','تلميع التابلوه','تلميع الإطارات والرنقات'],
        ['Exterior wash','Internal cleaning with wax','Dashboard polish','Tyres & rings shine'],'9 K.d','10 K.d')
    pk['2-ble']=package('ببلز','Bubbles',
        ['غسيل خارجي','تنظيف داخلي'],['Exterior wash','Internal cleaning'],'6 K.d','7 K.d')
    pk['4-super-top']=package('سوبر توب ببلز','Super Top Bubbles',
        [('غسيل خارجي مع طبقة واكس',True),('غسيل داخلي مع تلميع كامل من الداخل',True),('غسيل الكشنات والأرضيات',True),('تنظيف الماكينة بالهواء',False),('تلميع الإطارات والرنجات والأبواب',True),('تلميع ربلات السيارة',True),('تنظيف فتحات التكييف',False)],
        ['Exterior wash','Internal cleaning with wax','Tyres & rings shine, Doors & pads','Bubbles shine.','Ac cleaning'],'20 K.d','25 K.d')
    for k,img in pk.items():
        img.convert('RGB').save(OUT+k+'.jpg',quality=95); print('saved',k)
