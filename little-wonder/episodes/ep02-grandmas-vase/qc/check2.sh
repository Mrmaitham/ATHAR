#!/bin/bash
# fast part of the check: abaya colour + transcript (small.en)
N=$1
python3 - "$N" <<'PY'
import sys,subprocess,numpy as np
n=sys.argv[1];f=f"shots/shot{n}.mp4"
for t in (0.3,2.5,-0.2):
    a=["ffmpeg","-v","error"]+(["-sseof",str(t)] if t<0 else ["-ss",str(t)])+["-i",f,"-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"]
    b=subprocess.run(a,capture_output=True).stdout
    im=np.frombuffer(b,np.uint8).reshape(720,1280,3).astype(float)[150:600,820:1150].reshape(-1,3)
    L=im.mean(1);d=im[(L<60)&(L>8)]
    if len(d)<500: print("abaya t",t,": none");continue
    m=d.mean(0);print("abaya t",t,m.round().astype(int).tolist(),"OK" if (m[0]<=55 and m[0]-m[2]<=22) else "!! BROWN")
PY
python3 -c "
from faster_whisper import WhisperModel
m=WhisperModel('small.en',compute_type='int8')
s,_=m.transcribe('shots/shot$N.mp4',word_timestamps=True)
print([(w.word,round(w.start,2)) for x in s for w in x.words])" 2>/dev/null
