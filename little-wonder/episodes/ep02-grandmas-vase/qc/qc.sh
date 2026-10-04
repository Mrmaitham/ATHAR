#!/bin/bash
# usage: qc.sh <NN> <prevNN>  — QC report for shots/shotNN.mp4
set -e
cd "$(dirname "$0")/.."
N=$1; P=$2; F=shots/shot$N.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $F); echo "duration $D"
ffmpeg -y -v error -i $F -vf "fps=2,scale=400:-1,tile=4x3" -frames:v 1 qc/shot${N}_sheet.png
L=$(python3 -c "print(round($D-0.1,2))"); M=$(python3 -c "print(round($D/2,2))")
for t in 0 $M $L; do ffmpeg -y -v error -ss $t -i $F -frames:v 1 qc/_t$t.png; done
ffmpeg -y -v error -i qc/_t0.png -i qc/_t$M.png -i qc/_t$L.png -filter_complex "[0][1][2]vstack=3,scale=960:-1" qc/shot${N}_check3.png
cp qc/_t$L.png qc/shot${N}_last.png
ffmpeg -y -v error -i qc/shot${P}_last.png -i qc/_t0.png -filter_complex "[0]scale=640:-1[a];[1]scale=640:-1[b];[a][b]hstack" qc/shot${N}_vs_prev.png
rm qc/_t*.png
python3 - "$F" "qc/shot${P}_last.png" <<'P'
import subprocess,sys,numpy as np
f,prev=sys.argv[1],sys.argv[2]
def g(x,ss=None):
    a=["ffmpeg","-v","error"]+(["-ss",str(ss)] if ss is not None else [])+["-i",x,"-frames:v","1","-vf","scale=64:36,format=gray","-f","rawvideo","-"]
    return np.frombuffer(subprocess.run(a,capture_output=True).stdout,np.uint8).astype(float)
def band(x,ss):
    a=["ffmpeg","-v","error"]+(["-sseof",str(ss)] if ss<0 else ["-ss",str(ss)])+["-i",x,"-frames:v","1","-vf","scale=160:90","-f","rawvideo","-pix_fmt","rgb24","-"]
    r=np.frombuffer(subprocess.run(a,capture_output=True).stdout,np.uint8).reshape(90,160,3).astype(float)
    return r[:25].reshape(-1,3).mean(0).round(0).tolist()
print("light (ceiling RGB, target ~[175,140,108]): start",band(f,0),"end",band(f,-0.15))
def glare(x,ss):
    a=["ffmpeg","-v","error"]+(["-sseof",str(ss)] if ss<0 else ["-ss",str(ss)])+["-i",x,"-frames:v","1","-vf","scale=320:180","-f","rawvideo","-pix_fmt","rgb24","-"]
    r=np.frombuffer(subprocess.run(a,capture_output=True).stdout,np.uint8).reshape(180,320,3).astype(float)[:50]
    mx=r.max(2);mn=r.min(2);sat=(mx-mn)/(mx+1)
    # hue spread: blue/purple pixels on a warm ceiling = rainbow streaks
    cool=((r[:,:,2]>r[:,:,0])&(mx>120)).mean()*100
    return round(float(np.abs(np.diff(r.mean(2),axis=1)).mean()),2), round(cool,2)
print("ceiling streaks (edge, %cool px) [anchor ~ low]: start",glare(f,0),"end",glare(f,-0.15))
print("diff:",round(abs(g(prev)-g(f,0)).mean(),2))
raw=subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
x=np.frombuffer(raw,np.int16).astype(float)
r=[int(np.sqrt((x[i:i+1600]**2).mean())) for i in range(0,len(x),1600)]
print("rms/0.1s:",r)
seg=[];on=None
for i,v in enumerate(r):
    if v>1000 and on is None: on=i
    if v<=1000 and on is not None: seg.append((on/10,i/10)); on=None
if on is not None: seg.append((on/10,len(r)/10))
print("loud segments:",seg)
P
