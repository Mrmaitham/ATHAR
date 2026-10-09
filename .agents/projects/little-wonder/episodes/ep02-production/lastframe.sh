#!/bin/bash
# usage: lastframe.sh <shot#> <url>  -> downloads sNN.mp4, writes eNN.png (last frame) + eNN_prev.jpg
cd /home/user/lw_chain
n=$(printf "%02d" $((10#$1)))
curl -sS -o s$n.mp4 "$2"
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 s$n.mp4)
ffmpeg -v error -y -sseof -0.2 -i s$n.mp4 -frames:v 1 -update 1 e$n.png
ffmpeg -v error -y -i s$n.mp4 -vf "fps=1.5,scale=320:-2,tile=6x1" -frames:v 1 c$n.jpg
echo "shot $n dur=$d"
cuts=$(ffmpeg -v info -i s$n.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep -o "pts_time:[0-9.]*" | tr '\n' ' ')
[ -n "$cuts" ] && echo "HARD CUTS: $cuts"
ffmpeg -v error -y -ss 4 -i s$n.mp4 -vf "fps=1.5,scale=320:-2,tile=6x1" -frames:v 1 c${n}b.jpg 2>/dev/null && ffmpeg -v error -y -i c$n.jpg -i c${n}b.jpg -filter_complex vstack c${n}all.jpg 2>/dev/null
python3 -I /home/user/lw_tools/tr.py s$n.mp4 2>&1 | grep -v Warn
