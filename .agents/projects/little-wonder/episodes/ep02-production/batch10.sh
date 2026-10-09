#!/bin/bash
# Review cuts of 10 shots each, shot number burned in. Uses approved fixes for 3-10.
C=/home/user/lw_chain; X=/home/user/lw_fix; F=/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf
OUT=${1:-/home/user/ATHAR/.agents/projects/little-wonder/episodes/ep02-renders/review10}; mkdir -p $OUT
declare -A FIX=([3]=$X/s03fix.mp4 [4]=$X/s04fix.mp4 [5]=$X/s05fix_t.mp4 [6]=$X/s06fix2.mp4 [7]=$X/s07fix.mp4 [8]=$X/s08fix.mp4 [9]=$X/s09fix2.mp4 [10]=$X/s10fix.mp4)
clip(){ [ -n "${FIX[$1]}" ] && echo "${FIX[$1]}" || printf "$C/s%02d.mp4" $1; }
for s in $(seq 1 10 73); do
  e=$((s+9)); [ $e -gt 73 ] && e=73
  args=(); f=""; cat=""; i=0
  for n in $(seq $s $e); do
    args+=(-i "$(clip $n)")
    f+="[$i:v]scale=1280:720,fps=24,setsar=1,drawtext=fontfile=$F:text='SHOT $n':fontsize=40:fontcolor=white:box=1:boxcolor=0x000000AA:boxborderw=12:x=24:y=24[v$i];[$i:a]aresample=48000,aformat=channel_layouts=stereo[a$i];"
    cat+="[v$i][a$i]"; i=$((i+1))
  done
  o=$(printf "$OUT/ep02_shots%02d-%02d.mp4" $s $e)
  ffmpeg -v error -y "${args[@]}" -filter_complex "${f}${cat}concat=n=$i:v=1:a=1[v][a];[a]loudnorm=I=-14:TP=-1:LRA=11[an]" -map "[v]" -map "[an]" -c:v libx264 -crf 22 -preset medium -c:a aac -b:a 160k "$o" && echo "$o $(du -m "$o" | cut -f1)MB $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$o")s"
done
