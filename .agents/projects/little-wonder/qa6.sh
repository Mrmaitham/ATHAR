#!/bin/bash
# usage: qa6.sh NAME URL START.png  -> qa5 + whisper (vad / no vad) + zoom sheet scratchpad/z_NAME.jpg (4 times: full frame,
# Nadyah head (found by royal-blue vest), Grandma head (darkest tall blob = abaya, upper part)) for reference checks.
cd /home/user/lw_v3
bash /home/user/lw_tools/qa5.sh $1 "$2" $3 2>&1 | tail -7
python3 /tmp/trv.py ${1}_k.mp4 | grep "|"; python3 /home/user/lw_tools/tr.py ${1}_k.mp4 | grep "|"
python3 - $1 <<'P'
import sys, subprocess, numpy as np
from PIL import Image
n=sys.argv[1]; f=n+'_k.mp4'
d=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
o=Image.new('RGB',(1600,850))
for i,t in enumerate([0.1, d*0.35, d*0.65, d-0.1]):
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',f,'-frames:v','1','-vf','scale=1280:720','/tmp/qz.png'])
    im=Image.open('/tmp/qz.png').convert('RGB'); a=np.asarray(im).astype(int)
    o.paste(im.resize((400,225)),(i*400,0))
    v=(a[...,2]>140)&(a[...,2]-a[...,0]>110)&(a[...,2]-a[...,1]>45); v[:200]=False
    ys,xs=np.nonzero(v)
    if len(xs)>300:
        cx=int(np.median(xs)); top=int(np.percentile(ys,2))
        o.paste(im.crop((cx-160,top-230,cx+160,top+90)).resize((400,400)),(i*400,225))
    dk=(a.mean(2)<45); dk[:, :0]=False
    cols=dk[:400].sum(0); 
    if cols.max()>60:
        gx=int(np.argmax(np.convolve(cols,np.ones(80),'same'))); gy=int(np.argmax(dk[:,gx-40:gx+40].sum(1)>10))
        o.paste(im.crop((gx-120,max(gy-40,0),gx+120,max(gy-40,0)+200)).resize((400,225)),(i*400,625))
o.save('/tmp/claude-0/-home-user-ATHAR/bf9b7122-c083-55f7-8a76-f3452131c4d4/scratchpad/z_'+n+'.jpg')
P
