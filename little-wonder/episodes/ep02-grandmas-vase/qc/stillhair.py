#!/usr/bin/env python3
# stillhair.py IN OUT cx cy [box] — clean jet-black hair on ONE still (start/end frame for regeneration):
# hair matte (hair.tflite ∪ multiclass hair) around Hoor's head, rim-light halo included (neutral dark, soft sheen), cream bows kept
import sys,os,numpy as np,cv2,mediapipe as mp
from mediapipe.tasks.python import vision,BaseOptions
IN,OUT=sys.argv[1],sys.argv[2]; cx,cy=int(sys.argv[3]),int(sys.argv[4]); B=int(sys.argv[5]) if len(sys.argv)>5 else 300
MD=os.path.join(os.path.dirname(os.path.abspath(__file__)),'models')
mk=lambda p:vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=MD+p),output_confidence_masks=True))
hs,ms=mk('/hair.tflite'),mk('/selfie_multiclass.tflite')
im=cv2.imread(IN); H,W=im.shape[:2]
x0=int(np.clip(cx-B/2,0,W-B)); y0=int(np.clip(cy-B/2,0,H-B)); c=im[y0:y0+B,x0:x0+B].copy()
mi=mp.Image(image_format=mp.ImageFormat.SRGB,data=cv2.cvtColor(cv2.resize(c,(512,512)),cv2.COLOR_BGR2RGB))
h1=cv2.resize(np.squeeze(hs.segment(mi).confidence_masks[-1].numpy_view()),(B,B))
r=ms.segment(mi); cm=[cv2.resize(np.squeeze(r.confidence_masks[k].numpy_view()),(B,B)) for k in range(6)]
hair=np.maximum(h1,cm[1])
core=(hair>0.35).astype(np.uint8)
n,lab,st,cen=cv2.connectedComponentsWithStats(core); keep=np.zeros_like(core)
for k in range(1,n):
    if st[k,4]>=40 and np.hypot(cen[k][0]+x0-cx,cen[k][1]+y0-cy)<B*0.45: keep[lab==k]=1
# include the rim/halo ring just outside the hair, but never skin/clothes
ring=cv2.dilate(keep,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
body=np.maximum.reduce([cm[2],cm[3],cm[4]])>0.5
hsv0=cv2.cvtColor(c,cv2.COLOR_BGR2HSV)
halo=(ring>0)&(keep==0)&(hsv0[...,2]>150)&(hsv0[...,1]<90)&(hair>0.02)
a=np.clip(np.maximum.reduce([keep,ring*(hair>0.08),halo.astype(np.uint8)]).astype(np.float32),0,1)*(~body)
hsv=cv2.cvtColor(c,cv2.COLOR_BGR2HSV).astype(np.float32)
bow=np.clip((hsv[...,2]-140)/40,0,1)*np.clip((70-hsv[...,1])/30,0,1)*cv2.erode(keep,np.ones((5,5),np.uint8))   # bows sit INSIDE hair
a=cv2.GaussianBlur(a*(1-bow),(0,0),1.2)[...,None]
lab_=cv2.cvtColor(c,cv2.COLOR_BGR2LAB).astype(np.float32)
L=lab_[...,0]/255; l2=lab_.copy()
l2[...,0]=255*(0.06+0.22*np.power(L,2.2))          # jet-black with soft sheen, highlights compressed
l2[...,1]=128+(lab_[...,1]-128)*0.05; l2[...,2]=128+(lab_[...,2]-128)*0.05-2
d=cv2.cvtColor(np.clip(l2,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR).astype(np.float32)
im[y0:y0+B,x0:x0+B]=np.clip(c*(1-a)+d*a,0,255).astype(np.uint8)
cv2.imwrite(OUT,im)
