#!/usr/bin/env python3
# usage: hoorhair_track.py IN OUT "t:x:y,t:x:y,..." [box]
# Hoor's hair → jet-black without regeneration. Keypoints = Hoor head centre (full-res px) at time fractions t;
# each frame: mediapipe multiclass hair mask in a box around the predicted head, keep the brown-hair component
# nearest the prediction (so Noonoo/Nadyah/Mishoo are left alone), recolor it (L curve, low chroma), bows protected.
import sys,subprocess,numpy as np,cv2,os,json,mediapipe as mp
from mediapipe.tasks.python import vision,BaseOptions
IN,OUT,KP=sys.argv[1],sys.argv[2],sys.argv[3]; B=int(sys.argv[4]) if len(sys.argv)>4 else 320
R=int(sys.argv[5]) if len(sys.argv)>5 else 0   # strict mode: only a disk of radius R around Hoor's head, no drifting, skip already-dark hair
kp=sorted([tuple(map(float,k.split(':'))) for k in KP.split(',')])
MD=os.path.join(os.path.dirname(os.path.abspath(__file__)),'models')
seg=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=MD+'/selfie_multiclass.tflite'),output_confidence_masks=True))
info=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-count_packets','-show_entries','stream=width,height,r_frame_rate,nb_read_packets','-of','csv=p=0',IN],capture_output=True,text=True).stdout.strip().split(',')
W,H,fps,N=int(info[0]),int(info[1]),info[2],int(info[3])
SKIP=[k[0] for k in kp if k[1]<0]; ON=[k for k in kp if k[1]>=0]
def skipped(t):   # keypoint with x<0 = Hoor hidden from that time until the next normal keypoint
    prevk=[k for k in kp if k[0]<=t]; return bool(prevk) and prevk[-1][1]<0
def interp(t):
    kp=ON; ts=[k[0] for k in kp]
    return (np.interp(t,ts,[k[1] for k in kp]),np.interp(t,ts,[k[2] for k in kp]))
dec=subprocess.Popen(['ffmpeg','-v','error','-i',IN,'-f','rawvideo','-pix_fmt','bgr24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',fps,'-i','-','-i',IN,'-map','0:v','-map','1:a?','-c:v','libx264','-profile:v','high','-crf','16','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
prev=None; pm=None; i=0; found=0; log=[]
while True:
    b=dec.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    f=np.frombuffer(b,np.uint8).reshape(H,W,3).copy()
    if skipped(i/max(N-1,1)):
        prev=None; pm=None; log.append((i,-1,-1,0)); enc.stdin.write(f.tobytes()); i+=1; continue
    px,py=interp(i/max(N-1,1))
    if not R and prev is not None and np.hypot(prev[0]-px,prev[1]-py)<B*0.45: px,py=prev
    if R and prev is not None and np.hypot(prev[0]-px,prev[1]-py)<R*0.6: px,py=prev   # follow her, but never drift far from the plan
    x0=int(np.clip(px-B/2,0,W-B)); y0=int(np.clip(py-B/2,0,H-B)); x1,y1=x0+B,y0+B
    c=f[y0:y1,x0:x1]
    r=seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=cv2.cvtColor(cv2.resize(c,(512,512)),cv2.COLOR_BGR2RGB)))
    m=cv2.resize(np.squeeze(r.confidence_masks[1].numpy_view()).astype(np.float32),(B,B))
    hsv=cv2.cvtColor(c,cv2.COLOR_BGR2HSV).astype(np.float32)
    vmin=100 if R else 75
    DA=bool(R and os.environ.get('DISKALL'))
    mt=0.12 if DA else 0.5
    cand=((m>mt)&(hsv[...,1]>=70)&(hsv[...,2]>=vmin)&((hsv[...,0]<=28)|(hsv[...,0]>=170))).astype(np.uint8)
    cand=cv2.morphologyEx(cand,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(cand)
    best=None;bs=0
    for k in range(1,n):
        a=st[k,cv2.CC_STAT_AREA]
        if a<120: continue
        d=np.hypot(cen[k][0]+x0-px,cen[k][1]+y0-py); s=a/(1+d/50)
        if R and d>R: continue
        if s>bs: bs,best=s,k
    if best is not None:
        found+=1
        comp=(lab==best).astype(np.uint8)
        # also take nearby components (buns split from the head by the bows)
        near=cv2.dilate(comp,np.ones((25,25),np.uint8))
        for k in range(1,n):
            if k!=best and st[k,cv2.CC_STAT_AREA]>=40 and (near[lab==k]).any() and (not R or np.hypot(cen[k][0]+x0-px,cen[k][1]+y0-py)<R): comp|=(lab==k).astype(np.uint8)
        ys,xs=np.where(comp); prev=(xs.mean()+x0,ys.mean()+y0)
        if R and os.environ.get('DISKALL'):   # take every hair pixel inside the head disk (buns split off by bows/rim light)
            yy,xx=np.mgrid[0:B,0:B]; comp=(cand*(np.hypot(xx+x0-px,yy+y0-py)<R)).astype(np.uint8); prev=(px,py)
        reg=cv2.dilate(comp,np.ones((9,9),np.uint8)).astype(np.float32)
        bow=np.clip((hsv[...,2]-150)/40,0,1)*np.clip((80-hsv[...,1])/30,0,1)
        a=(np.clip((m-0.08)/0.22,0,1) if DA else np.clip((m-0.3)/0.4,0,1))*reg*(1-bow)
        if R:
            yy,xx=np.mgrid[0:B,0:B]; dd=np.hypot(xx+x0-prev[0],yy+y0-prev[1])
            a*=np.clip((R-dd)/12,0,1)
            a*=np.clip((hsv[...,2]-70)/25,0,1)   # leave already-dark (black) hair alone
        a=cv2.GaussianBlur(a,(0,0),1.5)
        full=np.zeros((H,W),np.float32); full[y0:y1,x0:x1]=a
        if pm is not None: full=np.maximum(full*0.7+pm*0.3, full*0.85)
        pm=full
        A=full[y0:y1,x0:x1][...,None]
        labc=cv2.cvtColor(c,cv2.COLOR_BGR2LAB).astype(np.float32); l2=labc.copy()
        l2[...,0]=255*np.power(labc[...,0]/255,1.8)*0.72
        l2[...,1]=128+(labc[...,1]-128)*0.22; l2[...,2]=128+(labc[...,2]-128)*0.22
        d=cv2.cvtColor(np.clip(l2,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR).astype(np.float32)
        f[y0:y1,x0:x1]=np.clip(c*(1-A)+d*A,0,255).astype(np.uint8)
        log.append((i,int(prev[0]),int(prev[1]),int(comp.sum())))
    else:
        prev=None; pm=None; log.append((i,-1,-1,0))
    enc.stdin.write(f.tobytes()); i+=1
enc.stdin.close(); enc.wait()
json.dump(log,open(OUT+'.track.json','w'))
print('frames',i,'found',found)
