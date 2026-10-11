#!/bin/bash
# usage: xf.sh out.mp4 a.mp4 b.mp4 [dissolve_seconds]  (0 = hard cut). Output yuv420p/aac 48k.
out=$1; a=$2; b=$3; d=${4:-0}
if [ "$d" = "0" ]; then
  ffmpeg -v error -y -i "$a" -i "$b" -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][au];[v]format=yuv420p[vo]" -map "[vo]" -map "[au]" -c:v libx264 -crf 17 -profile:v high -movflags +faststart -c:a aac -ar 48000 "$out"
else
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$a"); O=$(python3 -c "print($D-$d)")
  ffmpeg -v error -y -i "$a" -i "$b" -filter_complex "[0:v][1:v]xfade=transition=fade:duration=$d:offset=$O,format=yuv420p[v];[0:a][1:a]acrossfade=d=$d[au]" -map "[v]" -map "[au]" -c:v libx264 -crf 17 -profile:v high -movflags +faststart -c:a aac -ar 48000 "$out"
fi
