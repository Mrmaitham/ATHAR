#!/bin/bash
# usage: fixshot.sh NAME [x y r ...]   (NAME_k.mp4 -> NAME_f.mp4 + NAME_flast.png + lamp contact strip lf_NAME.jpg)
# 1) optional wall-lamp glass positions (mid frame) -> lampoff.py MID; 2) dotkill over the house band; 3) strip for review.
cd /home/user/lw_v3; N=$1; shift; IN=${N}_k.mp4
if [ $# -gt 0 ]; then FR=$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $IN)
  MID=$((FR/2)) python3 /home/user/lw_tools/lampoff.py $IN ${N}_lo.mp4 "$@" > /dev/null; IN=${N}_lo.mp4; fi
python3 /home/user/lw_tools/dotkill.py $IN ${N}_f.mp4 0 30 1280 330 | tail -1
ffmpeg -y -loglevel error -sseof -0.3 -i ${N}_f.mp4 -frames:v 1 -update 1 ${N}_flast.png
python3 - ${N}_f.mp4 /tmp/claude-0/-home-user-ATHAR/bf9b7122-c083-55f7-8a76-f3452131c4d4/scratchpad/lf_$N.jpg <<'P'
import sys, subprocess
from PIL import Image
d = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',sys.argv[1]],capture_output=True,text=True).stdout)
o = Image.new('RGB', (1280, 3*200))
for i, t in enumerate([0.15*d, 0.5*d, 0.95*d]):
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',sys.argv[1],'-frames:v','1','/tmp/fx.png'])
    o.paste(Image.open('/tmp/fx.png').convert('RGB').resize((1280,720)).crop((0,40,1280,240)), (0, i*200))
o.save(sys.argv[2])
P
