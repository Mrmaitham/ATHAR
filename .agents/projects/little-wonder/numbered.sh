#!/bin/bash
# Build Ep2 review cut with a shot-number label burned on every clip
C=/home/user/lw_chain; E=/home/user/lw_edit; F=/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf
L=(); T=()
add(){ L+=("$1"); T+=("$2"); }
add $C/s36.mp4 "HOOK - 36"; add $C/s35.mp4 "HOOK - 35"; add $E/intro_song.mp4 "INTRO"
add $C/s01.mp4 1; add $C/s02.mp4 2; add $C/s03.mp4 3; add $C/s04.mp4 4; add $C/s05t.mp4 5
for n in $(seq 6 35); do add $(printf "$C/s%02d.mp4" $n) $n; done
add $E/card_day2.mp4 CARD; add $C/s36.mp4 36; add $C/s37.mp4 37; add $E/card_day3.mp4 CARD; add $C/s38.mp4 38
add $E/card_day4.mp4 CARD; add $C/s39.mp4 39; add $C/s40.mp4 40; add $C/s41.mp4 41; add $E/card_day5.mp4 CARD
for n in $(seq 42 60); do add $C/s$n.mp4 $n; done
add $E/card_next.mp4 CARD; add $C/s61.mp4 61; add $E/card_few.mp4 CARD
for n in $(seq 62 66); do add $C/s$n.mp4 $n; done
add $E/card_week.mp4 CARD; for n in $(seq 67 73); do add $C/s$n.mp4 $n; done
add $E/outro.mp4 OUTRO
args=(); f=""; i=0
for k in "${!L[@]}"; do
  args+=(-i "${L[$k]}"); t="${T[$k]}"; case "$t" in [0-9]*) t="SHOT $t";; esac
  f+="[$i:v]scale=1280:720,fps=24,setsar=1,drawtext=fontfile=$F:text='$t':fontsize=40:fontcolor=white:box=1:boxcolor=0x000000AA:boxborderw=12:x=24:y=24[v$i];[$i:a]aresample=48000,aformat=channel_layouts=stereo[a$i];"
  i=$((i+1)); done
cat=""; for ((k=0;k<i;k++)); do cat+="[v$k][a$k]"; done
ffmpeg -v error -y "${args[@]}" -filter_complex "${f}${cat}concat=n=$i:v=1:a=1[v][a];[a]loudnorm=I=-14:TP=-1:LRA=11[an]" -map "[v]" -map "[an]" -c:v libx264 -crf 20 -preset medium -c:a aac -b:a 160k "$1"
