#!/bin/bash
# usage: join.sh out.mp4 clip1 clip2 ...  (re-encode concat + loudnorm)
out=$1; shift
args=(); f=""; i=0
for c in "$@"; do args+=(-i "$c"); f+="[$i:v]scale=1280:720,fps=24,setsar=1[v$i];[$i:a]aresample=48000,aformat=channel_layouts=stereo[a$i];"; i=$((i+1)); done
cat=""; for ((k=0;k<i;k++)); do cat+="[v$k][a$k]"; done
ffmpeg -v error -y "${args[@]}" -filter_complex "${f}${cat}concat=n=$i:v=1:a=1[v][a];[a]loudnorm=I=-14:TP=-1:LRA=11[an]" -map "[v]" -map "[an]" -c:v libx264 -crf 18 -preset medium -c:a aac -b:a 192k "$out"
