#!/bin/bash
# usage: qa5.sh NAME URL PREV_LAST.png  -> qv (cuts, first-vs-prev, sky fix -> NAME_k.mp4, whisper medium, contact sheet tNAME.jpg)
#        + house-band stability vs PREV, morph check, lamp brightness trend (top 40% of frame)
cd /home/user/lw_v3
bash /home/user/lw_tools/qv.sh $1 "$2" $3 $3 2>&1 | grep -E "cuts|first vs|graded|duration|@" | cut -c1-300
python3 /home/user/lw_tools/housecheck.py ${1}_k.mp4 $3 | tail -1
python3 /tmp/claude-0/-home-user-ATHAR/bf9b7122-c083-55f7-8a76-f3452131c4d4/scratchpad/mc2.py ${1}_k.mp4 | tail -1
python3 - ${1}_k.mp4 <<'P'
import sys, subprocess, numpy as np
raw = subprocess.run(['ffmpeg','-v','error','-i',sys.argv[1],'-vf','fps=2,scale=640:360','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
F = np.frombuffer(raw,np.uint8).reshape(-1,360,640,3).astype(np.float32)
# warm small bright blobs = lamps: count pixels R>235,G>200,B<190 in top 45%
c = [int(((f[:162,:,0]>235)&(f[:162,:,1]>200)&(f[:162,:,2]<190)).sum()) for f in F]
print('lamp-px', ' '.join(map(str,c)), '| rise', max(c)-c[0])
P
