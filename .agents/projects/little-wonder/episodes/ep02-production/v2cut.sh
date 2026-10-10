#!/bin/bash
# Ep2 v2 review cut: approved shots, frozen starts trimmed, shot number burned in
V=/home/user/lw_v2; F=/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf
# shot:file:trim_start_seconds
LIST="1:s01:0.0 2:s02:0.3 3:s03:0.6 4:s04:0.4 5:s05b:0.5 6:s06:0.2 7:s07:0.15 8:s08:0.7 9:s09b:0.0 10:s10d:0.3 11:s11c:0.0 12:s12f:0.2 13:s13:0.0"
args=(); f=""; cat=""; i=0
for e in $LIST; do IFS=: read n file t <<< "$e"
  args+=(-ss "$t" -i "$V/$file.mp4")
  f+="[$i:v]scale=1280:720,fps=24,setsar=1,setpts=PTS-STARTPTS,drawtext=fontfile=$F:text='SHOT $n':fontsize=40:fontcolor=white:box=1:boxcolor=0x000000AA:boxborderw=12:x=24:y=24[v$i];[$i:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,afade=t=in:d=0.04[a$i];"
  cat+="[v$i][a$i]"; i=$((i+1)); done
ffmpeg -v error -y "${args[@]}" -filter_complex "${f}${cat}concat=n=$i:v=1:a=1[v][a];[a]loudnorm=I=-14:TP=-1:LRA=11[an]" -map "[v]" -map "[an]" -c:v libx264 -crf 22 -preset medium -c:a aac -b:a 160k "$1"
