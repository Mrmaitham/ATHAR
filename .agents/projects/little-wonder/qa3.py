#!/usr/bin/env python3
# usage: qa3.py NAME URL PREV_LAST_PNG KEY_START_PNG KEY_END_PNG
# downloads, checks cuts, transcript, keyframe/continuity diffs, colour gains to match prev last frame, writes graded NAME_g.mp4 (yuv420p) and NAME_last.png, contact sheet dNAME.jpg
import sys, subprocess, re
from PIL import Image, ImageStat, ImageChops
D="/home/user/lw_v3/"; n,url,prev,ks,ke=sys.argv[1:6]
run=lambda *a: subprocess.run(list(a),capture_output=True,text=True,stdin=subprocess.DEVNULL)
run("curl","-s","-o",D+n+".mp4",url)
vd=float(run("ffprobe","-v","error","-select_streams","v","-show_entries","stream=duration","-of","csv=p=0",D+n+".mp4").stdout)
print("duration",vd)
o=run("ffmpeg","-v","error","-i",D+n+".mp4","-vf","select='gt(scene,0.25)',showinfo","-f","null","-").stderr
print("cuts:",re.findall(r"pts_time:([\d.]+)",o))
def grab(t,out): run("ffmpeg","-v","error","-y","-ss",str(t),"-i",D+n+".mp4","-frames:v","1",D+out)
grab(0,n+"_first_raw.png"); grab(vd-0.05,n+"_last_raw.png")
def diff(a,b):
    A=Image.open(D+a).convert("L").resize((160,90)); B=Image.open(D+b).convert("L").resize((160,90))
    return round(ImageStat.Stat(ImageChops.difference(A,B)).mean[0],1)
print("first vs keystart",diff(n+"_first_raw.png",ks),"| first vs prev last",diff(n+"_first_raw.png",prev),"| last vs keyend",diff(n+"_last_raw.png",ke))
P=ImageStat.Stat(Image.open(D+prev).convert("RGB")).mean; F=ImageStat.Stat(Image.open(D+n+"_first_raw.png").convert("RGB")).mean
g=[p/f for p,f in zip(P,F)]; print("gains",[round(x,3) for x in g])
run("ffmpeg","-v","error","-y","-i",D+n+".mp4","-vf",f"colorchannelmixer=rr={g[0]:.3f}:gg={g[1]:.3f}:bb={g[2]:.3f},format=yuv420p","-c:v","libx264","-crf","17","-c:a","aac","-ar","48000",D+n+"_g.mp4")
gd=float(run("ffprobe","-v","error","-select_streams","v","-show_entries","stream=duration","-of","csv=p=0",D+n+"_g.mp4").stdout)
run("ffmpeg","-v","error","-y","-ss",str(gd-0.05),"-i",D+n+"_g.mp4","-frames:v","1",D+n+"_last.png")
run("ffmpeg","-v","error","-y","-ss","0","-i",D+n+"_g.mp4","-frames:v","1",D+n+"_first.png")
print("graded first vs prev last",diff(n+"_first.png",prev))
run("ffmpeg","-v","error","-y","-i",D+n+"_g.mp4","-vf","fps=2,scale=480:-1,drawtext=text='%{pts\\:flt}':x=5:y=5:fontsize=22:fontcolor=yellow:box=1,tile=4x4","-frames:v","1",D+"d"+n+".jpg")
# lamp detector: bright small spots in upper 45% of last graded frame
im=Image.open(D+n+"_last.png").convert("RGB"); px=im.load(); w,h=im.size
pts=[(x,y) for y in range(0,int(h*0.45)) for x in range(w) if sum(px[x,y])>700 and px[x,y][2]>215 and px[x,y][0]>215]
cl=[]
for p in pts:
    for c in cl:
        if abs(c[0]-p[0])<20 and abs(c[1]-p[1])<20: c[2]+=1; break
    else: cl.append([p[0],p[1],1])
print("BRIGHT SPOTS (check lamps/clouds):",[(c[0],c[1],c[2]) for c in cl if 3<c[2]<400])
