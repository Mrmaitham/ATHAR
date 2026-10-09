#!/bin/bash
# usage: qc/check.sh NN PREV URL  — download, QC, face/tail crops, transcript
S=/tmp/claude-0/-home-user-ATHAR/808f4051-f44a-5338-a794-9ee8e53308d1/scratchpad
N=$1; P=$2; U=$3
[ -n "$U" ] && curl -sS -o shots/shot$N.mp4 "$U"
bash qc/qc.sh $N $P 2>&1 | tail -6 | grep -v rms
ffmpeg -loglevel error -y -i shots/shot$N.mp4 -vf "fps=8,crop=300:70:740:130,scale=200:-1,tile=8x5" -frames:v 1 $S/f.png
ffmpeg -loglevel error -y -i shots/shot$N.mp4 -vf "fps=2,crop=500:300:780:340,scale=320:-1,tile=5x2" -frames:v 1 $S/t.png
python3 -c "
from faster_whisper import WhisperModel
m=WhisperModel('medium.en',compute_type='int8')
s,_=m.transcribe('shots/shot$N.mp4',word_timestamps=True)
print([(w.word,round(w.start,2),round(w.end,2)) for x in s for w in x.words])
" 2>/dev/null
# Grandma's abaya must stay black (reference). Darkest cloth pixels in her usual box (right side of the wide living-room frame).
python3 - "$N" <<'PY'
import sys,subprocess,numpy as np
n=sys.argv[1];f=f"shots/shot{n}.mp4"
for t in (0.3,2.5,-0.2):
    a=["ffmpeg","-v","error"]+(["-sseof",str(t)] if t<0 else ["-ss",str(t)])+["-i",f,"-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"]
    b=subprocess.run(a,capture_output=True).stdout
    if len(b)!=1280*720*3: continue
    im=np.frombuffer(b,np.uint8).reshape(720,1280,3).astype(float)[330:520,890:1090].reshape(-1,3)
    L=im.mean(1);d=im[(L<90)&(L>15)]
    if len(d)<200: print("abaya t",t,": not in box");continue
    m=d.mean(0);ok=m[0]<=55 and m[0]-m[2]<=22
    print("abaya t",t,m.round().astype(int).tolist(),"OK" if ok else "!! BROWN DRIFT — reject")
PY
