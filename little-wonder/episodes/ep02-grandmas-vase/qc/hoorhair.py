#!/usr/bin/env python3
# usage: hoorhair.py IN OUT x0 y0 x1 y1 [model_dir]
# darken Hoor's hair to jet-black inside box (x0,y0)-(x1,y1): mediapipe multiclass hair mask (class 1),
# keeps shading (L curve) + cream bows (low-sat bright pixels protected), mask smoothed over time
import sys,subprocess,numpy as np,cv2,os,mediapipe as mp
from mediapipe.tasks.python import vision,BaseOptions
IN,OUT=sys.argv[1],sys.argv[2]; x0,y0,x1,y1=map(int,sys.argv[3:7])
MD=sys.argv[7] if len(sys.argv)>7 else os.path.join(os.path.dirname(__file__),'models')
seg=vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=MD+'/selfie_multiclass.tflite'),output_confidence_masks=True))
W,H=1280,720
info=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate','-of','csv=p=0',IN],capture_output=True,text=True).stdout.strip().split(',')
W,H=int(info[0]),int(info[1]); fps=info[2]
dec=subprocess.Popen(['ffmpeg','-v','error','-i',IN,'-f','rawvideo','-pix_fmt','bgr24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',fps,'-i','-','-i',IN,'-map','0:v','-map','1:a?','-c:v','libx264','-profile:v','high','-crf','18','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
prev=None;n=0
while True:
    b=dec.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    f=np.frombuffer(b,np.uint8).reshape(H,W,3).copy()
    c=f[y0:y1,x0:x1]; s=512
    big=cv2.resize(c,(s,s)); r=seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,data=cv2.cvtColor(big,cv2.COLOR_BGR2RGB)))
    m=cv2.resize(np.squeeze(r.confidence_masks[1].numpy_view()).astype(np.float32),(x1-x0,y1-y0))
    m=prev*0.4+m*0.6 if prev is not None else m; prev=m
    hsv=cv2.cvtColor(c,cv2.COLOR_BGR2HSV).astype(np.float32)
    bow=np.clip((hsv[...,2]-150)/40,0,1)*np.clip((80-hsv[...,1])/30,0,1)   # cream bows stay
    a=np.clip((m-0.3)/0.4,0,1)*(1-bow); a=cv2.GaussianBlur(a,(0,0),1.5)[...,None]
    lab=cv2.cvtColor(c,cv2.COLOR_BGR2LAB).astype(np.float32)
    L=lab[...,0]/255; lab2=lab.copy()
    lab2[...,0]=255*np.power(L,1.8)*0.72
    lab2[...,1]=128+(lab[...,1]-128)*0.22; lab2[...,2]=128+(lab[...,2]-128)*0.22
    d=cv2.cvtColor(np.clip(lab2,0,255).astype(np.uint8),cv2.COLOR_LAB2BGR).astype(np.float32)
    f[y0:y1,x0:x1]=np.clip(c*(1-a)+d*a,0,255).astype(np.uint8)
    enc.stdin.write(f.tobytes()); n+=1
enc.stdin.close(); enc.wait(); print('frames',n)
