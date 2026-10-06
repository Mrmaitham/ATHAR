#!/usr/bin/env python3
# abayatone.py IN.mp4 OUT.mp4 x0 y0 x1 y1 — per frame, darken Grandma's abaya/hijab (dark warm pixels in the box)
# to the reference black [40,28,21] (as in shot 47 v4). Same fabric, only tone — skin/highlights fade out of the mask.
import sys,subprocess,numpy as np
from PIL import Image,ImageFilter
src,dst=sys.argv[1],sys.argv[2];x0,y0,x1,y1=map(int,sys.argv[3:7])
W,H=1280,720;ref=np.array([30,27,26.]);tint=ref/ref.mean()   # ref = characters_lineup_clean.png abaya (neutral black)
fps=subprocess.run(["ffprobe","-v","error","-select_streams","v","-show_entries","stream=r_frame_rate","-of","csv=p=0",src],capture_output=True,text=True).stdout.strip()
dec=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",fps,"-i","-","-i",src,"-map","0:v","-map","1:a?","-c:v","libx264","-profile:v","high","-crf","18","-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",dst],stdin=subprocess.PIPE)
while True:
    b=dec.stdout.read(W*H*3)
    if len(b)<W*H*3: break
    im=np.frombuffer(b,np.uint8).reshape(H,W,3).astype(float)
    bx=im[y0:y1,x0:x1];L=bx.mean(2)
    cl=bx[(L<75)&(L>8)]
    if len(cl)>500:
        k=min(1.0,ref.mean()/cl.mean())
        w=np.clip((95-L)/20,0,1)*(bx[...,0]>=bx[...,2])   # L<75 full, fades out by 95 (protects tray wood/skin)
        m=np.zeros((H,W));m[y0:y1,x0:x1]=w
        m=np.array(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1))).astype(float)[...,None]/255
        im=im.mean(2,keepdims=True)*k*tint*m+im*(1-m)
    enc.stdin.write(im.clip(0,255).astype(np.uint8).tobytes())
enc.stdin.close();enc.wait()
