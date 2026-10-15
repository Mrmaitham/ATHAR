import sys, subprocess, json, os, hashlib
import numpy as np
from PIL import Image
# usage: cut2.py OUT.mp4 items.json   items=[[file,label,override_or_null],...]
out, items = sys.argv[1], json.load(open(sys.argv[2]))
def frame(f, last):
    p='fr/'+hashlib.md5((f+str(last)).encode()).hexdigest()+'.png'
    if not os.path.exists(p):
        a=['ffmpeg','-v','error','-y']+(['-sseof','-0.1'] if last else [])+['-i',f,'-frames:v','1','-vf','scale=96:54',p]
        subprocess.run(a+['-update','1'],check=True)
        if not os.path.exists(p): subprocess.run(['ffmpeg','-v','error','-y','-sseof','-1','-i',f,'-vf','scale=96:54','-update','1',p],check=True)
    return np.asarray(Image.open(p).convert('RGB'),dtype=float)/255
def auto(a,b):
    d=float(np.abs(frame(a,True)-frame(b,False)).mean())
    return (0.4 if d<0.04 else 0.5 if d<0.10 else 0.6 if d<0.18 else 0.7), d
dur=lambda f: float(subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=duration","-of","csv=p=0",f],capture_output=True,text=True).stdout.split()[0])
clips=[i[0] for i in items]; D=[dur(c) for c in clips]
ds=[]
for i in range(len(items)-1):
    o=items[i][2]
    if o is None:
        d,diff=auto(clips[i],clips[i+1]); print(i,items[i][1],'->',items[i+1][1],'diff %.3f d %.2f'%(diff,d),flush=True)
    else: d=o
    ds.append(min(d, D[i]*0.45, D[i+1]*0.45))
inp=sum([["-i",c] for c in clips],[]); f=[]
for i in range(len(clips)):
    t_=items[i][1]
    lab=f",drawtext=text='{t_}':x=20:y=16:fontsize=40:fontcolor=white:borderw=3:bordercolor=black" if t_ else ""
    f.append(f"[{i}:v]scale=1280:720,fps=24,setsar=1,format=yuv420p,settb=AVTB{lab}[v{i}];[{i}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,apad,atrim=0:{D[i]:.4f}[a{i}]")
v,au,t="v0","a0",D[0]
for i in range(1,len(clips)):
    d=ds[i-1]
    f.append(f"[{v}][v{i}]xfade=transition=fade:duration={d:.3f}:offset={t-d:.3f}[vx{i}];[{au}][a{i}]acrossfade=d={d:.3f}[ax{i}]"); t=t-d+D[i]
    v,au=f"vx{i}",f"ax{i}"
f.append(f"[{au}]loudnorm=I=-14:TP=-1:LRA=11,aresample=48000[aout]")
subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",";".join(f),"-map",f"[{v}]","-map","[aout]","-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-movflags","+faststart","-c:a","aac","-b:a","160k","-ar","48000",out],check=True)
print("ok",out,round(t,2))
