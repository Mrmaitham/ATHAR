#!/bin/bash
# usage: lastframe.sh <shot#> <url>  -> downloads sNN.mp4, writes eNN.png (last frame) + eNN_prev.jpg
cd /home/user/lw_chain
n=$(printf "%02d" $((10#$1)))
curl -sS -o s$n.mp4 "$2"
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 s$n.mp4)
ffmpeg -v error -y -sseof -0.2 -i s$n.mp4 -frames:v 1 -update 1 e$n.png
ffmpeg -v error -y -i s$n.mp4 -vf "fps=1.5,scale=320:-2,tile=6x1" -frames:v 1 c$n.jpg
echo "shot $n dur=$d"
