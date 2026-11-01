from PIL import Image, ImageFilter, ImageDraw
import numpy as np, cv2, sys
def flood(bgl):
    cur=np.zeros_like(bgl); cur[0]=bgl[0]; cur[-1]=bgl[-1]; cur[:,0]=bgl[:,0]; cur[:,-1]=bgl[:,-1]
    while True:
        n=cur.copy(); n[1:]|=cur[:-1]; n[:-1]|=cur[1:]; n[:,1:]|=cur[:,:-1]; n[:,:-1]|=cur[:,1:]; n&=bgl
        if (n==cur).all(): return cur
        cur=n
def sprite(k,view):  # view: 'back' (right third) / 'side' (middle)
    im=Image.open(f'/home/user/lw_ep3/new/turn/t_{k}.png').convert('RGB'); W,H=im.size
    a0,a1={'back':(0.66,1.0),'side':(0.34,0.66),'front':(0.0,0.34)}[view]
    sub=im.crop((int(W*a0),0,int(W*a1),H)); a=np.asarray(sub).astype(int)
    edge=np.concatenate([a[:,:10],a[:,-10:]],axis=1); rowbg=np.median(edge,axis=1)
    d=np.abs(a-rowbg[:,None,:]).sum(2); fg=~flood(d<12)
    fg[int(H*0.93):]&=(d[int(H*0.93):]>=30)
    n,lab,st,_=cv2.connectedComponentsWithStats(fg.astype(np.uint8),connectivity=8)
    big=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); fg=(lab==big)
    ys=np.where(fg.any(1))[0]; xs=np.where(fg.any(0))[0]
    box=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
    al=Image.fromarray((fg*255).astype('uint8')).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))
    r=sub.copy(); r.putalpha(al); return r.crop(box)
K=0.31; YH=641; M={'zoozoo':1.45,'noonoo':1.45*84/90,'nadyah':1.45*55/90,'hoor':1.45*49/90}
def place(c,k,view,x,y,flip=False):
    s=sprite(k,view); 
    if flip: s=s.transpose(Image.FLIP_LEFT_RIGHT)
    h=round(M[k]*K*(y-YH)); s=s.resize((round(s.width*h/s.height),h),Image.LANCZOS)
    sh=Image.new('RGBA',c.size,(0,0,0,0)); d=ImageDraw.Draw(sh); w=s.width
    d.ellipse((x-int(w*0.65),y-int(h*0.02),x+int(w*0.65),y+int(h*0.04)),fill=(20,45,20,110)); sh=sh.filter(ImageFilter.GaussianBlur(6))
    c=Image.alpha_composite(c,sh); lay=Image.new('RGBA',c.size,(0,0,0,0)); lay.paste(s,(x-s.width//2,y-h),s)
    print(k,view,'h',h,'y',y); return Image.alpha_composite(c,lay)
def run(out,items,ribbon=True):
    base=Image.open('USER_house.png').convert('RGB').resize((2000,1493),Image.LANCZOS)
    d=ImageDraw.Draw(base)
    d.line((690,1330,1290,1330),fill=(240,242,238),width=5)
    if ribbon:
        d.line((865,1018,1128,1018),fill=(200,30,40),width=5); d.ellipse((855,1008,877,1030),fill=(200,30,40)); d.ellipse((1116,1008,1138,1030),fill=(200,30,40))   # chalk start line across the path
    c=base.convert('RGBA')
    for it in items: c=place(c,*it)
    c.convert('RGB').crop((0,368,2000,1493)).resize((2688,1512),Image.LANCZOS).save(out)
if __name__=='__main__':
    Y=1330
    run('S007_start_house.png',[('hoor','back',815,Y),('nadyah','back',925,Y),('noonoo','back',1050,Y),('zoozoo','back',1185,Y)])
