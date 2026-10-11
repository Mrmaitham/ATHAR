#!/bin/bash
# usage: qa.sh NAME URL PREV_GRADED   -> downloads, contact sheet, end frame, cut check, matchgrade, transcript
set -e; cd /home/user/lw_v2; N=$1; U=$2; P=$3
curl -s -o $N.mp4 "$U"
ffprobe -v error -show_entries format=duration -of csv=p=0 $N.mp4
ffmpeg -v error -y -i $N.mp4 -vf "fps=2,scale=480:-1,tile=4x3" -frames:v 1 c_$N.jpg
ffmpeg -v error -y -sseof -0.3 -i $N.mp4 -frames:v 1 -update 1 e_$N.png
ffmpeg -v error -y -i e_$N.png -vf "scale=960:-1" z_$N.jpg
echo "cuts: $(ffmpeg -v error -i $N.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep -o 'pts_time:[0-9.]*' | tr '\n' ' ')"
PT=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $P | awk '{printf "%.1f",$1-0.2}')
python3 /home/user/lw_tools/matchgrade.py $N.mp4 ${N}_g.mp4 $P $PT first
timeout 300 python3 /home/user/lw_tools/tr.py $N.mp4 2>/dev/null | tail -1 || true
