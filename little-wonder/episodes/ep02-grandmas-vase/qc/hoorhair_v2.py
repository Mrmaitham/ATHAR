#!/usr/bin/env python3
# usage: hoorhair_v2.py IN OUT "t:x:y,..." [B] [R]   (same keypoints as hoorhair_track.py; x=-1 → Hoor hidden)
# v2 = flicker-free: (1) per frame, mediapipe multiclass → hair region (dilated hair minus face-skin) around Hoor's head
# (2) region averaged over ±3 frames, warped with optical flow so it follows her and never jumps
# (3) darkening strength = region × per-pixel "brown hair" likeness (deterministic → stable), white rim-light & cream bows kept
import sys,os,subprocess,numpy as np,cv2,mediapipe as mp
from mediapipe.tasks.python import vision,BaseOptions
IN,OUT,KP=sys.argv[1],sys.argv[2],sys.argv[3]
B=int(sys.argv[4]) if len(sys.argv)>4 else 320; R=int(sys.argv[5]) if len(sys.argv)>5 else 0
kp=sorted([tuple(map(float,k.split(':'))) for k in KP.split(',')]); ON=[k for k in kp if k[1]>=0]
MD=os.path.join(os.path.dirname(os.path.abspath(__file__)),'models')
hseg=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=MD+'/hair.tflite'),output_confidence_masks=True))
seg=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=MD+'/selfie_multiclass.tflite'),output_confidence_masks=True))
info=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate','-of','csv=p=0',IN],capture_output=True,text=True).stdout.strip().split(',')
W,H,fps=int(info[0]),int(info[1]),info[2]
raw=subprocess.run(['ffmpeg','-v','error','-i',IN,'-f','rawvideo','-pix_fmt','bgr24','-'],capture_output=True).stdout
F=np.frombuffer(raw,np.uint8).reshape(-1,H,W,3); N=len(F)
def skipped(t): p=[k for k in kp if k[0]<=t]; return bool(p) and p[-1][1]<0
def interp(t): ts=[k[0] for k in ON]; return np.interp(t,ts,[k[1] for k in ON]),np.interp(t,ts,[k[2] for k in ON])
reg=np.zeros((N,H,W),np.float32); skip=np.zeros(N,bool); prev=None
for i in range(N):
    t=i/max(N-1,1)
    if skipped(t): skip[i]=True; prev=None; continue
    px,py=interp(t)
    if prev is not None and np.hypot(prev[0]-px,prev[1]-py)<(R*0.6 if R else B*0.45): px,py=prev
    x0=int(np.clip(px-B/2,0,W-B)); y0=int(np.clip(py-B/2,0,H-B)); c=F[i,y0:y0+B,x0:x0+B]
    r=seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=cv2.cvtColor(cv2.resize(c,(512,512)),cv2.COLOR_BGR2RGB)))
    cm=[cv2.resize(np.squeeze(r.confidence_masks[k].numpy_view()).astype(np.float32),(B,B)) for k in range(6)]
    hair=(cm[1]>(0.12 if R else 0.3)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(hair); keep=np.zeros_like(hair)
    for k in range(1,n):   # Hoor's hair pieces only: near her head centre
        d=np.hypot(cen[k][0]+x0-px,cen[k][1]+y0-py)
        if st[k,cv2.CC_STAT_AREA]>=30 and d<(R if R else B*0.3): keep[lab==k]=1
    if keep.sum()==0: continue
    ys,xs=np.where(keep); prev=(xs.mean()+x0,ys.mean()+y0)
    # wispy rim-lit curls: model calls them "person" but not "hair" → take person pixels near the hair that aren't skin/clothes
    near=cv2.dilate(keep,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,((21,21) if R else (41,41))))
    person=np.clip((0.7-cm[0])/0.4,0,1)
    notbody=np.clip((0.6-np.maximum.reduce([cm[2],cm[3],cm[4]]))/0.3,0,1)
    rh=hseg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=cv2.cvtColor(cv2.resize(c,(512,512)),cv2.COLOR_BGR2RGB)))
    hm=cv2.resize(np.squeeze(rh.confidence_masks[-1].numpy_view()).astype(np.float32),(B,B))   # soft matte incl. wispy curls
    g=np.maximum(keep.astype(np.float32),near*np.maximum(person*notbody*0.0,np.clip((hm-0.15)/0.5,0,1)))
    face=cv2.dilate((cm[3]>0.5).astype(np.uint8),np.ones((3,3),np.uint8)).astype(np.float32)
    g*=1-face
    if R: yy,xx=np.mgrid[0:B,0:B]; g*=np.clip((R-np.hypot(xx+x0-px,yy+y0-py))/12,0,1)
    reg[i,y0:y0+B,x0:x0+B]=g
# temporal smoothing with optical-flow warping (ROI = union of regions)
ys,xs=np.where(reg.max(0)>0)
if len(xs)==0: subprocess.run(['cp',IN,OUT]); print('frames',N,'nothing'); sys.exit()
X0,X1=max(xs.min()-40,0),min(xs.max()+40,W); Y0,Y1=max(ys.min()-40,0),min(ys.max()+40,H)
G=[cv2.cvtColor(F[i,Y0:Y1,X0:X1],cv2.COLOR_BGR2GRAY) for i in range(N)]
h,w=Y1-Y0,X1-X0; gx,gy=np.meshgrid(np.arange(w,dtype=np.float32),np.arange(h,dtype=np.float32))
sm=np.zeros((N,h,w),np.float32)
for i in range(N):
    if skip[i]: continue
    acc=np.zeros((h,w),np.float32); ws=0
    for k in range(-3,4):
        j=i+k
        if j<0 or j>=N or skip[j]: continue
        wk=np.exp(-(k*k)/4.5); src=reg[j,Y0:Y1,X0:X1]
        if k:
            fl=cv2.calcOpticalFlowFarneback(G[i],G[j],None,0.5,3,21,3,5,1.1,0)
            src=cv2.remap(src,gx+fl[...,0],gy+fl[...,1],cv2.INTER_LINEAR)
        acc+=wk*src; ws+=wk
    cur=cv2.GaussianBlur(cv2.dilate(reg[i,Y0:Y1,X0:X1],np.ones((7,7),np.uint8)),(0,0),1.5)   # never reach past this frame's own hair
    sm[i]=np.minimum(cv2.GaussianBlur(acc/ws,(0,0),1.2),cur)
enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',fps,'-i','-','-i',IN,'-map','0:v','-map','1:a?','-c:v','libx264','-profile:v','high','-crf','16','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
for i in range(N):
    f=F[i].copy()
    if not skip[i]:
        c=f[Y0:Y1,X0:X1]; hsv=cv2.cvtColor(c,cv2.COLOR_BGR2HSV).astype(np.float32); Hh,Ss,Vv=hsv[...,0],hsv[...,1],hsv[...,2]
        like=np.clip((Ss-35)/25,0,1)*((Hh<=32)|(Hh>=165))          # brown/caramel
        like*=1-np.clip((Vv-215)/20,0,1)*np.clip((75-Ss)/25,0,1)      # keep only the thin white outline
        like*=1-np.clip((Vv-150)/40,0,1)*np.clip((80-Ss)/30,0,1)      # keep cream bows
        if R: like*=np.clip((Vv-60)/25,0,1)                            # leave already-black hair (other girls)
        like=cv2.GaussianBlur(like,(0,0),0.8)
        a=np.clip(sm[i]*1.4,0,1)*like; a=a[...,None]
        lab=cv2.cvtColor(c,cv2.COLOR_BGR2LAB).astype(np.float32); l2=lab.copy()
        l2[...,0]=255*np.power(lab[...,0]/255,2.4)*0.55   # bright rim-lit curls → black too (keeps a soft sheen)
        l2[...,1]=128+(lab[...,1]-128)*0.08; l2[...,2]=128+(lab[...,2]-128)*0.08
        d=cv2.cvtColor(np.clip(l2,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR).astype(np.float32)
        f[Y0:Y1,X0:X1]=np.clip(c*(1-a)+np.minimum(d,c)*a,0,255).astype(np.uint8)
    enc.stdin.write(f.tobytes())
enc.stdin.close(); enc.wait(); print('frames',N,'skipped',int(skip.sum()))
