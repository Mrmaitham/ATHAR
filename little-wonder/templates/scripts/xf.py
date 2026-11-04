import subprocess,numpy as np,json
G="/tmp/claude-0/-home-user-ATHAR/808f4051-f44a-5338-a794-9ee8e53308d1/scratchpad/build/g3/"
L=[G+l.split("'")[1] for l in open(G+"list.txt") if l.startswith("file")]
L[0]="/tmp/claude-0/-home-user-ATHAR/808f4051-f44a-5338-a794-9ee8e53308d1/scratchpad/op/intro_named2.mp4"
L[-1]="/tmp/claude-0/-home-user-ATHAR/808f4051-f44a-5338-a794-9ee8e53308d1/scratchpad/op/outro_named.mp4"
FPS=24
def nfr(f):
    o=subprocess.run(["ffprobe","-v","error","-count_packets","-select_streams","v","-show_entries","stream=nb_read_packets","-of","csv=p=0",f],capture_output=True,text=True).stdout
    return int(o.strip())
def fr(f,ss):
    b=subprocess.run(["ffmpeg","-v","error"]+(["-sseof",str(ss)] if ss<0 else ["-ss",str(ss)])+["-i",f,"-frames:v","1","-vf","scale=64:36,format=gray","-f","rawvideo","-"],capture_output=True).stdout
    return np.frombuffer(b,np.uint8).astype(float)
N=[nfr(f) for f in L]
D=[]  # transition frames between i and i+1
for i in range(len(L)-1):
    if i==0 or i==len(L)-2: D.append(14); continue
    c=np.abs(fr(L[i],-0.05)-fr(L[i+1],0)).mean()
    D.append(6)
P=[N[i]+(D[i-1]//2 if i>0 else 0)+(D[i]//2 if i<len(L)-1 else 0) for i in range(len(L))]
fc=[]
for i in range(len(L)):
    a=D[i-1]//2 if i>0 else 0; b=D[i]//2 if i<len(L)-1 else 0
    fc.append(f"[{i}:v]fps={FPS},settb=1/{FPS},format=yuv420p,tpad=start={a}:start_mode=clone:stop={b}:stop_mode=clone,setpts=PTS-STARTPTS[p{i}]")
acc=0;prev="p0"
for i in range(len(L)-1):
    acc+=P[i]
    off=(acc-sum(D[:i])-D[i])/FPS
    fc.append(f"[{prev}][p{i+1}]xfade=transition=fade:duration={D[i]/FPS:.6f}:offset={off:.6f}[x{i}]")
    prev=f"x{i}"
open(G+"xf_fc.txt","w").write(";".join(fc))
open(G+"xf_inputs.txt","w").write("\n".join(L)+"\n")
print("frames",sum(N),"out",sum(P)-sum(D),"soft",D.count(6),"dissolve",D.count(10),"last",prev)
