#!/bin/bash
# Full numbered review cut of Ep2 v2 (approved versions). entry = label:file:trim ; label "-" = no number (title card)
V=/home/user/lw_v2; F=/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf
LIST="1:s01:0.0 2:s02:0.3 3:s03:0.6 4:s04:0.4 5:s05b:0.5 6:s06:0.2 7:s07:0.15 8:s08:0.7 9:s09b:0.0 10:s10d:0.3 11:s11c:0.0 12:s12f:0.2 13:s13b:0.0 -:card_nextday:0.0 14:s14_g:0.0 15:s15b_g:0.0 16:s16b_g:0.0 17:s17b_g:0.0 18:s18_g:0.0 19:s19_g:0.0 20:s20_g:0.0 21:s21_g:0.0 22:s22b_g:0.0 23:s23b_g:0.0 24:s24b_g:0.0 25:s25c_g:0.0 26:r26_g:0.0 27:r27_g:0.0 28:r28_g:0.0 29:r29_g:0.0 30:r30_g:0.0 31:r31_g:0.0"
args=(); f=""; cat=""; i=0
for e in $LIST; do IFS=: read n file t <<< "$e"
  args+=(-ss "$t" -i "$V/$file.mp4")
  if [ "$n" = "-" ]; then dt=""; else dt=",drawtext=fontfile=$F:text='SHOT $n':fontsize=40:fontcolor=white:box=1:boxcolor=0x000000AA:boxborderw=12:x=24:y=24"; fi
  f+="[$i:v]scale=1280:720,fps=24,setsar=1,format=yuv420p,setpts=PTS-STARTPTS$dt[v$i];[$i:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,afade=t=in:d=0.04[a$i];"
  cat+="[v$i][a$i]"; i=$((i+1)); done
ffmpeg -v error -y "${args[@]}" -filter_complex "${f}${cat}concat=n=$i:v=1:a=1[vc][a];[vc]format=yuv420p[v];[a]loudnorm=I=-14:TP=-1:LRA=11[an]" -map "[v]" -map "[an]" -c:v libx264 -crf 25 -preset medium -c:a aac -b:a 128k -movflags +faststart "$1"
