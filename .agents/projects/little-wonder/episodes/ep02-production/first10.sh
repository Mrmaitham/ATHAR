#!/bin/bash
# Review cut: shots 1-10 with approved fixes for 3,4,5, shot number burned in
C=/home/user/lw_chain; X=/home/user/lw_fix; F=/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf
L=($C/s01.mp4 $C/s02.mp4 $X/s03fix.mp4 $X/s04fix.mp4 $X/s05fix_t.mp4 $C/s06.mp4 $C/s07.mp4 $C/s08.mp4 $C/s09.mp4 $C/s10.mp4)
args=(); f=""; cat=""
for i in "${!L[@]}"; do
  args+=(-i "${L[$i]}")
  f+="[$i:v]scale=1280:720,fps=24,setsar=1,drawtext=fontfile=$F:text='SHOT $((i+1))':fontsize=40:fontcolor=white:box=1:boxcolor=0x000000AA:boxborderw=12:x=24:y=24[v$i];[$i:a]aresample=48000,aformat=channel_layouts=stereo[a$i];"
  cat+="[v$i][a$i]"
done
ffmpeg -v error -y "${args[@]}" -filter_complex "${f}${cat}concat=n=${#L[@]}:v=1:a=1[v][a];[a]loudnorm=I=-14:TP=-1:LRA=11[an]" -map "[v]" -map "[an]" -c:v libx264 -crf 22 -preset medium -c:a aac -b:a 160k "$1"
