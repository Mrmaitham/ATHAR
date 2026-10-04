#!/usr/bin/env python3
# usage: grade.py NN [NN...] — match each shot's ceiling band to shot 37's light
# per-channel curve f(x)=255*(1-(1-x/255)^k): blacks stay black, highlights roll off; k interpolated over time
import subprocess,sys,numpy as np,os
os.chdir(os.path.join(os.path.dirname(__file__),".."))
TARGET=np.array([175.,140.,108.])
def fr(x,ss):
    a=["ffmpeg","-v","error","-ss",str(ss),"-i",x,"-frames:v","1","-vf","scale=320:180","-f","rawvideo","-pix_fmt","rgb24","-"]
    return np.frombuffer(subprocess.run(a,capture_output=True).stdout,np.uint8).reshape(180,320,3).astype(float)
def dur(f): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f],capture_output=True,text=True).stdout)
def gam(px,t):
    lo,hi=0.5,3.0
    for _ in range(40):
        m=(lo+hi)/2
        if (255*(1-(1-px/255)**m)).mean()<t: lo=m
        else: hi=m
    return (lo+hi)/2
for n in sys.argv[1:]:
    f=f"shots/shot{n}.mp4"; d=dur(f)
    g=[[gam(fr(f,t)[:50,:,c].ravel(),TARGET[c]) for c in range(3)] for t in (0,d-0.15)]
    e=lambda c,ch:f"255*(1-pow(1-{ch}(X,Y)/255,{g[0][c]:.4f}+({g[1][c]-g[0][c]:.4f})*min(T/{d:.3f},1)))"
    # de-rainbow: in the ceiling band (top 32%), any pixel bluer than red = streak -> pull it back to the warm ceiling tone
    cond="lt(Y,H*0.32)*gt(r(X,Y),110)*(gt(b(X,Y),r(X,Y)*0.9)+gt(g(X,Y),r(X,Y)*0.95))"
    dr=f"geq=r='r(X,Y)':g='if({cond},r(X,Y)*0.80,g(X,Y))':b='if({cond},r(X,Y)*0.63,b(X,Y))'"
    vf=f"format=rgb24,{dr},geq=r='{e(0,'r')}':g='{e(1,'g')}':b='{e(2,'b')}',format=yuv420p"
    out=f"shots_graded/shot{n}.mp4"
    subprocess.run(["ffmpeg","-y","-v","error","-i",f,"-vf",vf,"-c:v","libx264","-profile:v","high","-crf","18","-c:a","copy","-movflags","+faststart",out],check=True)
    print(n,"k start",np.round(g[0],3),"end",np.round(g[1],3))
